"""Material de treino da IA propria: exportar e, so depois de treinar, apagar.

O ciclo tem 2 passos separados de proposito -- NADA e apagado sem a IA ter aprendido:

  1) python exportar_treino.py exportar treino.jsonl [tarefa]
     Grava o arquivo e MARCA no banco o que entrou nele (exportado_em). Nao apaga nada.
     Cada exemplo leva um "peso" (o quanto confiar nele no treino):
       1.0  correcao APROVADA pelo professor (a nota dele e a resposta certa) e tarefas sem nota;
       0.5  correcao que so a IA fez, ainda sem o professor: serve, mas vale menos. Esta NAO e
            marcada: quando o professor aprovar, ela sai de novo com a nota dele e peso 1.0
            (o "id" de cada linha deixa o treino trocar a versao antiga pela nova).
  2) Treinar o modelo com o arquivo e conferir que ele ficou bom.
  3) python exportar_treino.py apagar-treinados
     Apaga do banco SO o que foi marcado no passo 1. Rode apenas depois do passo 2 dar certo
     (e guarde o arquivo .jsonl: ele e a copia do que foi apagado).

  Extra) python exportar_treino.py materiais materiais.jsonl
     O que os professores ENSINARAM (trechos dos arquivos enviados em "Treinar IA" e os exemplos
     de correcao aprovada), por materia e professor. Isto e a base permanente: nunca e apagado.

Cada linha do arquivo: tarefa, entrada (o pedido), saida_modelo (o que Claude/Gemini respondeu)
e, nas correcoes, "correcao_final" com as notas do PROFESSOR, o motivo quando ele mudou a nota e
o feedback. O arquivo tem texto de aluno: nao subir no git.
"""
import json
import sys
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models.enum import StatusCorrecaoEnum
from app.models.usuario import Correcao, CorrecaoCriterio, IaChamada, IaTrecho, Tema


PESO_CHEIO, PESO_SEM_PROFESSOR = 1.0, 0.5


def _linha(db, chamada) -> dict:
    linha = {"id": str(chamada.id), "tarefa": chamada.tarefa, "modelo": chamada.modelo, "imagens": chamada.imagens,
             "peso": PESO_CHEIO, "entrada": chamada.entrada, "saida_modelo": chamada.saida, "correcao_final": None}
    correcao = db.get(Correcao, chamada.correcao_id) if chamada.correcao_id else None
    if correcao and correcao.status != StatusCorrecaoEnum.APROVADA:
        linha["peso"] = PESO_SEM_PROFESSOR
    elif correcao:
        criterios = (db.query(CorrecaoCriterio, Tema).join(Tema, Tema.id == CorrecaoCriterio.tema_id)
                     .filter(CorrecaoCriterio.correcao_id == correcao.id).order_by(Tema.habilidade_codigo))
        notas = [{"codigo": t.habilidade_codigo, "nota_ia": float(c.nota), "nota_professor": float(c.nota_professor)}
                 for c, t in criterios]
        linha["correcao_final"] = {
            "notas": notas,
            "professor_mudou": any(abs(n["nota_ia"] - n["nota_professor"]) > 0.01 for n in notas),
            "motivo_mudanca": correcao.motivo_mudanca,
            "feedback": correcao.feedback,
        }
    return linha


def exportar(db, destino: str, tarefa=None) -> int:
    """Grava os exemplos ainda nao exportados. Marca so os definitivos. Nao apaga nada."""
    q = db.query(IaChamada).filter(IaChamada.exportado_em.is_(None))
    if tarefa:
        q = q.filter(IaChamada.tarefa == tarefa)
    chamadas = q.order_by(IaChamada.criado_em).all()
    agora = datetime.now(timezone.utc).replace(tzinfo=None)
    with open(destino, "w", encoding="utf-8") as f:
        for chamada in chamadas:
            linha = _linha(db, chamada)
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")
            if linha["peso"] == PESO_CHEIO:  # sem o professor ainda nao e definitivo: nao marca
                chamada.exportado_em = agora
    db.commit()  # so marca depois que o arquivo inteiro foi gravado
    return len(chamadas)


def exportar_materiais(db, destino: str) -> int:
    total = 0
    with open(destino, "w", encoding="utf-8") as f:
        for t in db.query(IaTrecho).order_by(IaTrecho.materia_id, IaTrecho.criado_em).yield_per(500):
            f.write(json.dumps({"id": str(t.id), "origem": t.origem, "materia_id": str(t.materia_id),
                                "professor_id": str(t.professor_id) if t.professor_id else None,
                                "titulo": t.titulo, "texto": t.texto}, ensure_ascii=False) + "\n")
            total += 1
    return total


def apagar_treinados(db) -> int:
    total = db.query(IaChamada).filter(IaChamada.exportado_em.isnot(None)).delete(synchronize_session=False)
    db.commit()
    return total


if __name__ == "__main__":
    comando = sys.argv[1] if len(sys.argv) > 1 else ""
    with SessionLocal() as db:
        if comando == "exportar" and len(sys.argv) > 2:
            total = exportar(db, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
            print(f"{total} exemplos em {sys.argv[2]} (nada foi apagado)")
        elif comando == "materiais" and len(sys.argv) > 2:
            print(f"{exportar_materiais(db, sys.argv[2])} trechos em {sys.argv[2]} (nada foi apagado)")
        elif comando == "apagar-treinados":
            print(f"{apagar_treinados(db)} registros ja treinados apagados do banco")
        else:
            print(__doc__)
