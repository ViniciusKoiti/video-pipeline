# Ficha de canal de referência

Use quando o dono cita um canal ("ele parece ir bem; isso daria problema?"). A ficha mostra o que o canal faz de
fato e como ele se sustenta. Nenhum vídeo dele entra em ativo do projeto.

## Metadados, sem baixar nada

- **Título e canal:** `https://www.youtube.com/oembed?url=<url do vídeo>&format=json` devolve o título original e
  o canal. Use para confirmar o idioma, porque a busca com `hl=pt` traduz títulos.
- **Lista de vídeos:** a aba `/@canal/videos` (curl simples) traz o `ytInitialData` com título, duração, views e
  idade. A página `/watch` costuma pedir login para robôs, e o `yt-dlp` sem cookies esbarra no mesmo bloqueio.
- **Histórico:** o Social Blade (`/youtube/handle/<handle>`) mostra os últimos 14 dias de inscritos, views, número
  de vídeos e receita estimada. O histórico mensal exige login. Vídeo removido aparece como queda na contagem de
  vídeos ou de views.
- **O que nunca se vê de fora:** reivindicações do Content ID (o vídeo fica no ar e a receita vai para o
  detentor) e strikes (só o dono do canal vê).

## Amostra de 10 minutos, quando os metadados não respondem

1. **Ferramenta.** O `yt-dlp` precisa do componente EJS e do Node para o desafio em JavaScript do YouTube; a
   preparação está em `docs/specs/video-acquisition-adapters.md` ("Preparação e resultado observado"). O ambiente
   em `/tmp` some quando a máquina reinicia.
2. **Cookies, só com consentimento do dono.**
   - **Exportação, feita pelo dono:** em janela anônima, só `youtube.com`, salvo fora do repositório. A janela é
     fechada logo depois, senão os cookies são trocados.
   - **Antes de usar:** confira se o arquivo não está dentro do projeto sem `.gitignore`. Copie só as linhas de
     `youtube.com` e `google.com` para o scratchpad, com `chmod 600`.
   - **Ao conferir:** mostre só o cabeçalho e os domínios, nunca os valores.
3. **Download:**
   ```bash
   yt-dlp --ignore-config --no-plugin-dirs --no-cache-dir --js-runtimes node --no-playlist \
     --cookies <cópia filtrada> --download-sections "*<início_s>-<fim_s>" \
     -f "bv*[height<=480]+ba/b[height<=480]/b" --write-description --write-info-json \
     --write-auto-subs --sub-langs "pt.*,en" -o "trecho.%(ext)s" "<url>"
   ```
4. **Transcrição.** A legenda automática `pt-orig` é a transcrição da narração. Junte as linhas repetidas que a
   legenda automática gera. O Whisper local só entra se não houver legenda.
5. **Quadros.**
   ```bash
   ffmpeg -i trecho.webm \
     -vf "fps=1/5,scale=320:-2,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=14:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=6x5" \
     -frames:v 4 folha-%d.png
   ```
   Isso gera 4 folhas de 30 quadros, que você lê como imagem. Para ampliar um quadro, extraia todos com
   `fps=1/5` em arquivos separados. O arquivo `001` corresponde ao tempo 0, então o quadro do tempo `t` é o de
   número `t/5 + 1`.

## O que anotar

| Item | Como conferir |
|---|---|
| Cena da obra na tela | Fração dos quadros que mostra a obra, e se há algum elemento próprio (moldura, apresentador, gráfico) |
| Espelhamento | Texto escrito na animação (letreiros, onomatopeias) aparece invertido? Amplie os quadros que têm texto |
| Comentário ou enredo | Na transcrição, conte a análise, o contexto e as observações em primeira pessoa contra o enredo recontado |
| Crédito | A descrição cita a obra, o estúdio ou o distribuidor? Há link para assistir legalmente? |
| Cobertura | Duração do vídeo contra a duração da obra (episódios × minutos) |
| Receita visível | Membros, patrocínio, outras plataformas |
| Voz | Fica com o dono: você não ouve o áudio. Uma medição possível, que só é feita se o dono pedir: comparar a voz com vídeos antigos do canal e com controles (outro narrador e um TTS local) usando o `VoiceEncoder` do ambiente do Chatterbox |

Registre a ficha como tabela "Item | O que se viu" no adendo do relatório. Cite o canal pelo nome público, sem
nomes pessoais que apareçam em tags ou metadados.

## Limpeza

Apague o trecho, os quadros, as transcrições e as duas cópias de cookies com um `rm` para cada item. Avise o dono
do que foi apagado. Se o arquivo exportado tinha cookies de outros sites, diga isso a ele.
