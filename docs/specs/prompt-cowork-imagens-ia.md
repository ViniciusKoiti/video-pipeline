# Prompt: avaliar como gerar com IA as imagens de `prompts-cenas.md` (Claude Cowork)

Prompt para o Claude Cowork, escrito em 2026-11-06 a pedido do dono, sobre as imagens de
`data/episodes/idade-media-ser-rico/imagens-ia/prompts-cenas.md` (piloto "Como era ser rico na Idade Média?"). Não é uma
decisão: o relatório volta para o dono, e nada vira padrão sem ADR.

## Como usar

1. A pasta de trabalho já está montada fora do Git, em `data/cache/cowork-imagens-ia/`. Em `entrada/` estão cópias de
   `prompts-cenas.md`, `00-guia-e-estilo.md`, `mapa-planos.csv`, `plano-imagens.md` e `pauta.md`, o teste do prompt 05, o pedido
   ao motion-kit e, em `testes-personagem/`, as folhas de peças de 2026-11-06. A `saida/` está vazia.
2. No Cowork, escolha a pasta `\\wsl.localhost\UbuntuRecovered\home\viniciusk\projetos\auto-play\data\cache\cowork-imagens-ia`.
   Se ele não aceitar um caminho do WSL, copie a pasta para o Windows e escolha a cópia; no fim, traga a `saida/` de volta.
3. Cole no Cowork tudo o que vem depois da linha `<!-- PROMPT -->`. Para copiar com os acentos certos:
   `! { printf '\xff\xfe'; sed '1,/^<!-- PROMPT/d' docs/specs/prompt-cowork-imagens-ia.md | iconv -f utf-8 -t utf-16le; } | /mnt/c/Windows/System32/clip.exe`
4. Com a `saida/` de volta, peça ao Claude Code para levar o relatório a `docs/pesquisa/` e os termos a `data/benchmarks/`.

<!-- PROMPT -->

Você vai avaliar qual é a abordagem mais adequada para gerar com IA as imagens de um vídeo, descritas em
`entrada/prompts-cenas.md`. Entregue uma recomendação com evidência e um protocolo de teste. Trabalhe em português do Brasil.

A pasta que você recebeu tem `entrada/` (só leitura) e `saida/` (onde você escreve). Leia todos os arquivos de `entrada/` e olhe
as imagens antes de pesquisar. Pare para perguntar ao dono só antes de gerar ou enviar algo a um serviço externo e antes de
qualquer gasto; o resto, faça até o fim.

## 1. Contexto

Sou o dono de um canal de vídeos narrados em português (Cena e Conceito). Os vídeos saem de um pipeline local: roteiro em JSON,
voz clonada, montagem em Remotion e quatro revisões humanas antes de publicar.

O vídeo em questão é o piloto de um formato novo, uma história em segunda pessoa: "Como era ser rico na Idade Média?". Ele conta a
vida de um grande senhor na Inglaterra do século XIV, tem cerca de 10,6 minutos e 53 cenas. Se funcionar, vira uma escada, "sua
vida em cada nível da Idade Média": um degrau por vídeo, com o mesmo avatar recorrente (o "você") trocando de roupa conforme o
degrau. O elenco de apoio é inventado: senescal, senhora da casa, capelão e camponês.

O que `prompts-cenas.md` pede:

- 78 prompts em inglês, um por imagem, na ordem do vídeo: 53 principais (uma por cena, obrigatórias) e 25 extras opcionais para as
  cenas longas. O `mapa-planos.csv` liga cada um dos 118 planos de imagem do roteiro a uma dessas imagens.
- Os prompts dependem do `00-guia-e-estilo.md`. Um bloco de estilo é colado como primeira mensagem de um chat novo, e cada prompt
  termina com "Same style as before. No text at all. 16:9. Keep the bottom clear for subtitles."
- `[AVATAR]` aparece em 22 prompts (15 principais e 7 extras) e pede para anexar a folha do personagem; `[ELENCO]` aparece em 5 e
  pede a folha do elenco. Essas folhas (2a, 2b e 2c no guia) vêm antes de tudo, e o dono aprova o rosto antes de seguir.
- O prompt 49 usa a imagem 01 como referência (o mesmo pátio, de manhã).
- O guia também traz 3 capas, sem texto e com espaço livre no alto para a palavra que entra na edição.
- As cenas de peste, revolta e morte foram pedidas sem gore.

## 2. O plano atual e o que já se sabe

- **Plano:** o dono gera as imagens no chat do ChatGPT (assinatura Plus que ele já paga), uma por vez, salva cada PNG com o nome do
  prompt e anota uma linha em `registro.csv` (`arquivo, prompt_id, cena, gerador, data, aprovado, observacao`). O plano anota
  quatro riscos: o rosto do avatar mudar de uma imagem para outra; texto ou objeto moderno aparecerem; mão deformada; recusa por
  segurança nas cenas de peste e revolta.
- **Um teste feito:** o prompt `05-comitiva-estrada` gerou `teste-prompt-05-comitiva-estrada.png`, com 1024×572 e sem
  transparência. O gerador deve ser confirmado com o dono, porque o PNG não traz metadados de origem. O vídeo sai em 1920×1080.
- **Avatar em aberto:** o guia descreve olhos de ponto e nariz não marcado, mas os testes do personagem saíram com o rosto mais
  detalhado. Esses testes (`testes-personagem/`) são folhas de peças para animação e estão fora do foco desta avaliação. Nas
  folhas com transparência, um script mediu um halo: nenhum pixel é totalmente opaco, e há dezenas a centenas de milhares de
  pixels quase transparentes em volta das peças, muitos deles vermelhos. Isso só importa se a abordagem recomendada usar recortes
  com transparência.
- **Alternativa em estudo para as cenas com o avatar:** fundo gerado sem personagem, com o personagem animado da biblioteca de
  animação do canal (o motion-kit) por cima. Ela depende de peças que o kit ainda não tem (`pedido-motion-kit-2026-11-06.md`,
  pedido ainda sem resposta). Avalie-a como alternativa, não como ponto de partida.

## 3. Regras que não mudam

1. **Custo zero.** Nada de API paga, crédito comprado, assinatura nova ou cartão cadastrado. Valem as assinaturas que o dono já tem
   (ChatGPT Plus e o plano do Claude, pelos apps) e as camadas gratuitas. Se uma ferramenta pede cartão até no plano grátis,
   registre e descarte.
2. **Licença registrada por imagem.** Cada imagem entra no projeto como `Generated`, com `sha256`, o registro da geração
   (ferramenta, modelo e versão, prompt, semente se houver, data) e os termos do gerador lidos na página oficial, com link e data
   da consulta. Os termos do ChatGPT estão pendentes: em 2026-10-27, a página https://openai.com/policies/row-terms-of-use/
   recusou o acesso automático (HTTP 403), e falta copiar a seção "Ownership of content".
3. **Ilustração, nunca registro de época.** Proibido: texto, logotipo, marca d'água, brasão de família real, rosto de pessoa
   real, personagem de franquia e estilo copiado de outro canal. O canal de referência do formato usa um avatar de cabeça branca
   em forma de ovo; o nosso tem de ser outro. Não proponha que um agente desenhe ilustração ou personagem à mão em SVG: três
   rascunhos assim foram reprovados.
4. **Política de conteúdo não original do YouTube.** O Programa de Parcerias não monetiza "apresentações de slides com imagens,
   histórias com modelos ou texto com pouco ou nenhum valor narrativo, analítico ou educativo" nem conteúdo "repetitivo ou
   produzido em massa" (texto conferido em 2026-10-23, support.google.com/youtube/answer/1311392). São 118 planos de imagem parada
   com narração; hoje o movimento previsto é zoom lento e panorâmica. Pese isso. A divulgação de conteúdo sintético é decisão do
   dono na revisão final.
5. **Dado pessoal.** Rosto e voz do dono não vão a nenhum provedor por causa deste trabalho. Os personagens são inventados.
6. **Ambiente.** Windows com WSL2, 12 GB de RAM e 12 threads para o Linux; o projeto roda só em CPU, sem GPU local. O dono tem conta
   no Modal (GPU na nuvem, já usada para a voz). O vídeo sai em 1920×1080, e 1080×1920 é desejável para cortes verticais.

## 4. O que avaliar

**Formas de produzir** (combine por grupo de imagem, se fizer sentido):

- A. Chat, uma imagem por vez (o plano atual), num app ou em mais de um.
- B. Lote por API ou script, numa camada gratuita.
- C. Modelo aberto rodando no Modal (ou na CPU, se der), com técnicas de consistência: imagem de referência, LoRA do personagem,
  IP-Adapter, ControlNet.
- D. Mistura: por exemplo, cenário e multidão em lote e as cenas do avatar no chat com a folha anexada, ou o que a pesquisa mostrar.
- E. Para as cenas do avatar, a rota híbrida com o personagem do kit.

**Ferramentas** (ponto de partida; confira o que cada uma faz hoje, sem supor):

- Apps: ChatGPT, Gemini, Microsoft Copilot, Adobe Firefly, Ideogram, Recraft, Leonardo, Krea, Grok.
- APIs com camada gratuita: Cloudflare Workers AI (já é o gerador do pipeline para lacunas, com FLUX.1 Schnell; o projeto anota
  10.000 neurons por dia grátis e cerca de 58 por imagem de 1024×1024 em 4 passos), Google AI Studio, Hugging Face e Together AI.
- Modelos abertos: FLUX (as variantes têm licenças diferentes), Qwen-Image e Qwen-Image-Edit, SDXL, Stable Diffusion 3.5 e o que
  houver de mais atual, com ComfyUI ou equivalente.
- Pós-processo: ampliação para 1920×1080, recorte em 16:9, conferência de texto e de objeto moderno.

**Critérios** (proponha pesos e diga por quê):

1. Fidelidade ao prompt e qualidade da ilustração.
2. Um estilo só nas 78 imagens.
3. Consistência do avatar e do elenco nos 27 prompts com personagem e nas capas, e entre episódios.
4. Resolução e formato: 16:9 em 1920×1080, nativo ou ampliado sem perda visível.
5. Horas do dono para as 78 imagens, as folhas e as capas, contando as refações.
6. Custo zero de fato, e os limites: cota diária, fila, marca d'água, recusa de conteúdo.
7. Termos: quem é dono do resultado, uso comercial em canal monetizado, licença do modelo, o que registrar.
8. Rastreio e repetição: dá para guardar modelo, versão, prompt e semente, e refazer uma imagem igual ou parecida?
9. Reuso nos próximos degraus da escada (mesmo avatar, mesmo estilo).
10. Riscos: a política do YouTube e a semelhança com personagem ou estilo de terceiros.

## 5. Perguntas que o relatório responde

1. Que abordagem você recomenda para gerar estas imagens (por grupo, se for o caso), e por quê? O que faria você mudar de ideia?
2. O passo a passo do dono na abordagem recomendada: do bloco de estilo e das folhas até a imagem salva e anotada em
   `registro.csv`.
3. Os prompts servem como estão na ferramenta recomendada? "Same style as before" depende da memória do chat; num lote, cada prompt
   tem de ser completo. Proponha o modelo de prompt (estilo, cena, restrições, formato, referência) e reescreva 5 prompts como
   exemplo, sem mudar o conteúdo de nenhuma cena.
4. Como manter o avatar e o elenco iguais em todas as imagens em que aparecem, e de um vídeo para o outro?
5. Como chegar a 16:9 em 1920×1080 (tamanho nativo de cada ferramenta, ampliação, recorte) sem perder a faixa livre embaixo para a
   legenda?
6. Quantas imagens por dia cada finalista permite, e quanto tempo leva o lote completo?
7. Os termos de cada finalista: link oficial, data da consulta, o trecho que decide (dono do resultado, uso comercial) e o que
   segue pendente.
8. A rota híbrida vale para as cenas do avatar? Quanto ela reduz o risco de o vídeo virar slideshow, e quanto depende do kit?

O relatório não depende do teste da seção 6: recomende com o que a pesquisa mostrar e diga o que o teste vai confirmar ou derrubar.

## 6. Protocolo de teste (você escreve; o dono decide se roda)

Escolha no máximo 3 finalistas e escreva um teste igual para todos, com os mesmos prompts de `prompts-cenas.md`. Sugestão (ajuste):

- as folhas 2a e 2c do guia (personagem e elenco), pré-requisito dos prompts com personagem;
- `01-patio-madrugada` e `49-patio-manha` (continuidade de lugar);
- `02-voce-retrato` e `26-voce-falcao` (avatar; cavalo e objeto na mão);
- `08-senescal-moedas` (elenco e várias pessoas);
- `05-comitiva-estrada` (já testado uma vez; compare com o teste);
- `44-casa-tochas` (noite e cena sensível).

Para cada geração, anote: ferramenta, modelo e versão, app ou endpoint, data, tamanho entregue, tempo por imagem, tentativas até
uma imagem útil, limite observado, custo, recusas e erros, avaliação do dono e link dos termos. O dono avalia às cegas: os
arquivos são renomeados por sorteio, e a chave fica numa planilha à parte.

## 7. Limites

- Não crie conta, não assine plano, não cadastre cartão, não compre crédito.
- Não gere imagem nem envie arquivo a um serviço externo sem o OK do dono nesta sessão. Com o OK, use só as contas dele já
  logadas e só os prompts do protocolo, e anote cada geração.
- Não envie a nenhum gerador, como referência, imagem de outro canal ou de outra obra.
- A fonte é a página oficial (termos, preços, cotas, documentação). Blog, catálogo, fórum e vídeo servem só para descobrir. Cada
  número, cota ou termo vai com link e data da consulta. Se uma página oficial recusar o acesso automático, tente pelo navegador;
  se não der, marque como pendente.
- Separe o que você conferiu, o que inferiu e o que não conseguiu conferir.
- Gasto, estilo, contratação e mudanças no kit são decisões do dono: apresente-as como decisão, com opções e a sua recomendação.
- Escreva só em `saida/`.

## 8. Entrega (em `saida/`)

1. `avaliacao-imagens-ia-AAAA-MM-DD.md` (com a data do dia): começa pela recomendação, em meia página. Depois vêm a tabela das
   formas de produzir por critério, a tabela das ferramentas finalistas, as respostas da seção 5 e os riscos. Frases curtas, sem
   marketing.
2. `modelo-de-prompt.md`: o modelo de prompt da ferramenta recomendada e os 5 prompts reescritos como exemplo.
3. `protocolo-teste.md`: os casos da seção 6 com o prompt exato de cada ferramenta, onde salvar cada arquivo e a planilha de
   anotação.
4. `termos/<ferramenta>.md`: um por finalista, com link oficial, data, trechos citados literalmente e pendências.
