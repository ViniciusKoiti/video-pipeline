# Gravações de referência para a voz do dono

Guia preparado a pedido do dono em 2026-11-01. A seleção por idioma e `delivery`
foi integrada aos Shorts e vídeos longos, localmente e no Modal (ADR 053).
O `CHATTERBOX_REFERENCE`, hoje `/home/viniciusk/projetos/lab-voz/referencia.wav`,
continua sendo usado quando não há mapeamento para a cena. Preservar essa referência.
O teste automatizado comprova a seleção; a qualidade da entonação depende da escuta.

## Coleta recebida em 2026-11-01

O dono gravou os cinco tons em português e inglês em
`/home/viniciusk/projetos/lab-voz/voice-references/{pt-BR,en}/`.
Foram copiadas as dez gravações M4A para `data/voice-references/{pt-BR,en}/`,
padronizando os nomes como `<delivery>-01.m4a` e preservando todos os originais.
Versões WAV PCM de 16 bits, mono, a 48 kHz foram criadas ao lado, sem cortes
ou mudanças de velocidade. Durações e hashes estão no inventário privado
`data/voice-references/inventario.json`; as durações são de 13,9 a 21,8 segundos.
Foi conferido que cada WAV abre e conserva a duração do M4A. Isso não substitui
a escuta de ruído, pronúncia, identidade e intenção.

As dez gravações estão cadastradas em `[chatterbox.references]` de
`config/providers.toml`. O envio ao volume privado e a síntese real do teste inicial
têm registros privados em `data/voice-references/`; consultar esses registros para
confirmar a sincronização. Nenhuma geração deste teste aprova um vídeo para publicar.

## Onde gravar e guardar

Use o gravador do celular ou o gravador do computador que já tiver. Só precisamos
do áudio. Grave em ambiente silencioso, com pouca reverberação; mantenha o mesmo
microfone, posição, distância e volume de fala nas tomadas.
Comece com o microfone a aproximadamente 15–20 cm e ajuste se houver sopro ou estalos.
Fale um pouco de lado para o microfone se os sons de P/B estiverem estourando.

Pasta local preparada:

```text
/home/viniciusk/projetos/auto-play/data/voice-references/
├── pt-BR/
│   ├── hook-01.wav
│   ├── hook-02.wav
│   ├── neutral-01.wav
│   ├── neutral-02.wav
│   ├── calm-01.wav
│   ├── calm-02.wav
│   ├── turn-01.wav
│   ├── turn-02.wav
│   ├── invite-01.wav
│   └── invite-02.wav
└── en/  (opcional, se quiser gravar naturalmente em inglês)
```

O diretório inteiro é ignorado pelo Git, inclusive arquivos M4A e vídeos.
O gerador usa os caminhos cadastrados no TOML. Colocar ou renomear um arquivo na
pasta não cria um cadastro novo automaticamente.
Se estiver no Windows com este projeto aberto no VS Code/WSL, navegue pela árvore
do projeto até `data/voice-references/pt-BR` e copie os arquivos para ela.

Prefira exportar WAV sem compressão se o gravador permitir. Se ele salvar M4A,
guarde o original como `hook-01.m4a`, por exemplo; não renomeie a extensão para WAV.
A conversão pode ser feita depois, preservando os originais.

## Como fazer as tomadas

- Faça duas tomadas de cada texto, em arquivos separados, sem mudar o tom no meio.
- Mire aproximadamente 10–15 segundos de fala por tomada; não acelere para caber.
  É um ponto de partida para nosso teste, não um requisito mínimo do modelo.
- Comece a frase já com a intenção desejada. Deixe apenas uma margem curta antes
  e depois da fala; não leia o nome do tom nem diga "teste de gravação" no áudio.
- Fale como se explicasse para uma pessoa. Varie a intenção mantendo sua voz habitual.
- Grave só sua voz, sem música, efeitos, outra pessoa falando ou filtro de personagem.
- Escute cada tomada: as palavras devem estar completas, sem distorção, ruído forte
  ou distância variável. Regrave a tomada se houver um erro, sem concatenar tentativas.

## Textos em português

### hook — curiosidade, abertura

Intenção: uma pergunta que você realmente quer responder. Destaque "por quê" e
"olhar de perto" com naturalidade, sem gritar.

> Você já percebeu que um programa pode funcionar bem sozinho e apresentar problemas quando recebe várias requisições? Por que isso acontece? Vamos olhar de perto o caminho que cada uma percorre.

### neutral — conversa natural, explicação

Intenção: sua voz habitual de explicação, sem suspense. Faça pausas nos pontos.

> Neste exemplo, vamos acompanhar uma requisição desde a entrada até a resposta. Cada bloco representa uma parte da aplicação, e as setas ajudam a mostrar como essas partes se conectam.

### calm — didático, leitura de fluxo e números

Intenção: dê tempo para alguém acompanhar o desenho. Faça pausas leves após
"com calma", "primeiro" e "depois", sem ficar artificialmente lento.

> Vamos olhar esse fluxo com calma. Primeiro, acompanhe a entrada da requisição. Depois, observe cada etapa do processamento e veja em que momento a resposta fica pronta para voltar ao cliente.

### turn — descoberta, limite ou mudança

Intenção: destaque "detalhe importante" e "nesse ponto". Firme, sem teatralizar.

> Mas tem um detalhe importante nessa escolha. Quando o sistema fica sobrecarregado, precisamos entender onde a espera aparece. É nesse ponto que vale olhar de novo para o desenho da aplicação.

### invite — convite, fecho

Intenção: uma pergunta a alguém com quem você está conversando; leve e próximo.
Deixe a pergunta terminar antes de fazer o convite seguinte.

> E no seu projeto, onde você usaria essa ideia? Conta nos comentários qual parte você gostaria de entender melhor. Podemos acompanhar outro exemplo e mostrar o que muda no desenho da aplicação.

Os textos são amostras para gravar, não o roteiro aprovado de um episódio.
O modelo receberá o novo texto da cena para gerar; você não precisa regravar esses
cinco trechos para cada vídeo futuro.

## Inglês opcional

Se quiser gravar também em inglês, mantenha seu sotaque natural e a mesma intenção.
Não é necessário fazer este segundo conjunto antes do primeiro teste em português.
Use os mesmos nomes em `en/`.

| Referência | Texto para gravar |
| --- | --- |
| hook | Have you noticed that a program can work well on its own and run into problems when several requests arrive? Why does that happen? Let's take a closer look at the path each request follows. |
| neutral | In this example, we will follow a request from the moment it arrives until the response is ready. Each box represents part of the application, and the arrows show how those parts connect. |
| calm | Let's follow this flow slowly. First, look at where the request arrives. Then, follow each step of the processing and notice when the response becomes ready to return to the client. |
| turn | But there is an important detail in this choice. When the system is overloaded, we need to understand where the waiting happens. That is where we should look at the application design again. |
| invite | Where would you use this idea in your own project? Tell me in the comments which part you would like to understand better. We can follow another example and see how the application design changes. |

## Como o fluxo usa as referências

Exemplo de configuração já em uso:

```toml
[chatterbox.references."pt-BR"]
hook = "data/voice-references/pt-BR/hook-01.wav"
calm = "data/voice-references/pt-BR/calm-01.wav"
```

Os cinco tons também estão cadastrados para `en`. A cena mantém só `delivery`,
sem caminhos pessoais no roteiro. Uma explicação pausada em inglês, por exemplo:

```json
{"scene": "explicacao", "text": "Let's follow the flow.", "delivery": "calm"}
```

Com `language: "en"` na narração, o gerador escolhe o WAV inglês `calm`.
Sem `delivery`, usa `neutral`. Sem mapeamento para idioma/entrega, usa a referência
global. Se um WAV cadastrado sumir ou for inválido, a cena fica `needs_review`,
com o motivo no manifest; as outras cenas continuam. Não há troca silenciosa de tom.

Os comandos são os mesmos:

```bash
.venv/bin/vp short voz data/episodes/SEU-EPISODIO data/episodes/SEU-EPISODIO/narracao.json
.venv/bin/vp voice SEU-EPISODIO --voz-final
```

No Short, `narracao.voz.json` registra a referência local, o SHA-256 e o nome remoto
em `lines[].reference`; o comando também os imprime. Nos dois formatos,
`manifest.json` guarda a identidade da referência/entrega em `steps.voice.scenes.<id>.detail`.
No banco ativo, o nome do WAV considera os parâmetros efetivos, a gravação, o texto
e a divisão da fala. Trocar uma referência invalida somente as cenas que a usam.

### Nivelamento incorporado à geração

Com o banco de referências ativo, `vp short voz`, `vp voice --voz-final` e a voz de
`vp render --voz-final` também preparam cópias niveladas de cada cena, a aproximadamente
−16 LUFS, com teto de pico −1,5 dBTP. O TTS bruto permanece em `voice/`; as cópias e
seus relatórios ficam em `voice/leveled/` (ADR 054).

O registro do Short aponta `wav` para a cópia nivelada e inclui `level`, com fonte,
hashes, política, volume antes/depois e pico. No longo, `episode.json` também conserva
o caminho real `voice/leveled/...`. `tempos`, legendas e montagem usam essas cópias.
Não escolher o WAV bruto por conta própria após rodar a geração.

O cache do nivelamento considera os bytes do bruto e a política de volume. Repetir
o comando usa as cópias válidas; mudar somente a política refaz o tratamento local,
sem uma nova síntese no Modal. Falha de nivelamento deixa a cena em `needs_review`,
com motivo `voice_level_failed`, preservando o bruto para a retomada. Um áudio sem
fala mensurável é recusado, em vez de amplificar silêncio.

O nivelamento individual não substitui a mistura nem a conferência de áudio final:
efeitos e trilha ainda mudam o resultado. A escuta de cada vídeo continua obrigatória.

### Uso na rotina de vídeo

1. Na pauta e no plano de animação, definir a função e a intenção de cada cena.
2. No `narracao.json` do Short, indicar `language` e `delivery` em cada fala;
   no longo, usar `delivery` nas cenas do `scenes.json`.
3. Rodar `vp short voz` ou `vp voice --voz-final`: escolhe a referência, gera/reutiliza
   o bruto e prepara/reutiliza a cópia nivelada. A rotina `short-diario` chama essa etapa.
4. Usar os caminhos devolvidos pela geração para tempos, legendas e render. No Short,
   seguir com `vp short tempos`, render do kit e `vp short juntar`; no longo,
   `vp render --voz-final` coordena as etapas de montagem.
5. Conferir o áudio final e a prévia antes do gate e da publicação autorizada.

O teste final da integração passou em 1.495 testes (8 desmarcados), Ruff e Mypy.
Na CLI real, as dez falas brutas em cache foram niveladas e reutilizadas sem TTS;
relatório: `renders/teste-referencias-voz/fluxo-nivelado.json`.

## Sincronização privada do Modal

A função remota já escolhe `reference_name` por pedido e confere seu hash.
O cliente atualizado envia esse nome e o hash, sem enviar os bytes de referência
durante a geração. Os arquivos ficam no volume privado `voz-dono-referencia`:

```text
references/pt-BR/hook.wav
references/pt-BR/neutral.wav
references/pt-BR/calm.wav
references/pt-BR/turn.wav
references/pt-BR/invite.wav
references/en/hook.wav
references/en/neutral.wav
references/en/calm.wav
references/en/turn.wav
references/en/invite.wav
```

Para uma referência nova, o dono confere a gravação e envia o WAV correspondente;
por exemplo, na raiz do projeto:

```bash
~/.local/share/uv/tools/modal/bin/modal volume put voz-dono-referencia \
  data/voice-references/pt-BR/hook-01.wav /references/pt-BR/hook.wav
```

O comando sem `--force` não sobrescreve um destino existente. Uma substituição
deliberada precisa atualizar o WAV local e o mesmo destino no volume; versões
divergentes são recusadas pela síntese. O serviço existente atende esse protocolo,
sem trocar de modelo nem redeploy para cadastrar outra gravação.
A rotina diária usa arquivos previamente disponibilizados, sem enviar referências novas.

## Teste real inicial

Os dez WAVs foram enviados aos novos destinos no volume privado, com SHA-256
conferido após o envio; `referencia.wav` permaneceu intacta. Registro privado:
`data/voice-references/modal-sync.json`. O serviço existente atendeu sem redeploy.

O fluxo de produção gerou cinco falas com as novas referências e uma com a referência
antiga em cada idioma, usando a mesma frase. As comparações para escuta estão em
[`renders/teste-referencias-voz/escuta.md`](../renders/teste-referencias-voz/escuta.md),
com um WAV por idioma e os tempos de cada trecho. As amostras usam os parâmetros
de produção de cada entrega; não isolam apenas o efeito do áudio de referência.
A segunda execução de `vp short voz` reutilizou todos os WAVs, sem alterar bytes
ou datas dos arquivos. Os renders publicados foram conferidos por hash e preservados.

A seleção técnica está validada. Depois do nivelamento, o dono aprovou a comparação
em português e inglês na conversa: "Gostei, me parece adequado agora". Registro em
`renders/teste-referencias-voz/nivelamento.verificacao.json`. A aprovação vale para
essas amostras; novas falas e vídeos continuam passando pela escuta de prévia.
O dono identificou volume baixo na versão neutra. Para a comparação de tons, as
12 falas agora também têm cópias niveladas por trecho a aproximadamente −16 LUFS;
usar os links nivelados da página de escuta para evitar confundir volume com intenção.
Essa preparação da comparação preserva os WAVs brutos e não altera o TTS. Depois da
aprovação, o mesmo tratamento foi integrado à geração por cena. A verificação pela
CLI, em português e inglês, está em `renders/teste-referencias-voz/fluxo-nivelado.json`.

## Como avaliar as gravações e as falas geradas

1. Conferir os arquivos e escolher a melhor tomada de cada intenção.
2. Gerar a mesma frase com a referência atual e com duas referências novas,
   mantendo os demais parâmetros iguais para comparar o efeito da gravação.
3. O dono ouve identidade, naturalidade, intenção e pronúncia. Usar outro texto
   além daquele que foi gravado, para avaliar a transferência para uma cena nova.
4. Ajustar o mapeamento `delivery → referência` somente após a comparação, mantendo
   os originais e a referência global disponíveis. Os vídeos aprovados não são regravados
   pelo teste; usar episódios novos para a comparação.
5. Depois da fala escolhida, ajustar as animações à duração real dos WAVs.

O Chatterbox usa `audio_prompt_path` para condicionar a fala, mas isso não garante
que reproduza exatamente a intenção de uma gravação. Na versão fixada neste projeto,
partes do condicionamento usam os primeiros 6 e 10 segundos; por isso a intenção
deve aparecer logo no começo, sem uma longa apresentação neutra.
Fonte: [implementação oficial fixada no deploy, prepare_conditionals](https://github.com/resemble-ai/chatterbox/blob/5de7a54aa4e5e2baadb0182dde554908b48b85c2/src/chatterbox/mtl_tts.py).

Guardar arquivos sem cadastrá-los no TOML não muda a seleção. O pedido do dono de
integrar o fluxo completo cobre a sincronização inicial e a comparação desta sessão.
Pela ADR 024, novos envios continuam sob controle do dono; este guia não autoriza
uploads futuros de gravações pessoais ou substituição da referência global.
