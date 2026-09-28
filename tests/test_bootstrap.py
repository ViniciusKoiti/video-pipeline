from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.bootstrap import (
    DEFAULT_REGISTRY,
    ConfigurationError,
    LazyContext,
    Registration,
    Registry,
    build_context,
)
from app.pipeline.schemas import EpisodeFormat, Provider
from app.providers.errors import PaidApiBlocked
from app.settings import CONFIG_FILE, load_settings
from tests.fakes import REPO_ROOT, FakeArchive, FakeText, make_root

CONFIG = (REPO_ROOT / CONFIG_FILE).read_text()
CASCADE = re.search(r"^archives = \[[^\]]*\]", CONFIG, re.MULTILINE).group(0)  # type: ignore[union-attr]


def config_with(old: str, new: str) -> str:
    assert CONFIG.count(old) == 1
    return CONFIG.replace(old, new)


def registry_with(port: str, entries: dict[str, Registration]) -> Registry:
    return {**DEFAULT_REGISTRY, port: entries}


# --- Configuração -------------------------------------------------------------------------------


def test_defaults_come_from_providers_toml(tmp_path: Path) -> None:
    settings = load_settings(make_root(tmp_path), environ={})
    assert settings.providers.text == "ollama"
    assert settings.providers.render == {"archival_documentary": "ffmpeg", "explainer": "remotion"}
    assert settings.providers.archives[0] == "wikimedia_commons"
    assert settings.ollama.num_thread == 8
    assert (settings.budget.max_api_spend_usd, settings.budget.allow_paid_api) == (0, False)
    assert settings.data_dir == tmp_path / "data"


def test_environment_overrides_dotenv_which_overrides_toml(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    (root / ".env").write_text("OLLAMA_MODEL=qwen3.5:4b\nWORKERS_AI_MODEL='from-dotenv'\n# comentário\n")
    settings = load_settings(root, environ={"WORKERS_AI_MODEL": "from-env", "MAX_CANDIDATES_PER_SCENE": "3"})
    assert settings.ollama.model == "qwen3.5:4b"
    assert settings.workers_ai.model == "from-env"
    assert settings.limits.max_candidates_per_scene == 3


def test_secrets_only_from_environment_and_never_in_repr(tmp_path: Path) -> None:
    settings = load_settings(make_root(tmp_path), environ={"PEXELS_API_KEY": "s3cr3t"})
    assert settings.secrets.pexels_api_key is not None
    assert settings.secrets.pexels_api_key.get_secret_value() == "s3cr3t"
    assert "s3cr3t" not in repr(settings)
    root = make_root(tmp_path / "leak", CONFIG + '\n[secrets]\npexels_api_key = "s3cr3t"\n')
    with pytest.raises(ValueError, match="segredos"):
        load_settings(root, environ={})


# --- Troca de implementação ---------------------------------------------------------------------


def test_switching_implementation_is_one_line_in_the_config(tmp_path: Path) -> None:
    registry = registry_with(
        "text",
        {
            "alpha": Registration(0, lambda settings: FakeText(name="alpha")),
            "beta": Registration(0, lambda settings: FakeText(name="beta")),
        },
    )
    for name in ("alpha", "beta"):
        root = make_root(tmp_path / name, config_with('text = "ollama"', f'text = "{name}"'))
        assert build_context(root, environ={}, registry=registry).text.info.name == name


def test_cascade_follows_config_order(tmp_path: Path) -> None:
    registry = registry_with(
        "archives", {p.value: Registration(0, lambda s, p=p: FakeArchive(p)) for p in Provider}
    )
    root = make_root(tmp_path, config_with(
        CASCADE,
        'archives = ["pexels", "wikimedia_commons"]',
    ))
    context = build_context(root, environ={}, registry=registry)
    assert [a.info.name for a in context.archives] == ["pexels", "wikimedia_commons"]


def test_ports_are_built_lazily_and_once(tmp_path: Path) -> None:
    calls: list[str] = []

    def factory(settings: object) -> FakeText:
        calls.append("built")
        return FakeText(name="alpha")

    root = make_root(tmp_path, config_with('text = "ollama"', 'text = "alpha"'))
    registry = registry_with("text", {"alpha": Registration(0, factory)})
    context = build_context(root, environ={}, registry=registry)
    assert context.settings.providers.text == "alpha" and calls == []
    assert context.text is context.text
    assert calls == ["built"]


def test_unknown_choice_fails_early_with_options(tmp_path: Path) -> None:
    root = make_root(tmp_path, config_with('text = "ollama"', 'text = "gpt"'))
    with pytest.raises(ConfigurationError, match=r"text = 'gpt' não existe \(opções: gemini, groq, ollama\)"):
        build_context(root, environ={})


def test_unimplemented_adapter_points_to_roadmap_step(tmp_path: Path) -> None:
    context = build_context(make_root(tmp_path), environ={})
    with pytest.raises(ConfigurationError, match=r"etapa #24"):
        _ = context.image_gen


def test_pexels_needs_its_key(tmp_path: Path) -> None:
    root = make_root(tmp_path, config_with(CASCADE, 'archives = ["pexels"]'))
    with pytest.raises(ConfigurationError, match="PEXELS_API_KEY ausente"):
        _ = build_context(root, environ={}).archives
    [pexels] = build_context(root, environ={"PEXELS_API_KEY": "s3cr3t"}).archives
    assert pexels.info.name == Provider.PEXELS.value and pexels.info.remote


# --- Custo zero (§2.1) --------------------------------------------------------------------------


def paid_context(tmp_path: Path, environ: dict[str, str]) -> LazyContext:
    paid = Registration(0, lambda s: FakeText(name="paid", usd_per_call=0.01))
    registry = registry_with("text", {"paid": paid})
    root = make_root(tmp_path, config_with('text = "ollama"', 'text = "paid"'))
    return build_context(root, environ=environ, registry=registry)


def test_paid_provider_is_blocked_by_default(tmp_path: Path) -> None:
    with pytest.raises(PaidApiBlocked, match="ALLOW_PAID_API=false"):
        _ = paid_context(tmp_path, environ={}).text


def test_paid_provider_needs_both_flag_and_budget(tmp_path: Path) -> None:
    with pytest.raises(PaidApiBlocked):
        _ = paid_context(tmp_path / "a", environ={"ALLOW_PAID_API": "true"}).text
    allowed = paid_context(tmp_path / "b", environ={"ALLOW_PAID_API": "true", "MAX_API_SPEND_USD": "5"})
    assert allowed.text.info.name == "paid"


# --- Motor por formato (ADR 001) ----------------------------------------------------------------


def test_render_engine_follows_episode_format(tmp_path: Path) -> None:
    context = build_context(make_root(tmp_path), environ={})
    assert context.renderer(EpisodeFormat.ARCHIVAL_DOCUMENTARY).info.name == "ffmpeg"
    assert context.renderer(EpisodeFormat.ARCHIVAL_DOCUMENTARY) is context.renderer("archival_documentary")
    assert context.renderer(EpisodeFormat.EXPLAINER).info.name == "remotion"  # etapa #48


def test_format_without_engine_is_a_clear_error(tmp_path: Path) -> None:
    config = config_with(
        'render = { archival_documentary = "ffmpeg", explainer = "remotion" }',
        'render = { archival_documentary = "ffmpeg" }',
    )
    context = build_context(make_root(tmp_path, config), environ={})
    with pytest.raises(ConfigurationError, match="nenhum motor de render para o formato explainer"):
        context.renderer(EpisodeFormat.EXPLAINER)


def test_documentary_engine_is_mandatory(tmp_path: Path) -> None:
    config = config_with(
        'render = { archival_documentary = "ffmpeg", explainer = "remotion" }',
        'render = { explainer = "remotion" }',
    )
    with pytest.raises(ValueError, match="archival_documentary"):
        load_settings(make_root(tmp_path, config), environ={})
