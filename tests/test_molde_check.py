"""Molde do nicho no `vp check` (ADR 031, partes C e D): leitura da cópia e alertas de forma. Dados
sintéticos."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.pipeline.check import check_episode
from app.pipeline.molde import (
    MOLDE_FILE,
    Molde,
    claimless_statements,
    molde_summary,
    molde_warnings,
)
from app.pipeline.schemas import ScenesManifest
from app.storage.json_files import JsonFileStore

CPS = 14.0
V1 = {"visual_need": "contextual_stock", "search_query": "papel"}
PHOTO = {"kind": "photo", "visual_need": "contextual_stock", "search_query": "papel", "asset_id": None}
CLAIM = {"text": "a frase tem fonte", "source_ids": ["source-01"]}
# ~10 s por cena a 14 caracteres por segundo
FILLER = "Uma frase comprida de narração que serve para encher o tempo do roteiro e seguir a conversa."
FILLER_B = "Outro trecho de fala sem nenhum dado, só para o relógio andar até o fim do vídeo de teste."
OPENING = "A caixa da minha avó ficou no corredor durante vinte anos inteiros, sem ninguém abrir."
CLOSING = "O navio trocou todas as tábuas e ninguém no porto soube dizer se era o mesmo barco."
PROPER = "Em 2006 o anime estreou no Japão e durou trinta e sete episódios na televisão."


def medida(mediana: float, q1: float | None = None, q3: float | None = None, n: int = 13) -> dict[str, Any]:
    item: dict[str, Any] = {"mediana": mediana, "n": n, "origem": "teste"}
    if q1 is not None:
        item["q1"], item["q3"] = q1, q3
    return item


def traco(com: int, n: int = 13, forca: str = "padrao") -> dict[str, Any]:
    return {"com": com, "n": n, "pct": round(100 * com / n), "forca": forca, "unidade": "videos"}


def molde(**changes: Any) -> Molde:
    raw: dict[str, Any] = {
        "gerado_em": "2026-10-22", "grupos": ["FILO"], "assunto": None,
        "videos": {"n": 13, "ids": [], "com_batidas": 13, "canais": {"@canal": 13}},
        "medidas": {
            "cortes_60s": medida(2.0, 0.5, 27.0),
            "voce_por_mil": medida(7.9, 4.8, 13.7),
        },
        "prevalencia": {"confissao": traco(11), "fecho_volta": traco(11)},
        "curvas": {
            "decimos": 10, "n_videos": 13,
            "cortes_min": [0.8, 3.1, 1.6, 2.8, 2.0, 1.5, 2.0, 1.0, 2.5, 6.0],
            "voce_por_10min": [20, 24, 14, 10, 15, 16, 15, 15, 10, 23],
            "eu_por_10min": [15, 16, 15, 10, 5, 16, 15, 5, 24, 40],
        },
        "campo_novo_da_skill": {"qualquer": 1},
        **changes,
    }
    return Molde.model_validate(raw)


def scenes(
    *narrations: str, language: str = "pt-BR", claims: bool = False, title: str | None = None
) -> ScenesManifest:
    extra = {"claims": [CLAIM]} if claims else {}
    raw = [
        {"id": f"S{i:02d}", "narration": text, **V1, **extra} for i, text in enumerate(narrations, start=1)
    ]
    manifest: dict[str, Any] = {"episode_id": "ep", "language": language, "scenes": raw}
    if title is not None:
        manifest["title"] = title
    return ScenesManifest.model_validate(manifest)


def long_script(n: int = 24, first: str = OPENING, last: str = CLOSING) -> ScenesManifest:
    """~3 min a 14 caracteres por segundo, sem "você" nem "eu"; o primeiro e o último minuto não repetem
    nenhuma expressão (enchimento diferente em cada metade)."""
    half = n // 2 - 1
    return scenes(first, *[FILLER] * half, *[FILLER_B] * (n - 2 - half), last)


def test_molde_is_read_by_its_contract_and_summarised() -> None:
    read = molde(episodio={"duracao_min": 12, "assunto": "obra", "blocos": 2})
    assert read.padrao("confissao") is not None and read.padrao("gancho_pago") is None
    assert read.curva("eu_por_10min")[9] == 40 and read.curva("inexistente") == []
    assert molde_summary(read) == (
        "molde.json: 13 vídeo(s) de FILO, 13 com batidas, gerado em 2026-10-22; partitura: 12 min, 2 bloco(s)"
    )


def test_duration_is_checked_against_the_partitura() -> None:
    short = molde(episodio={"duracao_min": 12})
    warnings = molde_warnings(long_script(), short, CPS)
    assert any("duração estimada ~2." in w and "a partitura pede 12 min" in w for w in warnings)
    fits = molde(episodio={"duracao_min": 3})
    assert not any("duração" in w for w in molde_warnings(long_script(), fits, CPS))
    assert not any("duração" in w for w in molde_warnings(long_script(), molde(), CPS))


def test_cuts_in_the_opening_and_after_it() -> None:
    words = FILLER.split()
    anchors = [" ".join(words[i : i + 2]) for i in range(0, 16, 2)]  # 8 fotos numa cena de ~10 s
    busy = {"id": "S01", "narration": FILLER, "shots": [{**PHOTO, "anchor": a} for a in anchors]}
    calm = [{"id": f"S{i:02d}", "narration": FILLER, **V1} for i in range(2, 25)]
    manifest = ScenesManifest.model_validate(
        {"episode_id": "ep", "language": "pt-BR", "scenes": [busy, *calm]}
    )
    warnings = molde_warnings(manifest, molde(), CPS)
    assert not any("abertura com" in w for w in warnings)  # as fotos do 1º minuto cabem no q3 do molde (27)
    tight = molde(medidas={"cortes_60s": medida(2.0, 0.5, 4.0)})
    (opening,) = [w for w in molde_warnings(manifest, tight, CPS) if "abertura com" in w]
    assert "planos nos primeiros 60 s; o molde corta entre 0.5 e 4" in opening

    fast = [
        {"id": f"S{i:02d}", "narration": FILLER, "shots": [{**PHOTO, "anchor": a} for a in anchors[:4]]}
        for i in range(1, 25)
    ]
    manifest = ScenesManifest.model_validate({"episode_id": "ep", "language": "pt-BR", "scenes": fast})
    (body,) = [w for w in molde_warnings(manifest, molde(), CPS) if "planos por minuto depois" in w]
    assert "o molde troca de imagem 2 vez(es) por minuto" in body
    slow = scenes(*[" ".join([FILLER] * 3)] * 8)  # uma foto a cada ~20 s: dentro do dobro do molde
    assert not any("planos por minuto" in w for w in molde_warnings(slow, molde(), CPS))


def test_viewer_address_per_thousand_words_outside_the_molde_range() -> None:
    (warning,) = [w for w in molde_warnings(long_script(), molde(), CPS) if "por mil palavras" in w]
    assert '"você" 0.0 por mil palavras; o molde fica entre 4.8 e 13.7' in warning
    too_much = scenes(*["Você já parou para pensar nisso hoje, você mesmo?"] * 12)
    assert any("por mil palavras; o molde fica entre" in w for w in molde_warnings(too_much, molde(), CPS))
    in_range = scenes(
        "Você sabe o que é isso e você mesmo lembra quando viu uma caixa no corredor pela primeira vez?",
        *[FILLER] * 11,
    )
    assert not any("por mil palavras" in w for w in molde_warnings(in_range, molde(), CPS))


def test_title_length_is_compared_with_the_molde_quartiles() -> None:
    sized = molde(medidas={"titulo_video_chars": medida(71.0, 61.5, 80.5)})
    short = scenes(OPENING, *[FILLER] * 11, title="E se o Light tivesse ganhado?")
    (warning,) = [w for w in molde_warnings(short, sized, CPS) if "título com" in w]
    assert "título com 29 caracteres; o molde fica entre 61.5 e 80.5 caracteres (mediana 71, n 13)" in warning
    long_title = "O Que Não Está na Sua Mão | Epicteto e a única coisa que você controla"  # 70 caracteres
    fits = scenes(OPENING, *[FILLER] * 11, title=long_title)
    assert not any("título" in w for w in molde_warnings(fits, sized, CPS))
    # molde antigo, sem a medida: o título não gera alerta nenhum
    assert not any("título" in w for w in molde_warnings(short, molde(), CPS))
    # sem title, mas com a medida no molde: um aviso de que falta o que comparar
    (missing,) = [w for w in molde_warnings(scenes(OPENING, FILLER), sized, CPS) if "sem title" in w]
    assert "scenes.json sem title; o molde mede o título do vídeo" in missing
    assert not any("title" in w for w in molde_warnings(scenes(OPENING, FILLER), molde(), CPS))


def test_title_subject_must_be_said_before_the_molde_q3() -> None:
    said = molde(
        medidas={"titulo_video_dito_s": medida(40.0, 9.0, 82.0, n=36)},
        prevalencia={"titulo_video_dito": traco(36, 40)},
    )
    # "caixa" está na primeira frase: 1 de 3 palavras de conteúdo basta
    early = scenes(OPENING, *[FILLER] * 11, title="O navio de Teseu e a caixa da avó")
    assert not any("assunto do título" in w for w in molde_warnings(early, said, CPS))
    # "navio" só na última cena, depois de ~20 cenas de ~6 s: passa do q3 de 82 s
    late = scenes(*[FILLER] * 20, CLOSING, title="O navio de Teseu")
    (warning,) = [w for w in molde_warnings(late, said, CPS) if "assunto do título" in w]
    assert "a fala só diz o assunto do título aos ~1" in warning
    assert "o molde diz entre 9 e 82 s (mediana 40, n 36)" in warning
    # nunca dito: o aviso traz as palavras procuradas e a prevalência do molde
    never = scenes(*[FILLER] * 5, title="Epicteto e a liberdade")
    (warning,) = [w for w in molde_warnings(never, said, CPS) if "assunto do título" in w]
    assert "nunca diz o assunto do título (epicteto, liberdade); o molde diz em 36 de 40 vídeos" in warning
    # título só de palavras de função: não há assunto a procurar
    only_function_words = never.model_copy(update={"title": "Como ouvir"})
    assert not any("assunto do título" in w for w in molde_warnings(only_function_words, said, CPS))


def test_closing_rise_of_you_and_i_is_checked_in_the_last_tenth() -> None:
    opening_only = long_script(first="Eu abri a caixa e você sabe o que eu vi ali dentro naquele dia.")
    warnings = molde_warnings(opening_only, molde(), CPS)
    assert any('sobe "você" no fecho (23 por 10 min contra 15 no corpo)' in w for w in warnings)
    assert any('sobe "eu" no fecho (40 por 10 min contra 15 no corpo)' in w for w in warnings)
    closing_too = long_script(
        first="Eu abri a caixa e você sabe o que eu vi ali dentro naquele dia.",
        last="E você, eu pergunto: eu fecharia a caixa de novo, e você fecharia também?",
    )
    assert not any("no fecho" in w for w in molde_warnings(closing_too, molde(), CPS))
    flat = molde(curvas={"decimos": 10, "voce_por_10min": [15] * 10, "eu_por_10min": [15] * 10})
    assert not any("no fecho" in w for w in molde_warnings(opening_only, flat, CPS))


def test_confession_and_closing_return_only_when_the_molde_holds_them_as_pattern() -> None:
    plain = long_script()
    warnings = molde_warnings(plain, molde(), CPS)
    assert any("confissão do narrador em 11 de 13 vídeos" in w for w in warnings)
    assert any("o fim retoma a abertura em 11 de 13 vídeos" in w for w in warnings)

    confessed = long_script(first="Eu confesso que escrevi este roteiro três vezes antes de acertar.")
    assert not any("confissão" in w for w in molde_warnings(confessed, molde(), CPS))
    returns = long_script(
        first="A caixa da minha avó ficou no corredor durante vinte anos inteiros.",
        last="No fim, a caixa da minha avó continua no corredor, vinte anos depois.",
    )
    assert not any("retoma a abertura" in w for w in molde_warnings(returns, molde(), CPS))

    weak = molde(
        prevalencia={"confissao": traco(5, forca="indicio"), "fecho_volta": traco(6, forca="indicio")}
    )
    assert not any("confissão" in w or "retoma" in w for w in molde_warnings(plain, weak, CPS))


def test_small_sample_is_labelled_and_english_is_skipped() -> None:
    small = molde(videos={"n": 5, "com_batidas": 5})
    warnings = molde_warnings(long_script(), small, CPS)
    assert warnings and all(w.startswith("molde (5 vídeos, só descrição):") for w in warnings)
    english = scenes(*["A long English sentence that says nothing in particular."] * 24, language="en")
    assert molde_warnings(english, molde(), CPS) == []


def test_claimless_statements_need_a_number_or_a_proper_noun() -> None:
    manifest = scenes(
        "Quando Light achou o caderno, ele tinha dezessete anos e morava em Tóquio.",  # nome próprio
        "Em 2006 o anime estreou no Japão e durou trinta e sete episódios.",  # número
        "Você faria o mesmo no lugar dele?",  # pergunta
        "Eu acho que Light errou desde o primeiro dia.",  # primeira pessoa
        "Mas antes, uma pergunta.",  # curta
        "O medo muda o caminho de casa e a hora de voltar para quem mora longe.",  # sem número nem nome
    )
    warnings = claimless_statements(manifest)
    assert [w.split(":")[0] for w in warnings] == ["S01", "S02"]
    assert "frase afirmativa em cena sem claims: 'Quando Light achou" in warnings[0]
    assert claimless_statements(scenes(PROPER, claims=True)) == []


def write_episode(root: Path, molde_raw: dict[str, Any] | None, manifest: ScenesManifest) -> JsonFileStore:
    folder = root / "ep"
    folder.mkdir(parents=True)
    (folder / "scenes.json").write_text(manifest.model_dump_json())
    if molde_raw is not None:
        (folder / MOLDE_FILE).write_text(json.dumps(molde_raw))
    return JsonFileStore(root)


def test_vp_check_reads_the_episode_molde_and_only_warns(tmp_path: Path) -> None:
    raw = json.loads(molde(episodio={"duracao_min": 12, "blocos": 2}).model_dump_json())
    report = check_episode(write_episode(tmp_path, raw, long_script()), "ep", chars_per_second=CPS)
    assert report.ok  # forma nunca é erro
    assert any(line.startswith("molde.json: 13 vídeo(s) de FILO") for line in report.checked)
    assert any(w.startswith("molde: duração estimada") for w in report.warnings)
    assert any("confissão do narrador" in w for w in report.warnings)


def test_vp_check_without_molde_keeps_the_general_claimless_alert(tmp_path: Path) -> None:
    report = check_episode(write_episode(tmp_path, None, scenes(PROPER)), "ep")
    assert not any(line.startswith("molde.json") for line in report.checked)
    assert any("frase afirmativa em cena sem claims" in w for w in report.warnings)
    assert not any(w.startswith("molde") for w in report.warnings)


def test_broken_molde_is_an_error_of_the_file_not_of_the_script(tmp_path: Path) -> None:
    report = check_episode(write_episode(tmp_path, {"gerado_em": "x"}, scenes(FILLER)), "ep")
    assert any(e.startswith("molde.json:") for e in report.errors)
