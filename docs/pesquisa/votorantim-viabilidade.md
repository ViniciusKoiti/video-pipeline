# Viabilidade: família Ermírio de Moraes / Grupo Votorantim (2026-09-26)

Checagem antes da fatia vertical no formato explicativo ("dinheiro e poder", referência: How Money Works).
Nenhum fato daqui entra em roteiro sem passar pelo `vp sources` e pelo gate 1.

## Fontes encontradas

| Fonte | Tipo | Independência | Acesso |
|---|---|---|---|
| [CPDOC/FGV — verbete José Ermírio de Morais](https://www18.fgv.br/cpdoc/acervo/dicionarios/verbete-biografico/jose-ermirio-de-morais) | Dicionário histórico-biográfico (acadêmico) | Independente | Aberto |
| [CPDOC/FGV — verbete Antônio Ermírio de Morais](https://www18.fgv.br/cpdoc/acervo/dicionarios/verbete-biografico/morais-antonio-ermirio-de) | Acadêmico | Independente | Aberto |
| [A formação do Grupo Votorantim (1891–1929) — SciELO](http://www.scielo.br/j/ecos/a/mdgbqQ3sy8bdNyKQnWpYXhj/?lang=pt) | Artigo revisado por pares | Independente | Aberto |
| [Da fábrica sorocabana ao conglomerado nacional (1891–1980) — Redalyc](https://www.redalyc.org/journal/5798/579865865011/html/) | Artigo revisado por pares | Independente | Aberto |
| [Senado Federal — perfil do senador](https://www25.senado.leg.br/web/senadores/senador/-/perfil/1917) | Oficial | Independente | Aberto |
| [Pioneiros & Empreendedores — FEA-USP](https://pioneiros.fea.usp.br/jose-ermirio-de-moraes/) | Acadêmico (divulgação) | Independente | Aberto |
| [Memória Votorantim](https://memoriavotorantim.com/historias/familia/150-anos-de-antonio-pereira-ignacio/) e [Votorantim 100 anos](https://www.votorantim100.com/) | Primária da empresa | **Interessada**: cruzar com as independentes | Aberto |
| [Jornal Cruzeiro (Sorocaba)](https://www.jornalcruzeiro.com.br/economia/grupo-votorantim-que-nasceu-e-se-expandiu-na-regiao-faz-100-anos/) | Imprensa regional | Independente | Aberto |
| Hemeroteca Digital (Biblioteca Nacional) | Jornais de época | Independente | A pesquisar |

Conclusão: **passa com folga** no mínimo de 2 fontes independentes para os fatos principais, ao menos até ~1980.

## Imagens (Wikimedia Commons)

| Imagem | Licença | Situação |
|---|---|---|
| `José Ermírio de Moraes.tiff` (Arquivo Nacional, fundo Agência Nacional, 1970) | Domínio público (`Arquivo Nacional PD-license\|Gov`) | **Conferir no gate 3**: a descrição original diz "João Ermiro de Morais" |
| `Antônio Ermírio de Morais.jpg` (Antônio Cruz/Agência Brasil, 2003) | CC BY 3.0 BR | **Decisão pendente**: a variante brasileira não está na lista fechada da ADR 007 |
| Funeral de Antônio Ermírio, 2014 (Ascom Vice-Presidência) | CC BY 2.0 | Aceita |
| Hotel Esplanada, 1923 (hoje Edifício Ermírio de Moraes) | Domínio público | Aceita |
| Fábricas de cimento na Bahia, 2009 (governo da BA) | CC BY 2.0 | Aceita |
| Fábricas recentes da Votorantim | CC BY-SA | **Fora** (ADR 007) |
| Fábrica de Tecidos Votorantim (1910–1920), Antônio Pereira Ignácio | — | **Não encontradas.** Procurar na Brasiliana Fotográfica e no Arquivo Público de SP (o Museu da Pessoa é CC BY-SA, fora) |

Conclusão: **fraco para um documentário de fotos, suficiente para o formato explicativo**, que se apoia em
gráficos, mapas, linha do tempo, árvore da família e cartões tipográficos.

## Cobertura no YouTube (visualizações não obtidas)

- [Antônio Ermírio de Moraes: A Vida do Capitão da Votorantim](https://www.youtube.com/watch?v=GczRkWwPxMk) (jul/2025)
- [Como Antônio Ermírio de Moraes transformou a Votorantim num símbolo de sucesso no Brasil](https://www.youtube.com/watch?v=MHM0Xk3Vq1U) (mai/2025)
- [A história de José Ermírio de Moraes](https://www.youtube.com/watch?v=yRm5FHiP8N4)
- [The story of Antônio Ermírio de Moraes (Short, em inglês)](https://www.youtube.com/shorts/M9EuzQTCZIk)
- Roda Viva com Antônio Ermírio ([1988](https://www.youtube.com/watch?v=bZcLCu6xd68), [1991](https://www.youtube.com/watch?v=nFAjgf0vLbw))

O tema existe e é consumido, **centrado numa pessoa (Antônio Ermírio)**. Diferencial possível: contar a
**dinastia** (1918 → quinta geração) pela ótica do dinheiro e do poder, com dados e gráficos, e com fontes
acadêmicas citadas na tela.

## Riscos

- **Membros vivos** (quarta e quinta gerações) e uma empresa ativa: só fatos empresariais e públicos, com
  documento; nada de vida privada; revisão jurídica antes de publicar trechos sobre pessoas vivas.
- **Fontes da empresa** contam a própria história: nenhum fato só com elas.

## Decisões pendentes

1. **Idioma.** Amostras em `data/benchmarks/voz-pt/` (fora do Git): `pf_dora`, `pm_alex`, `pm_santa` (português)
   e `am_michael` (inglês, a voz já aprovada), com o mesmo parágrafo.
2. **CC BY 3.0 BR** na lista de licenças aceitas (mesmos termos do CC BY 3.0, com atribuição).
3. **Recorte da fatia vertical.** Proposta: 1918–1926, "como uma massa falida virou a semente de um império".
   É o trecho mais bem documentado pelas fontes acadêmicas, tem menos risco com pessoas vivas e cabe em 60–90 s.
4. **Antecipar a etapa #43** (Remotion + motion-kit no `main`) e a lista de planos (ADR 007 v2) para esta fatia.
