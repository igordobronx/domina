import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Query, status, UploadFile
from sqlalchemy.orm import Session

from app import correcao as ia
from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.models.enum import PerfilEnum, StatusCorrecaoEnum, TipoEnvioEnum, UsuarioTurmaPapelEnum
from app.models.usuario import (
    Atividade, Correcao, CorrecaoCriterio, Submissao, Tema, Turma, Usuario, UsuarioTurma,
)
from app.routers.ocr import ler_imagem, ocr
from app.schemas.submissao import (
    AlunoResumo, AtividadeResponse, ConfirmarTextoRequest, CorrecaoResponse, CorrigirRequest,
    CriterioResponse, EnviarTextoRequest, SubmissaoResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["submissoes"])

# abaixo disso a correcao vai para o topo da fila do professor (RF-17/RF-23)
CONFIANCA_MINIMA = 0.6


def _na_turma(db: Session, usuario_id, turma_id, papel: UsuarioTurmaPapelEnum | None = None) -> bool:
    vinculo = db.get(UsuarioTurma, (usuario_id, turma_id))
    return vinculo is not None and (papel is None or vinculo.papel == papel)


def _professor_da_turma(db: Session, usuario: Usuario, turma_id) -> bool:
    return usuario.perfil == PerfilEnum.PROFESSOR and _na_turma(
        db, usuario.id, turma_id, UsuarioTurmaPapelEnum.PROFESSOR
    )


def _submissao_visivel(db: Session, submissao_id, usuario: Usuario) -> Submissao:
    # aluno dono ou professor da turma; o resto recebe 404 (nao revela que existe)
    submissao = db.get(Submissao, submissao_id)
    if submissao and (
        submissao.aluno_id == usuario.id
        or _professor_da_turma(db, usuario, db.get(Atividade, submissao.atividade_id).turma_id)
    ):
        return submissao
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Submissão não encontrada.")


def _validar_envio(db: Session, usuario: Usuario, atividade_id: uuid.UUID, aluno_id: uuid.UUID | None):
    if usuario.perfil == PerfilEnum.ALUNO:
        aluno_id = usuario.id
    elif usuario.perfil != PerfilEnum.PROFESSOR:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só alunos e professores enviam redação.")
    elif aluno_id is None:
        raise HTTPException(422, "Informe o aluno (aluno_id).")

    atividade = db.get(Atividade, atividade_id)
    turma = db.get(Turma, atividade.turma_id) if atividade else None
    # Nao revela atividades de outra turma ou escola.
    papel = UsuarioTurmaPapelEnum.ALUNO if usuario.perfil == PerfilEnum.ALUNO else UsuarioTurmaPapelEnum.PROFESSOR
    if not turma or turma.escola_id != usuario.escola_id or not _na_turma(db, usuario.id, turma.id, papel):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Atividade não encontrada.")

    aluno = db.get(Usuario, aluno_id)
    if (
        not aluno or aluno.perfil != PerfilEnum.ALUNO or aluno.escola_id != usuario.escola_id
        or not _na_turma(db, aluno.id, turma.id, UsuarioTurmaPapelEnum.ALUNO)
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Aluno não encontrado nesta turma.")
    return atividade, aluno


@router.get("/atividades", response_model=list[AtividadeResponse])
def listar_atividades(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    # atividades das turmas do usuario, com os alunos de cada turma (o professor escolhe em nome de quem envia)
    turma_ids = [ut.turma_id for ut in db.query(UsuarioTurma).filter_by(usuario_id=usuario.id)]
    resposta = []
    for atividade in db.query(Atividade).filter(Atividade.turma_id.in_(turma_ids)):
        alunos = (
            db.query(Usuario).join(UsuarioTurma, UsuarioTurma.usuario_id == Usuario.id)
            .filter(UsuarioTurma.turma_id == atividade.turma_id, UsuarioTurma.papel == UsuarioTurmaPapelEnum.ALUNO)
            .order_by(Usuario.nome)
        )
        if usuario.perfil == PerfilEnum.ALUNO:
            alunos = alunos.filter(Usuario.id == usuario.id)
        resposta.append(AtividadeResponse(
            id=atividade.id, titulo=atividade.titulo, turma=db.get(Turma, atividade.turma_id).nome,
            alunos=[AlunoResumo(id=a.id, nome=a.nome) for a in alunos],
        ))
    return resposta


@router.post("/submissoes/texto", response_model=SubmissaoResponse, status_code=status.HTTP_201_CREATED)
def enviar_texto(
    payload: EnviarTextoRequest,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    atividade, aluno = _validar_envio(db, usuario, payload.atividade_id, payload.aluno_id)
    texto = payload.texto.strip()
    if not texto:
        raise HTTPException(422, "Texto vazio.")

    submissao = Submissao(
        atividade_id=atividade.id,
        aluno_id=aluno.id,
        tipo_envio=TipoEnvioEnum.TEXTO,
        conteudo_bruto=texto,
        texto_ocr=None,
        texto_confirmado=texto,
    )
    db.add(submissao)
    db.commit()
    db.refresh(submissao)
    return submissao


@router.get("/submissoes", response_model=list[SubmissaoResponse])
def listar_submissoes(
    atividade_id: uuid.UUID | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if usuario.perfil not in (PerfilEnum.ALUNO, PerfilEnum.PROFESSOR):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só alunos e professores listam redações.")

    if atividade_id is not None:
        atividade = db.get(Atividade, atividade_id)
        turma = db.get(Turma, atividade.turma_id) if atividade else None
        papel = UsuarioTurmaPapelEnum.ALUNO if usuario.perfil == PerfilEnum.ALUNO else UsuarioTurmaPapelEnum.PROFESSOR
        if not turma or turma.escola_id != usuario.escola_id or not _na_turma(db, usuario.id, turma.id, papel):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Atividade não encontrada.")

    consulta = (
        db.query(Submissao)
        .join(Atividade, Submissao.atividade_id == Atividade.id)
        .join(Turma, Atividade.turma_id == Turma.id)
        .join(Usuario, Submissao.aluno_id == Usuario.id)
        .filter(Turma.escola_id == usuario.escola_id, Usuario.escola_id == usuario.escola_id)
    )
    if usuario.perfil == PerfilEnum.ALUNO:
        consulta = consulta.filter(Submissao.aluno_id == usuario.id)
    else:
        turmas_professor = db.query(UsuarioTurma.turma_id).filter(
            UsuarioTurma.usuario_id == usuario.id,
            UsuarioTurma.papel == UsuarioTurmaPapelEnum.PROFESSOR,
        )
        consulta = consulta.filter(Atividade.turma_id.in_(turmas_professor))
    if atividade_id is not None:
        consulta = consulta.filter(Submissao.atividade_id == atividade_id)
    return consulta.order_by(Submissao.criado_em.desc(), Submissao.id.desc()).offset(offset).limit(limit).all()


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
    atividade, aluno = _validar_envio(db, usuario, atividade_id, aluno_id)

    image_bytes = ler_imagem(file)
    texto = ocr(image_bytes, file.content_type)  # se o OCR falhar, nada e gravado

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
        confianca=float(correcao.confianca), status=correcao.status.value, modelo_usado=correcao.modelo_usado,
        feedback=correcao.feedback,
        criterios=[
            CriterioResponse(codigo=t.habilidade_codigo, nome=t.nome, nota=float(c.nota), justificativa=c.justificativa)
            for c, t in criterios
        ],
    )


def _so_professor(db: Session, submissao: Submissao, usuario: Usuario):
    # a nota da IA so e vista pelo professor; o aluno so ve depois da aprovacao (RN-01)
    if not _professor_da_turma(db, usuario, db.get(Atividade, submissao.atividade_id).turma_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só o professor da turma vê a correção antes da aprovação.")


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
    temas = {t.habilidade_codigo: t for t in db.query(Tema).filter_by(materia_id=atividade.materia_id)}
    if sorted(temas) != ["C1", "C2", "C3", "C4", "C5"]:
        raise HTTPException(status.HTTP_409_CONFLICT, "A matéria desta atividade não tem as 5 competências do ENEM.")

    if not settings.GEMINI_API_KEY:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Correção indisponível: servidor sem chave do Gemini.")
    try:
        resultado, modelo = ia.corrigir(submissao.texto_confirmado, (payload.tema or "").strip() or atividade.titulo)
    except Exception:
        logger.exception("falha na correcao")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Falha ao gerar a correção. Tente de novo.")

    # nota do modelo reserva (lite) e mais rasa: no teste deu 120 em tudo com "95% de confianca".
    # vai para o topo da fila do professor junto com as de baixa confianca
    atencao = resultado.confianca < CONFIANCA_MINIMA or modelo != settings.GEMINI_MODEL
    correcao = Correcao(
        submissao_id=submissao.id,
        nota_ia=sum(c.nota for c in resultado.competencias),
        confianca=round(resultado.confianca, 2),
        status=StatusCorrecaoEnum.REQUER_ATENCAO if atencao else StatusCorrecaoEnum.PENDENTE,
        modelo_usado=modelo,
        versao_prompt=ia.VERSAO_PROMPT,
        feedback=resultado.feedback_geral,
    )
    db.add(correcao)
    db.flush()
    for c in resultado.competencias:
        db.add(CorrecaoCriterio(correcao_id=correcao.id, tema_id=temas[c.codigo].id, nota=c.nota, justificativa=c.justificativa))
    db.commit()
    return _correcao_response(db, correcao)


@router.get("/submissoes/{submissao_id}/correcao", response_model=CorrecaoResponse)
def ver_correcao(submissao_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    submissao = _submissao_visivel(db, submissao_id, usuario)
    _so_professor(db, submissao, usuario)
    correcao = db.query(Correcao).filter_by(submissao_id=submissao.id).first()
    if not correcao:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ainda não corrigida.")
    return _correcao_response(db, correcao)
