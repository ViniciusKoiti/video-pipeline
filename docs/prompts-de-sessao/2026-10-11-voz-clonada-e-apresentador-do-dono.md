# Prompt de sessão: voz clonada e apresentador do dono (2026-10-11)

Colar numa sessão nova do Claude Code aberta em `~/projetos/auto-play`. Estado de partida: branch
`clipe-fim-dos-cortes` com alterações não commitadas em `video/src/clipe/`; ADRs 016 e 017 escritas como
**propostas**, ainda não aceitas e não commitadas; laboratório de voz em `~/projetos/lab-voz` (fora deste
repositório), com o Chatterbox instalado, a gravação do dono e os dois áudios de teste.

---

Contexto: video-pipeline (CLAUDE.md na raiz). Foco, decisão do dono: uma frente por vez, com calma. Uma frente =
um PR; me mostre o resultado antes de qualquer merge. Leia primeiro `docs/decisions/016-voz-clonada-do-dono.md` e
`docs/decisions/017-apresentador-do-dono-em-palco.md`, e as ADRs 012, 013 e 014 que elas citam.

De onde vem isto: o projeto reels-radar (`~/projetos/radar-de-reels`) analisou Reels de privacidade e achou que os
mais compartilhados abrem com pessoa falando para a câmera e com texto de alerta na tela. Os números e os limites
estão na ADR 017. O dono quer testar um apresentador com a aparência e a voz dele. É experimento: nada aqui é
fato comprovado, e o dado é de pessoa real, não de desenho.

Frente de hoje: **só a preparação dos sprites do apresentador** (parte A da ADR 017). Sem código de template, sem
mudar contrato, sem chamar provedor.

Antes de qualquer coisa, me apresente, em linguagem simples e com as dúvidas agrupadas:

1. O que o kit exige de uma pele de imagem. Confirme pelo MCP `motion-kit` (skill `componentes-do-kit`) e pelo
   `src/COMPONENTS.md` do kit, seção "Apresentador com pele trocável": o contrato `HostSkin`, os três tipos de
   desenho, como a boca dirigida por áudio (`mouthLevels`) escolhe o visema e como a piscada entra. Confira o SHA do
   kit contra o pin de `video/package.json`. Diga se o conjunto mínimo da ADR 017 (seis visemas, com e sem piscada,
   de frente, em busto) está certo ou se o kit pede outra coisa.
2. A especificação dos sprites que sai disso: quantas imagens, nome de cada arquivo, tamanho em pixels, proporção,
   fundo transparente, onde ficam os olhos e a boca para o rosto não "pular" entre quadros, e a pasta local (fora
   do Git) onde elas vão morar.
3. **O prompt de geração de imagem**, que é o entregável principal desta sessão. Escreva-o para eu usar com fotos
   minhas como referência, de forma que sirva em mais de um gerador:
   - um prompt para a **folha inteira** (todos os quadros numa imagem só, em grade, para manter o mesmo rosto) e
     um prompt alternativo **quadro a quadro** a partir de uma base aprovada, mudando só a boca e os olhos;
   - a descrição de cada um dos seis visemas em termos de formato da boca (não só o nome), e da piscada;
   - estilo ilustrado, não fotorrealista, em busto, de frente, olhando para a câmera, luz e traço constantes;
   - o que **não** pode variar entre os quadros (cabelo, roupa, enquadramento, cores) e o que pedir para evitar
     (texto, marca d'água, fundo, mãos na frente do rosto);
   - duas ou três variações de estilo para eu escolher.
   Diga também quais fotos minhas servem de referência (ângulo, luz, expressão) e quantas.
4. As opções de **onde** gerar, sem escolher por mim: o que cada uma custa, se aceita foto de referência e o que
   diz sobre uso do material enviado. Só o que estiver em `data/benchmarks/` ou em página oficial lida nesta
   sessão; o resto fica como "não confirmado". Inclua a opção sem provedor (desenho ou decalque à mão).
5. Como os sprites entram pela regra 3: que licença se registra para ativo de autoria do dono e se a lista fechada
   da ADR 007 precisa de emenda.

Limites desta sessão:

- **Nenhuma foto, voz ou dado pessoal meu sai da máquina.** Não envie nada a provedor remoto; não gere imagem.
  O prompt é texto para eu usar depois, onde eu decidir.
- Nenhuma chamada a provedor externo (Gemini, Pexels, Cloudflare, Higgsfield…). Ollama e Kokoro locais podem rodar.
- Nada de custo: `MAX_API_SPEND_USD=0` continua valendo (§2.1).
- Nenhuma mudança em `app/`, `video/src/`, `config/` nem em contrato. As ADRs 016 e 017 são propostas: pode sugerir
  correções nelas, mas não as marque como aceitas.
- Não mexa nas alterações não commitadas de `video/src/clipe/`; se precisar de branch, crie uma nova a partir do
  `main` e me diga antes.
- Arquivos `approved` em `data/episodes/*/` ficam intactos. Dúvida de licença ou de termos: parar e perguntar.
- Fotos, sprites e a gravação de voz ficam fora do Git.

Pronto quando: eu tiver, numa resposta só, a especificação dos sprites conferida no kit, o prompt de geração
pronto para colar (folha inteira e quadro a quadro, com as variações de estilo), a lista de fotos que preciso
tirar e as opções de gerador com o que está confirmado e o que não está.

Fica para outras sessões, nesta ordem sugerida: escuta às cegas e medição de tempo da voz clonada (ADR 016);
palco na abertura com o Notionists (parte B da ADR 017); pele `dono` no template depois que os sprites existirem.
