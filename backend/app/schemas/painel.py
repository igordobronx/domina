import uuid

from pydantic import BaseModel


class ResumoEscola(BaseModel):
    escola_id: uuid.UUID
    escola_nome: str
    ativa: bool
    mes: str  # AAAA-MM
    # pessoas
    alunos_cadastrados: int
    professores: int
    turmas: int
    alunos_ativos: int  # alunos que enviaram algo no mes (base da cobranca)
    # consumo (o que o app mede; CPU/memoria do servidor ficam fora)
    submissoes: int
    execucoes_agente: int
    tokens_llm: int
    chamadas_ocr: int
    armazenamento_bytes: int
    # financeiro (R$): receita = plano fixo + valor por aluno ativo; custo = IA+OCR estimado
    receita: float
    custo_ia: float
    margem: float


class ResumoPlataforma(BaseModel):
    mes: str
    escolas_ativas: int
    totais: dict[str, float]  # alunos_ativos, receita, custo_ia, margem, tokens_llm, chamadas_ocr, armazenamento_bytes...
    escolas: list[ResumoEscola]
