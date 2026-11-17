"""Tira o texto de um material do professor. Levanta ArquivoNaoLido com um motivo curto, que
aparece na tela do professor."""
import io
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree


class ArquivoNaoLido(Exception):
    pass


def _pdf(conteudo: bytes) -> str:
    from pypdf import PdfReader

    leitor = PdfReader(io.BytesIO(conteudo))
    return "\n\n".join((pagina.extract_text() or "") for pagina in leitor.pages)


def _docx(conteudo: bytes) -> str:
    # um .docx e um zip; o texto fica em word/document.xml, um <w:p> por paragrafo
    w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with zipfile.ZipFile(io.BytesIO(conteudo)) as z:
        raiz = ElementTree.fromstring(z.read("word/document.xml"))
    return "\n".join("".join(t.text or "" for t in p.iter(f"{w}t")) for p in raiz.iter(f"{w}p"))


IMAGENS = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp",
           ".heic": "image/heic", ".heif": "image/heif"}
MAX_PAGINAS_OCR = 30  # PDF escaneado: cada pagina vira uma imagem para o Gemini ler

PROMPT_MATERIAL = """Transcreva TODO o conteúdo deste material de um professor (apostila, rubrica, gabarito,
lista de exercícios, prova corrigida). Copie o texto fielmente, na ordem de leitura, mantendo
títulos, numeração de questões e tabelas (uma linha por linha da tabela). Fórmulas: escreva em
texto simples. Onde houver figura, gráfico, partitura ou esquema, descreva em uma linha
[figura: ...]. Não resuma, não comente e não corrija nada. Responda só com a transcrição."""


def paginas_do_pdf(conteudo: bytes, maximo: int) -> list[bytes]:
    """Cada pagina do PDF como uma imagem JPEG (para ler PDF escaneado ou prova enviada em PDF)."""
    import pypdfium2

    pdf = pypdfium2.PdfDocument(conteudo)
    try:
        if len(pdf) > maximo:
            raise ArquivoNaoLido(f"O PDF tem {len(pdf)} páginas; o limite é {maximo}.")
        imagens = []
        for pagina in pdf:
            saida = io.BytesIO()
            pagina.render(scale=2).to_pil().convert("RGB").save(saida, "JPEG", quality=85)
            imagens.append(saida.getvalue())
        return imagens
    finally:
        pdf.close()


def _ler_imagens(imagens: list[tuple[bytes, str]]) -> str:
    """Foto ou pagina escaneada -> texto, pelo Gemini (o mesmo que le a foto do aluno)."""
    from google.genai import types

    from app.config import settings
    from app.ia import registro
    from app.ocr.gemini import LADO_EXATAS, gerar, reduzir

    if not settings.GEMINI_API_KEY:
        raise ArquivoNaoLido("Para ler foto ou PDF escaneado o servidor precisa da chave do Gemini.")
    partes = []
    for i in range(0, len(imagens), 6):  # 6 paginas por chamada, como no envio do aluno
        lote = [reduzir(b, m, LADO_EXATAS) for b, m in imagens[i:i + 6]]
        with registro.tarefa("ler_material"):
          resposta, _ = gerar(
            [*(types.Part.from_bytes(data=b, mime_type=m) for b, m in lote), PROMPT_MATERIAL],
            types.GenerateContentConfig(temperature=0, thinking_config=types.ThinkingConfig(thinking_level="minimal")),
        )
        partes.append((resposta.text or "").strip())
    return "\n\n".join(p for p in partes if p)


def extrair_texto(nome_arquivo: str, conteudo: bytes) -> str:
    sufixo = Path(nome_arquivo).suffix.lower()
    try:
        if sufixo == ".pdf":
            texto = _pdf(conteudo)
            if len(texto.strip()) < 20:  # PDF escaneado: so imagem, sem texto dentro
                texto = _ler_imagens([(p, "image/jpeg") for p in paginas_do_pdf(conteudo, MAX_PAGINAS_OCR)])
        elif sufixo in IMAGENS:
            texto = _ler_imagens([(conteudo, IMAGENS[sufixo])])
        elif sufixo == ".docx":
            texto = _docx(conteudo)
        elif sufixo in (".txt", ".md", ".csv"):
            texto = conteudo.decode("utf-8", errors="replace")
        else:
            raise ArquivoNaoLido("Formato ainda não lido pela IA. Envie PDF, foto (JPG/PNG), DOCX ou TXT.")
    except ArquivoNaoLido:
        raise
    except Exception as e:
        raise ArquivoNaoLido("Não consegui abrir este arquivo.") from e
    texto = re.sub(r"[ \t]+", " ", texto).strip()
    if len(texto) < 20:
        raise ArquivoNaoLido("Não achei texto para ler neste arquivo.")
    return texto


def dividir(texto: str, tamanho: int = 1200, sobra: int = 150) -> list[str]:
    """Corta o texto em trechos de ~tamanho letras, respeitando paragrafos; cada trecho repete
    o fim do anterior (sobra) para nao perder uma ideia cortada no meio."""
    trechos, atual = [], ""
    for paragrafo in re.split(r"\n\s*\n|\n", texto):
        paragrafo = paragrafo.strip()
        if not paragrafo:
            continue
        while len(paragrafo) > tamanho:  # paragrafo gigante: corta no tamanho mesmo
            paragrafo, resto = paragrafo[:tamanho], paragrafo[tamanho - sobra:]
            if atual:
                trechos.append(atual)
            trechos.append(paragrafo)
            atual, paragrafo = "", resto
        if atual and len(atual) + len(paragrafo) + 1 > tamanho:
            trechos.append(atual)
            atual = atual[-sobra:]
        atual = f"{atual}\n{paragrafo}".strip()
    if atual:
        trechos.append(atual)
    return trechos
