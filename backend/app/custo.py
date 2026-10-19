from datetime import date

from sqlalchemy.orm import Session

from app.models.usuario import CustoUso

# ponytail: estimativa grosseira (sem preco real nem contagem exata de tokens da API);
# ajustar quando o usage_metadata do Gemini estiver disponivel no retorno de app.correcao
CUSTO_POR_1K_TOKENS = 0.0005
CUSTO_POR_CHAMADA_OCR = 0.001


def registrar_uso(db: Session, escola_id, tokens_llm: int = 0, chamadas_ocr: int = 0) -> None:
    mes = date.today().strftime("%Y-%m")
    custo_adicional = tokens_llm / 1000 * CUSTO_POR_1K_TOKENS + chamadas_ocr * CUSTO_POR_CHAMADA_OCR
    uso = db.query(CustoUso).filter_by(escola_id=escola_id, mes_referencia=mes).first()
    if uso is None:
        db.add(CustoUso(
            escola_id=escola_id, mes_referencia=mes, tokens_llm=tokens_llm,
            chamadas_ocr=chamadas_ocr, custo_estimado=custo_adicional,
        ))
    else:
        uso.tokens_llm += tokens_llm
        uso.chamadas_ocr += chamadas_ocr
        uso.custo_estimado = float(uso.custo_estimado) + custo_adicional
