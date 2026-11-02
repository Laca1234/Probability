"""Probability, recurrence, pair-count and display helpers."""

from __future__ import annotations

import math
from decimal import Decimal, localcontext, ROUND_CEILING
from fractions import Fraction
from typing import Iterable

from probability_of_us.domain.models import DoubleCountingError, ModelInputError, ProbabilityChain, ProbabilityFactor


def as_probability(value: float | int | str | Fraction | Decimal) -> Fraction:
    """Validate and convert a probability while retaining decimal input exactly."""
    try:
        if isinstance(value, Fraction):
            result = value
        elif isinstance(value, Decimal):
            if not value.is_finite():
                raise ModelInputError("Probability must be finite.")
            result = Fraction(value)
        elif isinstance(value, int) and not isinstance(value, bool):
            result = Fraction(value, 1)
        else:
            numeric = float(value)
            if not math.isfinite(numeric):
                raise ModelInputError("Probability must be finite.")
            result = Fraction(str(value))
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ModelInputError("Probability must be a finite number.") from exc
    if not 0 <= result <= 1:
        raise ModelInputError("Probability must be between 0 and 1 inclusive.")
    return result


def _prob_float(p: float | int | str | Fraction | Decimal) -> float:
    if isinstance(p, Fraction):
        value = float(p)
    else:
        try:
            value = float(p)
        except (ValueError, TypeError, OverflowError) as exc:
            raise ModelInputError("Probability must be numeric.") from exc
    if not math.isfinite(value) or value < 0.0 or value > 1.0:
        raise ModelInputError("Probability must be finite and in [0, 1].")
    return value


def _fraction_log_one_minus(probability: Fraction) -> Decimal:
    """Compute ln(1-p) without rounding a tiny p or 1-p away."""
    if probability == 1:
        return Decimal("-Infinity")
    with localcontext() as ctx:
        ctx.prec = 90
        if probability < Fraction(1, 100):
            p = Decimal(probability.numerator) / Decimal(probability.denominator)
            term = p
            total = Decimal(0)
            for k in range(1, 20):
                total -= term / k
                term *= p
            return +total
        complement = 1 - probability
        q = Decimal(complement.numerator) / Decimal(complement.denominator)
        return +q.ln()


def probability_at_least_one(p: float | int | str | Fraction | Decimal, attempts: int) -> float | Decimal:
    """Return 1-(1-p)^N; Decimal is returned when float would erase a nonzero result."""
    exact_probability = as_probability(p)
    if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 0:
        raise ModelInputError("Attempt count must be a non-negative integer.")
    if attempts == 0 or exact_probability == 0:
        return 0.0
    if exact_probability == 1:
        return 1.0
    probability = float(exact_probability)
    if 1e-300 <= probability < 1.0 and attempts <= 10**300:
        return -math.expm1(attempts * math.log1p(-probability))
    with localcontext() as ctx:
        ctx.prec = 90
        negative_log_no_success = -_fraction_log_one_minus(exact_probability) * attempts
        if negative_log_no_success < Decimal("1e-20"):
            # Series form of 1-exp(-x) avoids cancellation for tiny x.
            result = Decimal(0)
            term = negative_log_no_success
            for k in range(1, 24):
                result += term
                term *= -negative_log_no_success / (k + 1)
            return +result
        return +(Decimal(1) - (-negative_log_no_success).exp())


def attempts_for_target(p: float | int | str | Fraction | Decimal, target: float | int | str | Fraction | Decimal) -> int | None:
    """Minimum integer attempts to reach target; None means unreachable or infinite."""
    probability = as_probability(p)
    goal = as_probability(target)
    if goal == 0:
        return 0
    if probability == 1:
        return 1
    if probability == 0 or goal == 1:
        return None
    with localcontext() as ctx:
        ctx.prec = 80
        numerator = _fraction_log_one_minus(goal)
        denominator = _fraction_log_one_minus(probability)
        count = numerator / denominator
        return int(count.to_integral_value(rounding=ROUND_CEILING))


def pair_count(population: int) -> int:
    if isinstance(population, bool) or not isinstance(population, int) or population < 0:
        raise ModelInputError("Population size must be a non-negative integer.")
    return population * (population - 1) // 2


def multiply_factors(factors: Iterable[ProbabilityFactor]) -> ProbabilityChain:
    """Multiply a valid chain rule factorization and reject repeated events."""
    materialized = tuple(factors)
    established: set[str] = set()
    value = Fraction(1, 1)
    missing: list[str] = []
    warnings: list[str] = []
    for factor in materialized:
        if factor.event_id in established:
            raise DoubleCountingError(f"Event {factor.event_id!r} is included more than once.")
        unknown_dependencies = set(factor.conditioned_on) - established
        if unknown_dependencies:
            raise ModelInputError(
                f"Factor {factor.event_id!r} is conditioned on event(s) not established earlier: "
                + ", ".join(sorted(unknown_dependencies))
            )
        if factor.probability is None:
            missing.append(factor.event_id)
        elif not missing:
            value *= factor.probability
        established.add(factor.event_id)
        if factor.evidence in ("assumed", "unknown", "illustrative"):
            warnings.append(f"{factor.label} is {factor.evidence} ({factor.source}).")
    if missing:
        warnings.append("End-to-end probability is incomplete because these factors are unknown: " + ", ".join(missing) + ".")
        return ProbabilityChain(materialized, None, tuple(warnings))
    return ProbabilityChain(materialized, value, tuple(warnings))


def format_probability(p: Fraction | Decimal | float | int | None, significant_digits: int = 4) -> str:
    if p is None:
        return "Unknown"
    if isinstance(p, Decimal):
        if not p.is_finite():
            return "Unknown"
        if p == 0:
            return "0"
        if p < Decimal("1e-5"):
            exponent = p.adjusted()
        decimal_mantissa = p.scaleb(-exponent)
        return f"{decimal_mantissa:.{max(0, significant_digits - 1)}f}e{exponent:+d}"
        return f"{p:.{significant_digits}g}"
    if isinstance(p, Fraction):
        if p == 0:
            return "0"
        if p == 1:
            return "1"
        # Use a logarithm from numerator and denominator without first underflowing.
        log10p = math.log10(p.numerator) - math.log10(p.denominator)
        if log10p < -5:
            fraction_mantissa = 10 ** (log10p - math.floor(log10p))
            return f"{fraction_mantissa:.{max(0, significant_digits - 1)}f} × 10^{math.floor(log10p)}"
        return f"{float(p):.{significant_digits}g}"
    try:
        number = float(p)
    except (TypeError, ValueError, OverflowError):
        return "Unknown"
    if not math.isfinite(number):
        return "Unknown"
    if number == 0:
        return "0"
    if number < 1e-5:
        return f"{number:.{max(0, significant_digits - 1)}e}"
    return f"{number:.{significant_digits}g}"


def probability_odds(p: Fraction | None) -> str:
    if p is None:
        return "Unknown"
    if p == 0:
        return "Impossible under this model"
    reciprocal = Fraction(1, 1) / p
    if reciprocal.denominator == 1:
        return f"1 in {reciprocal.numerator:,}"
    try:
        return f"1 in {float(reciprocal):,.4g}"
    except OverflowError:
        return f"1 in approximately {format_probability(Decimal(reciprocal.numerator) / Decimal(reciprocal.denominator))}"


def bayes_probability(prior: float, sensitivity: float, false_positive_rate: float) -> float:
    """P(H|+) from P(H), P(+|H), and P(+|not H)."""
    p, se, fpr = map(_prob_float, (prior, sensitivity, false_positive_rate))
    denominator = se * p + fpr * (1.0 - p)
    if denominator == 0:
        raise ModelInputError("Bayes result is undefined because P(+) is zero.")
    return se * p / denominator


def birthday_collision_probability(population_size: int, categories: int) -> float:
    """Chance that at least two independent uniform draws share a category."""
    if population_size < 0 or categories <= 0:
        raise ModelInputError("Draw count must be non-negative and category count positive.")
    if population_size <= 1:
        return 0.0
    if population_size > categories:
        return 1.0
    log_no_collision = sum(math.log1p(-i / categories) for i in range(population_size))
    return -math.expm1(log_no_collision)

