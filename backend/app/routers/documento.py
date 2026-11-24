import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auditoria import registrar
from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.ia import memoria, registro
from app.models.enum import PerfilEnum, TipoDocumentoEnum
from app.lecionados import materias_do_professor
from app.routers.assuntos import assunto_do_usuario
from app.models.usuario import Correcao, DocumentoBase, IaTrecho, Materia, Usuario
from app.schemas.documento import (
    DispensarSugestaoRequest, DocumentoBaseResponse, EmUsoRequest, ErroDaIA, InstrucaoRequest, InstrucaoResponse,
    ItemAprendido, MemoriaIAResponse, SugestaoInstrucao,
)

router = APIRouter(tags=["documentos"])

MAX_DOCUMENTO_BYTES = 20 * 1024 * 1024  # 20 MB: apostila/rubrica em PDF cabe com folga
EXTENSOES = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".webp"}


def _so_equipe(usuario: Usuario) -> None:
    if usuario.perfil not in (PerfilEnum.PROFESSOR, PerfilEnum.GESTOR):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Só professores e gestores usam os materiais.")


def _materia_da_escola(db: Session, usuario: Usuario, materia_id) -> Materia:
    materia = db.get(Materia, materia_id)
    if not materia or materia.escola_id != usuario.escola_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Matéria não encontrada.")
    return materia


def _visiveis(db: Session, usuario: Usuario, inativos: bool = False):
    """Gestor ve os materiais da escola toda; professor so os que ele mesmo enviou.
    inativos=True inclui os "tirados de uso" (arquivados), para a tela poder mostrar o botao "Voltar a usar"."""
    q = (db.query(DocumentoBase, Materia, Usuario)
         .join(Materia, Materia.id == DocumentoBase.materia_id)
         .join(Usuario, Usuario.id == DocumentoBase.enviado_por)
         .filter(Materia.escola_id == usuario.escola_id))
    if not inativos:
        q = q.filter(DocumentoBase.ativo.is_(True))
    if usuario.perfil == PerfilEnum.PROFESSOR:
        q = q.filter(DocumentoBase.enviado_por == usuario.id)
    return q


def _resposta(d: DocumentoBase, m: Materia, u: Usuario) -> DocumentoBaseResponse:
    return DocumentoBaseResponse(
        id=d.id, materia_id=d.materia_id, materia_nome=m.nome, nome_arquivo=d.nome_arquivo, tipo=d.tipo,
        status_processamento=d.status_processamento, tamanho_bytes=d.tamanho_bytes, enviado_por_nome=u.nome,
        assunto_id=d.assunto_id, pode_baixar=bool(d.caminho) and d.ativo, criado_em=d.criado_em, detalhe=d.detalhe, ativo=d.ativo,
    )


@router.get("/documentos", response_model=list[DocumentoBaseResponse])
def listar_documentos(materia_id: uuid.UUID | None = None, incluir_inativos: bool = False,
                      usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _so_equipe(usuario)
    q = _visiveis(db, usuario, incluir_inativos)
    if materia_id:
        q = q.filter(DocumentoBase.materia_id == materia_id)
    return [_resposta(d, m, u) for d, m, u in q.order_by(DocumentoBase.criado_em.desc()).all()]


@router.get("/materias/{materia_id}/documentos", response_model=list[DocumentoBaseResponse])
def listar_documentos_da_materia(materia_id: uuid.UUID, usuario: Usuario = Depends(get_current_user),
                                 db: Session = Depends(get_db)):
    _so_equipe(usuario)
    _materia_da_escola(db, usuario, materia_id)
    return listar_documentos(materia_id=materia_id, usuario=usuario, db=db)


# RF-13: professor/gestor sobe material de apoio (apostila, rubrica, gabarito) de uma materia da escola.
# Na mesma chamada a IA le o arquivo e guarda os trechos na memoria da materia (app/ia/memoria.py):
# o material ja vale para a proxima correcao/exercicio. Se nao der para ler, fica ERRO com o motivo.
# ponytail: leitura dentro da requisicao (PDF grande demora alguns segundos); fila se virar problema
@router.post("/materias/{materia_id}/documentos", response_model=DocumentoBaseResponse,
             status_code=status.HTTP_201_CREATED)
def enviar_documento(
    materia_id: uuid.UUID,
    file: UploadFile,
    tipo: TipoDocumentoEnum = Form(...),
    assunto_id: uuid.UUID | None = Form(default=None),
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _so_equipe(usuario)
    materia = _materia_da_escola(db, usuario, materia_id)
    if usuario.perfil == PerfilEnum.PROFESSOR and materia.id not in materias_do_professor(db, usuario.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"Você não leciona {materia.nome}.")

    if assunto_id:
        assunto_do_usuario(db, usuario, assunto_id, materia.id)
    sufixo = Path(file.filename or "").suffix.lower()
    if sufixo not in EXTENSOES:
        raise HTTPException(422, "Envie PDF, DOCX, TXT ou imagem (PNG, JPG, WEBP).")
    conteudo = file.file.read(MAX_DOCUMENTO_BYTES + 1)
    if len(conteudo) > MAX_DOCUMENTO_BYTES:
        raise HTTPException(413, "Arquivo maior que 20 MB.")
    if not conteudo:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Arquivo vazio.")

    nome_no_disco = f"{uuid.uuid4()}{sufixo}"
    caminho = Path(settings.UPLOAD_DIR) / nome_no_disco
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(conteudo)

    documento = DocumentoBase(
        materia_id=materia.id,
        enviado_por=usuario.id,
        nome_arquivo=file.filename or nome_no_disco,
        tipo=tipo,
        tamanho_bytes=len(conteudo),
        caminho=nome_no_disco,
        assunto_id=assunto_id,
    )
    db.add(documento)
    db.flush()
    memoria.indexar_documento(db, documento)
    registro.gravar(db, materia_id=materia.id, professor_id=usuario.id)  # leitura de foto/PDF escaneado
    registrar(db, usuario.id, "CRIAR", "DocumentoBase", documento.id)
    db.commit()
    db.refresh(documento)
    return _resposta(documento, materia, usuario)


def _meu_documento(db: Session, usuario: Usuario, documento_id: uuid.UUID):
    _so_equipe(usuario)
    linha = _visiveis(db, usuario).filter(DocumentoBase.id == documento_id).first()
    if not linha:  # de outra escola, de outro professor ou arquivado = nao existe
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Material não encontrado.")
    return linha


@router.get("/documentos/{documento_id}/arquivo")
def baixar_documento(documento_id: uuid.UUID, usuario: Usuario = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    d, _, _ = _meu_documento(db, usuario, documento_id)
    arquivo = Path(settings.UPLOAD_DIR) / (d.caminho or "")
    if not d.caminho or not arquivo.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "O arquivo deste material não está disponível.")
    return FileResponse(arquivo, filename=d.nome_arquivo)


# excluir = arquivar: o registro e o arquivo ficam (um material ja usado para treinar a IA nao some)
@router.delete("/documentos/{documento_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_documento(documento_id: uuid.UUID, usuario: Usuario = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    d, _, _ = _meu_documento(db, usuario, documento_id)
    d.ativo = False  # a memoria da IA ja ignora material arquivado (memoria._do_professor)
    registrar(db, usuario.id, "ARQUIVAR", "DocumentoBase", d.id)
    db.commit()


@router.get("/materias/{materia_id}/ia", response_model=MemoriaIAResponse)
def ver_memoria_da_ia(materia_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Quanto a IA ja aprendeu nesta materia: trechos de material e correcoes aprovadas."""
    _materia_de_quem_ensina(db, usuario, materia_id)
    return memoria.resumo(db, materia_id, usuario.id)


# "Treinar IA" > Escrever instrucoes: o professor escreve direto para a IA o jeito dele ("sempre
# exija a verificacao final", "nao desconte erro de acento"). Valem sempre, em toda correcao e
# exercicio daquela materia (app/ia/memoria.py > instrucoes_de). So o professor/gestor mexe.
def _materia_de_quem_ensina(db: Session, usuario: Usuario, materia_id) -> Materia:
    _so_equipe(usuario)
    return _materia_da_escola(db, usuario, materia_id)


@router.get("/materias/{materia_id}/instrucoes", response_model=list[InstrucaoResponse])
def listar_instrucoes(materia_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _materia_de_quem_ensina(db, usuario, materia_id)
    return [InstrucaoResponse(id=t.id, materia_id=t.materia_id, texto=t.texto, assunto_id=t.assunto_id,
                              criado_em=t.criado_em)
            for t in memoria.instrucoes_de(db, materia_id, usuario.id, todas=True)]


@router.post("/materias/{materia_id}/instrucoes", response_model=InstrucaoResponse, status_code=status.HTTP_201_CREATED)
def criar_instrucao(materia_id: uuid.UUID, payload: InstrucaoRequest,
                    usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    materia = _materia_de_quem_ensina(db, usuario, materia_id)
    if payload.assunto_id:
        assunto_do_usuario(db, usuario, payload.assunto_id, materia.id)
    if len(memoria.instrucoes_de(db, materia.id, usuario.id, todas=True)) >= memoria.MAX_INSTRUCOES:
        raise HTTPException(status.HTTP_409_CONFLICT,
                            f"Você já tem {memoria.MAX_INSTRUCOES} instruções nesta matéria. Apague alguma antes.")
    texto = payload.texto.strip()
    trecho = IaTrecho(materia_id=materia.id, professor_id=usuario.id, origem=memoria.INSTRUCAO,
                      assunto_id=payload.assunto_id, titulo="Instrução do professor", texto=texto)
    db.add(trecho)
    db.commit()
    db.refresh(trecho)
    return InstrucaoResponse(id=trecho.id, materia_id=trecho.materia_id, texto=trecho.texto,
                             assunto_id=trecho.assunto_id, criado_em=trecho.criado_em)


@router.get("/materias/{materia_id}/erros-da-ia", response_model=list[ErroDaIA])
def erros_da_ia(materia_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """As correcoes em que a IA mais errou (para o professor ver onde ela ainda falha)."""
    _materia_de_quem_ensina(db, usuario, materia_id)
    return memoria.erros_da_ia(db, materia_id, usuario.id)


@router.get("/materias/{materia_id}/aprendido", response_model=list[ItemAprendido])
def ver_aprendido(materia_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _materia_de_quem_ensina(db, usuario, materia_id)
    return memoria.aprendido(db, materia_id, usuario.id)


# "Esquecer" = tirar de uso: a IA para de usar o item nas correcoes, mas NADA e apagado (a regra do
# projeto: o que a IA propria ainda nao aprendeu fica guardado; ia_trecho e ia_chamada continuam).
@router.put("/materias/{materia_id}/aprendido/{tipo}/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def uso_do_item(materia_id: uuid.UUID, tipo: str, item_id: uuid.UUID, payload: EmUsoRequest,
                usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _materia_de_quem_ensina(db, usuario, materia_id)
    tipo = tipo.upper()
    if tipo not in (memoria.CORRECAO, memoria.EXERCICIO) or not memoria.tirar_de_uso(
            db, materia_id, usuario.id, tipo, item_id, payload.em_uso):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item não encontrado.")
    db.commit()


# Quando o professor muda a nota varias vezes pelo mesmo motivo, a IA sugere virar instrucao.
# So vira instrucao se ele aceitar (POST /instrucoes); "dispensar" esconde a sugestao.
@router.get("/materias/{materia_id}/sugestoes-instrucoes", response_model=list[SugestaoInstrucao])
def sugestoes_de_instrucao(materia_id: uuid.UUID, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _materia_de_quem_ensina(db, usuario, materia_id)
    return memoria.sugerir_instrucoes(db, materia_id, usuario.id)


@router.post("/materias/{materia_id}/sugestoes-instrucoes/dispensar", status_code=status.HTTP_204_NO_CONTENT)
def dispensar_sugestao(materia_id: uuid.UUID, payload: DispensarSugestaoRequest,
                       usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _materia_de_quem_ensina(db, usuario, materia_id)
    db.query(Correcao).filter(Correcao.id.in_(payload.correcao_ids), Correcao.revisado_por == usuario.id).update(
        {Correcao.motivo_dispensado: True}, synchronize_session=False)
    db.commit()


@router.delete("/materias/{materia_id}/instrucoes/{instrucao_id}", status_code=status.HTTP_204_NO_CONTENT)
def apagar_instrucao(materia_id: uuid.UUID, instrucao_id: uuid.UUID,
                     usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _materia_de_quem_ensina(db, usuario, materia_id)
    trecho = db.get(IaTrecho, instrucao_id)
    # so apaga a PROPRIA instrucao (a do gestor vale para a escola e e dele)
    if not trecho or trecho.origem != memoria.INSTRUCAO or trecho.materia_id != materia_id or trecho.professor_id != usuario.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Instrução não encontrada.")
    db.delete(trecho)
    db.commit()


# "Tirar de uso" / "Voltar a usar" um material (na tela Treinar IA): mesmo efeito do excluir acima, mas
# reversivel. Tirado de uso, a IA nao usa e o treino da IA propria ignora; nada e apagado.
@router.put("/documentos/{documento_id}/uso", response_model=DocumentoBaseResponse)
def uso_do_documento(documento_id: uuid.UUID, payload: EmUsoRequest, usuario: Usuario = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    _so_equipe(usuario)
    linha = _visiveis(db, usuario, inativos=True).filter(DocumentoBase.id == documento_id).first()
    if not linha:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Material não encontrado.")
    d, m, u = linha
    d.ativo = payload.em_uso
    registrar(db, usuario.id, "REATIVAR" if payload.em_uso else "ARQUIVAR", "DocumentoBase", d.id)
    db.commit()
    return _resposta(d, m, u)
