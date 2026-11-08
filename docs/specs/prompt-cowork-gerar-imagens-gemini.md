<!-- Cópia para registro (2026-11-06). O Cowork lê o original em E:\personagens\PROMPT-COWORK.md, fora do Git, junto com cópias de 00-guia-e-estilo.md e prompts-cenas.md em E:\personagens\entrada\. O Cowork não acessa o WSL: tudo o que ele lê e escreve fica em E:. A avaliação de ferramentas, separada, está em docs/specs/prompt-cowork-imagens-ia.md. -->

# Cowork: gerar no Gemini as imagens do piloto "Como era ser rico na Idade Média?"

Escrito em 2026-11-06 pelo Claude Code, a pedido do dono. Leia o arquivo inteiro antes de agir. Trabalhe em português do Brasil.

## O que é

Gere no Gemini (https://gemini.google.com), pelo Chrome e com a conta do dono já logada, as imagens de um vídeo. Salve cada uma
nesta pasta, com o nome certo e o registro da geração. Os prompts já existem e não mudam:

- `entrada\00-guia-e-estilo.md`: bloco de estilo (§1), folhas do personagem (§2: 2a e 2b) e do elenco (§2c, no fim do arquivo),
  as 3 capas (§3) e o checklist (§4).
- `entrada\prompts-cenas.md`: 53 imagens principais (`NN-slug`) e 25 extras (`xNN-slug`), na ordem do vídeo.

`[AVATAR]` é o personagem principal das folhas 2a e 2b. `[ELENCO]` é o elenco da folha 2c. A imagem 49 usa a 01 como referência.
São ilustrações, nunca registro histórico. Você gera, confere e registra. Quem aprova é o dono.

Tudo de que você precisa está em `E:\personagens`. Os arquivos de `entrada\` citam caminhos do repositório do dono (`CLAUDE.md`,
`data\...`, `referencias\...`), que ficam no WSL, fora do seu alcance: ignore-os. A miniatura de outro canal citada no guia (§3)
nunca vai ao Gemini.

## 1. Regras

1. Só o Gemini, só a conta que já está logada no Chrome. Não faça login, não digite senha, não resolva captcha nem verificação.
   Se aparecer, pare (seção 7).
2. Custo zero: não clique em upgrade, assinatura, teste grátis nem compra. Nenhum outro gerador, conta ou API.
3. Não mude configurações da conta Google nem do Gemini. Anote o que vê.
4. Não compartilhe conversas (nada de link público). Não abra outros sites além do Gemini e das páginas da seção 9.
5. Nunca apague nem sobrescreva arquivo. Nome repetido ganha `__v2`, `__v3`. Não mexa em `E:\personagem` (sem o "s").
6. Não edite as imagens: nada de cortar, redimensionar, converter, tirar fundo ou marca. Salve o arquivo como o Gemini entregou.
7. Envie os prompts como estão nos arquivos. As únicas mudanças permitidas estão nas seções 4, 5 e 6. Registre sempre o texto
   exato que enviou.
8. Uma imagem por vez, uma conversa do Gemini de cada vez.
9. Ao Gemini, só anexe as folhas aprovadas e a imagem 01. Nenhuma imagem de outro canal ou de outra obra.
10. Não escreva o e-mail do dono em lugar nenhum. Do plano, anote só o nome que a interface mostra.

## 2. Pastas e registros

```
E:\personagens\
  PROMPT-COWORK.md           este arquivo (só leitura)
  entrada\                   cópias dos prompts (só leitura)
  aprovacao.md               decisões do dono (você cria o modelo da seção 5; só o dono preenche)
  registro.csv               uma linha por imagem salva, no formato do plano do episódio
  _downloads\                pasta de download do Chrome durante a tarefa
  personagem\  capa\         folhas e capas (as cenas ficam na raiz)
  controle\progresso.csv     uma linha por imagem planejada
  controle\registro.jsonl    uma linha por arquivo baixado, com todos os dados
  controle\relatorio.md      o que aconteceu em cada execução (só acrescente)
  controle\termos-gemini.md  seção 9
```

Ao começar, leia `controle\progresso.csv` e `aprovacao.md` e continue de onde parou: o que está `ok` ou `revisar` não se refaz.
Se o progresso não existir, crie-o com todas as imagens das seções 5 e 6, em `pendente`.

- `progresso.csv`: `id,fase,alternativa,conversa_url,status,tentativas,arquivo,observacao`. Status: `pendente`, `ok`,
  `revisar`, `falhou`, `bloqueado`.
- `registro.csv`: `arquivo,prompt_id,cena,gerador,data,aprovado,observacao`. Em `gerador`:
  `Gemini — <modelo mostrado> — <plano mostrado>`. Deixe `aprovado` vazio.
- `registro.jsonl`, um objeto por linha: `arquivo`, `id`, `cena`, `fase`, `alternativa`, `tentativa`, `formato_real` (pelos bytes
  iniciais), `largura`, `altura`, `bytes`, `sha256`, `data_hora` (ISO 8601 com fuso, ex. `2026-11-06T21:40:00-03:00`),
  `plano_mostrado`, `modelo_mostrado` (nome exato na interface), `conversa_url`, `prompt_enviado` (texto exato e completo),
  `anexos`, `marca_dagua_visivel` (`não` ou onde), `conferencia` (cada item da seção 4), `observacao`.

Calcule `sha256`, tamanho e dimensões com Python (Pillow se houver; senão, pelo cabeçalho do arquivo).

## 3. Antes da primeira imagem

- Confira se o Chrome baixa em `E:\personagens\_downloads` sem perguntar onde salvar. Se perguntar, pare: o dono configura.
- Abra o Gemini e anote o plano mostrado. Se houver tela de limites de uso, copie o que ela diz.
- Use a ferramenta de criar imagem. Se houver escolha de modelo, modo ou resolução, use a de maior qualidade que a conta oferecer,
  sempre a mesma, e anote o nome exato. Se ela acabar no meio, pare: com outro modelo o traço muda.

## 4. Gerar, salvar e conferir cada imagem

1. Envie o prompt numa mensagem só, com o texto inteiro. Se a interface tiver opção de proporção, use 16:9 (folhas também).
2. Se o Gemini responder só com texto, mande uma vez: `Generate the image now, following all the rules above.`
3. Recusa por segurança (peste, revolta, morte): suavize a descrição uma vez, sem gore e sem mudar o que a cena mostra. Se recusar
   de novo, marque `falhou` com o motivo.
4. Baixe pelo botão de download da própria imagem, no tamanho original ou completo. Não use "salvar imagem como", cópia nem captura
   de tela. Se vierem várias imagens numa resposta, baixe todas (`__v1a`, `__v1b`).
5. Pegue o arquivo novo em `_downloads` (espere até 60 s; se não vier, baixe de novo uma vez). Mova para o nome final com a
   extensão do formato real (se o nome pede `.png` e o arquivo é JPEG, use `.jpg` e anote). Registre em `registro.csv`,
   `registro.jsonl` e `progresso.csv`.
6. Abra o arquivo baixado e confira pelo checklist do guia (§4):
   - texto, letras, números, placa escrita ou rótulo;
   - objeto moderno ou fora de época;
   - personagem diferente das folhas aprovadas (rosto, cabelo, olhos, proporções) ou mão deformada;
   - logo, marca d'água ou brasão reconhecível;
   - assunto fora do centro ou sem espaço livre embaixo para a legenda;
   - formato longe de 16:9 (quadrado ou vertical);
   - resolução (anote; o vídeo é 1920×1080).
   Se um item falhar, faça uma nova tentativa na mesma conversa:
   `Redo the same image. Fix: <o problema>. Keep everything else identical.`
   No máximo 2 tentativas por imagem; guarde as duas. Se a segunda também falhar, marque `revisar` com o motivo e siga.
7. Se uma imagem demorar mais de 3 minutos, recarregue a página uma vez. Se não vier, `falhou`.

## 5. Fase 1: duas alternativas de folhas, cada uma com três cenas de teste

Faça a alternativa **A** numa conversa nova e depois a **B** em outra conversa nova, com a mesma sequência:

1. Primeira mensagem: o bloco de estilo do guia (§1), uma linha em branco e o prompt **2a**.
   Salve `personagem\00a-expressoes__A.png` (na B, `__B`).
2. Prompt **2b**, trocando "Using the attached character as reference" por "Using the character sheet you just made as
   reference". Salve `personagem\00b-roupas__A.png`.
3. Prompt **2c**, trocando "Using the attached main character as a style reference" por "Using the main character from the sheet
   you made earlier in this conversation as a style reference". Salve `personagem\00c-elenco__A.png`.
4. Esta mensagem, que só pede texto (se vier imagem mesmo assim, não salve):
   `From now on, [AVATAR] means the main character exactly as on the character sheets you made above (same face, hair, eyes and proportions; the outfit is the one each prompt describes). [ELENCO] means the four supporting characters exactly as on the cast sheet you made above. Reply only with the word OK, no image.`
5. Os prompts **01**, **02** e **08** de `prompts-cenas.md`, como estão. Salve `01-patio-madrugada__A.png`,
   `02-voce-retrato__A.png` e `08-senescal-moedas__A.png`.

Se a primeira imagem da tarefa vier com marca d'água visível, pare antes da segunda e avise: o dono decide antes de gastar a cota.

Ao terminar A e B, crie `aprovacao.md` com o modelo abaixo, escreva o relatório e **pare**.

```
# Decisões do dono (o Cowork só lê)
folhas:
# A ou B. Ajuste opcional depois de um travessão, ex.: "folhas: A — cabelo mais curto"
extras: não
# "sim" para gerar também as 25 imagens extras, depois das principais e das capas
conversa:
# opcional: link de uma conversa do Gemini preparada pelo dono, com as folhas anexadas
```

## 6. Fase 2: o resto (só com `folhas: A` ou `folhas: B` escrito pelo dono)

1. Se houver ajuste depois do travessão: refaça as folhas afetadas e as cenas 02 e 08 na conversa da alternativa escolhida
   (nova versão `__v2`), registre e pare de novo.
2. Sem ajuste: copie (não mova) os arquivos da alternativa escolhida para os nomes finais, sem o sufixo:
   `personagem\00a-expressoes`, `personagem\00b-roupas`, `personagem\00c-elenco`, `01-patio-madrugada`, `02-voce-retrato` e
   `08-senescal-moedas`, com a extensão de cada arquivo. Marque-os `ok` no progresso.
3. Ordem: as principais que faltam, na ordem do vídeo (03 a 53); depois as 3 capas do guia (§3), em `capa\`; depois, só com
   `extras: sim`, as extras, começando pelas das cenas S19, S43, S47 e S48 e seguindo na ordem.
4. Abra uma conversa nova a cada 12 imagens, nesta ordem de preferência:
   a) a conversa que o dono indicou em `conversa:` (continue nela);
   b) uma conversa nova em que você anexa as três folhas finais (`personagem\00a`, `00b`, `00c`) e manda como primeira mensagem o
      bloco de estilo do guia seguido de:
      `The attached images are the approved character sheets. [AVATAR] means the main character exactly as on the first two sheets (same face, hair, eyes and proportions; the outfit is the one each prompt describes). [ELENCO] means the four supporting characters exactly as on the third sheet. Reply only with the word OK, no image.`
      Anexe como suas ferramentas permitirem; o dono pode ter anexado as folhas nesta tarefa para isso;
   c) se não conseguir anexar, continue na conversa da alternativa escolhida, onde as folhas e a definição já estão, e reenvie o
      bloco de estilo a cada 10 imagens.
   Se o rosto do avatar mudar em duas imagens seguidas, ou a conversa ficar lenta ou errática, pare e peça ao dono uma conversa
   preparada (`conversa:`).
5. A **49** vai na conversa da alternativa escolhida, onde está a imagem 01. Troque `[IMAGEM 01 como referência]` por
   `Use the courtyard image you made earlier in this conversation (prompt 01) as the reference.`
6. Os outros prompts vão como estão, as capas também (elas começam com `[AVATAR]`).

## 7. Quando parar (escreva o relatório e termine a tarefa, sem ficar tentando)

- Aviso de limite, cota ou "tente mais tarde" (copie o texto e o horário de liberação, se houver).
- Login, senha, captcha, verificação, pagamento ou upgrade.
- O modelo escolhido sumiu ou trocou no meio.
- Download que não aparece duas vezes seguidas, ou o Chrome perguntando onde salvar.
- Marca d'água visível na primeira imagem.
- A interface mudou e você não tem certeza de onde clicar: pare em vez de adivinhar.
- O rosto do avatar mudou em duas imagens seguidas.
- Fim de uma fase.

O dono retoma depois com o mesmo pedido, e o progresso diz onde continuar.

## 8. Relatório (acrescente em `controle\relatorio.md`)

Início e fim; plano, modelo e resolução vistos; imagens `ok`, `revisar` e `falhou`, com os motivos; marca d'água visível (sim ou
não, e onde); limites vistos, com o texto; a próxima fase e o que falta. No fim, responda ao dono com um resumo de 5 linhas.

## 9. Uma vez só: termos oficiais (se `controle\termos-gemini.md` não existir)

Abra estas páginas e copie para `controle\termos-gemini.md`, com o link e a data de hoje, os trechos **literais** sobre: quem é dono
do conteúdo gerado e como pode usá-lo; uso comercial; marca d'água, SynthID ou identificação de conteúdo gerado; proibições
ligadas a esconder que é IA. Nada de resumo sem o trecho. O que não achar, marque `[pendente]`.

- https://policies.google.com/terms/generative-ai
- https://policies.google.com/terms/generative-ai/use-policy
- https://policies.google.com/terms
- https://support.google.com/gemini/answer/13594961
