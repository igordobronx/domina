import uuid
from datetime import datetime

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
    false,
    true,
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
    # desativar = a conta nao entra mais, mas notas e historico ficam (nunca excluimos pessoa)
    ativo = Column(Boolean, nullable=False, default=True, server_default=true())
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

class ProfessorMateria(Base):
    """Qual materia o professor da em qual turma (quem define e o gestor). E o que limita o que o
    professor ve e cria: ele so enxerga estatisticas de aluno nas materias que leciona nas turmas do aluno."""
    __tablename__ = "professor_materia"

    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), primary_key=True)
    turma_id = Column(UUID(as_uuid=True), ForeignKey("turma.id"), primary_key=True)
    materia_id = Column(UUID(as_uuid=True), ForeignKey("materia.id"), primary_key=True)


class Materia(Base):
    __tablename__ = "materia"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    escola_id = Column(UUID(as_uuid=True), ForeignKey("escola.id"), nullable=False)
    nome = Column(String(150), nullable=False)
    tipo = Column(SQLEnum(TipoMateriaEnum), nullable=False)
    # area do conhecimento (EXATAS, NATUREZA, HUMANAS, LINGUAGENS, REDACAO, OUTRA); o formato da atividade
    # (redacao x gabarito) vem do tipo da ATIVIDADE, nao da materia
    area = Column(String(20), nullable=False, default="OUTRA", server_default="OUTRA")
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
    # questao objetiva (estilo ENEM): textos das alternativas A, B, C... ; nulo = discursiva.
    # Nas objetivas resposta_correta guarda so a letra do gabarito.
    alternativas = Column(JSON, nullable=True)
    # figura do enunciado (ex.: estruturas quimicas), anexada pelo professor; caminho em UPLOAD_DIR
    imagem = Column(String(255), nullable=True)
    # assunto da questao (so exatas/gabarito): o professor escreve ou a IA identifica; alimenta a evolucao por subtopico
    subtopico = Column(String(150), nullable=True)
    valor = Column(Numeric(6, 2), nullable=True)  # pontos desta questao (vazio = total dividido igual)

class DocumentoBase(Base):
    __tablename__ = "documento_base"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    materia_id = Column(UUID(as_uuid=True), ForeignKey("materia.id"), nullable=False)
    enviado_por = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    tipo = Column(SQLEnum(TipoDocumentoEnum), nullable=False)
    tamanho_bytes = Column(BigInteger, nullable=True)  # para medir o armazenamento da escola
    caminho = Column(String(255), nullable=True)  # nome do arquivo em UPLOAD_DIR (nulo nos antigos, que nao dao para baixar)
    ativo = Column(Boolean, nullable=False, default=True, server_default=true())  # excluir = arquivar
    status_processamento = Column(
        SQLEnum(StatusProcessamentoEnum), default=StatusProcessamentoEnum.PENDENTE, nullable=False
    )
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)
    detalhe = Column(String(255), nullable=True)  # motivo quando a IA nao conseguiu ler (status ERRO)


class IaTrecho(Base):
    """Memoria da IA por materia (RAG): pedaco de material do professor ou correcao que ele
    aprovou. Ver app/ia/memoria.py."""
    __tablename__ = "ia_trecho"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    materia_id = Column(UUID(as_uuid=True), ForeignKey("materia.id"), nullable=False, index=True)
    professor_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=True)
    origem = Column(String(20), nullable=False)  # MATERIAL | CORRECAO | INSTRUCAO | EXERCICIO
    documento_id = Column(UUID(as_uuid=True), ForeignKey("documento_base.id"), nullable=True)
    correcao_id = Column(UUID(as_uuid=True), ForeignKey("correcao.id"), nullable=True)
    # origem EXERCICIO: a resposta de aluno que o professor marcou certo/parcial/errado
    exercicio_resposta_id = Column(UUID(as_uuid=True), ForeignKey("exercicio_resposta.id"), nullable=True)
    titulo = Column(String(255), nullable=False)
    texto = Column(Text, nullable=False)
    # "tirado de uso": a memoria nao usa mais, mas o dado fica guardado (base de treino da IA propria)
    ignorado = Column(Boolean, nullable=False, default=False, server_default=false())
    embedding = Column(JSON, nullable=True)  # vetor do texto; nulo = busca por palavras
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)


class IaChamada(Base):
    """Material de treino da IA propria: um pedido ao modelo de fora e a resposta dele.
    Ver app/ia/registro.py e exportar_treino.py."""
    __tablename__ = "ia_chamada"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tarefa = Column(String(40), nullable=False, index=True)  # corrigir_redacao, corrigir_gabarito, criar_exercicios...
    modelo = Column(String(100), nullable=False)  # quem respondeu (o "professor" do nosso modelo)
    entrada = Column(Text, nullable=False)  # o pedido inteiro, ja com a memoria do professor
    saida = Column(Text, nullable=False)
    imagens = Column(Integer, nullable=False, default=0)  # quantas fotos foram junto (ficam em UPLOAD_DIR)
    materia_id = Column(UUID(as_uuid=True), ForeignKey("materia.id"), nullable=True)
    professor_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=True)
    # correcao gerada por esta chamada: e por ela que se chega a nota FINAL do professor
    correcao_id = Column(UUID(as_uuid=True), ForeignKey("correcao.id"), nullable=True, index=True)
    # quando entrou num arquivo de treino. So registro exportado pode ser apagado, e so depois
    # que o treino deu certo (exportar_treino.py): NADA e apagado sem a IA ter aprendido.
    exportado_em = Column(DateTime, nullable=True)
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
    # "excluir" uma atividade que ja tem submissoes so a esconde (notas e dominio dos alunos ficam)
    arquivada = Column(Boolean, nullable=False, default=False, server_default=false())
    # quem propos a atividade; nulo = anterior a este campo (visivel a todos os professores da turma)
    criado_por = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=True)
    criado_em = Column(DateTime, default=datetime.now, nullable=True)  # lista: mais recentes primeiro


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


class Meta(Base):
    """Meta de estudo criada por professor/gestor. Escopo: aluno_id preenchido = individual; senao
    turma_id preenchido = turma; senao a escola toda. O progresso NAO e gravado (e calculado dos
    dados reais); so a conclusao (MetaConcluida). Nivel do aluno = soma dos pontos das concluidas."""
    __tablename__ = "meta"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    escola_id = Column(UUID(as_uuid=True), ForeignKey("escola.id"), nullable=False)
    criado_por = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False)
    titulo = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=True)
    # ENTREGAS | ENTREGAS_NO_PRAZO | NOTA_ATIVIDADE | MEDIA_MATERIA | DOMINIO_COMPETENCIA
    tipo = Column(String(30), nullable=False)
    alvo = Column(Numeric(7, 2), nullable=False)  # quantidade (entregas) ou percentual (0-100)
    materia_id = Column(UUID(as_uuid=True), ForeignKey("materia.id"), nullable=True)
    competencia = Column(String(2), nullable=True)  # C1..C5, so DOMINIO_COMPETENCIA
    pontos = Column(Integer, nullable=False)
    inicio = Column(Date, nullable=False)  # so conta o que acontece a partir daqui
    fim = Column(Date, nullable=True)
    turma_id = Column(UUID(as_uuid=True), ForeignKey("turma.id"), nullable=True)
    aluno_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=True)
    ativa = Column(Boolean, nullable=False, server_default=true())  # excluir = desativar (pontos ganhos ficam)


class MetaConcluida(Base):
    __tablename__ = "meta_concluida"

    meta_id = Column(UUID(as_uuid=True), ForeignKey("meta.id"), primary_key=True)
    aluno_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), primary_key=True)
    concluida_em = Column(DateTime, server_default=func.now(), nullable=False)


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


class SubmissaoPagina(Base):
    """Folhas de um envio por foto, em ordem (ordem 0 = primeira). Envio antigo, de uma foto so,
    nao tem linhas aqui: vale Submissao.conteudo_bruto (ver caminhos_da_submissao)."""
    __tablename__ = "submissao_pagina"

    submissao_id = Column(UUID(as_uuid=True), ForeignKey("submissao.id"), primary_key=True)
    ordem = Column(Integer, primary_key=True)
    caminho = Column(String(500), nullable=False)


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
    # por que o professor mudou a nota da IA; so a memoria da IA usa (app/ia/memoria.py)
    motivo_mudanca = Column(Text, nullable=True)
    # o que da memoria do professor entrou no pedido a IA (so o professor ve; app/ia/memoria.py > montar_contexto)
    fontes_ia = Column(JSON, nullable=True)
    # o professor dispensou a sugestao de instrucao feita a partir do motivo desta correcao
    motivo_dispensado = Column(Boolean, nullable=False, default=False, server_default=false())
    # o professor marcou que a explicacao/feedback da IA estava ruim, mesmo com a nota certa
    explicacao_ruim = Column(Boolean, nullable=False, default=False, server_default=false())
    # o professor marcou esta correcao como exemplo modelo: entra primeiro na busca de exemplos
    boa_correcao = Column(Boolean, nullable=False, default=False, server_default=false())
    # avaliacao intermediaria: correcao razoavel (nem modelo, nem ruim)
    correcao_razoavel = Column(Boolean, nullable=False, default=False, server_default=false())


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


class ErroAluno(Base):
    """Onde o aluno errou numa questao de exatas (nota final < 80% da questao), guardado a partir
    da correcao aprovada. E a base do plano de estudo de exatas: cada exercicio aponta para o seu erro."""
    __tablename__ = "erro_aluno"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    aluno_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False)
    materia_id = Column(UUID(as_uuid=True), ForeignKey("materia.id"), nullable=False)
    atividade_id = Column(UUID(as_uuid=True), ForeignKey("atividade.id"), nullable=False)
    correcao_id = Column(UUID(as_uuid=True), ForeignKey("correcao.id"), nullable=False)
    # uma linha por questao corrigida: garante que registrar de novo nao duplica
    criterio_id = Column(UUID(as_uuid=True), ForeignKey("correcao_criterio.id"), unique=True, nullable=False)
    enunciado = Column(Text, nullable=False)  # a questao, como estava na prova
    gabarito = Column(Text, nullable=True)
    nota = Column(Numeric(6, 2), nullable=False)
    valor = Column(Numeric(6, 2), nullable=False)  # quanto a questao valia
    percentual = Column(Numeric(5, 2), nullable=False)  # nota / valor * 100
    detalhe = Column(Text, nullable=False)  # onde errou: justificativa + os pontos de erro da correcao
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)


class Exercicio(Base):
    """Exercicio de PRATICA criado pelo professor (escrito por ele ou com ajuda da IA, que ele revisa
    antes de salvar). Nao vale nota: as provas continuam em Atividade. Os gerados pela IA a partir
    dos pontos fracos do aluno NAO ficam aqui (app/estudos.py, gerados na hora)."""
    __tablename__ = "exercicio"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # competencia ligada (opcional, sobra do esquema antigo); o tema livre fica em `assunto`
    tema_id = Column(UUID(as_uuid=True), ForeignKey("tema.id"), nullable=True)
    enunciado = Column(Text, nullable=False)
    # True = o professor usou a IA para criar (aparece um selo para o aluno); continua sendo "do professor"
    gerado_por_ia = Column(Boolean, default=True, nullable=False)
    aprovado_por = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=True)
    # exercicio de pratica que a IA gerou PARA um aluno so (plano de estudo, app/estudos.py); nulo = do professor
    aluno_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=True)
    # exercicio de exatas gerado a partir de um erro registrado do aluno (ver ErroAluno)
    erro_id = Column(UUID(as_uuid=True), ForeignKey("erro_aluno.id"), nullable=True)
    titulo = Column(String(200), nullable=True)
    assunto = Column(String(200), nullable=True)  # tema digitado pelo professor (ex.: "Coesão", "Função afim")
    materia_id = Column(UUID(as_uuid=True), ForeignKey("materia.id"), nullable=True)
    turma_id = Column(UUID(as_uuid=True), ForeignKey("turma.id"), nullable=True)
    # so alguns alunos da turma: lista de ids (texto). Nulo = a turma toda
    alunos = Column(JSON, nullable=True)
    criado_por = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=True)
    tipo = Column(String(12), nullable=False, default="OBJETIVO", server_default="OBJETIVO")  # OBJETIVO | DISCURSIVO
    alternativas = Column(JSON, nullable=True)  # so no objetivo
    resposta_correta = Column(Integer, nullable=True)  # indice da alternativa certa (objetivo)
    resposta_exemplo = Column(Text, nullable=True)  # discursivo: o aluno compara depois de responder (= a 1a)
    # discursivo com mais de uma resposta de exemplo (todas, inclusive a 1a); nulo = so a resposta_exemplo
    respostas_exemplo = Column(JSON, nullable=True)
    explicacao = Column(Text, nullable=True)
    # varias questoes no mesmo exercicio: cada questao e uma linha, e as do mesmo exercicio (por turma)
    # dividem o grupo_id; `ordem` e a posicao dela. Sem grupo = exercicio de uma questao so
    grupo_id = Column(UUID(as_uuid=True), nullable=True)
    ordem = Column(Integer, nullable=False, default=0, server_default="0")
    # excluir = desativar (as respostas dos alunos ficam)
    ativo = Column(Boolean, nullable=False, default=True, server_default=true())
    criado_em = Column(DateTime, server_default=func.now(), nullable=True)


class ExercicioResposta(Base):
    __tablename__ = "exercicio_resposta"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exercicio_id = Column(UUID(as_uuid=True), ForeignKey("exercicio.id"), nullable=False)
    aluno_id = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False)
    resposta = Column(Text, nullable=False)
    # objetivo: calculada na hora. Discursivo: nulo ate o professor marcar certo/errado
    correta = Column(Boolean, nullable=True)
    # CERTA | PARCIAL | ERRADA (nulo = discursivo ainda sem correcao). correta acompanha: PARCIAL -> nulo
    resultado = Column(String(8), nullable=True)
    comentario = Column(Text, nullable=True)  # comentario do professor para o aluno
    criado_em = Column(DateTime, server_default=func.now(), nullable=True)


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
