"""Memoria do Domina por materia (o "R" do RAG): guarda e busca o que o professor ensinou.

Duas origens na tabela ia_trecho:
- MATERIAL: pedacos dos arquivos que o professor subiu (apostila, rubrica, gabarito...).
- CORRECAO: cada correcao que o professor APROVOU (resposta do aluno + nota que ele deu +
  quando ele mudou a nota da IA). Sao os exemplos do "jeito de corrigir" dele.

Nada aqui pode derrubar o fluxo principal: se a memoria falhar, a correcao sai sem contexto.
"""
import logging
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.ia.embeddings import embutir
from app.ia.extracao import ArquivoNaoLido, dividir, extrair_texto
from app.models.enum import PerfilEnum, StatusProcessamentoEnum
from app.models.usuario import (
    Atividade, Correcao, CorrecaoCriterio, DocumentoBase, IaTrecho, Submissao, Tema, Usuario,
)

logger = logging.getLogger(__name__)

MATERIAL, CORRECAO, INSTRUCAO = "MATERIAL", "CORRECAO", "INSTRUCAO"
MAX_INSTRUCOES = 30        # por professor e materia
MAX_LETRAS_INSTRUCOES = 8000  # o que entra no pedido ao modelo
# ponytail: a busca compara com os trechos da materia em memoria (Python). Aguenta bem milhares
# de trechos por materia; passando disso, trocar por pgvector no Postgres.
MAX_CANDIDATOS = 3000
MAX_TRECHOS_POR_DOCUMENTO = 400  # ~480 mil letras; apostila maior que isso e cortada

_VAZIAS = set("a o e de da do das dos em no na nos nas um uma para por com que se os as ao aos "
              "como mais mas ou ser foi sao e ha sua seu qual quais the".split())


# ---------- busca ----------

def _palavras(texto: str) -> list[str]:
    sem_acento = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    return [p for p in re.findall(r"[a-z0-9]+", sem_acento) if p not in _VAZIAS and (len(p) > 2 or p.isdigit())]


def _por_palavras(consulta: str, textos: list[str]) -> list[float]:
    # BM25 enxuto: palavra rara que aparece nos dois textos vale mais
    docs = [Counter(_palavras(t)) for t in textos]
    n = len(docs)
    termos = set(_palavras(consulta))
    notas = []
    for doc in docs:
        nota = 0.0
        for termo in termos:
            if doc[termo]:
                raridade = math.log(1 + n / sum(1 for d in docs if d[termo]))
                nota += raridade * doc[termo] / (doc[termo] + 1.5)
        notas.append(nota)
    return notas


def _cosseno(a: list[float], b: list[float]) -> float:
    norma = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / norma if norma else 0.0


def _do_professor(db: Session, materia_id, origem: str, professor_id):
    """A memoria e de CADA professor: o jeito de corrigir muda de um para outro (a inteligencia
    da IA, nao). Vale o que o proprio professor ensinou; material enviado pelo GESTOR e da
    escola e vale para todos os professores da materia."""
    q = db.query(IaTrecho).filter_by(materia_id=materia_id, origem=origem)
    if origem == CORRECAO:
        return q.filter(IaTrecho.professor_id == professor_id)
    gestores = db.query(Usuario.id).filter(Usuario.perfil == PerfilEnum.GESTOR)
    return q.filter(or_(IaTrecho.professor_id == professor_id, IaTrecho.professor_id.in_(gestores)))


def instrucoes_de(db: Session, materia_id, professor_id) -> list[IaTrecho]:
    """Instrucoes escritas pelo professor ("sempre faca tal coisa"). Valem SEMPRE (nao dependem
    de parecer com o pedido) e sao as mais fortes: o professor escreveu para a IA."""
    return (_do_professor(db, materia_id, INSTRUCAO, professor_id)
            .order_by(IaTrecho.criado_em).limit(MAX_INSTRUCOES).all())


def buscar(db: Session, materia_id, consulta: str, origem: str, k: int = 4,
           professor_id=None) -> list[IaTrecho]:
    """Os k trechos mais parecidos com a consulta, na memoria DESTE professor nesta materia.
    Sem professor (atividade antiga, sem dono) so vale o material do gestor."""
    if k <= 0:
        return []
    q = _do_professor(db, materia_id, origem, professor_id)
    candidatos = q.order_by(IaTrecho.criado_em.desc()).limit(MAX_CANDIDATOS).all()
    if not candidatos or not consulta.strip():
        return []
    com_vetor = [t for t in candidatos if t.embedding]
    vetor = embutir([consulta[:4000]], consulta=True) if com_vetor else None
    if vetor:
        pares = [(_cosseno(vetor[0], t.embedding), t) for t in com_vetor]
    else:
        notas = _por_palavras(consulta, [t.texto for t in candidatos])
        pares = [(nota, t) for nota, t in zip(notas, candidatos) if nota > 0]
    pares.sort(key=lambda par: par[0], reverse=True)
    return [t for _, t in pares[:k]]


# ---------- guardar ----------

def _guardar(db: Session, trechos: list[IaTrecho]) -> None:
    vetores = embutir([t.texto[:4000] for t in trechos])
    for i, trecho in enumerate(trechos):
        trecho.embedding = vetores[i] if vetores else None
        db.add(trecho)


def indexar_documento(db: Session, documento: DocumentoBase) -> None:
    """Le o arquivo, corta em trechos e guarda. Marca o documento como PROCESSADO ou ERRO
    (com o motivo em documento.detalhe). Nao da commit: quem chama decide."""
    db.query(IaTrecho).filter_by(documento_id=documento.id).delete()
    try:
        texto = extrair_texto(documento.nome_arquivo, Path(documento.caminho).read_bytes())
        partes = dividir(texto)[:MAX_TRECHOS_POR_DOCUMENTO]
        _guardar(db, [
            IaTrecho(materia_id=documento.materia_id, professor_id=documento.enviado_por, origem=MATERIAL,
                     documento_id=documento.id, titulo=f"{documento.tipo.value}: {documento.nome_arquivo}"[:255],
                     texto=parte)
            for parte in partes
        ])
        documento.status_processamento = StatusProcessamentoEnum.PROCESSADO
        documento.detalhe = None
    except ArquivoNaoLido as e:
        documento.status_processamento = StatusProcessamentoEnum.ERRO
        documento.detalhe = str(e)
    except Exception:
        logger.exception("falha ao indexar documento %s", documento.id)
        documento.status_processamento = StatusProcessamentoEnum.ERRO
        documento.detalhe = "Erro ao ler o arquivo. Tente enviar de novo."


def _exemplo(db: Session, correcao: Correcao, submissao: Submissao, atividade: Atividade) -> str:
    linhas = [f"Atividade: {atividade.titulo}",
              f'Resposta do aluno: """{(submissao.texto_confirmado or "").strip()[:1500]}"""']
    criterios = (
        db.query(CorrecaoCriterio, Tema).join(Tema, Tema.id == CorrecaoCriterio.tema_id)
        .filter(CorrecaoCriterio.correcao_id == correcao.id).order_by(Tema.habilidade_codigo).all()
    )
    valor = float(atividade.valor_total or 1000) / max(len(criterios), 1)
    mudou = False
    for c, tema in criterios:
        nota_prof, nota_ia = float(c.nota_professor), float(c.nota)
        linha = f"{tema.habilidade_codigo}) {tema.nome[:300]}"
        if tema.resposta_correta:
            linha += f" | Gabarito: {tema.resposta_correta[:200]}"
        linha += f" | Nota do professor: {nota_prof:g} de {valor:g}"
        if abs(nota_prof - nota_ia) > 0.01:
            mudou = True
            linha += (f" (a IA tinha dado {nota_ia:g} e o professor CORRIGIU a nota: a IA ERROU aqui, foi "
                      f"{'rigorosa' if nota_ia < nota_prof else 'generosa'} demais. O que a IA tinha "
                      f"escrito: {c.justificativa[:300]})")
        else:
            linha += f" (professor concordou com a IA: {c.justificativa[:300]})"
        linhas.append(linha)
    if mudou and correcao.motivo_mudanca:
        linhas.append(f"POR QUE o professor mudou a nota (explicação dele para a IA): {correcao.motivo_mudanca[:1000]}")
    if correcao.feedback:
        linhas.append(f"Feedback final aprovado pelo professor: {correcao.feedback[:600]}")
    return "\n".join(linhas)


def indexar_correcao(db: Session, correcao: Correcao) -> None:
    """Guarda uma correcao aprovada como exemplo do jeito do professor. Nunca levanta erro."""
    try:
        if correcao.revisado_por is None:  # objetiva corrigida por gabarito: nao ha "jeito" a aprender
            return
        submissao = db.get(Submissao, correcao.submissao_id)
        atividade = db.get(Atividade, submissao.atividade_id)
        db.query(IaTrecho).filter_by(correcao_id=correcao.id).delete()
        _guardar(db, [IaTrecho(
            materia_id=atividade.materia_id, professor_id=correcao.revisado_por, origem=CORRECAO,
            correcao_id=correcao.id, titulo=atividade.titulo[:255],
            texto=_exemplo(db, correcao, submissao, atividade),
        )])
    except Exception:
        logger.exception("falha ao guardar a correcao %s na memoria", correcao.id)


# ---------- usar ----------

def contexto_do_professor(db: Session, materia_id, consulta: str, professor_id=None,
                          materiais: int = 4, exemplos: int = 3) -> str:
    """Bloco de texto para colar no prompt: material do professor + correcoes parecidas que ele
    ja aprovou. Devolve "" quando a memoria nao tem nada util (o prompt fica igual ao de antes)."""
    try:
        do_material = buscar(db, materia_id, consulta, MATERIAL, materiais, professor_id)
        das_correcoes = buscar(db, materia_id, consulta, CORRECAO, exemplos, professor_id) if exemplos else []
        instrucoes = instrucoes_de(db, materia_id, professor_id)
    except Exception:
        logger.exception("falha ao buscar na memoria da materia %s", materia_id)
        return ""
    if not do_material and not das_correcoes and not instrucoes:
        return ""
    partes = ["=== MEMÓRIA DO DOMINA: COMO ESTE PROFESSOR TRABALHA ===",
              "Use o que estiver abaixo para trabalhar do jeito DESTE professor. Ignore o que não "
              "tiver relação com o pedido atual. O que o professor pede aqui é um COMPLEMENTO: sem "
              "orientação dele sobre um ponto, siga as regras normais deste pedido."]
    if instrucoes:
        usado, linhas = 0, []
        for t in instrucoes:
            if usado + len(t.texto) > MAX_LETRAS_INSTRUCOES:
                break
            usado += len(t.texto)
            linhas.append(f"- {t.texto}")
        partes.append("\nINSTRUÇÕES que o professor pediu para você SEMPRE seguir (valem mais que o resto da "
                      "memória; só não valem contra o gabarito e as regras do pedido atual):")
        partes += linhas
    if do_material:
        partes.append("\nTrechos do material que o professor enviou:")
        partes += [f"[{t.titulo}]\n{t.texto}" for t in do_material]
    if das_correcoes:
        partes.append("\nCorreções parecidas que o professor já aprovou (imite o rigor, o critério "
                      "de nota e o tom dele. Onde ele mudou a nota, a IA tinha ERRADO: entenda o motivo e "
                      "não repita o mesmo erro em casos parecidos):")
        partes += [f"--- Exemplo {i} ---\n{t.texto}" for i, t in enumerate(das_correcoes, start=1)]
    partes.append("=== FIM DA MEMÓRIA ===")
    return "\n".join(partes) + "\n\n"


def resumo(db: Session, materia_id, professor_id) -> dict:
    """Quanto a IA ja aprendeu com ESTE professor nesta materia (para a tela dele)."""
    def conta(origem):
        return _do_professor(db, materia_id, origem, professor_id).count()
    return {"trechos_de_material": conta(MATERIAL), "correcoes_aprendidas": conta(CORRECAO),
            "instrucoes": conta(INSTRUCAO)}
