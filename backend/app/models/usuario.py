import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    true,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from app.models.enum import (
    PerfilEnum,
    StatusCorrecaoEnum,
    StatusProcessamentoEnum,
    TipoAtividadeEnum,
    TipoDocumentoEnum,
    TipoEnvioEnum,
    TipoMateriaEnum,
    UsuarioTurmaPapelEnum,
)

class Escola(Base):
    __tablename__ = "escola"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(250), nullable=False)
    cnpj = Column(String(18), nullable=False)
    ativa = Column(Boolean, server_default=true(), default=True, nullable=False)
    # cobranca (rascunho RN-26): valor fixo por mes + valor por aluno ativo no mes
    plano_fixo = Column(Numeric(10, 2), server_default="1000", default=1000, nullable=False)
    valor_por_aluno = Column(Numeric(10, 2), server_default="8", default=8, nullable=False)
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)

class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # nulo = administrador da plataforma (nao pertence a nenhuma escola)
    escola_id = Column(UUID(as_uuid=True), ForeignKey("escola.id"), nullable=True)
    nome = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(SQLEnum(PerfilEnum), nullable=False)
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)

class Turma(Base):
    __tablename__ = "turma"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    escola_id = Column(UUID(as_uuid=True), ForeignKey("escola.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    ano = Column(Integer, nullable=False)

class UsuarioTurma(Base):
    __tablename__ = "usuario_turma"

    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), primary_key=True)
    turma_id = Column(UUID(as_uuid=True), ForeignKey("turma.id"), primary_key=True)
    papel = Column(SQLEnum(UsuarioTurmaPapelEnum), nullable=False)

class Materia(Base):
    __tablename__ = "materia"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    escola_id = Column(UUID(as_uuid=True), ForeignKey("escola.id"), nullable=False)
    nome = Column(String(150), nullable=False)
    tipo = Column(SQLEnum(TipoMateriaEnum), nullable=False)
    versao = Column(Integer, default=1, nullable=False) #começa no 1 mesmo como default de acordo co a documentação

class Tema(Base):
    __tablename__ = "tema"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    materia_id = Column(UUID(as_uuid=True), ForeignKey("materia.id"), nullable=False)
    # nulo = competencia generica da materia toda (ex.: C1..C5 da redacao, reaproveitada em
    # qualquer atividade). Preenchido = questao especifica de UMA atividade de exatas, com
    # seu proprio gabarito (nao faz sentido reaproveitar entre atividades diferentes).
    atividade_id = Column(UUID(as_uuid=True), ForeignKey("atividade.id"), nullable=True)
    # Text, nao String(150): para uma competencia da redacao (C1..C5) e so um nome curto, mas
    # para uma questao de exatas e o enunciado inteiro digitado pelo professor (sem limite curto)
    nome = Column(Text, nullable=False)
    habilidade_codigo = Column(String(20), nullable=False)
    # gabarito da questao; so preenchido quando atividade_id tambem esta preenchido
    resposta_correta = Column(Text, nullable=True)
    # figura do enunciado (ex.: estruturas quimicas), anexada pelo professor; caminho em UPLOAD_DIR
    imagem = Column(String(255), nullable=True)

class DocumentoBase(Base):
    __tablename__ = "documento_base"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    materia_id = Column(UUID(as_uuid=True), ForeignKey("materia.id"), nullable=False)
    enviado_por = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    tipo = Column(SQLEnum(TipoDocumentoEnum), nullable=False)
    tamanho_bytes = Column(BigInteger, nullable=True)  # para medir o armazenamento da escola
    status_processamento = Column(
        SQLEnum(StatusProcessamentoEnum), default=StatusProcessamentoEnum.PENDENTE, nullable=False
    )
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)


class Atividade(Base):
    __tablename__ = "atividade"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    materia_id = Column(UUID(as_uuid=True), ForeignKey("materia.id"), nullable=False)
    turma_id = Column(UUID(as_uuid=True), ForeignKey("turma.id"), nullable=False)
    titulo = Column(String(200), nullable=False)
    tipo = Column(SQLEnum(TipoAtividadeEnum), nullable=False)
    # so usado em materias de exatas (gabarito): valor total da atividade, dividido igualmente
    # entre as questoes. Nulo = redacao, que usa sempre as 5 competencias de 0..200 (soma 1000).
    valor_total = Column(Numeric(6, 2), nullable=True)
    prazo = Column(Date, nullable=True)  # data de entrega; aparece sozinha no calendario


class Evento(Base):
    """Calendario da escola: uma tabela so, todo mundo le dela (por isso fica "sincronizado")."""
    __tablename__ = "evento"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    escola_id = Column(UUID(as_uuid=True), ForeignKey("escola.id"), nullable=False)
    turma_id = Column(UUID(as_uuid=True), ForeignKey("turma.id"), nullable=True)  # nulo = escola toda
    criado_por = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    tipo = Column(String(20), nullable=False, default="AVISO")  # PROVA | ENTREGA | REUNIAO | AVISO
    inicio = Column(Date, nullable=False)
    fim = Column(Date, nullable=True)  # nulo = so um dia


class Submissao(Base):
    __tablename__ = "submissao"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    atividade_id = Column(UUID(as_uuid=True), ForeignKey("atividade.id"), nullable=False)
    aluno_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False)
    tipo_envio = Column(SQLEnum(TipoEnvioEnum), nullable=False)
    conteudo_bruto = Column(Text, nullable=False)
    texto_ocr = Column(Text, nullable=True)  # o que o OCR leu, intocado (serve para medir o OCR)
    # texto que o aluno conferiu e confirmou; e ESTE que vai para a correcao por IA.
    # nulo = envio aguardando confirmacao (RF-11). Envio TEXTO ja nasce preenchido.
    texto_confirmado = Column(Text, nullable=True)
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)


class Correcao(Base):
    __tablename__ = "correcao"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submissao_id = Column(UUID(as_uuid=True), ForeignKey("submissao.id"), unique=True, nullable=False)
    revisado_por = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=True)
    # 6,2: a nota da redacao ENEM vai ate 1000 (5,2 so guardava ate 999.99)
    nota_ia = Column(Numeric(6, 2), nullable=False)
    nota_professor = Column(Numeric(6, 2), nullable=True)
    confianca = Column(Numeric(3, 2), nullable=False)
    status = Column(
        SQLEnum(StatusCorrecaoEnum), default=StatusCorrecaoEnum.PENDENTE, nullable=False
    )
    modelo_usado = Column(String(100), nullable=False)
    versao_prompt = Column(String(50), nullable=False)
    feedback = Column(Text, nullable=True)  # feedback geral; o professor edita antes de liberar (RF-21)


class CorrecaoCriterio(Base):
    __tablename__ = "correcao_criterio"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    correcao_id = Column(UUID(as_uuid=True), ForeignKey("correcao.id"), nullable=False)
    tema_id = Column(UUID(as_uuid=True), ForeignKey("tema.id"), nullable=False)
    # 6,2 (nao 5,2): atividade de exatas com poucas questoes pode valer ate 1000 por questao
    # (valor_total dividido pelo numero de questoes) -- mesmo motivo do Correcao.nota_ia acima
    nota = Column(Numeric(6, 2), nullable=False)  # nota da IA
    nota_professor = Column(Numeric(6, 2), nullable=True)  # nota final, editada na aprovacao (RF-21)
    justificativa = Column(Text, nullable=False)
    # lista de pontos [{trecho, tipo: "acerto"|"erro", comentario, caixa?}], pra destacar na
    # tela exatamente onde a IA viu cada acerto/erro (caixa so em exatas por foto)
    pontos = Column(JSON, nullable=True)


class DominioAluno(Base):
    __tablename__ = "dominio_aluno"
    __table_args__ = (
        UniqueConstraint("aluno_id", "tema_id", name="uq_dominio_aluno_tema"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    aluno_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False)
    tema_id = Column(UUID(as_uuid=True), ForeignKey("tema.id"), nullable=False)
    percentual_dominio = Column(Numeric(5, 2), nullable=False)
    num_evidencias = Column(Integer, default=0, nullable=False)
    atualizado_em = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class Exercicio(Base):
    __tablename__ = "exercicio"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tema_id = Column(UUID(as_uuid=True), ForeignKey("tema.id"), nullable=False)
    enunciado = Column(Text, nullable=False)
    gerado_por_ia = Column(Boolean, default=True, nullable=False)
    aprovado_por = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=True)


class ExercicioResposta(Base):
    __tablename__ = "exercicio_resposta"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exercicio_id = Column(UUID(as_uuid=True), ForeignKey("exercicio.id"), nullable=False)
    aluno_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False)
    resposta = Column(Text, nullable=False)
    correta = Column(Boolean, nullable=True)


class ConsentimentoLGPD(Base):
    __tablename__ = "consentimento_lgpd"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    aluno_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), unique=True, nullable=False)
    responsavel_nome = Column(String(200), nullable=False)
    responsavel_email = Column(String(255), nullable=False)
    aceito_em = Column(DateTime, server_default=func.now(), nullable=False)


class CustoUso(Base):
    __tablename__ = "custo_uso"
    __table_args__ = (
        UniqueConstraint("escola_id", "mes_referencia", name="uq_custo_escola_mes"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    escola_id = Column(UUID(as_uuid=True), ForeignKey("escola.id"), nullable=False)
    mes_referencia = Column(String(7), nullable=False)  # AAAA-MM
    tokens_llm = Column(BigInteger, default=0, nullable=False)
    chamadas_ocr = Column(Integer, default=0, nullable=False)
    custo_estimado = Column(Numeric(10, 2), nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False)
    acao = Column(String(50), nullable=False)
    entidade = Column(String(50), nullable=False)
    entidade_id = Column(UUID(as_uuid=True), nullable=False)
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)
    # ampliacao do log (migration 0007). Nulos nas linhas antigas.
    escola_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # escola de quem agiu; nulo = admin
    ip = Column(String(45), nullable=True)
    request_id = Column(String(32), nullable=True)
    resultado = Column(String(10), nullable=True)  # OK | NEGADO
    # cadeia de hash (app/cadeia.py): so as linhas novas entram nela
    seq = Column(BigInteger, nullable=True, unique=True)
    hash_anterior = Column(String(64), nullable=True)
    hash = Column(String(64), nullable=True)

class EventoSeguranca(Base):
    """Log de autenticacao/acesso. Append-only: a aplicacao so faz INSERT (nunca UPDATE/DELETE)."""
    __tablename__ = "evento_seguranca"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    criado_em = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    tipo = Column(String(20), nullable=False, index=True)  # LOGIN_OK | LOGIN_FALHA | NAO_AUTENTICADO | ACESSO_NEGADO
    usuario_id = Column(UUID(as_uuid=True), nullable=True)  # sem FK de proposito: o log sobrevive a conta apagada
    email_tentado = Column(String(254), nullable=True)
    ip = Column(String(45), nullable=False)
    request_id = Column(String(32), nullable=False)
    detalhe = Column(String(200), nullable=True)  # ex.: "GET /painel/plataforma"
    # cadeia de hash (ver app/seguranca.py): hash = sha256(hash_anterior + campos desta linha).
    # Nulos so nas linhas anteriores a cadeia (migration 0006); a verificacao as ignora.
    seq = Column(BigInteger, nullable=True, unique=True)
    hash_anterior = Column(String(64), nullable=True)
    hash = Column(String(64), nullable=True)


class AgenteExecucao(Base):
    # passo a passo do agente de correcao (app/agente.py): o que ele decidiu e por que.
    # uma por submissao; rodar o agente de novo sobrescreve.
    __tablename__ = "agente_execucao"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submissao_id = Column(UUID(as_uuid=True), ForeignKey("submissao.id"), unique=True, nullable=False)
    passos = Column(JSON, nullable=False)
    mensagem_aluno = Column(Text, nullable=True)
    resumo_professor = Column(Text, nullable=True)
    exercicios = Column(JSON, nullable=True)
    modelo_usado = Column(String(100), nullable=False)
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)
