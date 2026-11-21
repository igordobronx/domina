import logging
import mimetypes
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import correcao as ia
from app import correcao_exatas as ia_exatas
from app.erros import registrar_erros
from app.correcao import NOTAS_VALIDAS
from app.auditoria import registrar
from app.auth.dependencies import get_current_user
from app.config import settings
from app.custo import registrar_uso
from app.database import get_db
from app.ia import memoria, registro
from app.models.enum import PerfilEnum, StatusCorrecaoEnum, TipoEnvioEnum, TipoMateriaEnum
from app.models.usuario import (
    Atividade, Correcao, CorrecaoCriterio, DominioAluno, Materia, Submissao, Tema, Usuario,
)
from app.competencias import garantir_competencias
from app.metas import avaliar_seguro
from app.routers.submissoes import MATERIAS_EXATAS, _gestor_da_escola, caminhos_da_submissao, _professor_da_turma, _submissao_visivel
from app.schemas.submissao import AprovarRequest, AvaliacaoIARequest, CorrecaoResponse, CorrigirRequest, CriterioResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["correcoes"])

# abaixo disso a correcao vai para o topo da fila do professor (RF-17/RF-23)
CONFIANCA_MINIMA = 0.6


def _correcao_response(db: Session, correcao: Correcao) -> CorrecaoResponse:
    criterios = (
        db.query(CorrecaoCriterio, Tema).join(Tema, Tema.id == CorrecaoCriterio.tema_id)
        .filter(CorrecaoCriterio.correcao_id == correcao.id).order_by(Tema.habilidade_codigo)
    )
    return CorrecaoResponse(
        id=correcao.id, submissao_id=correcao.submissao_id, nota_ia=float(correcao.nota_ia),
        nota_professor=float(correcao.nota_professor) if correcao.nota_professor is not None else None,
        revisado_por=correcao.revisado_por,
        confianca=float(correcao.confianca), status=correcao.status.value, modelo_usado=correcao.modelo_usado,
        feedback=correcao.feedback,
        avaliacao_ia="BOA" if correcao.boa_correcao else "MA" if correcao.explicacao_ruim else "MEDIA" if correcao.correcao_razoavel else None,
        criterios=[
            CriterioResponse(
                codigo=t.habilidade_codigo, nome=t.nome, nota=float(c.nota),
                nota_professor=float(c.nota_professor) if c.nota_professor is not None else None,
                justificativa=c.justificativa, pontos=c.pontos or [],
            )
            for c, t in criterios
        ],
    )


def _so_professor(db: Session, submissao: Submissao, usuario: Usuario):
    # aprovar e uma acao, nao so visualizacao: gestor nao entra aqui (RF-22). So o professor
    # confirma o resultado final -- isso nao mudou mesmo com o aluno podendo gerar a propria
    # correcao (ver _pode_corrigir).
    if not _professor_da_turma(db, usuario, db.get(Atividade, submissao.atividade_id).turma_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só o professor da turma realiza esta ação.")


def _pode_corrigir(db: Session, submissao: Submissao, usuario: Usuario):
    # o proprio aluno pode gerar a correcao da sua submissao (ve a nota da IA na hora,
    # provisoria ate o professor confirmar), alem do professor da turma
    if submissao.aluno_id == usuario.id:
        return
    if _professor_da_turma(db, usuario, db.get(Atividade, submissao.atividade_id).turma_id):
        return
    raise HTTPException(status.HTTP_403_FORBIDDEN, "Só o aluno dono da submissão ou o professor da turma geram a correção.")


def _pode_ver_correcao(db: Session, submissao: Submissao, usuario: Usuario):
    # o aluno ve a propria correcao mesmo antes da aprovacao (e quem pode te-la gerado);
    # o professor/gestor sempre veem. So terceiros ficam de fora.
    if submissao.aluno_id == usuario.id:
        return
    turma_id = db.get(Atividade, submissao.atividade_id).turma_id
    if not (_professor_da_turma(db, usuario, turma_id) or _gestor_da_escola(db, usuario, turma_id)):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Você não tem acesso a esta correção.")


def _temas_da_atividade(db: Session, atividade: Atividade, materia: Materia) -> dict:
    """Criterios que valem para esta atividade: questoes do gabarito (exatas) ou as 5 competencias."""
    if materia.tipo in MATERIAS_EXATAS:
        temas = {t.habilidade_codigo: t for t in db.query(Tema).filter_by(atividade_id=atividade.id)}
        if not temas:
            raise HTTPException(status.HTTP_409_CONFLICT, "Esta atividade não tem gabarito cadastrado.")
    else:
        garantir_competencias(db, materia)  # materia criada sem as 5 competencias: completa em vez de falhar
        temas = {t.habilidade_codigo: t for t in db.query(Tema).filter_by(materia_id=materia.id, atividade_id=None)}
        if sorted(temas) != ["C1", "C2", "C3", "C4", "C5"]:
            raise HTTPException(status.HTTP_409_CONFLICT, "A matéria desta atividade não tem as 5 competências do ENEM.")
    return temas


@router.post("/submissoes/{submissao_id}/corrigir", response_model=CorrecaoResponse, status_code=status.HTTP_201_CREATED)
def corrigir_submissao(
    submissao_id: uuid.UUID,
    payload: CorrigirRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submissao = _submissao_visivel(db, submissao_id, usuario)
    _pode_corrigir(db, submissao, usuario)
    if submissao.texto_confirmado is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Confirme o texto antes de corrigir.")
    if db.query(Correcao).filter_by(submissao_id=submissao.id).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Esta redação já foi corrigida.")

    atividade = db.get(Atividade, submissao.atividade_id)
    materia = db.get(Materia, atividade.materia_id)

    temas = _temas_da_atividade(db, atividade, materia)

    exatas = materia.tipo in MATERIAS_EXATAS
    # exatas continua no Gemini; a nota da redacao agora vem do Claude (ver app/llm/claude.py)
    if not (settings.GEMINI_API_KEY if exatas else settings.ANTHROPIC_API_KEY):
        provedor = "do Gemini" if exatas else "do Claude"
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, f"Correção indisponível: servidor sem chave {provedor}.")
    # memoria do professor (RAG): material que ele subiu + correcoes parecidas que ja aprovou.
    # Vazio enquanto a materia nao tem nada guardado -- ai o prompt e o mesmo de antes.
    contexto, fontes = "", []
    if exatas or settings.IA_MEMORIA_NA_REDACAO:
        consulta = "\n".join([atividade.titulo, *(f"{t.nome} {t.resposta_correta or ''}" for t in temas.values() if exatas),
                              submissao.texto_confirmado])
        contexto, fontes = memoria.montar_contexto(
            db, materia.id, consulta,
            professor_id=atividade.criado_por or (usuario.id if usuario.perfil == PerfilEnum.PROFESSOR else None),
            **({} if exatas else {"exemplos": 0}),  # redacao: so o material do professor (ver config.py)
        )
    try:
        if exatas:
            questoes = [(t.habilidade_codigo, t.nome, t.resposta_correta) for t in temas.values()]
            imagem = []  # todas as folhas do envio, em ordem
            for caminho in caminhos_da_submissao(db, submissao):
                caminho_foto = Path(caminho)
                if caminho_foto.exists():
                    mime, _ = mimetypes.guess_type(str(caminho_foto))
                    imagem.append((caminho_foto.read_bytes(), mime or "image/jpeg"))
            imagem = imagem or None
            figuras = {}  # figura de cada questao (se o professor anexou): o Gemini ve junto do enunciado
            for t in temas.values():
                if t.imagem and Path(t.imagem).exists():
                    mime_fig, _ = mimetypes.guess_type(t.imagem)
                    figuras[t.habilidade_codigo] = (Path(t.imagem).read_bytes(), mime_fig or "image/jpeg")
            resultado, modelo = ia_exatas.corrigir(
                submissao.texto_confirmado, materia.nome, questoes, imagem=imagem, figuras=figuras,
                contexto=contexto, teorica=materia.tipo == TipoMateriaEnum.MATERIA_DISCURSIVA,
            )
            itens = resultado.questoes
            versao_prompt = ia_exatas.VERSAO_PROMPT
            modelo_principal = ia_exatas.MODELO_PRINCIPAL
            feedback = None  # montado abaixo, depois de reescalar as notas (precisa dos pontos reais)
        else:
            resultado, modelo = ia.corrigir(submissao.texto_confirmado, (payload.tema or "").strip() or atividade.titulo, contexto=contexto)
            itens = resultado.competencias
            versao_prompt = ia.VERSAO_PROMPT
            modelo_principal = ia.MODELO_PRINCIPAL
            feedback = resultado.feedback_geral
    except Exception:
        logger.exception("falha na correcao")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Falha ao gerar a correção. Tente de novo.")

    if materia.tipo in MATERIAS_EXATAS:
        # a IA sempre avalia numa escala relativa de 0..200 por questao (ver correcao_exatas.py);
        # aqui reescalamos para o valor real da atividade, dividido igualmente entre as questoes
        # (RF do professor definir o valor total, em vez de cada questao valer 200 fixo)
        valor_por_questao = float(atividade.valor_total or 1000) / len(temas)
        cheias = sum(1 for i in itens if i.nota == 200)  # nota relativa 200 = questao toda certa
        parciais = sum(1 for i in itens if 0 < i.nota < 200)
        for i in itens:
            i.nota = round(i.nota / 200 * valor_por_questao, 2)
        feedback = (
            f"{round(sum(i.nota for i in itens), 2):g} de {float(atividade.valor_total or 1000):g} pontos: "
            f"{cheias} questão(ões) certa(s), {parciais} com acerto parcial, "
            f"{len(itens) - cheias - parciais} sem pontos."
        )

    # modelo diferente do principal (ex.: reserva do Gemini) e mais raso: no teste deu 120 em
    # tudo com "95% de confianca". Vai para o topo da fila do professor junto com as de baixa confianca
    # exatas por foto tambem: a confianca nao distingue leitura estavel de instavel (Q3 deu 0 e 80)
    atencao = resultado.confianca < CONFIANCA_MINIMA or modelo != modelo_principal or (exatas and imagem is not None)
    # nesta materia o professor vem mudando muito a nota da IA: a IA ainda nao pegou o jeito dele,
    # entao a correcao vai para o topo da fila para ele olhar com cuidado
    dono = atividade.criado_por or (usuario.id if usuario.perfil == PerfilEnum.PROFESSOR else None)
    if dono and memoria.concorda_pouco(memoria.concordancia(db, materia.id, dono)):
        atencao = True
    correcao = Correcao(
        submissao_id=submissao.id,
        nota_ia=sum(i.nota for i in itens),
        confianca=round(resultado.confianca, 2),
        status=StatusCorrecaoEnum.REQUER_ATENCAO if atencao else StatusCorrecaoEnum.PENDENTE,
        modelo_usado=modelo,
        versao_prompt=versao_prompt + ("+memoria" if contexto else ""),  # da para auditar quais usaram a memoria
        feedback=feedback,
        fontes_ia=fontes or None,
    )
    db.add(correcao)
    db.flush()
    for i in itens:
        db.add(CorrecaoCriterio(
            correcao_id=correcao.id, tema_id=temas[i.codigo].id, nota=i.nota, justificativa=i.justificativa,
            pontos=[p.model_dump() for p in i.pontos],
        ))
    # ponytail: estimativa de tokens por tamanho do texto (sem usage_metadata real da API ainda)
    registro.gravar(db, materia_id=materia.id, professor_id=atividade.criado_por, correcao_id=correcao.id)
    tokens_estimados = len(submissao.texto_confirmado) // 4
    registrar_uso(db, usuario.escola_id, tokens_llm=tokens_estimados)
    db.commit()
    return _correcao_response(db, correcao)


@router.get("/submissoes/{submissao_id}/correcao-manual", response_model=CorrecaoResponse)
def modelo_correcao_manual(submissao_id: uuid.UUID, usuario: Usuario = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    """Ficha em branco para o professor corrigir direto, sem a IA. Nao grava nada: so ao aprovar."""
    submissao = _submissao_visivel(db, submissao_id, usuario)
    _so_professor(db, submissao, usuario)
    if db.query(Correcao).filter_by(submissao_id=submissao.id).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Esta redação já foi corrigida.")
    atividade = db.get(Atividade, submissao.atividade_id)
    temas = _temas_da_atividade(db, atividade, db.get(Materia, atividade.materia_id))
    return CorrecaoResponse(
        id=submissao.id, submissao_id=submissao.id, nota_ia=0, nota_professor=None, revisado_por=None, confianca=1,
        status=StatusCorrecaoEnum.PENDENTE.value, modelo_usado=memoria.SEM_IA, feedback=None,
        criterios=[CriterioResponse(codigo=c, nome=t.nome, nota=0, nota_professor=None, justificativa="", pontos=[])
                   for c, t in sorted(temas.items())],
    )


@router.get("/submissoes/{submissao_id}/correcao", response_model=CorrecaoResponse)
def ver_correcao(submissao_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    submissao = _submissao_visivel(db, submissao_id, usuario)
    _pode_ver_correcao(db, submissao, usuario)
    correcao = db.query(Correcao).filter_by(submissao_id=submissao.id).first()
    if not correcao:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ainda não corrigida.")
    return _correcao_response(db, correcao)


# O que da memoria do professor a IA usou nesta correcao, para ele conferir. So professor/gestor:
# o aluno nao pode ver o material do professor.
@router.get("/submissoes/{submissao_id}/fontes-ia")
def ver_fontes_da_ia(submissao_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if usuario.perfil not in (PerfilEnum.PROFESSOR, PerfilEnum.GESTOR):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores veem o que a IA usou.")
    submissao = _submissao_visivel(db, submissao_id, usuario)
    correcao = db.query(Correcao).filter_by(submissao_id=submissao.id).first()
    if not correcao:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ainda não corrigida.")
    atividade = db.get(Atividade, submissao.atividade_id)
    c = memoria.concordancia(db, atividade.materia_id, correcao.revisado_por or atividade.criado_por)
    aviso = (f"Nesta matéria a IA tem concordado pouco com você ({c['concordancia_recente']}% nas últimas "
             "correções). Confira esta com cuidado.") if memoria.concorda_pouco(c) else None
    return {"fontes": correcao.fontes_ia or [], "aviso": aviso}


# RF-25: cada aprovacao e uma "evidencia" de desempenho do aluno naquela competencia (tema).
# percentual_dominio e uma media movel: pondera o historico pelo numero de evidencias ja visto.
def _atualizar_dominio(db: Session, aluno_id, criterios: dict) -> None:
    for criterio in criterios.values():
        nota_pct = float(criterio.nota_professor) / 200 * 100
        dominio = db.query(DominioAluno).filter_by(aluno_id=aluno_id, tema_id=criterio.tema_id).first()
        if dominio is None:
            db.add(DominioAluno(
                aluno_id=aluno_id, tema_id=criterio.tema_id,
                percentual_dominio=nota_pct, num_evidencias=1,
            ))
        else:
            dominio.percentual_dominio = (
                float(dominio.percentual_dominio) * dominio.num_evidencias + nota_pct
            ) / (dominio.num_evidencias + 1)
            dominio.num_evidencias += 1


@router.put("/submissoes/{submissao_id}/avaliacao-ia", response_model=CorrecaoResponse)
def avaliar_ia(submissao_id: uuid.UUID, payload: AvaliacaoIARequest,
               usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """1 clique: marca a correcao como BOA (exemplo modelo) ou MA (explicacao ruim), sem mexer na nota.
    Depois de aprovada, a memoria da IA e refeita na hora."""
    submissao = _submissao_visivel(db, submissao_id, usuario)
    _so_professor(db, submissao, usuario)
    correcao = db.query(Correcao).filter_by(submissao_id=submissao.id).first()
    if not correcao:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ainda não corrigida.")
    correcao.boa_correcao = payload.avaliacao == "BOA"
    correcao.explicacao_ruim = payload.avaliacao == "MA"
    correcao.correcao_razoavel = payload.avaliacao == "MEDIA"
    if correcao.status == StatusCorrecaoEnum.APROVADA:
        memoria.indexar_correcao(db, correcao)
    db.commit()
    return _correcao_response(db, correcao)


@router.put("/submissoes/{submissao_id}/aprovar", response_model=CorrecaoResponse)
def aprovar_correcao(
    submissao_id: uuid.UUID,
    payload: AprovarRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submissao = _submissao_visivel(db, submissao_id, usuario)
    _so_professor(db, submissao, usuario)

    correcao = db.query(Correcao).filter_by(submissao_id=submissao.id).first()
    if correcao and correcao.status == StatusCorrecaoEnum.APROVADA:
        raise HTTPException(status.HTTP_409_CONFLICT, "Esta correção já foi aprovada.")
    atividade = db.get(Atividade, submissao.atividade_id)
    materia = db.get(Materia, atividade.materia_id)
    if not correcao:
        # o professor corrige direto, sem a IA ter corrigido antes: guarda so a nota dele
        # (modelo_usado = SEM_IA; a nota/justificativa da IA ficam como a dele e nao entram na comparacao)
        correcao = Correcao(
            submissao_id=submissao.id, nota_ia=0, confianca=1, status=StatusCorrecaoEnum.PENDENTE,
            modelo_usado=memoria.SEM_IA, versao_prompt=memoria.SEM_IA,
        )
        db.add(correcao)
        db.flush()
        for codigo, tema in _temas_da_atividade(db, atividade, materia).items():
            db.add(CorrecaoCriterio(correcao_id=correcao.id, tema_id=tema.id, nota=0,
                                    justificativa="Corrigido direto pelo professor, sem correção da IA."))
        db.flush()

    criterios = {
        t.habilidade_codigo: (c, t)
        for c, t in db.query(CorrecaoCriterio, Tema).join(Tema, Tema.id == CorrecaoCriterio.tema_id)
        .filter(CorrecaoCriterio.correcao_id == correcao.id)
    }
    if sorted(n.codigo for n in payload.notas) != sorted(criterios):
        raise HTTPException(422, "Informe a nota de cada critério desta correção, uma vez cada.")

    if materia.tipo in MATERIAS_EXATAS:
        # faixa valida depende do valor total da atividade (definido pelo professor), dividido
        # igualmente entre as questoes -- nao e mais fixo em 0..200 como na redacao
        valor_por_questao = float(atividade.valor_total or 1000) / len(criterios)
        for nota in payload.notas:
            if not (0 <= nota.nota <= valor_por_questao + 0.01):
                raise HTTPException(422, f"a nota de {nota.codigo} deve estar entre 0 e {valor_por_questao:g}.")
    else:
        for nota in payload.notas:
            if nota.nota not in NOTAS_VALIDAS:
                raise HTTPException(422, f"a nota de {nota.codigo} deve ser uma das {sorted(NOTAS_VALIDAS)}.")

    for nota in payload.notas:
        criterios[nota.codigo][0].nota_professor = nota.nota

    correcao.nota_professor = sum(n.nota for n in payload.notas)
    if correcao.modelo_usado == memoria.SEM_IA:
        correcao.nota_ia = correcao.nota_professor  # sem IA: neutro (nao conta na comparacao, ver memoria.py)
        for codigo, (c, _) in criterios.items():
            c.nota = c.nota_professor
    correcao.revisado_por = usuario.id
    correcao.status = StatusCorrecaoEnum.APROVADA
    if payload.feedback is not None:
        correcao.feedback = payload.feedback.strip()
    correcao.motivo_mudanca = (payload.motivo_mudanca or "").strip() or None
    correcao.explicacao_ruim = payload.explicacao_ruim and not payload.boa_correcao
    correcao.boa_correcao = payload.boa_correcao
    correcao.correcao_razoavel = payload.correcao_razoavel and not (payload.boa_correcao or payload.explicacao_ruim)
    # RF-25/dominio real: so para redacao. As temas de exatas sao especificas de UMA atividade
    # (nunca se repetem), entao nao ha "evolucao" a acumular -- e um unico ponto fora da curva
    # dominaria /dominio/meu e /estudos/meu para sempre. O aluno ainda ve a nota/feedback normal.
    if materia.tipo not in MATERIAS_EXATAS:
        _atualizar_dominio(db, submissao.aluno_id, {codigo: c for codigo, (c, _) in criterios.items()})
    if materia.tipo in MATERIAS_EXATAS:
        registrar_erros(db, submissao.aluno_id)  # onde ele errou, para o plano de estudo
    registrar(db, usuario.id, "APROVAR", "Correcao", correcao.id)
    db.flush()
    memoria.indexar_correcao(db, correcao)  # a IA aprende com esta aprovacao (nunca bloqueia)
    db.commit()
    avaliar_seguro(submissao.aluno_id)  # metas de nota/dominio
    return _correcao_response(db, correcao)

