import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, status, UploadFile
from sqlalchemy.orm import Session

from app import correcao as ia
from app import correcao_exatas as ia_exatas
from app.correcao import NOTAS_VALIDAS
from app.auditoria import registrar
from app.auth.dependencies import get_current_user
from app.config import settings
from app.custo import registrar_uso
from app.database import get_db
from app.models.enum import (
    PerfilEnum, StatusCorrecaoEnum, TipoAtividadeEnum, TipoEnvioEnum, TipoMateriaEnum, UsuarioTurmaPapelEnum,
)
from app.models.usuario import (
    Atividade, Correcao, CorrecaoCriterio, DominioAluno, Materia, Submissao, Tema, Turma, Usuario, UsuarioTurma,
)
from app.routers.ocr import ler_imagem, ocr
from app.schemas.submissao import (
    AlunoResumo, AprovarRequest, AtividadeResponse, ConfirmarTextoRequest, CorrecaoResponse,
    CriarAtividadeRequest, CriarMateriaRequest, CorrigirRequest, CriterioResponse, EnviarTextoRequest,
    MateriaResponse, MinhaSubmissaoResponse, QuestaoAtividadeResponse, SubmissaoResponse,
    SubmissaoRevisaoResponse,
)

MATERIAS_EXATAS = (TipoMateriaEnum.MATERIA_OBJETIVA, TipoMateriaEnum.MATERIA_DISCURSIVA)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["submissoes"])

# abaixo disso a correcao vai para o topo da fila do professor (RF-17/RF-23)
CONFIANCA_MINIMA = 0.6


def _na_turma(db: Session, usuario_id, turma_id) -> bool:
    return db.get(UsuarioTurma, (usuario_id, turma_id)) is not None


def _professor_da_turma(db: Session, usuario: Usuario, turma_id) -> bool:
    return usuario.perfil == PerfilEnum.PROFESSOR and _na_turma(db, usuario.id, turma_id)


def _gestor_da_escola(db: Session, usuario: Usuario, turma_id) -> bool:
    # gestor so observa (RF-22): nunca corrige nem aprova, so enxerga o que ja existe
    if usuario.perfil != PerfilEnum.GESTOR:
        return False
    turma = db.get(Turma, turma_id)
    return bool(turma and turma.escola_id == usuario.escola_id)


def _submissao_visivel(db: Session, submissao_id, usuario: Usuario) -> Submissao:
    # aluno dono, professor da turma ou gestor da escola; o resto recebe 404 (nao revela que existe)
    submissao = db.get(Submissao, submissao_id)
    if submissao:
        turma_id = db.get(Atividade, submissao.atividade_id).turma_id
        if (
            submissao.aluno_id == usuario.id
            or _professor_da_turma(db, usuario, turma_id)
            or _gestor_da_escola(db, usuario, turma_id)
        ):
            return submissao
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Submissão não encontrada.")


def _atividade_response(db: Session, atividade: Atividade, usuario: Usuario) -> AtividadeResponse:
    alunos = (
        db.query(Usuario).join(UsuarioTurma, UsuarioTurma.usuario_id == Usuario.id)
        .filter(UsuarioTurma.turma_id == atividade.turma_id, UsuarioTurma.papel == UsuarioTurmaPapelEnum.ALUNO)
        .order_by(Usuario.nome)
    )
    if usuario.perfil == PerfilEnum.ALUNO:
        alunos = alunos.filter(Usuario.id == usuario.id)

    materia = db.get(Materia, atividade.materia_id)
    questoes = None
    if materia.tipo in MATERIAS_EXATAS:
        temas = (
            db.query(Tema).filter_by(atividade_id=atividade.id)
            .order_by(Tema.habilidade_codigo)
        )
        questoes = [QuestaoAtividadeResponse(codigo=t.habilidade_codigo, enunciado=t.nome) for t in temas]

    return AtividadeResponse(
        id=atividade.id, titulo=atividade.titulo, turma=db.get(Turma, atividade.turma_id).nome,
        materia=materia.nome, tipo=atividade.tipo.value,
        alunos=[AlunoResumo(id=a.id, nome=a.nome) for a in alunos],
        questoes=questoes,
        valor_total=float(atividade.valor_total) if atividade.valor_total is not None else 1000.0,
    )


# materias da escola do usuario, para o professor/gestor escolher ao criar uma atividade
@router.get("/materias", response_model=list[MateriaResponse])
def listar_materias(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    materias = db.query(Materia).filter_by(escola_id=usuario.escola_id)
    return [MateriaResponse(id=m.id, nome=m.nome, tipo=m.tipo.value) for m in materias]


@router.post("/materias", response_model=MateriaResponse, status_code=status.HTTP_201_CREATED)
def criar_materia(payload: CriarMateriaRequest, usuario: Usuario = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    if usuario.perfil not in (PerfilEnum.PROFESSOR, PerfilEnum.GESTOR):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores criam matérias.")
    materia = Materia(escola_id=usuario.escola_id, nome=payload.nome.strip(), tipo=TipoMateriaEnum(payload.tipo))
    db.add(materia)
    db.commit()
    db.refresh(materia)
    return MateriaResponse(id=materia.id, nome=materia.nome, tipo=materia.tipo.value)


@router.get("/atividades", response_model=list[AtividadeResponse])
def listar_atividades(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    # atividades das turmas do usuario, com os alunos de cada turma (o professor escolhe em nome de quem envia)
    turma_ids = [ut.turma_id for ut in db.query(UsuarioTurma).filter_by(usuario_id=usuario.id)]
    atividades = db.query(Atividade).filter(Atividade.turma_id.in_(turma_ids))
    return [_atividade_response(db, atividade, usuario) for atividade in atividades]


# RF-09/RF-10: professor (ou gestor) cria a atividade numa turma dele, vinculada a uma materia da escola
@router.post("/atividades", response_model=AtividadeResponse, status_code=status.HTTP_201_CREATED)
def criar_atividade(payload: CriarAtividadeRequest, usuario: Usuario = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    turma = db.get(Turma, payload.turma_id)
    if not turma or turma.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")
    if usuario.perfil == PerfilEnum.PROFESSOR and not _na_turma(db, usuario.id, turma.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Você não leciona nesta turma.")
    elif usuario.perfil not in (PerfilEnum.PROFESSOR, PerfilEnum.GESTOR):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores criam atividades.")

    materia = db.get(Materia, payload.materia_id)
    if not materia or materia.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Matéria não encontrada.")
    if materia.tipo in MATERIAS_EXATAS and not payload.questoes:
        raise HTTPException(422, "Informe as questões e o gabarito desta atividade.")

    atividade = Atividade(
        materia_id=materia.id, turma_id=turma.id, titulo=payload.titulo.strip(),
        tipo=TipoAtividadeEnum(payload.tipo),
        valor_total=(payload.valor_total or 1000) if materia.tipo in MATERIAS_EXATAS else None,
    )
    db.add(atividade)
    db.flush()

    if materia.tipo in MATERIAS_EXATAS:
        # um Tema por questao, especifico desta atividade (ver comentario em models/usuario.py::Tema)
        for i, questao in enumerate(payload.questoes, start=1):
            db.add(Tema(
                materia_id=materia.id, atividade_id=atividade.id, habilidade_codigo=f"Q{i}",
                nome=questao.enunciado.strip(), resposta_correta=questao.resposta_correta.strip(),
            ))

    db.commit()
    db.refresh(atividade)
    return _atividade_response(db, atividade, usuario)


# fluxo RF-11: foto -> OCR -> confere/corrige o texto -> confirma -> correcao por IA.
# o aluno envia a propria redacao; o professor pode enviar em nome de um aluno da turma (RF-12).
@router.post("/submissoes/imagem", response_model=SubmissaoResponse, status_code=status.HTTP_201_CREATED)
def enviar_imagem(
    file: UploadFile,
    atividade_id: uuid.UUID = Form(...),
    aluno_id: uuid.UUID | None = Form(None),
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    atividade = db.get(Atividade, atividade_id)
    if usuario.perfil == PerfilEnum.ALUNO:
        aluno_id = usuario.id
    elif usuario.perfil != PerfilEnum.PROFESSOR:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só alunos e professores enviam redação.")
    elif aluno_id is None:
        raise HTTPException(422, "Informe o aluno (aluno_id).")

    # mesma resposta para "nao existe" e "nao e da sua turma": nao revela atividades alheias
    if not atividade or not _na_turma(db, usuario.id, atividade.turma_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Atividade não encontrada.")
    aluno = db.get(Usuario, aluno_id)
    if not aluno or aluno.perfil != PerfilEnum.ALUNO or not _na_turma(db, aluno.id, atividade.turma_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Aluno não encontrado nesta turma.")

    image_bytes = ler_imagem(file)
    texto = ocr(image_bytes, file.content_type)  # se o OCR falhar, nada e gravado
    registrar_uso(db, usuario.escola_id, chamadas_ocr=1)

    # guarda a foto original (o professor pode querer ver ao revisar)
    # ponytail: disco local; trocar por bucket (GCS/S3) quando houver mais de um servidor
    sufixo = Path(file.filename or "").suffix.lower()[:10] or ".img"
    caminho = Path(settings.UPLOAD_DIR) / f"{uuid.uuid4()}{sufixo}"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(image_bytes)

    submissao = Submissao(
        atividade_id=atividade.id,
        aluno_id=aluno.id,
        tipo_envio=TipoEnvioEnum.IMAGEM,
        conteudo_bruto=str(caminho),
        texto_ocr=texto,
    )
    db.add(submissao)
    db.commit()
    db.refresh(submissao)
    return submissao


# RF-17/RF-23: fila de revisao do professor (ou visao do gestor) -- submissoes das turmas dele, com status
@router.get("/submissoes", response_model=list[SubmissaoRevisaoResponse])
def listar_submissoes(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if usuario.perfil == PerfilEnum.PROFESSOR:
        turma_ids = [
            ut.turma_id for ut in
            db.query(UsuarioTurma).filter_by(usuario_id=usuario.id, papel=UsuarioTurmaPapelEnum.PROFESSOR)
        ]
    elif usuario.perfil == PerfilEnum.GESTOR:
        turma_ids = [t.id for t in db.query(Turma).filter_by(escola_id=usuario.escola_id)]
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores usam esta rota.")

    linhas = (
        db.query(Submissao, Atividade, Materia, Usuario)
        .join(Atividade, Atividade.id == Submissao.atividade_id)
        .join(Materia, Materia.id == Atividade.materia_id)
        .join(Usuario, Usuario.id == Submissao.aluno_id)
        .filter(Atividade.turma_id.in_(turma_ids))
        .order_by(Submissao.criado_em.desc())
    )
    resposta = []
    for s, atividade, materia, aluno in linhas:
        correcao = db.query(Correcao).filter_by(submissao_id=s.id).first()
        aprovada = correcao and correcao.status == StatusCorrecaoEnum.APROVADA
        resposta.append(SubmissaoRevisaoResponse(
            id=s.id, atividade_id=atividade.id, atividade_titulo=atividade.titulo, materia=materia.nome,
            aluno_id=aluno.id, aluno_nome=aluno.nome,
            status=correcao.status.value if correcao else "AGUARDANDO_CORRECAO",
            criado_em=s.criado_em,
            nota=float(correcao.nota_professor) if aprovada else None,
            valor_total=float(atividade.valor_total) if atividade.valor_total is not None else 1000.0,
        ))
    return resposta


# rota literal: tem que vir antes de /submissoes/{submissao_id}, senao o FastAPI tenta
# interpretar "minhas" como UUID e quebra com 422 (casa pela posicao do path, nao pelo tipo)
@router.get("/submissoes/minhas", response_model=list[MinhaSubmissaoResponse])
def minhas_submissoes(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if usuario.perfil != PerfilEnum.ALUNO:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só alunos usam esta rota.")
    submissoes = db.query(Submissao).filter_by(aluno_id=usuario.id).order_by(Submissao.criado_em.desc())
    resposta = []
    for s in submissoes:
        correcao = db.query(Correcao).filter_by(submissao_id=s.id).first()
        aprovada = correcao and correcao.status == StatusCorrecaoEnum.APROVADA
        criterios = None
        if aprovada:
            linhas = (
                db.query(CorrecaoCriterio, Tema).join(Tema, Tema.id == CorrecaoCriterio.tema_id)
                .filter(CorrecaoCriterio.correcao_id == correcao.id).order_by(Tema.habilidade_codigo)
            )
            criterios = [
                CriterioResponse(
                    codigo=t.habilidade_codigo, nome=t.nome, nota=float(c.nota),
                    nota_professor=float(c.nota_professor) if c.nota_professor is not None else None,
                    justificativa=c.justificativa,
                )
                for c, t in linhas
            ]
        resposta.append(MinhaSubmissaoResponse(
            id=s.id,
            atividade_id=s.atividade_id,
            atividade_titulo=db.get(Atividade, s.atividade_id).titulo,
            status=correcao.status.value if correcao else "AGUARDANDO_CORRECAO",
            criado_em=s.criado_em,
            nota=float(correcao.nota_professor) if aprovada else None,
            feedback=correcao.feedback if aprovada else None,
            criterios=criterios,
        ))
    return resposta


@router.get("/submissoes/{submissao_id}", response_model=SubmissaoResponse)
def ver_submissao(submissao_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return _submissao_visivel(db, submissao_id, usuario)


@router.put("/submissoes/{submissao_id}/confirmar", response_model=SubmissaoResponse)
def confirmar_texto(
    submissao_id: uuid.UUID,
    payload: ConfirmarTextoRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submissao = _submissao_visivel(db, submissao_id, usuario)
    if submissao.texto_confirmado is not None:
        # depois de confirmado o texto vai para correcao; mudar agora invalidaria a nota
        raise HTTPException(status.HTTP_409_CONFLICT, "Texto já confirmado.")

    texto = payload.texto.strip()
    if not texto:
        raise HTTPException(422, "Texto vazio.")

    submissao.texto_confirmado = texto
    db.commit()
    db.refresh(submissao)
    return submissao


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
        criterios=[
            CriterioResponse(
                codigo=t.habilidade_codigo, nome=t.nome, nota=float(c.nota),
                nota_professor=float(c.nota_professor) if c.nota_professor is not None else None,
                justificativa=c.justificativa,
            )
            for c, t in criterios
        ],
    )


def _so_professor(db: Session, submissao: Submissao, usuario: Usuario):
    # corrigir e aprovar sao acoes, nao so visualizacao: gestor nao entra aqui (RF-22)
    if not _professor_da_turma(db, usuario, db.get(Atividade, submissao.atividade_id).turma_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só o professor da turma realiza esta ação.")


def _pode_ver_correcao(db: Session, submissao: Submissao, usuario: Usuario):
    # a nota da IA so e vista pelo professor/gestor; o aluno so ve depois da aprovacao (RN-01)
    turma_id = db.get(Atividade, submissao.atividade_id).turma_id
    if not (_professor_da_turma(db, usuario, turma_id) or _gestor_da_escola(db, usuario, turma_id)):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só o professor da turma ou um gestor vê a correção antes da aprovação.")


@router.post("/submissoes/{submissao_id}/corrigir", response_model=CorrecaoResponse, status_code=status.HTTP_201_CREATED)
def corrigir_submissao(
    submissao_id: uuid.UUID,
    payload: CorrigirRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submissao = _submissao_visivel(db, submissao_id, usuario)
    _so_professor(db, submissao, usuario)
    if submissao.texto_confirmado is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Confirme o texto antes de corrigir.")
    if db.query(Correcao).filter_by(submissao_id=submissao.id).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Esta redação já foi corrigida.")

    atividade = db.get(Atividade, submissao.atividade_id)
    materia = db.get(Materia, atividade.materia_id)

    if materia.tipo in MATERIAS_EXATAS:
        temas = {t.habilidade_codigo: t for t in db.query(Tema).filter_by(atividade_id=atividade.id)}
        if not temas:
            raise HTTPException(status.HTTP_409_CONFLICT, "Esta atividade não tem gabarito cadastrado.")
    else:
        temas = {t.habilidade_codigo: t for t in db.query(Tema).filter_by(materia_id=materia.id, atividade_id=None)}
        if sorted(temas) != ["C1", "C2", "C3", "C4", "C5"]:
            raise HTTPException(status.HTTP_409_CONFLICT, "A matéria desta atividade não tem as 5 competências do ENEM.")

    if not settings.GEMINI_API_KEY:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Correção indisponível: servidor sem chave do Gemini.")
    try:
        if materia.tipo in MATERIAS_EXATAS:
            questoes = [(t.habilidade_codigo, t.nome, t.resposta_correta) for t in temas.values()]
            resultado, modelo = ia_exatas.corrigir(submissao.texto_confirmado, materia.nome, questoes)
            itens = resultado.questoes
            versao_prompt = ia_exatas.VERSAO_PROMPT
            acertos = sum(1 for q in itens if q.nota == 200)
            feedback = f"{acertos}/{len(itens)} questões corretas."
        else:
            resultado, modelo = ia.corrigir(submissao.texto_confirmado, (payload.tema or "").strip() or atividade.titulo)
            itens = resultado.competencias
            versao_prompt = ia.VERSAO_PROMPT
            feedback = resultado.feedback_geral
    except Exception:
        logger.exception("falha na correcao")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Falha ao gerar a correção. Tente de novo.")

    if materia.tipo in MATERIAS_EXATAS:
        # a IA sempre avalia numa escala relativa de 0..200 por questao (ver correcao_exatas.py);
        # aqui reescalamos para o valor real da atividade, dividido igualmente entre as questoes
        # (RF do professor definir o valor total, em vez de cada questao valer 200 fixo)
        valor_por_questao = float(atividade.valor_total or 1000) / len(temas)
        for i in itens:
            i.nota = round(i.nota / 200 * valor_por_questao, 2)

    # nota do modelo reserva (lite) e mais rasa: no teste deu 120 em tudo com "95% de confianca".
    # vai para o topo da fila do professor junto com as de baixa confianca
    atencao = resultado.confianca < CONFIANCA_MINIMA or modelo != settings.GEMINI_MODEL
    correcao = Correcao(
        submissao_id=submissao.id,
        nota_ia=sum(i.nota for i in itens),
        confianca=round(resultado.confianca, 2),
        status=StatusCorrecaoEnum.REQUER_ATENCAO if atencao else StatusCorrecaoEnum.PENDENTE,
        modelo_usado=modelo,
        versao_prompt=versao_prompt,
        feedback=feedback,
    )
    db.add(correcao)
    db.flush()
    for i in itens:
        db.add(CorrecaoCriterio(correcao_id=correcao.id, tema_id=temas[i.codigo].id, nota=i.nota, justificativa=i.justificativa))
    # ponytail: estimativa de tokens por tamanho do texto (sem usage_metadata real da API ainda)
    tokens_estimados = len(submissao.texto_confirmado) // 4
    registrar_uso(db, usuario.escola_id, tokens_llm=tokens_estimados)
    db.commit()
    return _correcao_response(db, correcao)


@router.get("/submissoes/{submissao_id}/correcao", response_model=CorrecaoResponse)
def ver_correcao(submissao_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    submissao = _submissao_visivel(db, submissao_id, usuario)
    _pode_ver_correcao(db, submissao, usuario)
    correcao = db.query(Correcao).filter_by(submissao_id=submissao.id).first()
    if not correcao:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ainda não corrigida.")
    return _correcao_response(db, correcao)


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
    if not correcao:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ainda não corrigida.")
    if correcao.status == StatusCorrecaoEnum.APROVADA:
        raise HTTPException(status.HTTP_409_CONFLICT, "Esta correção já foi aprovada.")

    criterios = {
        t.habilidade_codigo: (c, t)
        for c, t in db.query(CorrecaoCriterio, Tema).join(Tema, Tema.id == CorrecaoCriterio.tema_id)
        .filter(CorrecaoCriterio.correcao_id == correcao.id)
    }
    if sorted(n.codigo for n in payload.notas) != sorted(criterios):
        raise HTTPException(422, "Informe a nota de cada critério desta correção, uma vez cada.")

    atividade = db.get(Atividade, submissao.atividade_id)
    materia = db.get(Materia, atividade.materia_id)
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
    correcao.revisado_por = usuario.id
    correcao.status = StatusCorrecaoEnum.APROVADA
    if payload.feedback is not None:
        correcao.feedback = payload.feedback.strip()
    # RF-25/dominio real: so para redacao. As temas de exatas sao especificas de UMA atividade
    # (nunca se repetem), entao nao ha "evolucao" a acumular -- e um unico ponto fora da curva
    # dominaria /dominio/meu e /estudos/meu para sempre. O aluno ainda ve a nota/feedback normal.
    if materia.tipo not in MATERIAS_EXATAS:
        _atualizar_dominio(db, submissao.aluno_id, {codigo: c for codigo, (c, _) in criterios.items()})
    registrar(db, usuario.id, "APROVAR", "Correcao", correcao.id)
    db.commit()
    return _correcao_response(db, correcao)


def _validar_envio(db: Session, usuario: Usuario, atividade_id, aluno_id) -> tuple[Atividade, Usuario]:
    atividade = db.get(Atividade, atividade_id)
    if usuario.perfil == PerfilEnum.ALUNO:
        aluno_id = usuario.id
    elif usuario.perfil != PerfilEnum.PROFESSOR:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só alunos e professores enviam redação.")
    elif aluno_id is None:
        raise HTTPException(422, "Informe o aluno (aluno_id).")

    # mesma resposta para "nao existe" e "nao e da sua turma": nao revela atividades alheias
    if not atividade or not _na_turma(db, usuario.id, atividade.turma_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Atividade não encontrada.")
    aluno = db.get(Usuario, aluno_id)
    if not aluno or aluno.perfil != PerfilEnum.ALUNO or not _na_turma(db, aluno.id, atividade.turma_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Aluno não encontrado nesta turma.")
    return atividade, aluno


@router.post("/submissoes/texto", response_model=SubmissaoResponse, status_code=status.HTTP_201_CREATED)
def enviar_texto(payload: EnviarTextoRequest, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    atividade, aluno = _validar_envio(db, usuario, payload.atividade_id, payload.aluno_id)
    texto = payload.texto.strip()
    if not texto:
        raise HTTPException(422, "Texto vazio.")

    # envio por texto ja nasce confirmado: nao ha etapa de OCR pra revisar
    submissao = Submissao(
        atividade_id=atividade.id, aluno_id=aluno.id,
        tipo_envio=TipoEnvioEnum.TEXTO,
        conteudo_bruto=texto,
        texto_confirmado=texto,
    )
    db.add(submissao)
    db.commit()
    db.refresh(submissao)
    return submissao


