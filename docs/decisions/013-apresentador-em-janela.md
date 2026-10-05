# 013 — Apresentador em janela flutuante no formato explicativo

- **Status:** aceito (2026-10-05, depois de o dono rever o render de teste `votorantim-apresentador`)
- **Data:** 2026-10-05
- **Etapa do roadmap:** frente do apresentador (derivada do #48); B1 de duas etapas, o 9:16 fica para o B2
- **Relaciona-se com:** ADR 001 (motor por formato), ADR 007 (contratos), ADR 008 (planos), ADR 011 (planos
  editoriais), ADR 012 (voz); motion-kit `<FloatingWindow>` e `<Host>` (pin `527c708`)

## Contexto

Em teste (2026-10-05) o dono viu o explicativo com um personagem narrando numa janelinha que muda de canto a cada
cena, por cima dos planos do template, e aprovou a direção. O protótipo era uma composição avulsa sobre o vídeo
pronto. Para virar parte do pipeline, o apresentador precisa existir no contrato (`episode.json` só muda com ADR,
CLAUDE.md §6), no motor e no template, sem mexer nos episódios que não o usam, em especial o vídeo-régua.

## Opções consideradas

1. **Composição avulsa sobre o vídeo renderizado** (o protótipo). Rápido, mas fora do contrato: o personagem não
   segue a regra de cantos do template, não entra no cache por cena e não é reproduzível pelo `vp`.
2. **Camada `host` no contrato e na cena do template** (escolhida). A janela é renderizada junto com cada cena;
   o motor entrega o canto e o envelope da boca como props.
3. **Personagem como plano da lista de planos** (ADR 008). Um plano cobre um trecho da narração e tem âncora;
   o apresentador atravessa a cena inteira e as cenas seguintes, então não é um plano.
4. **Janela do `<FloatingWindow>` contínua pelo vídeo, renderizada fora das cenas.** Permitiria arrastar a janela
   sobre o corte, mas quebra o cache por cena (a janela dependeria de todas) e o motor renderiza uma cena por vez.

## Decisão

- **Contrato (campos opcionais, sem mudar `schema_version`).** `scenes.json` e `episode.json` ganham `host`:
  `HostSpec { skin: "notionists", identity: HostIdentity, width: 0.1–0.4 (padrão 0,16) }`, com
  `HostIdentity { hair, outfit, eyes = variant05, brows?, nose?, facial_hair?, glasses? }` (nomes de peça do
  Notionists: `variantNN` ou `hat`). Cada cena aceita `host_corner` (`top-left`, `top-right`, `bottom-right`,
  `bottom-left`) como ajuste. Sem `host`, nada muda. No `episode.json`, `host` só vale no formato `explainer`.
- **Canto por regra.** `app/media/host.py` escolhe o canto de cada cena pelo que o template ocupa: a fonte do
  plano em cima à direita (tela cheia) ou embaixo à direita (sobre foto ou B-roll), a tarja e o painel do número
  embaixo à esquerda, o título do gráfico em cima à esquerda e os rótulos da comparação embaixo. A janela segue
  em sentido horário, pulando cantos ocupados; sem outro canto livre, fica onde estava. `host_corner` da cena
  vale como está. Mudou o template, muda a tabela.
- **Boca pelo áudio.** O motor lê o WAV da cena (`app/media/envelope.py`) e passa o envelope RMS, um valor por
  quadro, normalizado pelo percentil 95 da cena. O envelope é derivado, não faz parte do contrato.
- **Render.** `video/src/HostWindow.tsx` usa `<FloatingWindow>` e `<Host>` do motion-kit, em busto, com
  `gesticulate`. A janela vem do canto da cena anterior (`fromCorner`) e é arrastada ao da cena nos primeiros 26
  quadros; o arrasto não cruza o corte, porque cada cena é um render. A janela fica fora da camada de fade das
  cenas, então não some nas bordas. As props `host` só existem quando o episódio tem apresentador: sem ele, as
  props e a chave de cache de cada cena ficam como estavam.
- **Licença e dependências.** O desenho do Notionists é CC0 1.0 (Zoish) e o código do DiceBear é MIT (regra 3 e
  lista fechada da ADR 007). Entram em `video/package.json`, exatas: `@dicebear/core` e `@dicebear/collection`
  9.4.3 (MIT). A coleção instala os outros estilos (13 em CC-BY-4.0, 4 com licença própria), que o template nunca
  renderiza: usar um deles exige atribuição e nova conferência. O personagem é ilustração estilizada, não imagem
  realista de fato histórico (regra 4), e não é fonte de nada: a narração continua vindo das fichas.
- **Fora desta ADR:** perfil vertical 9:16 (B2, outra ADR: o template inteiro assume paisagem), selo ou ícone de
  profissão, gestos e olhar agendados por cena, outras peles, e validar nomes de peça contra o schema do
  Notionists no `vp check`.

## Consequências

- `app/pipeline/schemas.py` (`HostSpec`, `HostIdentity`, `host` e `host_corner`), `app/media/host.py` e
  `app/media/envelope.py` (novos), `app/render/remotion.py` (props), `video/src/HostWindow.tsx`, `Scene.tsx` e
  `types.ts`, `scripts/provisorio/montar_episodio.py` (repassa `host` de `scenes.json`). `tests/test_host.py`.
- Qualquer mudança em `video/src/*.tsx` muda o `template_hash`: o primeiro render depois do merge refaz todas as
  cenas. O vídeo-régua fica sem `host`, então seu visual não muda; a folha de quadros da próxima versão confirma.
- A regra dos cantos duplica conhecimento do template (onde ficam fonte, tarja e título). Os dois mudam juntos.
- O teste visual vive numa cópia local da régua (`data/episodes/votorantim-apresentador`, fora do Git); a régua e
  os arquivos `approved` seguem intactos.
