# Logs do sistema

## O que existe e onde fica
| Log | Onde | Retenção | Quem lê |
|---|---|---|---|
| Access log (toda requisição: método, rota, status, ms, IP, usuário, `request_id`) | stdout em JSON (`domina.acesso`) | 6 meses, na plataforma (Railway/journald) | quem tem acesso ao Railway/servidor |
| Autenticação e acesso negado (`LOGIN_OK/FALHA`, `NAO_AUTENTICADO`, `ACESSO_NEGADO`) | tabela `evento_seguranca` + stdout | 12 meses (`retencao.py`) | admin, na tela Logs |
| Auditoria (quem fez o quê nos dados) | tabela `audit_log` + tela | 12 meses (`retencao.py`) | admin (tudo, com IP); gestor (só a escola, sem IP) |
| Sistema/erros | stdout em JSON | o da plataforma | quem tem acesso ao Railway/servidor |
| DNS | **fora do app**: o DOMINA não roda DNS. Fica no provedor do domínio (ex.: Cloudflare) ou no resolver do servidor | o do provedor | quem administra o domínio |

Nunca é gravado: senha, token JWT, corpo da requisição, query string, texto ou foto de redação.
Horários em UTC. Todo registro leva `request_id` (também devolvido em `X-Request-ID`).

## Integridade
`evento_seguranca` e `audit_log` têm cadeia de hash (`app/cadeia.py`): cada linha guarda o hash da anterior.
Alterar uma linha quebra as seguintes; apagar uma no meio deixa buraco em `seq`.
`python verificar_logs.py` (ou "Verificar integridade" na tela) confere. Sai com código 1 se adulterado.
O hash também sai no stdout: essa cópia fora do banco detecta quem apaga o FIM da tabela.
Limite: quem altera uma linha **e recalcula toda a cadeia depois dela** só é pego pela cópia externa.

## Acesso
- `/logs/seguranca` e `/logs/integridade`: só admin. `/logs/auditoria`: admin e gestor (gestor filtrado por escola no backend).
- Só leitura: não há rota para editar ou apagar. Consultar o log também é auditado (`CONSULTAR`).
- Ações sensíveis (desativar/reativar instituição, criar conta de GESTOR) pedem a senha de novo (`X-Confirmar-Senha`).
- Falta: 2FA do admin (decidido para depois).

## Railway (testes)
- Definir `CONFIAR_PROXY=true`, senão o IP gravado é o do proxy. O IP real vem do último valor de `X-Forwarded-For`.
- O painel Logs do Railway tem retenção curta: a fonte durável é o banco. Disco não é persistente: o app não grava arquivo.
- Agendar `python retencao.py` num Cron do Railway (ex.: diário). `RETENCAO_DIAS` (padrão 365).

## VPS (depois)
- Nginx/Caddy na frente: ligar `CONFIAR_PROXY=true` só então, e deixar o proxy sobrescrever `X-Forwarded-For`.
- Docker `logging driver` journald/syslog + `logrotate` (6 meses) para o access log; o proxy tem o próprio access/error log.
- fail2ban lendo `LOGIN_FALHA`; cópia dos logs para destino externo com escrita apenas (âncora da cadeia).
- cron diário: `python retencao.py` e `python verificar_logs.py` (alerta se sair com código 1).
- Na conta do banco usada pela API, tirar UPDATE/DELETE de `evento_seguranca` e `audit_log`; o `retencao.py` roda com outra conta.
