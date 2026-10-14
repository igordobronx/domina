import type { Activity, DemoState, Topic } from "../types";

export const topics: Topic[] = [
  {
    name: "Interpretação de texto",
    subject: "Redação",
    value: 82,
    evidence: 8,
    growth: 12,
  },
  {
    name: "Argumentação",
    subject: "Redação",
    value: 68,
    evidence: 6,
    growth: 8,
  },
  {
    name: "Coesão textual",
    subject: "Redação",
    value: 55,
    evidence: 7,
    growth: 15,
  },
  {
    name: "Funções do 1º grau",
    subject: "Matemática",
    value: 64,
    evidence: 6,
    growth: 6,
  },
];
export const initialActivities: Activity[] = [
  {
    id: "a1",
    title: "Os desafios da inclusão digital no Brasil",
    subject: "Redação ENEM",
    date: "Até 12 out",
    status: "disponivel",
    kind: "redacao",
    student: "Ana Silva",
  },
  {
    id: "a2",
    title: "Funções no dia a dia",
    subject: "Matemática",
    date: "Até 14 out",
    status: "disponivel",
    kind: "matematica",
    student: "Ana Silva",
  },
  {
    id: "a3",
    title: "Democratização do acesso à cultura",
    subject: "Redação ENEM",
    date: "Enviada em 05 out",
    status: "pendente",
    kind: "redacao",
    student: "Ana Silva",
    text: "A Constituição brasileira assegura o direito à cultura. Entretanto, a concentração de equipamentos culturais nos grandes centros dificulta o acesso de parte da população.\n\nNesse cenário, a desigualdade territorial e a ausência de incentivo à formação de público limitam a participação social. Bibliotecas e espaços comunitários podem aproximar a produção cultural das periferias.\n\nPortanto, o poder público deve ampliar os investimentos em centros culturais, por meio de editais locais e parcerias com escolas, para garantir a participação de todos.",
    aiScores: [160, 160, 120, 140, 160],
  },
  {
    id: "a4",
    title: "O papel da educação na transformação social",
    subject: "Redação ENEM",
    date: "Corrigida em 02 out",
    status: "aprovada",
    kind: "redacao",
    student: "Ana Silva",
    scores: [160, 160, 140, 160, 160],
    aiScores: [160, 160, 140, 140, 160],
    feedback:
      "Você apresentou uma tese clara e uma boa proposta de intervenção. No desenvolvimento, conecte melhor os exemplos à sua ideia central. Experimente variar os conectivos entre os parágrafos.",
    text: "A educação constitui um instrumento fundamental de transformação social. O acesso ao conhecimento permite que os cidadãos participem de maneira crítica da sociedade.\n\nÉ necessário ampliar o investimento na formação de professores e na infraestrutura escolar para reduzir as desigualdades de acesso.",
  },
];
export const initialState: DemoState = {
  activities: initialActivities,
  materials: [
    {
      id: "m1",
      name: "As 5 competências da redação ENEM",
      subject: "Redação ENEM",
      approved: true,
      fileName: "matriz-enem.pdf",
    },
  ],
  completed: [],
  name: "Ana Silva",
  goal: 4,
  drafts: {},
};
export const studyTasks = [
  {
    id: "s1",
    title: "Conecte melhor suas ideias",
    topic: "Coesão textual",
    time: "10 min",
    type: "Exercício guiado",
    description:
      "Seu próximo passo é usar conectivos para dar mais fluidez aos argumentos.",
    question: "Qual conectivo indica uma conclusão?",
    options: ["Entretanto", "Portanto", "Além disso", "Embora"],
    answer: 1,
    explanation:
      "“Portanto” apresenta uma conclusão. “Entretanto” indica oposição, “além disso” acrescenta uma ideia e “embora” expressa concessão.",
  },
  {
    id: "s2",
    title: "Da situação à função",
    topic: "Funções do 1º grau",
    time: "15 min",
    type: "Prática rápida",
    description:
      "Pratique a relação entre uma situação cotidiana e sua expressão matemática.",
    question:
      "Uma corrida custa R$ 5 fixos mais R$ 2 por km. Quanto custa percorrer 4 km?",
    options: ["R$ 8", "R$ 9", "R$ 13", "R$ 20"],
    answer: 2,
    explanation: "Use f(x) = 5 + 2x. Para 4 km: 5 + 2 × 4 = R$ 13.",
  },
  {
    id: "s3",
    title: "Um argumento com fundamento",
    topic: "Argumentação",
    time: "12 min",
    type: "Exercício guiado",
    description: "Aprenda a escolher evidências que sustentam uma tese.",
    question: "O que torna um argumento mais consistente?",
    options: [
      "Repetir a tese",
      "Usar apenas opinião pessoal",
      "Relacionar evidência e tese",
      "Aumentar o tamanho do texto",
    ],
    answer: 2,
    explanation:
      "Um argumento consistente apresenta uma evidência e explica como ela sustenta a tese defendida.",
  },
];
