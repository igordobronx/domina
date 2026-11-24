"""Exercicios de pratica criados pelo professor (a mao ou com ajuda da IA).

Separacao das abas do aluno: a regra e QUEM PUBLICOU.
- "Para voce (IA)": /estudos/meu, gerados na hora pelos pontos fracos do aluno (nada aqui).
- "Do professor": esta rota. Se o professor pediu ajuda da IA, continua sendo do professor
  (gerado_por_ia=True so liga um selo). A IA so sugere rascunhos; nada chega ao aluno sem o
  professor salvar (RN-13).
Exercicio nao vale nota: provas continuam em Atividade.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import avisos
from app.auditoria import registrar
from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.ia import memoria, registro
from app.exercicios_ia import SugestaoExercicio, sugerir_exercicios, sugerir_resposta_exemplo
from app.models.enum import PerfilEnum, UsuarioTurmaPapelEnum
from app.lecionados import leciona
from app.models.usuario import Exercicio, ExercicioResposta, Materia, Turma, Usuario, UsuarioTurma
from app.routers.submissoes import _professor_da_turma
from app.routers.assuntos import assunto_do_usuario
from app.schemas.exercicio import (
    AvaliarRespostaRequest, ExercicioAlunoResponse, ExercicioLoteRequest, ExercicioProfessorResponse,
    ExercicioRequest, RespostaAlunoResponse, ResponderRequest, ResumoAlunoResponse, SugerirRequest,
    SugerirRespostaRequest, SugestaoRespostaResponse,
)

router = APIRouter(prefix="/exercicios", tags=["exercicios"])


def _so_professor(usuario: Usuario) -> None:
    if usuario.perfil != PerfilEnum.PROFESSOR:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores criam exercícios.")


def _materia_da_escola(db: Session, usuario: Usuario, materia_id) -> Materia:
    materia = db.get(Materia, materia_id)
    if not materia or materia.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Matéria não encontrada.")
    return materia


def _alunos_da_turma(db: Session, turma_id) -> list[Usuario]:
    return (db.query(Usuario).join(UsuarioTurma, UsuarioTurma.usuario_id == Usuario.id)
            .filter(UsuarioTurma.turma_id == turma_id, UsuarioTurma.papel == UsuarioTurmaPapelEnum.ALUNO)
            .order_by(Usuario.nome).all())


def _exemplos(ex: Exercicio) -> list[str]:
    return ex.respostas_exemplo or ([ex.resposta_exemplo] if ex.resposta_exemplo else [])


def _resultado(r: ExercicioResposta | None) -> str | None:
    if r is None:
        return None
    if r.resultado:
        return r.resultado
    return "CERTA" if r.correta else "ERRADA" if r.correta is False else None


def _alvo(db: Session, ex: Exercicio) -> list[Usuario]:
    """Quem deve fazer: os escolhidos (se ainda estao na turma) ou a turma toda."""
    alunos = _alunos_da_turma(db, ex.turma_id)
    return [a for a in alunos if str(a.id) in ex.alunos] if ex.alunos else alunos


def _conferir(db: Session, usuario: Usuario, payload: ExercicioRequest) -> None:
    materia = _materia_da_escola(db, usuario, payload.materia_id)
    if payload.assunto_id:
        assunto_do_usuario(db, usuario, payload.assunto_id, materia.id)
    turma = db.get(Turma, payload.turma_id)
    if not turma or turma.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma não encontrada.")
    if not _professor_da_turma(db, usuario, turma.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Você não leciona nesta turma.")
    if not leciona(db, usuario, turma.id, materia.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"Você não leciona {materia.nome} na turma {turma.nome}.")
    if payload.aluno_ids:
        da_turma = {ut.usuario_id for ut in db.query(UsuarioTurma).filter_by(
            turma_id=turma.id, papel=UsuarioTurmaPapelEnum.ALUNO)}
        if not set(payload.aluno_ids) <= da_turma:
            raise HTTPException(422, "Algum aluno escolhido não é desta turma.")


def _meu(db: Session, usuario: Usuario, exercicio_id: uuid.UUID) -> Exercicio:
    _so_professor(usuario)
    ex = db.get(Exercicio, exercicio_id)
    if not ex or not ex.ativo or ex.criado_por != usuario.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Exercício não encontrado.")
    return ex


def _aplicar(ex: Exercicio, p: ExercicioRequest) -> None:
    ex.titulo, ex.assunto, ex.assunto_id = p.titulo.strip(), p.assunto.strip(), p.assunto_id
    ex.materia_id, ex.turma_id, ex.tipo = p.materia_id, p.turma_id, p.tipo
    ex.alunos = sorted({str(a) for a in p.aluno_ids}) if p.aluno_ids else None
    ex.enunciado = p.enunciado.strip()
    ex.alternativas, ex.resposta_correta = p.alternativas, p.resposta_correta
    ex.resposta_exemplo = p.resposta_exemplo.strip() if p.resposta_exemplo else None
    ex.respostas_exemplo = p.respostas_exemplo if p.respostas_exemplo and len(p.respostas_exemplo) > 1 else None
    ex.explicacao = (p.explicacao or "").strip() or None
    ex.gerado_por_ia = p.gerado_por_ia


def _resposta_professor(db: Session, ex: Exercicio) -> ExercicioProfessorResponse:
    total, acertos = db.query(
        func.count(ExercicioResposta.id), func.count(ExercicioResposta.id).filter(ExercicioResposta.correta.is_(True)),
    ).filter(ExercicioResposta.exercicio_id == ex.id).one()
    return ExercicioProfessorResponse(
        id=ex.id, titulo=ex.titulo or "", assunto=ex.assunto or "", assunto_id=ex.assunto_id, materia_id=ex.materia_id,
        materia_nome=db.get(Materia, ex.materia_id).nome, turma_id=ex.turma_id,
        turma_nome=db.get(Turma, ex.turma_id).nome, tipo=ex.tipo,
        aluno_ids=[uuid.UUID(a) for a in ex.alunos] if ex.alunos else None,
        alunos_nomes=sorted(u.nome for u in db.query(Usuario).filter(
            Usuario.id.in_([uuid.UUID(a) for a in ex.alunos]))) if ex.alunos else [], enunciado=ex.enunciado,
        alternativas=ex.alternativas, resposta_correta=ex.resposta_correta, resposta_exemplo=ex.resposta_exemplo,
        respostas_exemplo=_exemplos(ex),
        explicacao=ex.explicacao, gerado_por_ia=ex.gerado_por_ia, criado_em=ex.criado_em,
        respostas=total, acertos=acertos, alunos_alvo=len(_alvo(db, ex)), grupo_id=ex.grupo_id, ordem=ex.ordem or 0,
    )


def _resposta_aluno(db: Session, ex: Exercicio, minha: ExercicioResposta | None) -> ExercicioAlunoResponse:
    professor = db.get(Usuario, ex.criado_por)
    r = ExercicioAlunoResponse(
        id=ex.id, titulo=ex.titulo or "", assunto=ex.assunto or "", materia_nome=db.get(Materia, ex.materia_id).nome,
        professor_nome=professor.nome if professor else "", tipo=ex.tipo, enunciado=ex.enunciado,
        alternativas=ex.alternativas, gerado_por_ia=ex.gerado_por_ia, criado_em=ex.criado_em,
        grupo_id=ex.grupo_id, ordem=ex.ordem or 0,
    )
    if minha:  # gabarito so depois de responder
        r.minha_resposta, r.correta, r.comentario = minha.resposta, minha.correta, minha.comentario
        r.resultado = _resultado(minha)
        r.resposta_correta, r.resposta_exemplo, r.explicacao = ex.resposta_correta, ex.resposta_exemplo, ex.explicacao
        r.respostas_exemplo = _exemplos(ex)
    return r


def _guardar_treino(db: Session, materia: Materia, usuario: Usuario) -> None:
    # material de treino da IA propria (app/ia/registro.py); nunca derruba a rota
    try:
        registro.gravar(db, materia_id=materia.id, professor_id=usuario.id)
        db.commit()
    except Exception:
        db.rollback()


def _precisa_da_ia() -> None:
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "IA indisponível: servidor sem chave do Claude.")


# ---------- professor ----------

@router.get("", response_model=list[ExercicioProfessorResponse])
def listar_meus(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _so_professor(usuario)
    exercicios = (db.query(Exercicio).filter_by(criado_por=usuario.id, ativo=True)
                  .order_by(Exercicio.criado_em.desc(), Exercicio.ordem).all())
    return [_resposta_professor(db, ex) for ex in exercicios]


@router.post("", response_model=ExercicioProfessorResponse, status_code=status.HTTP_201_CREATED)
def criar(payload: ExercicioRequest, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _so_professor(usuario)
    _conferir(db, usuario, payload)
    ex = Exercicio(criado_por=usuario.id, aprovado_por=usuario.id)  # publicar = aprovar (RN-13)
    _aplicar(ex, payload)
    db.add(ex)
    db.flush()
    registrar(db, usuario.id, "CRIAR", "Exercicio", ex.id)
    db.commit()
    db.refresh(ex)
    avisos.tentar(db, avisos.exercicio_novo, ex, _alvo(db, ex))  # avisa quem deve fazer
    return _resposta_professor(db, ex)


@router.post("/lote", response_model=list[ExercicioProfessorResponse], status_code=status.HTTP_201_CREATED)
def criar_em_turmas(payload: ExercicioLoteRequest, usuario: Usuario = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    """O mesmo exercicio em varias turmas: um exercicio separado por turma (respostas nao se misturam)."""
    _so_professor(usuario)
    escolhidos = set(payload.aluno_ids or [])
    criados, usados = [], set()
    extras = [q.model_dump() for q in payload.mais_questoes]
    for turma_id in dict.fromkeys(payload.turma_ids):  # sem repetir, na ordem
        dados = payload.model_dump(exclude={"turma_ids", "turma_id", "aluno_ids", "mais_questoes"})
        if escolhidos:  # so os escolhidos que sao desta turma; nenhum = esta turma nao recebe
            da_turma = {a.id for a in _alunos_da_turma(db, turma_id)}
            daqui = escolhidos & da_turma
            if not daqui:
                continue
            usados |= daqui
            dados["aluno_ids"] = list(daqui)
        grupo = uuid.uuid4() if extras else None  # um grupo por turma: as respostas nao se misturam
        meta = {k: v for k, v in dados.items() if k in ("titulo", "assunto", "materia_id", "aluno_ids")}
        for ordem, questao in enumerate([None, *extras]):
            um = ExercicioRequest(**(dados if questao is None else {**meta, **questao}), turma_id=turma_id)
            if questao is None:
                _conferir(db, usuario, um)
            ex = Exercicio(criado_por=usuario.id, aprovado_por=usuario.id, grupo_id=grupo, ordem=ordem)
            _aplicar(ex, um)
            db.add(ex)
            db.flush()
            registrar(db, usuario.id, "CRIAR", "Exercicio", ex.id)
            criados.append(ex)
    if escolhidos - usados:
        db.rollback()
        raise HTTPException(422, "Algum aluno escolhido não é das turmas marcadas.")
    if not criados:
        raise HTTPException(422, "Escolha pelo menos um aluno.")
    db.commit()
    for ex in criados:
        avisos.tentar(db, avisos.exercicio_novo, ex, _alvo(db, ex))  # avisa quem deve fazer
    return [_resposta_professor(db, ex) for ex in criados]


@router.get("/resumo", response_model=list[ResumoAlunoResponse])
def resumo_da_turma(turma_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Por aluno da turma: quantos exercicios (deste professor) fez e quantos acertou."""
    _so_professor(usuario)
    if not _professor_da_turma(db, usuario, turma_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Você não leciona nesta turma.")
    exercicios = db.query(Exercicio).filter_by(criado_por=usuario.id, turma_id=turma_id, ativo=True).all()
    respostas = {(r.exercicio_id, r.aluno_id): r for r in db.query(ExercicioResposta).filter(
        ExercicioResposta.exercicio_id.in_([e.id for e in exercicios]))} if exercicios else {}
    linhas = []
    for aluno in _alunos_da_turma(db, turma_id):
        meus = [e for e in exercicios if not e.alunos or str(aluno.id) in e.alunos]
        feitas = [respostas[(e.id, aluno.id)] for e in meus if (e.id, aluno.id) in respostas]
        resultados = [_resultado(r) for r in feitas]
        linhas.append(ResumoAlunoResponse(
            aluno_id=aluno.id, nome=aluno.nome, total=len(meus), feitos=len(feitas),
            acertos=resultados.count("CERTA"), parciais=resultados.count("PARCIAL"),
            corrigidos=sum(1 for x in resultados if x is not None)))
    return linhas


@router.get("/{exercicio_id}/respostas", response_model=list[RespostaAlunoResponse])
def ver_respostas(exercicio_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    ex = _meu(db, usuario, exercicio_id)
    respostas = {r.aluno_id: r for r in db.query(ExercicioResposta).filter_by(exercicio_id=ex.id)}
    linhas = []
    for aluno in _alvo(db, ex):
        r = respostas.get(aluno.id)
        linhas.append(RespostaAlunoResponse(
            aluno_id=aluno.id, nome=aluno.nome, fez=r is not None,
            resposta=r.resposta if r else None, correta=r.correta if r else None, resultado=_resultado(r),
            comentario=r.comentario if r else None, respondido_em=r.criado_em if r else None))
    return linhas


@router.put("/{exercicio_id}/respostas/{aluno_id}", response_model=RespostaAlunoResponse)
def avaliar_resposta(exercicio_id: uuid.UUID, aluno_id: uuid.UUID, payload: AvaliarRespostaRequest,
                     usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Professor marca certa/parcial/errada (so no discursivo; o objetivo e automatico) e/ou comenta."""
    ex = _meu(db, usuario, exercicio_id)
    r = db.query(ExercicioResposta).filter_by(exercicio_id=ex.id, aluno_id=aluno_id).first()
    if not r:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Este aluno ainda não respondeu.")
    if "resultado" in payload.model_fields_set:
        if ex.tipo == "OBJETIVO":
            raise HTTPException(422, "No exercício objetivo o acerto é automático.")
        r.resultado = payload.resultado
        r.correta = {"CERTA": True, "ERRADA": False}.get(payload.resultado or "")
    if "comentario" in payload.model_fields_set:
        r.comentario = (payload.comentario or "").strip() or None
    # parcial ou errada: o aluno precisa saber o que faltou
    if r.resultado in ("PARCIAL", "ERRADA") and ex.tipo == "DISCURSIVO" and not r.comentario:
        db.rollback()
        raise HTTPException(422, "Para marcar como parcial ou errada, escreva um comentário para o aluno.")
    registrar(db, usuario.id, "AVALIAR", "ExercicioResposta", r.id)
    db.flush()
    if ex.tipo == "DISCURSIVO":
        memoria.indexar_exercicio(db, ex, r)  # a IA aprende com o que o professor marcou (nunca bloqueia)
    db.commit()
    aluno = db.get(Usuario, aluno_id)
    return RespostaAlunoResponse(aluno_id=aluno_id, nome=aluno.nome, fez=True, resposta=r.resposta,
                                 correta=r.correta, resultado=_resultado(r), comentario=r.comentario,
                                 respondido_em=r.criado_em)


@router.put("/{exercicio_id}", response_model=ExercicioProfessorResponse)
def editar(exercicio_id: uuid.UUID, payload: ExercicioRequest,
           usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    ex = _meu(db, usuario, exercicio_id)
    _conferir(db, usuario, payload)
    _aplicar(ex, payload)
    registrar(db, usuario.id, "EDITAR", "Exercicio", ex.id)
    db.commit()
    db.refresh(ex)
    return _resposta_professor(db, ex)


@router.delete("/{exercicio_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir(exercicio_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    ex = _meu(db, usuario, exercicio_id)
    # excluir um exercicio com varias questoes tira o exercicio inteiro (todas as questoes do grupo)
    grupo = [ex] if not ex.grupo_id else db.query(Exercicio).filter_by(grupo_id=ex.grupo_id, criado_por=usuario.id).all()
    for x in grupo:
        x.ativo = False  # some para os alunos; as respostas ficam
        registrar(db, usuario.id, "EXCLUIR", "Exercicio", x.id)
    db.commit()


@router.post("/sugerir", response_model=list[SugestaoExercicio])
def sugerir(payload: SugerirRequest, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Rascunhos da IA sobre um tema. NAO salva: o professor revisa e salva cada um."""
    _so_professor(usuario)
    materia = _materia_da_escola(db, usuario, payload.materia_id)
    _precisa_da_ia()
    if payload.assunto_id:
        assunto_do_usuario(db, usuario, payload.assunto_id, materia.id)
    instrucoes = (payload.instrucoes or "").strip() or None
    # memoria do professor (RAG): so o MATERIAL dele; exemplos de correcao nao ajudam a criar exercicio
    contexto = memoria.contexto_do_professor(
        db, materia.id, f"{payload.assunto} {instrucoes or ''}", professor_id=usuario.id, exemplos=0,
        assunto_id=payload.assunto_id)
    sugestoes = sugerir_exercicios(materia.nome, payload.assunto.strip(), payload.tipo, payload.quantidade,
                                   instrucoes, contexto=contexto)
    _guardar_treino(db, materia, usuario)
    return sugestoes


@router.post("/sugerir-resposta", response_model=SugestaoRespostaResponse)
def sugerir_resposta(payload: SugerirRespostaRequest, usuario: Usuario = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    """Resposta de exemplo para um discursivo (botao "IA sugere")."""
    _so_professor(usuario)
    materia = _materia_da_escola(db, usuario, payload.materia_id)
    _precisa_da_ia()
    if payload.assunto_id:
        assunto_do_usuario(db, usuario, payload.assunto_id, materia.id)
    contexto = memoria.contexto_do_professor(
        db, materia.id, f"{payload.assunto or ''} {payload.enunciado}", professor_id=usuario.id, exemplos=0,
        assunto_id=payload.assunto_id)
    resposta = sugerir_resposta_exemplo(
        materia.nome, (payload.assunto or "").strip(), payload.enunciado.strip(), contexto=contexto)
    _guardar_treino(db, materia, usuario)
    return SugestaoRespostaResponse(resposta_exemplo=resposta)


# ---------- aluno ----------

def _turmas_do_aluno(db: Session, usuario: Usuario) -> list:
    return [ut.turma_id for ut in db.query(UsuarioTurma).filter_by(
        usuario_id=usuario.id, papel=UsuarioTurmaPapelEnum.ALUNO)]


def _e_para_mim(ex: Exercicio, usuario: Usuario) -> bool:
    return not ex.alunos or str(usuario.id) in ex.alunos


@router.get("/turma", response_model=list[ExercicioAlunoResponse])
def da_minha_turma(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if usuario.perfil != PerfilEnum.ALUNO:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só alunos usam esta rota.")
    turmas = _turmas_do_aluno(db, usuario)
    if not turmas:
        return []
    exercicios = (db.query(Exercicio).filter(Exercicio.turma_id.in_(turmas), Exercicio.ativo.is_(True))
                  .order_by(Exercicio.criado_em.desc(), Exercicio.ordem).all())
    minhas = {r.exercicio_id: r for r in db.query(ExercicioResposta).filter(
        ExercicioResposta.aluno_id == usuario.id,
        ExercicioResposta.exercicio_id.in_([e.id for e in exercicios]))} if exercicios else {}
    return [_resposta_aluno(db, ex, minhas.get(ex.id)) for ex in exercicios if _e_para_mim(ex, usuario)]


@router.post("/{exercicio_id}/responder", response_model=ExercicioAlunoResponse)
def responder(exercicio_id: uuid.UUID, payload: ResponderRequest,
              usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if usuario.perfil != PerfilEnum.ALUNO:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só alunos respondem exercícios.")
    ex = db.get(Exercicio, exercicio_id)
    if not ex or not ex.ativo or ex.turma_id not in _turmas_do_aluno(db, usuario) or not _e_para_mim(ex, usuario):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Exercício não encontrado.")
    correta = None
    if ex.tipo == "OBJETIVO":
        try:
            indice = int(payload.resposta)
        except ValueError:
            raise HTTPException(422, "Escolha uma das alternativas.")
        if not 0 <= indice < len(ex.alternativas or []):
            raise HTTPException(422, "Escolha uma das alternativas.")
        correta = indice == ex.resposta_correta
    # so uma resposta por aluno: depois de responder, nao da para refazer
    if db.query(ExercicioResposta).filter_by(exercicio_id=ex.id, aluno_id=usuario.id).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Você já respondeu este exercício.")
    minha = ExercicioResposta(exercicio_id=ex.id, aluno_id=usuario.id, resposta=payload.resposta.strip(),
                              correta=correta, comentario=None,
                              resultado=None if correta is None else "CERTA" if correta else "ERRADA")
    db.add(minha)
    minha.criado_em = func.now()
    db.commit()
    return _resposta_aluno(db, ex, minha)
