# Assuntos dentro da matéria (18/11/2026)

- **Assunto** = nível entre a matéria e o material: Escola → Matéria → Assunto → materiais, instruções, correções. Sem assunto = "Geral".
- **Dono:** o professor cria os dele (privados); o gestor cria os "da escola" (valem para todos os professores da matéria). Professor só usa assunto de matéria que leciona. Lista plana, sem sub-assuntos. Nunca apaga: "tirar de uso".
- **Tabelas:** `assunto` + coluna opcional `assunto_id` em `documento_base`, `ia_trecho`, `atividade`, `exercicio` (migration 0031, sem backfill: o que existe fica no Geral).
- **IA:** com assunto, busca o do assunto + o Geral (o do assunto ganha um bônus no parecido); instrução de um assunto só vale nos pedidos dele; sem assunto, busca na matéria toda como antes. Correção aprovada e exercício corrigido entram na memória com o assunto da atividade/exercício.
- **Escolha opcional** ao criar atividade e exercício (`SeletorAssunto`); no Treinar IA o professor escolhe o assunto antes de enviar material ou instrução.
- **Fica para depois:** a IA sugerir o assunto sozinha; plano de estudo/`ErroAluno` por assunto; o aluno ver o nome do assunto.
