# Gemini (app, conta pessoal): termos para imagens geradas (consulta de 2026-11-14)

Registro pedido pela regra de licença do projeto (CLAUDE.md §2.3 e §6; ADR 007): imagem gerada só entra com os termos do
gerador registrados. Gerador informado pelo dono em 2026-11-14: **Gemini, app da conta pessoal do dono**. Vale para as
imagens de `idade-media-ser-rico` (onde o registro ainda diz "gerador: a confirmar pelo dono") e de
`idade-media-ter-20-anos`.

Páginas lidas em 2026-11-14 por um agente de leitura (todas com HTTP 200). As citações são literais, em inglês.

| Página | URL | Data que a página mostra |
|---|---|---|
| Termos de Serviço do Google | https://policies.google.com/terms | "Effective July 30, 2026"; "Country version: Brazil" |
| Termos adicionais de IA generativa | https://policies.google.com/terms/generative-ai | "Last Modified: August 9, 2023"; a página diz que **deixaram de valer** em 22/05/2024, salvo para parceiros com contrato ("these Generative AI Additional Terms of Service no longer apply") |
| Política de uso proibido de IA generativa | https://policies.google.com/terms/generative-ai/use-policy | "Last Modified: December 17, 2024" |
| Lista de termos por serviço | https://policies.google.com/terms/service-specific | sem data; o Gemini Apps aponta só para a política de uso proibido e para os termos de chamadas telefônicas (que não tratam de imagem) |

## O que as páginas dizem

| Pergunta | Resposta | Trecho |
|---|---|---|
| Dono da imagem | O Google não reivindica propriedade; o conteúdo continua do usuário, na medida em que ele tiver direitos. As páginas não dizem se uma imagem gerada por IA é protegida por direito autoral. | "Some of our services allow you to generate original content. Google won't claim ownership over that content."; "Your content remains yours, which means that you retain any intellectual property rights that you have in your content." |
| Uso comercial | Não há cláusula que proíba uso comercial da imagem gerada. É proibido usar o conteúdo gerado para treinar modelos. | "non-exclusive, which means you can license your content to others"; proibido "using AI-generated content from our services to develop machine learning models or related AI technology" |
| Aviso de IA e marca d'água | Nenhuma página fala em SynthID nem obriga o usuário a rotular a imagem. A regra é não enganar sobre a origem. | "misleading others into thinking that generative AI content was created by a human"; item 4.5 da política: "Misrepresenting the provenance of generated content by claiming it was created solely by a human, in order to deceive." |
| Política de uso proibido para ilustração histórica com pessoas inventadas | A política não fala de arte nem de história. Valem os itens gerais: não violar direito de terceiros (1.6, "Violates the rights of others, including privacy and intellectual property rights"), não contornar filtros (2.3), nada de ódio, assédio, incitação à violência ou conteúdo sexual (3.1–3.4). Personificar pessoa real sem aviso, para enganar, é proibido (4.2); pessoa inventada não entra nisso. | "We may make exceptions to these policies based on educational, documentary, scientific, or artistic considerations" (faculdade, não garantia) |
| Idade e conta | Nenhuma idade em número nas páginas lidas; o usuário responde pelo que faz com a conta. | "You're responsible for what you do with your Google Account" |

## Ponto em aberto

A definição de "consumidor" nos termos depende de uso "personal, non-commercial" ("uses Google services for personal,
non-commercial purposes outside of their trade, business, craft, or profession"). As páginas não dizem se monetizar um
vídeo muda a classificação da conta para "usuário empresarial", que tem regras próprias de responsabilidade. Não muda o
direito de usar a imagem; muda quem responde por quê. Decisão de risco do dono.

## Consequência para o projeto

- Licença `Generated`, `provider: original`, com o gerador **Gemini (app, conta pessoal do dono)** no registro de cada
  imagem e na `generation`, e o prompt usado.
- A divulgação de conteúdo sintético do YouTube continua sendo a regra do §2.4 do CLAUDE.md (obrigatória para imagem
  sintética **realista** de fato histórico). Os termos do Google não exigem rótulo, mas proíbem apresentar a imagem
  como feita só por humano: os créditos dizem "ilustrações geradas por IA".
- A ADR 007 só prevê `Generated` pelo Workers AI (Cloudflare). Falta uma emenda que aceite o gerador do dono (Gemini),
  com este arquivo como registro. Decisão do dono.

## Não lido

Termos do YouTube (https://www.youtube.com/t/terms), páginas de ajuda do Gemini sobre imagens e SynthID, Política de
Privacidade e a página de idade da Conta Google. Não é parecer jurídico.
