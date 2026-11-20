"""A tela não calcula, mas o `vp check` refaz a conta (ADR 020, item 4; ADR 028)."""

from __future__ import annotations

from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import CalculationShot, Language, ReceiptShot, Shot, screen_number, screen_parts
from app.pipeline.script.models.plan_check import PlanCheck


def _amount(text: str, language: Language) -> tuple[float, int, str, str] | None:
    """(valor, casas decimais, prefixo, sufixo) de um número na tela; "20%" vale 0,2 numa conta."""
    parts, number = screen_parts(text), screen_number(text, language)
    if parts is None or number is None:
        return None
    prefix, value, suffix = number
    _, separator, fraction = parts[1].partition(SchemasConstants.NUMBER_SEPARATORS[language][1])
    decimals = len(fraction) if separator else 0
    return (value / 100 if suffix.startswith("%") else value), decimals, prefix, suffix


def _written(value: float, decimals: int, language: Language) -> str:
    """Número com as casas e o separador decimal do idioma, para a mensagem."""
    return f"{value:.{decimals}f}".replace(".", SchemasConstants.NUMBER_SEPARATORS[language][1])


def _evaluate(values: list[float], operators: list[str]) -> float:
    """A conta como se escreve: × e ÷ antes de + e −, da esquerda para a direita."""
    terms, signs = [values[0]], []
    for op, value in zip(operators, values[1:], strict=True):
        if op == "×":
            terms[-1] *= value
        elif op == "÷":
            terms[-1] /= value
        else:
            signs.append(op)
            terms.append(value)
    total = terms[0]
    for op, value in zip(signs, terms[1:], strict=True):
        total = total + value if op == "+" else total - value
    return total


def _shown(value: float, decimals: int, suffix: str) -> float:
    """O valor como a tela o escreve: em porcentagem, ×100; arredondado nas casas que ela mostra."""
    return round(value * 100 if suffix.startswith("%") else value, decimals)


def arithmetic_errors(scene_id: str, shot: Shot, language: Language) -> list[str]:
    """A tela não calcula, mas o `vp check` refaz a conta (ADR 020, item 4; ADR 028): o resultado da conta e
    o total da nota têm de ser o que os números escritos dão, arredondados como a tela mostra."""
    where = f"{scene_id}: {shot.kind} ({shot.anchor!r})"
    if isinstance(shot, CalculationShot):
        texts = [term.text for term in shot.terms] + [shot.result.text]
        amounts = [_amount(text, language) for text in texts]
        missing = [text for text, amount in zip(texts, amounts, strict=True) if amount is None]
        if missing:
            return [f"{where}: sem número para refazer a conta: {', '.join(map(repr, missing))}"]
        values = [a[0] for a in amounts if a is not None]
        try:
            got = _evaluate(values[:-1], [term.op or "" for term in shot.terms[1:]])
        except ZeroDivisionError:
            return [f"{where}: divisão por zero"]
        _, decimals, _, suffix = amounts[-1]  # type: ignore[misc]
        expected = _shown(got, decimals, suffix)
        if abs(expected - _shown(values[-1], decimals, suffix)) > 10**-decimals / 2:
            expression = " ".join(
                [shot.terms[0].text] + [f"{term.op} {term.text}" for term in shot.terms[1:]]
            )
            return [f"{where}: {expression} dá {_written(expected, decimals, language)}, e a tela mostra "
                    f"{shot.result.text}"]
        return []
    if isinstance(shot, ReceiptShot):
        rows = [item.value for item in shot.items] + ([shot.total.value] if shot.total else [])
        amounts = [_amount(text, language) for text in rows]
        if any(amount is None for amount in amounts):
            return [f"{where}: linha da nota sem número"]
        units = {(a[2], a[3]) for a in amounts if a is not None}
        if len(units) > 1:
            return [f"{where}: linhas em unidades diferentes: {', '.join(map(repr, rows))}"]
        if shot.total is not None:
            *items, (total, decimals, _, _) = [a for a in amounts if a is not None]
            got = round(sum(item[0] for item in items), decimals)
            if abs(got - round(total, decimals)) > 10**-decimals / 2:
                return [f"{where}: as linhas somam {_written(got, decimals, language)}, e o total mostra "
                        f"{shot.total.value}"]
        return []
    return []


def check(plan: PlanCheck, report: CheckReport) -> None:
    report.errors += arithmetic_errors(plan.scene_id, plan.shot, plan.language)
