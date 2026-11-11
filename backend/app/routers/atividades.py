"""Editar e excluir atividade. Quem pode: o professor da turma e o gestor da escola.

- Editar: titulo e prazo sempre; valor_total e questoes/gabarito so enquanto ninguem enviou nada.
- Excluir: sem submissoes apaga de verdade; com submissoes ARQUIVA (some para os alunos e das listas,
  mas notas e dominio continuam), porque apagar levaria embora o historico de aluno.
"""
import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auditoria import registrar
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.usuario import Atividade, Materia, Submissao, Tema, Usuario
from app.routers.questoes import _apagar_arquivo, _pode_editar
from app.routers.submissoes import MATERIAS_EXATAS, _atividade_response
from app.schemas.submissao import AtividadeResponse, EditarAtividadeRequest, ExclusaoResponse

router = APIRouter(tags=["atividades"])


def _minha(db: Session, usuario: Usuario, atividade_id: uuid.UUID) -> Atividade:
    atividade = db.get(Atividade, atividade_id)
    if not atividade or atividade.arquivada:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Atividade não encontrada.")
    _pode_editar(db, atividade, usuario)  # 404 se for de outra escola, 403 se nao for da turma dele
    return atividade


def _tem_submissoes(db: Session, atividade: Atividade) -> bool:
    return db.query(Submissao.id).filter_by(atividade_id=atividade.id).first() is not None


@router.put("/atividades/{atividade_id}", response_model=AtividadeResponse)
def editar_atividade(atividade_id: uuid.UUID, payload: EditarAtividadeRequest,
                     usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    atividade = _minha(db, usuario, atividade_id)
    if payload.titulo is not None:
        atividade.titulo = payload.titulo.strip()
    if "prazo" in payload.model_fields_set:  # null explicito = tirar o prazo
        atividade.prazo = payload.prazo

    muda_gabarito = payload.valor_total is not None or payload.questoes is not None
    if muda_gabarito:
        if _tem_submissoes(db, atividade):
            raise HTTPException(status.HTTP_409_CONFLICT,
                                "Já há envios nesta atividade: só o título e o prazo podem mudar. "
                                "Para mudar o gabarito, crie uma nova atividade.")
        materia = db.get(Materia, atividade.materia_id)
        if materia.tipo not in MATERIAS_EXATAS:
            raise HTTPException(422, "Redação não tem gabarito nem valor total para editar.")
        if payload.valor_total is not None:
            atividade.valor_total = Decimal(str(payload.valor_total))
        if payload.questoes is not None:
            existentes = {t.habilidade_codigo: t for t in db.query(Tema).filter_by(atividade_id=atividade.id)}
            for i, q in enumerate(payload.questoes, start=1):
                tema = existentes.pop(f"Q{i}", None)
                if tema is None:
                    db.add(Tema(materia_id=materia.id, atividade_id=atividade.id, habilidade_codigo=f"Q{i}",
                                nome=q.enunciado.strip(), resposta_correta=q.resposta_correta.strip()))
                else:  # mesma posicao: edita no lugar e a figura da questao continua
                    tema.nome, tema.resposta_correta = q.enunciado.strip(), q.resposta_correta.strip()
            for sobra in existentes.values():  # a lista ficou menor: tira as ultimas (e as figuras delas)
                _apagar_arquivo(sobra.imagem)
                db.delete(sobra)

    registrar(db, usuario.id, "EDITAR", "Atividade", atividade.id)
    db.commit()
    db.refresh(atividade)
    return _atividade_response(db, atividade, usuario)


@router.delete("/atividades/{atividade_id}", response_model=ExclusaoResponse)
def excluir_atividade(atividade_id: uuid.UUID, usuario: Usuario = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    atividade = _minha(db, usuario, atividade_id)
    if _tem_submissoes(db, atividade):
        atividade.arquivada = True
        acao = "arquivada"
    else:
        for tema in db.query(Tema).filter_by(atividade_id=atividade.id):
            _apagar_arquivo(tema.imagem)
            db.delete(tema)
        db.delete(atividade)
        acao = "excluida"
    registrar(db, usuario.id, "ARQUIVAR" if acao == "arquivada" else "EXCLUIR", "Atividade", atividade_id)
    db.commit()
    return ExclusaoResponse(acao=acao)
