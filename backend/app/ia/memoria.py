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

from app.config import settings
from app.ia.embeddings import embutir
from app.ia.extracao import ArquivoNaoLido, dividir, extrair_texto
from app.models.enum import PerfilEnum, StatusProcessamentoEnum
from app.models.usuario import (
    Atividade, Correcao, CorrecaoCriterio, DocumentoBase, Exercicio, ExercicioResposta, IaTrecho, Submissao, Tema,
    Usuario,
)

logger = logging.getLogger(__name__)

MATERIAL, CORRECAO, INSTRUCAO, EXERCICIO = "MATERIAL", "CORRECAO", "INSTRUCAO", "EXERCICIO"
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
    q = db.query(IaTrecho).filter_by(materia_id=materia_id, origem=origem).filter(IaTrecho.ignorado.is_(False))
    # material arquivado ("excluir" na tela de materiais) tambem deixa de ser usado, sem apagar nada
    q = q.filter(or_(IaTrecho.documento_id.is_(None),
                     IaTrecho.documento_id.notin_(db.query(DocumentoBase.id).filter(DocumentoBase.ativo.is_(False)))))
    if origem in (CORRECAO, EXERCICIO):
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
    if origem != CORRECAO:
        return [t for _, t in pares[:k]]
    # correcoes marcadas "boa" pelo professor sao exemplo modelo: entre as 2k mais parecidas, vem primeiro
    topo = [t for _, t in pares[:2 * k]]
    boas = {cid for (cid,) in db.query(Correcao.id).filter(
        Correcao.id.in_([t.correcao_id for t in topo if t.correcao_id]), Correcao.boa_correcao.is_(True))}
    return sorted(topo, key=lambda t: t.correcao_id not in boas)[:k]


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
        texto = extrair_texto(documento.nome_arquivo, (Path(settings.UPLOAD_DIR) / documento.caminho).read_bytes())
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


SEM_IA = "professor"  # Correcao.modelo_usado quando o professor corrigiu direto, sem correcao da IA


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
        if correcao.modelo_usado == SEM_IA:
            linha += " (o professor corrigiu direto, sem correção da IA)"
        elif abs(nota_prof - nota_ia) > 0.01:
            mudou = True
            linha += (f" (a IA tinha dado {nota_ia:g} e o professor CORRIGIU a nota: a IA ERROU aqui, foi "
                      f"{'rigorosa' if nota_ia < nota_prof else 'generosa'} demais. O que a IA tinha "
                      f"escrito: {c.justificativa[:300]})")
        else:
            linha += f" (professor concordou com a IA: {c.justificativa[:300]})"
        linhas.append(linha)
    if correcao.boa_correcao:
        linhas.append("O professor marcou esta correção como EXEMPLO MODELO: imite o rigor, a explicação e o tom.")
    if correcao.correcao_razoavel:
        linhas.append("O professor marcou esta correção como RAZOÁVEL (nem modelo, nem ruim): serve de guia, mas melhore.")
    if correcao.explicacao_ruim:
        linhas.append("O professor marcou que a EXPLICAÇÃO da IA estava ruim (mesmo onde a nota estava certa): "
                      "explique de forma mais clara e útil para o aluno.")
    if correcao.motivo_mudanca:
        quem = "mudou a nota" if mudou else "avaliou assim a correção"
        linhas.append(f"POR QUE o professor {quem} (explicação dele para a IA): {correcao.motivo_mudanca[:1000]}")
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
        antigo = db.query(IaTrecho).filter_by(correcao_id=correcao.id).first()
        ignorado = bool(antigo and antigo.ignorado)  # refazer a memoria nao "destira" o que o professor tirou
        db.query(IaTrecho).filter_by(correcao_id=correcao.id).delete()
        _guardar(db, [IaTrecho(
            materia_id=atividade.materia_id, professor_id=correcao.revisado_por, origem=CORRECAO,
            correcao_id=correcao.id, titulo=atividade.titulo[:255], ignorado=ignorado,
            texto=_exemplo(db, correcao, submissao, atividade),
        )])
    except Exception:
        logger.exception("falha ao guardar a correcao %s na memoria", correcao.id)


def indexar_exercicio(db: Session, exercicio: Exercicio, resposta: ExercicioResposta) -> None:
    """A IA aprende com o que o professor marcou (certo/parcial/errado) numa resposta discursiva.
    Sem marca, apaga o exemplo antigo. Nunca levanta erro."""
    try:
        antigo = db.query(IaTrecho).filter_by(exercicio_resposta_id=resposta.id).first()
        ignorado = bool(antigo and antigo.ignorado)
        db.query(IaTrecho).filter_by(exercicio_resposta_id=resposta.id).delete()
        if not resposta.resultado or not exercicio.materia_id or not exercicio.criado_por:
            return
        linhas = [f"Exercício: {exercicio.enunciado.strip()[:800]}",
                  f'Resposta do aluno: """{resposta.resposta.strip()[:1200]}"""',
                  f"O professor marcou: {resposta.resultado}"]
        if resposta.comentario:
            linhas.append(f"Comentário do professor: {resposta.comentario[:600]}")
        exemplos = exercicio.respostas_exemplo or ([exercicio.resposta_exemplo] if exercicio.resposta_exemplo else [])
        if exemplos:
            linhas.append("Resposta de exemplo do professor: " + " | ".join(e[:400] for e in exemplos[:3]))
        _guardar(db, [IaTrecho(
            materia_id=exercicio.materia_id, professor_id=exercicio.criado_por, origem=EXERCICIO,
            exercicio_resposta_id=resposta.id, titulo=(exercicio.titulo or exercicio.enunciado)[:255], ignorado=ignorado,
            texto="\n".join(linhas),
        )])
    except Exception:
        logger.exception("falha ao guardar o exercicio %s na memoria", resposta.id)


# ---------- usar ----------

def contexto_do_professor(db: Session, materia_id, consulta: str, professor_id=None,
                          materiais: int = 4, exemplos: int = 3) -> str:
    """So o texto do contexto (ver montar_contexto)."""
    return montar_contexto(db, materia_id, consulta, professor_id, materiais, exemplos)[0]


def _fonte(tipo: str, titulo: str, texto: str) -> dict:
    resumo = " ".join(texto.split())
    return {"tipo": tipo, "titulo": titulo, "trecho": resumo[:220] + ("..." if len(resumo) > 220 else "")}


def montar_contexto(db: Session, materia_id, consulta: str, professor_id=None,
                    materiais: int = 4, exemplos: int = 3) -> tuple[str, list[dict]]:
    """Bloco de texto para colar no prompt: material do professor + correcoes parecidas que ele
    ja aprovou. Devolve ("", []) quando a memoria nao tem nada util (o prompt fica igual ao de antes).
    A lista de fontes diz o que entrou no pedido, para o professor conferir na revisao."""
    try:
        do_material = buscar(db, materia_id, consulta, MATERIAL, materiais, professor_id)
        das_correcoes = buscar(db, materia_id, consulta, CORRECAO, exemplos, professor_id) if exemplos else []
        dos_exercicios = buscar(db, materia_id, consulta, EXERCICIO, 2, professor_id) if exemplos else []
        instrucoes = instrucoes_de(db, materia_id, professor_id)
    except Exception:
        logger.exception("falha ao buscar na memoria da materia %s", materia_id)
        return "", []
    if not do_material and not das_correcoes and not instrucoes and not dos_exercicios:
        return "", []
    fontes: list[dict] = []
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
            fontes.append(_fonte("instrucao", "Instrução sua", t.texto))
        partes.append("\nINSTRUÇÕES que o professor pediu para você SEMPRE seguir (valem mais que o resto da "
                      "memória; só não valem contra o gabarito e as regras do pedido atual):")
        partes += linhas
    if do_material:
        partes.append("\nTrechos do material que o professor enviou:")
        partes += [f"[{t.titulo}]\n{t.texto}" for t in do_material]
        fontes += [_fonte("material", t.titulo, t.texto) for t in do_material]
    if das_correcoes:
        partes.append("\nCorreções parecidas que o professor já aprovou (imite o rigor, o critério "
                      "de nota e o tom dele. Onde ele mudou a nota, a IA tinha ERRADO: entenda o motivo e "
                      "não repita o mesmo erro em casos parecidos):")
        partes += [f"--- Exemplo {i} ---\n{t.texto}" for i, t in enumerate(das_correcoes, start=1)]
        fontes += [_fonte("exemplo", "Correção sua parecida", t.texto) for t in das_correcoes]
    if dos_exercicios:
        partes.append("\nExercícios parecidos em que o professor corrigiu a resposta do aluno (use para entender "
                      "o que ele aceita como certo, parcial ou errado):")
        partes += [f"--- Exercício {i} ---\n{t.texto}" for i, t in enumerate(dos_exercicios, start=1)]
        fontes += [_fonte("exemplo", "Exercício seu parecido", t.texto) for t in dos_exercicios]
    partes.append("=== FIM DA MEMÓRIA ===")
    return "\n".join(partes) + "\n\n", fontes


SIMILAR_MIN, VEZES_MIN, COBERTO_MIN = 0.4, 3, 0.6


def _chave(texto: str) -> set[str]:
    return {p for p in _palavras(texto) if len(p) > 3}


def sugerir_instrucoes(db: Session, materia_id, professor_id, limite: int = 3) -> list[dict]:
    """Quando o professor muda a nota varias vezes pelo mesmo motivo, sugere virar instrucao.

    Agrupa os "por que voce mudou a nota" parecidos (palavras em comum) deste professor nesta
    materia. Grupo com 3 ou mais vira sugestao, a menos que ja exista instrucao dizendo o mesmo ou
    ele tenha dispensado. Nada vira instrucao sem ele aceitar. Sem chamada a modelo: nao gasta token.
    """
    linhas = (
        db.query(Correcao.id, Correcao.motivo_mudanca)
        .join(Submissao, Submissao.id == Correcao.submissao_id)
        .join(Atividade, Atividade.id == Submissao.atividade_id)
        .filter(Atividade.materia_id == materia_id, Correcao.revisado_por == professor_id,
                Correcao.motivo_mudanca.isnot(None), Correcao.motivo_dispensado.is_(False))
        .order_by(Submissao.criado_em.desc())
        .all()
    )
    grupos: list[dict] = []
    for cid, motivo in linhas:
        chave = _chave(motivo or "")
        if not chave:
            continue
        for g in grupos:
            if len(chave & g["chave"]) / len(chave | g["chave"]) >= SIMILAR_MIN:
                g["ids"].append(cid)
                break
        else:
            grupos.append({"texto": motivo.strip(), "chave": chave, "ids": [cid]})
    ja_ditas = [_chave(t.texto) for t in instrucoes_de(db, materia_id, professor_id)]
    return [
        {"texto": g["texto"], "vezes": len(g["ids"]), "correcao_ids": [str(i) for i in g["ids"]]}
        for g in sorted(grupos, key=lambda g: -len(g["ids"]))
        if len(g["ids"]) >= VEZES_MIN
        and not any(len(g["chave"] & k) / len(g["chave"]) >= COBERTO_MIN for k in ja_ditas)
    ][:limite]


def concordancia(db: Session, materia_id, professor_id, recentes: int = 20) -> dict:
    """Quanto o professor concorda com a IA: compara a nota da IA com a nota final dele.

    'igual' = mesma nota; 'proxima' = diferenca de ate 10% (o mesmo criterio do ENEM: 20 em 200).
    So conta correcao que o professor realmente revisou (tem nota_professor). Sem nota dele nao ha
    o que comparar. Serve para o cliente ver se a IA ja corrige como ele, e para saber a hora de
    trocar o Claude/Gemini pela IA do Domina.
    """
    linhas = (
        db.query(Correcao.nota_ia, Correcao.nota_professor)
        .join(Submissao, Submissao.id == Correcao.submissao_id)
        .join(Atividade, Atividade.id == Submissao.atividade_id)
        .filter(Atividade.materia_id == materia_id, Correcao.revisado_por == professor_id,
                Correcao.nota_professor.isnot(None), Correcao.modelo_usado != SEM_IA)
        .order_by(Submissao.criado_em.desc())
        .all()
    )

    def classe(ia, prof):
        ia, prof = float(ia), float(prof)
        if ia == prof:
            return "igual"
        return "proxima" if abs(ia - prof) <= 0.10 * max(ia, prof, 1.0) else "longe"

    classes = [classe(ia, prof) for ia, prof in linhas]
    # "seu jeito": media com sinal de (professor - IA) em % da maior nota. Negativo = mais rigoroso que a IA.
    # diferenca total ponderada (as notas maiores pesam mais): (soma do professor - soma da IA) / soma da IA
    total_ia = sum(float(i) for i, _ in linhas)
    vies = round(100 * (sum(float(p) for _, p in linhas) - total_ia) / total_ia) if total_ia > 0 else None
    # mesmo com a media perto de zero, as notas podem diferir correcao a correcao: diferenca media absoluta
    diferenca_media = (round(100 * sum(abs(float(p) - float(i)) / max(float(i), float(p), 1.0) for i, p in linhas) / len(linhas))
                       if linhas else None)

    def taxa(lista):
        return round(100 * sum(c != "longe" for c in lista) / len(lista)) if lista else None

    # a cada 10 revisadas (da mais antiga para a mais nova): semana nao serve, o professor pode
    # corrigir poucas provas numa semana. Ultimo bloco so entra com 5 ou mais.
    ordem = classes[::-1]
    evolucao = [{"ate": min(i + 10, len(ordem)), "concordancia": taxa(ordem[i:i + 10])}
                for i in range(0, len(ordem), 10) if len(ordem[i:i + 10]) >= 5]
    return {
        "vies": vies,
        "diferenca_media": diferenca_media,
        "evolucao": evolucao,
        "revisadas": len(classes),
        "iguais": classes.count("igual"),
        "proximas": classes.count("proxima"),
        "longe": classes.count("longe"),
        "concordancia": taxa(classes),
        "concordancia_recente": taxa(classes[:recentes]),
    }


MIN_REVISADAS, CONCORDANCIA_BAIXA = 10, 60  # com pelo menos 10 revisadas, abaixo de 60% = a IA ainda erra o jeito dele


def concorda_pouco(c: dict) -> bool:
    return c["revisadas"] >= MIN_REVISADAS and (c["concordancia_recente"] or 0) < CONCORDANCIA_BAIXA


def resumo(db: Session, materia_id, professor_id) -> dict:
    """Quanto a IA ja aprendeu com ESTE professor nesta materia (para a tela dele)."""
    def conta(origem):
        return _do_professor(db, materia_id, origem, professor_id).count()
    c = concordancia(db, materia_id, professor_id)
    r = {"trechos_de_material": conta(MATERIAL), "correcoes_aprendidas": conta(CORRECAO),
         "instrucoes": conta(INSTRUCAO), "exercicios_aprendidos": conta(EXERCICIO), **c}
    r["nivel"], r["falta"] = _prontidao(r)
    return r


# limites escolhidos por nos (ainda sem dado real): ajustar quando houver correcoes de verdade
PRONTA_REVISADAS, PRONTA_CONCORDANCIA = 20, 85


def _prontidao(r: dict) -> tuple[str, list[str]]:
    """Selo e lista do que falta para a IA ficar pronta nesta materia (so regra simples, sem modelo)."""
    aprendeu = r["trechos_de_material"] + r["correcoes_aprendidas"] + r["instrucoes"] + r["exercicios_aprendidos"]
    if not aprendeu:
        return "SEM_TREINO", ["envie um material ou escreva uma instrução para começar."]
    falta = []
    if not r["trechos_de_material"] and not r["instrucoes"]:
        falta.append("envie um material ou escreva uma instrução.")
    if r["revisadas"] < PRONTA_REVISADAS:
        falta.append(f"revise mais {PRONTA_REVISADAS - r['revisadas']} correção(ões) da IA.")
    elif (r["concordancia_recente"] or 0) < PRONTA_CONCORDANCIA:
        falta.append(f"a concordância recente ({r['concordancia_recente']}%) precisa chegar a {PRONTA_CONCORDANCIA}%.")
    if not falta:
        return "PRONTA", []
    quase = r["revisadas"] >= MIN_REVISADAS and (r["concordancia_recente"] or 0) >= CONCORDANCIA_BAIXA
    return ("QUASE" if quase else "APRENDENDO"), falta


def erros_da_ia(db: Session, materia_id, professor_id, limite: int = 5) -> list[dict]:
    """Correcoes em que a IA mais errou segundo o professor (maior diferenca de nota, ou ele marcou
    a explicacao como ruim). So correcoes que ele ja revisou."""
    linhas = (
        db.query(Correcao, Atividade.titulo)
        .join(Submissao, Submissao.id == Correcao.submissao_id)
        .join(Atividade, Atividade.id == Submissao.atividade_id)
        .filter(Atividade.materia_id == materia_id, Correcao.revisado_por == professor_id,
                Correcao.nota_professor.isnot(None), Correcao.modelo_usado != SEM_IA)
        .all()
    )

    def peso(c: Correcao) -> float:
        ia, prof = float(c.nota_ia), float(c.nota_professor)
        return abs(ia - prof) / max(ia, prof, 1.0) + (0.05 if c.explicacao_ruim else 0)

    ruins = sorted((l for l in linhas if peso(l[0]) > 0), key=lambda l: -peso(l[0]))[:limite]
    return [{"submissao_id": c.submissao_id, "atividade": titulo, "nota_ia": float(c.nota_ia),
             "nota_professor": float(c.nota_professor), "motivo": c.motivo_mudanca,
             "explicacao_ruim": c.explicacao_ruim} for c, titulo in ruins]


def aprendido(db: Session, materia_id, professor_id) -> list[dict]:
    """O que a IA aprendeu deste professor (correcoes, exercicios e materiais), com 'em_uso'.
    Ordem: as correcoes em que a IA mais errou primeiro, depois o resto. Instrucao nao entra
    (ela ja tem o proprio botao de apagar). Material tambem nao: tirar de uso um material e
    "Arquivar" na lista de materiais (DELETE /documentos/{id}), um botao so."""
    itens = []
    for t, c in (db.query(IaTrecho, Correcao).outerjoin(Correcao, Correcao.id == IaTrecho.correcao_id)
                 .filter(IaTrecho.materia_id == materia_id, IaTrecho.professor_id == professor_id,
                         IaTrecho.origem.in_([CORRECAO, EXERCICIO])).all()):
        erro = 0.0
        if c is not None and c.nota_professor is not None and c.modelo_usado != SEM_IA:
            ia, prof = float(c.nota_ia), float(c.nota_professor)
            erro = abs(ia - prof) / max(ia, prof, 1.0) + (0.05 if c.explicacao_ruim else 0)
        itens.append({"tipo": t.origem, "id": t.id, "titulo": t.titulo, "trecho": " ".join(t.texto.split())[:160],
                      "em_uso": not t.ignorado, "erro": round(erro, 3)})
    return sorted(itens, key=lambda i: -i["erro"])


def tirar_de_uso(db: Session, materia_id, professor_id, tipo: str, item_id, em_uso: bool) -> bool:
    """Para de usar (ou volta a usar) um item na memoria. NUNCA apaga: o dado fica para treinar a IA propria."""
    q = db.query(IaTrecho).filter_by(materia_id=materia_id, professor_id=professor_id, id=item_id, origem=tipo)
    return bool(q.update({IaTrecho.ignorado: not em_uso}, synchronize_session=False))
