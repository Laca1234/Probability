"""Reproducible Monte Carlo for Bernoulli recurrence examples."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Callable

import numpy as np

from probability_of_us.domain.models import ModelInputError
from probability_of_us.statistics.probability import _prob_float


@dataclass(frozen=True, slots=True)
class SimulationResult:
    probability: float
    trials: int
    successes: int
    seed: int
    lower_95: float
    upper_95: float
    method: str = "Wilson score interval; binomial Monte Carlo"
    zero_success_note: str = ""


def simulate_bernoulli(
    probability: float,
    trials: int,
    seed: int,
    *,
    cancelled: Callable[[], bool] | None = None,
    progress: Callable[[int, int], None] | None = None,
    max_trials: int = 50_000_000,
) -> SimulationResult:
    p = _prob_float(probability)
    if isinstance(trials, bool) or not isinstance(trials, int) or trials <= 0 or trials > max_trials:
        raise ModelInputError(f"Trials must be an integer between 1 and {max_trials:,}.")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ModelInputError("Random seed must be a non-negative integer.")
    rng = np.random.default_rng(seed)
    chunk = min(500_000, trials)
    successes = 0
    completed = 0
    while completed < trials:
        if cancelled is not None and cancelled():
            raise InterruptedError("Simulation cancelled by user.")
        size = min(chunk, trials - completed)
        successes += int(np.count_nonzero(rng.random(size) < p))
        completed += size
        if progress is not None:
            progress(completed, trials)
    observed = successes / trials
    z = 1.959963984540054
    denominator = 1 + z * z / trials
    center = (observed + z * z / (2 * trials)) / denominator
    half = z * sqrt(observed * (1 - observed) / trials + z * z / (4 * trials * trials)) / denominator
    note = ""
    if successes == 0:
        upper = min(1.0, 1 - 0.05 ** (1 / trials))
        note = f"Zero successes is not proof of impossibility. Approximate one-sided 95% upper bound: {upper:.3g}."
        return SimulationResult(p, trials, 0, seed, 0.0, upper, "Wilson lower bound and exact one-sided zero-count upper bound", note)
    return SimulationResult(p, trials, successes, seed, max(0.0, center - half), min(1.0, center + half), zero_success_note=note)

