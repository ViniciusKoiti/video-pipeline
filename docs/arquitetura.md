# Arquitetura: portas e adaptadores

Decisão e motivos em [ADR 006](decisions/006-arquitetura-portas-adaptadores.md). As setas indicam
"importa". As regras são verificadas por `tests/test_architecture.py`.

```mermaid
flowchart TD
    CLI["app/cli.py<br/>vp (argparse)"] --> BOOT["app/bootstrap.py<br/>raiz de composição"]
    CLI --> PIPE
    BOOT --> SET["app/settings.py<br/>providers.toml + .env"]
    BOOT --> ADAPT
    BOOT --> PORTS

    subgraph PIPE["app/pipeline/ — etapas"]
        STEPS["etapas (sources, script, voice, ...)"] --> PPORTS["ports.py<br/>Context, ManifestStore, ReviewGate"]
        STEPS --> FAIL["failures.py<br/>erro para a cena"]
        STEPS --> SCH["schemas.py<br/>contratos §6"]
    end

    subgraph PORTS["portas (Protocols)"]
        TB["providers/text/base.py<br/>TextProvider"]
        SB["providers/tts/base.py<br/>TTSProvider"]
        IB["providers/image_gen/base.py<br/>ImageGenProvider"]
        AB["providers/archives/base.py<br/>ArchiveProvider"]
        LB["providers/alignment/base.py<br/>SubtitleAligner"]
        RB["render/base.py<br/>RenderEngine"]
        ERR["providers/errors.py"]
    end

    subgraph ADAPT["adapters concretos (ollama e kokoro desde a etapa 5)"]
        OLL["text/ollama.py"]
        KOK["tts/kokoro.py"]
        WAI["image_gen/workers_ai.py"]
        COM["archives/commons.py ..."]
        FFM["render/ffmpeg.py"]
    end

    PPORTS --> PORTS
    ADAPT --> PORTS
    ADAPT --> SCH
```

## Regras

| Módulo | Pode importar | Não pode importar |
|---|---|---|
| `app/pipeline/**` | `schemas`, `ports`, `app.settings`, módulos `base` e `errors` | adapters concretos, `app.bootstrap`, `app.cli`, bibliotecas pesadas (torch, kokoro…) |
| `app/providers/**`, `app/render/**` | `app.pipeline.schemas`, outras portas | resto de `app.pipeline`, `app.settings`, `app.bootstrap`, `app.cli` |
| `app/bootstrap.py` | tudo; é o único que conhece adapters concretos | — |

## Como trocar de abordagem

1. Escrever o adapter em `app/providers/<função>/<nome>.py` (ou `app/render/<nome>.py`) implementando a porta.
2. Registrar em `DEFAULT_REGISTRY` (`app/bootstrap.py`) com a fábrica, que importa o adapter dentro da função.
3. Acrescentar o adapter à lista da porta em `tests/test_contracts.py` e fazê-lo passar.
4. Mudar uma linha em `config/providers.toml`.
