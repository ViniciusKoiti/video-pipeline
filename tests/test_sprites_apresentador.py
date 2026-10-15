"""Sprites do apresentador (provisório, ADR 017): corte da folha, encaixe, máscara e retirada do fundo."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

np = pytest.importorskip("numpy")

GREEN = (0, 255, 0)
SKIN = (240, 180, 130)
DARK = (30, 32, 30)
CELL_W, CELL_H, GUTTER = 40, 60, 4


def sprites_module() -> Any:
    path = Path(__file__).resolve().parents[1] / "scripts" / "provisorio" / "sprites_apresentador.py"
    spec = importlib.util.spec_from_file_location("sprites_apresentador", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sheet(extra_width: int = 0) -> Any:
    """Folha 6×2: em cada célula, fundo verde em cima e um busto escuro que vai até o pé."""
    widths = [CELL_W + extra_width, *[CELL_W] * 5]
    image = np.zeros((2 * CELL_H, sum(widths) + 5 * GUTTER, 3))
    image[:] = GREEN
    x = 0
    for width in widths:
        for row in range(2):
            image[row * CELL_H + 20 : (row + 1) * CELL_H, x : x + width] = DARK
        x += width + GUTTER
    return image


def test_split_sheet_cuts_twelve_cells_of_the_same_size() -> None:
    sprites = sprites_module()
    cells = sprites.split_sheet(sheet(extra_width=3))
    assert sorted(cells) == [(r, c) for r in (1, 2) for c in range(1, 7)]
    assert {cell.shape for cell in cells.values()} == {(CELL_H, CELL_W, 3)}
    for cell in cells.values():  # nenhuma célula leva um pedaço da vizinha: verde em cima, busto embaixo
        assert (cell[:20] == GREEN).all()
        assert (cell[20:] == DARK).all()


def test_split_sheet_refuses_a_sheet_without_six_columns() -> None:
    sprites = sprites_module()
    with pytest.raises(ValueError, match="6 colunas"):
        sprites.split_sheet(sheet()[:, : 3 * (CELL_W + GUTTER)])


def test_fit_finds_the_shift_back_to_the_reference() -> None:
    sprites = sprites_module()
    rng = np.random.default_rng(7)
    ref = rng.uniform(0, 255, (120, 100, 3))
    moved = sprites.shift(ref, -3, 2)
    assert sprites.fit(moved, ref, sprites.NOSE) == (3, -2)
    assert sprites.fit(ref, ref, sprites.NOSE) == (0, 0)


def test_ellipse_is_full_inside_and_empty_outside() -> None:
    sprites = sprites_module()
    mask = sprites.ellipse((400, 300), sprites.MOUTH)
    cx, cy = round(sprites.MOUTH[0] * 300), round(sprites.MOUTH[1] * 400)
    assert mask[cy, cx] == 1
    assert mask[0, 0] == 0 and mask[cy, 0] == 0
    assert 0 < mask[cy, cx + round(sprites.MOUTH[2] * 300)] < 1  # a borda é uma rampa


def test_key_makes_the_green_transparent_and_keeps_the_drawing() -> None:
    sprites = sprites_module()
    image = np.zeros((1, 3, 3))
    image[0, 0], image[0, 1], image[0, 2] = GREEN, SKIN, DARK
    keyed = sprites.key(image)
    assert keyed.shape == (1, 3, 4)
    assert keyed[0, 0, 3] == 0
    assert keyed[0, 1, 3] == 255 and tuple(keyed[0, 1, :3]) == SKIN
    assert keyed[0, 2, 3] == 255
