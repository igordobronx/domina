import enum 

class PerfilEnum(str, enum.Enum):
    ALUNO = "ALUNO"
    PROFESSOR = "PROFESSOR"
    GESTOR = "GESTOR"
    ADMIN = "ADMIN"

class UsuarioTurmaPapelEnum(str, enum.Enum):
    ALUNO = "ALUNO"
    PROFESSOR = "PROFESSOR"

class TipoMateriaEnum(str, enum.Enum):
    REDACAO_ENEM = "REDACAO_ENEM"
    REDACAO_OUTRO_VESTIBULAR = "REDACAO_OUTRO_VESTIBULAR"
    MATERIA_OBJETIVA = "MATERIA_OBJETIVA"
    MATERIA_DISCURSIVA = "MATERIA_DISCURSIVA"

class TipoDocumentoEnum(str, enum.Enum):
    APOSTILA = "APOSTILA"
    RUBRICA = "RUBRICA"
    PLANO_DE_AULA = "PLANO_DE_AULA"
    GABARITO = "GABARITO"

class StatusProcessamentoEnum(str, enum.Enum):
    PENDENTE = "PENDENTE"
    PROCESSADO = "PROCESSADO"
    ERRO = "ERRO"

class TipoAtividadeEnum(str, enum.Enum):
    REDACAO = "REDACAO"
    PROVA_DISCURSIVA = "PROVA_DISCURSIVA"
    PROVA_OBJETIVA = "PROVA_OBJETIVA"
    EXERCICIO = "EXERCICIO"

class TipoEnvioEnum(str, enum.Enum):
    TEXTO = "TEXTO"
    IMAGEM = "IMAGEM"
    PDF = "PDF"

class StatusCorrecaoEnum(str, enum.Enum):
    PENDENTE = "PENDENTE"
    REQUER_ATENCAO = "REQUER_ATENCAO"
    APROVADA = "APROVADA"
