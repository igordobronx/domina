"""Rotas do agente de correcao (app/agente.py) e as ferramentas que ele pode usar.

POST /submissoes/{id}/agente roda o agente; GET devolve o ultimo passo a passo gravado.
As ferramentas reaproveitam o que ja existia (corrigir_submissao, _dominio_de, gerar_exercicios):
o agente nao corrige de um jeito novo, ele decide QUANDO e QUAL dessas pecas usar.
"""
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import agente
from app.agente import ErroFerramenta, Ferramenta
from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.estudos import gerar_exercicios
from app.models.enum import StatusCorrecaoEnum
from app.models.usuario import AgenteExecucao, Atividade, Correcao, Materia, Submissao, Usuario
from app.routers.dominio import _dominio_de
from app.routers.submissoes import (
    MATERIAS_EXATAS, _correcao_response, _pode_corrigir, _pode_ver_correcao, _submissao_visivel,
    corrigir_submissao,
)
from app.schemas.agente import AgenteRequest, AgenteResponse
from app.schemas.dominio import DominioResponse
from app.schemas.submissao import CorrigirRequest

logger = logging.getLogger(__name__)

router = APIRouter(tags=["agente"])


def _resposta(db: Session, execucao: AgenteExecucao) -> AgenteResponse:
    correcao = db.query(Correcao).filter_by(submissao_id=execucao.submissao_id).first()
    return AgenteResponse(
        passos=execucao.passos, mensagem_aluno=execucao.mensagem_aluno,
        resumo_professor=execucao.resumo_professor, exercicios=execucao.exercicios,
        modelo_usado=execucao.modelo_usado,
        correcao=_correcao_response(db, correcao) if correcao else None,
    )


def _ferramentas(db: Session, submissao: Submissao, usuario: Usuario, estado: dict) -> list[Ferramenta]:
    atividade = db.get(Atividade, submissao.atividade_id)
    materia = db.get(Materia, atividade.materia_id)
    exatas = materia.tipo in MATERIAS_EXATAS

    def correcao_atual():
        return db.query(Correcao).filter_by(submissao_id=submissao.id).first()

    def ler_envio(_):
        texto = submissao.texto_confirmado or ""
        return {
            "materia": materia.nome,
            "tipo_materia": "exatas" if exatas else "redacao_enem",
            "atividade": atividade.titulo,
            "enviado_como": submissao.tipo_envio.value,
            "palavras": len(texto.split()),
            "linhas": len([l for l in texto.splitlines() if l.strip()]),
            "texto": texto,
        }

    def _corrigir(tema: str | None):
        existente = correcao_atual()
        if existente:
            c = _correcao_response(db, existente)
        else:
            try:
                c = corrigir_submissao(submissao.id, CorrigirRequest(tema=tema), usuario, db)
            except HTTPException as e:
                raise ErroFerramenta(str(e.detail)) from e
        return {
            "nota_total": c.nota_ia,
            "confianca": c.confianca,
            "criterios": [
                {"codigo": cr.codigo, "nome": cr.nome, "nota": cr.nota, "justificativa": (cr.justificativa or "")[:300]}
                for cr in c.criterios
            ],
            "feedback": c.feedback,
        }

    def corrigir_redacao(entrada):
        if exatas:
            raise ErroFerramenta("Esta atividade é de exatas; use corrigir_exatas.")
        return _corrigir(entrada.get("tema"))

    def corrigir_mat(_):
        if not exatas:
            raise ErroFerramenta("Esta atividade é de redação; use corrigir_redacao_enem.")
        return _corrigir(None)

    def consultar_historico(_):
        anteriores = (
            db.query(Correcao, Submissao).join(Submissao, Submissao.id == Correcao.submissao_id)
            .filter(Submissao.aluno_id == submissao.aluno_id, Submissao.id != submissao.id)
            .order_by(Submissao.criado_em.desc()).limit(5)
        )
        return {
            "dominio_por_competencia": [
                {"codigo": d.habilidade_codigo, "nome": d.tema, "dominio_pct": round(d.percentual_dominio),
                 "correcoes_aprovadas": d.num_evidencias}
                for d in _dominio_de(db, submissao.aluno_id)
            ],
            "ultimas_notas": [
                {"nota_ia": float(c.nota_ia),
                 "nota_professor": float(c.nota_professor) if c.nota_professor is not None else None}
                for c, _ in anteriores
            ],
        }

    def gerar_reforco(entrada):
        if exatas:
            raise ErroFerramenta("Os exercícios de reforço são só para redação do ENEM.")
        correcao = correcao_atual()
        if not correcao:
            raise ErroFerramenta("Corrija o envio antes de gerar exercícios.")
        codigos = [c.upper() for c in entrada.get("competencias", [])][:3]
        atual = {cr.codigo: cr for cr in _correcao_response(db, correcao).criterios}
        historico = {d.habilidade_codigo: d for d in _dominio_de(db, submissao.aluno_id)}
        alvo = []
        for codigo in codigos:
            if codigo not in atual:
                continue
            d = historico.get(codigo)
            # sem historico aprovado, usa a nota de agora como estimativa do dominio
            pct = d.percentual_dominio if d else atual[codigo].nota / 200 * 100
            alvo.append(DominioResponse(
                tema_id=d.tema_id if d else uuid.uuid4(), tema=atual[codigo].nome, habilidade_codigo=codigo,
                percentual_dominio=pct, num_evidencias=d.num_evidencias if d else 0,
            ))
        if not alvo:
            raise ErroFerramenta("Informe competências válidas (C1 a C5).")
        exercicios = gerar_exercicios(submissao.aluno_id, alvo)
        estado["exercicios"] = [e.model_dump() for e in exercicios]
        return {"exercicios_gerados": [{"competencia": e.habilidade_codigo, "titulo": e.titulo} for e in exercicios]}

    def sinalizar(entrada):
        correcao = correcao_atual()
        if not correcao:
            raise ErroFerramenta("Ainda não há correção para sinalizar.")
        if correcao.status != StatusCorrecaoEnum.APROVADA:
            correcao.status = StatusCorrecaoEnum.REQUER_ATENCAO
            db.commit()
        estado["sinalizado"] = entrada.get("aviso", "")
        return {"ok": True, "status": correcao.status.value}

    def pedir_foto(entrada):
        estado["nova_foto"] = entrada.get("mensagem", "")
        return {"ok": True}

    def finalizar(entrada):
        estado["mensagem_aluno"] = entrada.get("mensagem_aluno", "")
        estado["resumo_professor"] = entrada.get("resumo_professor", "")
        estado["fim"] = True
        return {"ok": True}

    texto = {"type": "string"}
    return [
        Ferramenta("ler_envio", "Lê o envio do aluno: matéria, tipo de atividade e o texto confirmado.", {}, ler_envio),
        Ferramenta(
            "corrigir_redacao_enem",
            "Corrige uma redação do ENEM nas 5 competências (C1 a C5, 0 a 200 cada) com o corretor "
            "calibrado contra notas do INEP. Grava a correção provisória para o professor revisar.",
            {"tema": {"type": "string", "description": "Tema da proposta, se souber (opcional)."}},
            corrigir_redacao,
        ),
        Ferramenta(
            "corrigir_exatas",
            "Corrige uma atividade de matemática/exatas comparando com o gabarito. Grava a correção provisória.",
            {}, corrigir_mat,
        ),
        Ferramenta(
            "consultar_historico_aluno",
            "Mostra o domínio do aluno por competência (de correções aprovadas) e as últimas notas.",
            {}, consultar_historico,
        ),
        Ferramenta(
            "gerar_exercicios_reforco",
            "Gera um exercício de múltipla escolha para cada competência fraca escolhida (até 3).",
            {"competencias": {"type": "array", "items": texto, "description": "Códigos, ex.: [\"C3\", \"C5\"]"}},
            gerar_reforco, ["competencias"],
        ),
        Ferramenta(
            "sinalizar_professor",
            "Coloca a correção no topo da fila do professor, com um aviso do porquê.",
            {"aviso": {"type": "string", "description": "O que o professor deve olhar."}},
            sinalizar, ["aviso"],
        ),
        Ferramenta(
            "pedir_nova_foto",
            "Pede ao aluno uma nova foto quando o texto lido está ilegível, vazio ou cortado.",
            {"mensagem": {"type": "string", "description": "O que o aluno deve fazer."}},
            pedir_foto, ["mensagem"],
        ),
        Ferramenta(
            "finalizar",
            "Encerra o trabalho. Use sempre como último passo.",
            {"mensagem_aluno": texto, "resumo_professor": texto},
            finalizar, ["mensagem_aluno", "resumo_professor"],
        ),
    ]


@router.post("/submissoes/{submissao_id}/agente", response_model=AgenteResponse)
def rodar_agente(
    submissao_id: uuid.UUID,
    payload: AgenteRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submissao = _submissao_visivel(db, submissao_id, usuario)
    _pode_corrigir(db, submissao, usuario)
    if submissao.texto_confirmado is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Confirme o texto antes de corrigir.")
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Agente indisponível: servidor sem chave do Claude.")

    estado: dict = {}
    pedido = "Há um novo envio de um aluno para você cuidar. Comece lendo o envio."
    if payload.tema:
        pedido += f" O professor informou o tema da proposta: {payload.tema.strip()}"
    try:
        passos, modelo = agente.rodar(pedido, _ferramentas(db, submissao, usuario, estado), lambda: estado.get("fim", False))
    except Exception as e:  # noqa: BLE001 -- se o agente cair, a correcao normal ainda sai
        logger.exception("falha no agente")
        passos, modelo = [{"tipo": "aviso", "texto": f"O agente parou ({type(e).__name__}); usei a correção direta."}], settings.ANTHROPIC_MODEL
        db.rollback()
        if not db.query(Correcao).filter_by(submissao_id=submissao.id).first():
            corrigir_submissao(submissao.id, CorrigirRequest(tema=payload.tema), usuario, db)

    if estado.get("nova_foto") and not estado.get("mensagem_aluno"):
        estado["mensagem_aluno"] = estado["nova_foto"]
    execucao = db.query(AgenteExecucao).filter_by(submissao_id=submissao.id).first()
    if execucao is None:
        execucao = AgenteExecucao(submissao_id=submissao.id)
        db.add(execucao)
    execucao.passos = passos
    execucao.mensagem_aluno = estado.get("mensagem_aluno")
    execucao.resumo_professor = estado.get("resumo_professor")
    execucao.exercicios = estado.get("exercicios")
    execucao.modelo_usado = modelo
    db.commit()
    return _resposta(db, execucao)


@router.get("/submissoes/{submissao_id}/agente", response_model=AgenteResponse)
def ver_agente(submissao_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    submissao = _submissao_visivel(db, submissao_id, usuario)
    _pode_ver_correcao(db, submissao, usuario)
    execucao = db.query(AgenteExecucao).filter_by(submissao_id=submissao.id).first()
    if not execucao:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "O agente ainda não rodou para este envio.")
    return _resposta(db, execucao)
