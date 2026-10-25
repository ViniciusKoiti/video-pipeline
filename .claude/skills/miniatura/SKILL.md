---
name: miniatura
description: Miniatura do vídeo no padrão do canal de referência do nicho. Personagem de quadro oficial recortado, fundo (cor ou foto do tema), uma palavra larga com o personagem na frente. Use depois do gate 3 e antes do gate 4.
---

# Miniatura: canal de referência → camadas → escolha do dono

A miniatura segue o **canal de referência do nicho**, não o episódio anterior. A primeira miniatura do
`kira-voto-brasil` (olho do Kira + "TERIA VOTO?") repetiu o piloto e foi reprovada. A aprovada saiu de olhar o
Filosofatos (`docs/pesquisa/miniaturas-filosofatos-2026-10-20.md`) e de duas trocas pedidas pelo dono.

Leia primeiro `pauta.md`: o título provisório, a promessa e o conceito da capa são planejados antes do roteiro
(AGENT.MD, fluxo editorial). Aqui se produz a arte a partir desse conceito e do conteúdo efetivamente sustentado
pelas fichas. Se faltarem esses itens ou a promessa tiver mudado, registre a lacuna e prepare a proposta antes
de compor; não registre uma escolha do dono que ele ainda não fez. Reutilize a análise existente do canal quando
ela ainda servir ao recorte, declarando sua data. A coerência do conjunto é revista no gate 4.

Regras de base: CLAUDE.md §2.3 e §6 (licença registrada; quadro da obra só oficial, `Citacao`), a emenda de
citação da ADR 007 (a miniatura com quadro da obra é decisão do dono no gate 4) e a skill `plano-de-imagens` (registro
de ativos, conferência em resolução cheia).

## O que você escreve

- Na pasta `miniatura/` do episódio: as versões (`miniatura-<letra>-<descrição>.jpg` e a prévia `-320.jpg`) e, depois
  da escolha do dono, `miniatura-final.jpg`.
- `assets/<id>.json` de cada foto nova, com `used_in_scenes: []` e "SÓ NA MINIATURA" no `usage_notes`.
- O crédito de cada foto CC-BY em `credits.txt` e `comentario-fixado.txt` (os dois iguais), e a fonte da miniatura na
  linha de tipografia.
- `decisoes-imagens.md` (as escolhas do dono) e, em `publicacao.md`, os pontos do gate 4.

## Método

1. **Olhar o canal de referência.** Use o canal definido na pauta; se faltar, pergunte ao dono. Quando uma análise
   nova for necessária e solicitada, liste os 30 vídeos recentes,
   com as visualizações, e monte folhas das miniaturas (a página do canal e as miniaturas em `i.ytimg.com` são
   públicas). É acesso externo: só com pedido do dono na sessão.
   - **O que anotar:** quantos personagens, tipo de fundo por tema, texto (quantas palavras, fonte, posição) e
     tratamento (cor, cinza, linhas).
   - **Registro:** escreva a análise em `docs/pesquisa/miniaturas-<canal>-<data>.md`. Não guarde as miniaturas de
     terceiros no Git.
   - **Ressalva:** visualização depende também do tema, do título e da idade do vídeo. A amostra mostra o padrão,
     não prova qual miniatura rende mais.
2. **Escolher o personagem.** Só quadro oficial já registrado como `Citacao`.
   - **Bom de recortar:** personagem claro, separado do fundo, de busto ou meio corpo.
   - **Ruim de recortar:** silhueta escura contra luz (o Ryuk da janela sumiu no recorte) e close sem corpo.
   - **Quadro novo:** se nenhum quadro registrado servir, buscar outro é a busca da `plano-de-imagens`, com os cookies e
     o consentimento do dono.
3. **Recortar.** Rode `recortar.py` (abaixo) e abra a `-conferencia.jpg`, a figura sobre verde.
   - **Resto de outro personagem grudado:** use `--apagar-escuro` no retângulo onde ele está.
   - **Nunca corte o recorte num retângulo:** corta o braço. O script já guarda só a maior figura.
4. **Escolher o fundo** pelo tema, como o canal de referência faz.
   - **Vermelho chapado com vinheta:** política, poder, temas pesados (o Filosofatos usa em voto, fascismo e
     Maquiavel).
   - **Foto real do tema** (a urna, no `kira-voto-brasil`): a cascata de acervo da §8. Prefira **CC-BY de órgão
     público**, como Agência Brasil (CC-BY 3.0 BR) e Agência Senado (CC-BY 2.0). Public Domain Mark não está na lista
     fechada: pare e pergunte.
   - **Conferência:** confira a foto em resolução cheia e registre tudo o que aparece (pessoas, brasão, texto da
     tela, marcas).
   - **Paisagem real:** temas de vida e sentimento.
5. **Compor** com `compor.py`. Faça de duas a quatro versões que mudem uma coisa só de cada vez: com e sem texto,
   personagem maior ou menor, cinza ou colorido.
   - **Texto:** uma palavra (no máximo duas) que completa o título, como "JUSTIÇA", ou a pergunta do título em duas
     palavras, como "TERIA VOTOS?".
   - **Fonte:** Inter Display Black (OFL, já instalada), esticada na horizontal.
   - **O personagem fica na frente da palavra**, e o contorno da palavra volta por cima dele.
6. **Conferir em 320 px**, o tamanho da lista do YouTube.
   - **Leitura:** a palavra precisa ser lida e o objeto do tema reconhecido. Na urna, o teclado com "CONFIRMA".
   - **Recorte:** nenhum resto de recorte.
7. **Levar ao dono** numa pergunta só: as versões com caminho, a recomendação, e o comando do gate 3 para a foto nova
   (`vp approve <id> --step assets --asset <asset-id>`). Os gates são do dono.
8. Depois da escolha, copie para `miniatura-final.jpg` e registre a decisão.

## O que já deu errado

| Erro | Como evitar |
|---|---|
| Miniatura copiada do episódio anterior (olho do Kira + texto), reprovada | começar pelo canal de referência (passo 1) |
| `chromakey` do ffmpeg na cortina apagou o personagem junto | recorte com o modelo de anime (`recortar.py`) |
| Ryuk em silhueta escura: o modelo perdeu o corpo | escolher quadro claro, com o personagem separado do fundo |
| O modelo de anime não recortou uma foto (caderno) | objeto de foto: recorte por cor, ou outro quadro |
| Corte reto no braço do Light por recortar a imagem num retângulo | limpar por figura (`--apagar-escuro`), sem retângulo |
| Fonte espremida (escala horizontal menor que a vertical) | esticar na horizontal (`--esticar 1.25`) |
| Contorno branco sumiu sobre a camisa branca | palavra atrás do cabelo escuro (texto no topo) |
| Urna grande demais, o Light cobrindo o teclado: parecia um monitor | o que identifica o objeto fica à vista |
| Letra branca sobre o topo claro da urna | faixa escura e sombra na letra (`compor.py` faz isso com `--foto`) |
| Foto do TSE com Public Domain Mark: tipo fora da lista fechada, EXIF com copyright do fotógrafo | foto CC-BY de órgão público; na dúvida, perguntar |
| Tela da urna com "Presidente" a quatro dias do segundo turno | o personagem cobre o cargo; nunca alterar a urna nem pôr nome, número ou partido; anotar em `publicacao.md` |

## Ferramentas desta pasta

Os dois scripts rodam no ambiente do rembg, fora do projeto, com `python -I`.

- `recortar.py <quadro> <saida.png> [--apagar-escuro X0,Y0,X1,Y1]`: tira o fundo com o modelo `isnet-anime`, guarda só
  a maior figura e grava a conferência sobre verde.
- `compor.py <recorte.png> <saida.jpg> [--cor | --foto …] [--altura --x --cinza] [--texto --onde --esticar]`: monta as
  camadas e grava a prévia em 320 px. As opções estão no topo do arquivo.

**Ambiente (uma vez por máquina).** O rembg (MIT) e o modelo de anime (SkyTNT, Apache-2.0) ficam fora do projeto,
porque não são dependência do pipeline:

```
uv venv -p 3.12 ~/.local/share/rembg-env
VIRTUAL_ENV=~/.local/share/rembg-env uv pip install "rembg[cpu]" "lazy_loader==0.4" "pooch==1.8.2"
mkdir -p ~/.u2net && curl -L -o ~/.u2net/isnet-anime.onnx https://huggingface.co/skytnt/anime-seg/resolve/main/isnetis.onnx
md5sum ~/.u2net/isnet-anime.onnx   # 6f184e756bb3bd901c8849220a83e38e, o mesmo que o rembg espera
```

- **Versões fixas:** `lazy_loader` e `pooch` mais novos não instalam com o `uv` atual ("Metadata field Name not
  found").
- **Modelo pelo Hugging Face:** o download do GitHub, que o rembg tenta sozinho, não respondia nesta rede.
- **Custo:** um recorte leva ~13 s e usa ~1,8 GB de memória.

**Depois:** a peça `Miniatura` no motion-kit (Remotion, quadro parado) substitui o `compor.py`. Fica para um PR
próprio, com as questões em aberto levadas ao dono antes.
