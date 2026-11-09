import logging
import mimetypes
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, status, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.config import settings
from app.custo import registrar_uso
from app.database import get_db
from app.models.enum import (
    PerfilEnum, StatusCorrecaoEnum, TipoAtividadeEnum, TipoEnvioEnum, TipoMateriaEnum, UsuarioTurmaPapelEnum,
)
from app.models.usuario import (
    Atividade, Correcao, CorrecaoCriterio, Materia, Submissao, Tema, Turma, Usuario, UsuarioTurma,
)
from app.routers.ocr import ler_imagem, ocr
from app.schemas.submissao import (
    AlunoResumo, AtividadeResponse, ConfirmarTextoRequest,
    CriarAtividadeRequest, CriarMateriaRequest, CriterioResponse, EnviarTextoRequest,
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
        if correcao:
            # o aluno ve a propria correcao assim que ela existe (nota_professor nulo ate
            # aprovar): e provisoria, so o professor confirma depois (ver _pode_ver_correcao)
            linhas = (
                db.query(CorrecaoCriterio, Tema).join(Tema, Tema.id == CorrecaoCriterio.tema_id)
                .filter(CorrecaoCriterio.correcao_id == correcao.id).order_by(Tema.habilidade_codigo)
            )
            criterios = [
                CriterioResponse(
                    codigo=t.habilidade_codigo, nome=t.nome, nota=float(c.nota),
                    nota_professor=float(c.nota_professor) if c.nota_professor is not None else None,
                    justificativa=c.justificativa, pontos=c.pontos or [],
                )
                for c, t in linhas
            ]
        resposta.append(MinhaSubmissaoResponse(
            id=s.id,
            atividade_id=s.atividade_id,
            atividade_titulo=db.get(Atividade, s.atividade_id).titulo,
            status=correcao.status.value if correcao else "AGUARDANDO_CORRECAO",
            criado_em=s.criado_em,
            nota=float(correcao.nota_professor if aprovada else correcao.nota_ia) if correcao else None,
            feedback=correcao.feedback if correcao else None,
            criterios=criterios,
            texto=s.texto_confirmado or s.texto_ocr,
            tipo_envio=s.tipo_envio.value,
        ))
    return resposta


@router.get("/submissoes/{submissao_id}", response_model=SubmissaoResponse)
def ver_submissao(submissao_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return _submissao_visivel(db, submissao_id, usuario)


# serve a foto original (RF-11): usada para desenhar a caixa da IA em cima da imagem.
# mesma regra de visibilidade das outras rotas de submissao (aluno dono, professor, gestor).
@router.get("/submissoes/{submissao_id}/imagem")
def ver_imagem_submissao(submissao_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    submissao = _submissao_visivel(db, submissao_id, usuario)
    if submissao.tipo_envio != TipoEnvioEnum.IMAGEM or not submissao.conteudo_bruto:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Esta submissão não tem foto.")
    caminho = Path(submissao.conteudo_bruto)
    if not caminho.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Foto não encontrada.")
    mime, _ = mimetypes.guess_type(str(caminho))
    return FileResponse(caminho, media_type=mime or "image/jpeg")


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


