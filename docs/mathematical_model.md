# Mathematical model

## Sampling frame and denominator

For a selected interval `[y₀, y₁]`, the loaded dataset defines a finite sampling frame. A record `B(c,y)` is the count of represented births for country `c` and year `y`. The application samples two **distinct, unordered people without replacement** from all records represented in that interval. Its denominator is:

```text
N = Σc Σy B(c,y)
number of possible unordered pairs = C(N,2) = N(N−1)/2
```

If the selected target country has `Nₜ` births in the same interval, then:

```text
P(both born in target country) = C(Nₜ,2) / C(N,2)
```

This is a conditional share within the records and coverage represented by the imported dataset. It is a global birth share only when the dataset covers the global births consistently for every selected year. The bundled example does not.

## Birth-year compatibility

Let `nᵧ` denote target-country births in year `y`, and let `d` be the allowed birth-year difference. The conditional probability that a distinct pair from that country meets the year-gap rule is:

```text
eligible pairs = Σy C(nᵧ,2) + Σy<z, z−y≤d nᵧ n_z
P(gap≤d | both target-country births) = eligible pairs / C(Nₜ,2)
```

The model then calculates the demographic event as the product of these chain-rule factors. Equivalently, it is `eligible target-country pairs / C(N,2)`. The two results are tested for equality.

When two different cohorts are modeled in the numerical engine, birth-year counts can be passed as separate distributions. Compatibility is computed by a weighted sum over the two cohorts. `age_compatibility_probability` also supports sampling without replacement from one shared population by excluding self-pairs.

## Conditional chain

The implemented story chain is:

```text
P(both target-country births)
× P(compatible birth years | both target-country births)
× P(this pair meets | both demographic events)
× P(relationship forms | meeting and prior conditions)
```

Every factor has an event ID, formula, denominator, evidence status, source, and explicit dependencies. A dependency that has not appeared earlier is rejected. Repeating an event ID is rejected as double counting. If an encounter or relationship factor is unknown, the complete story probability remains unknown; demographic factors remain separately inspectable.

The encounter factor concerns one specified pair satisfying the configured population and demographic conditions. It is not the fraction of existing couples who report meeting online. The relationship factor is conditional on a defined encounter; it is not inferred by reversing that survey quantity.

## Other implemented calculations

- Independent sampling with separate populations: `P(C₁,C₂)=P(C₁)P(C₂)`; if sampling the same finite group without replacement, use `n(n−1)/[N(N−1)]`.
- Country share: `Σᵧ B(c,y) / Σᵧ Σc B(c,y)` over the selected interval.
- Hierarchical region check: `P(region) × P(country | region)` must equal the direct country share, when classifications and coverage agree.
- Pair count: `C(N,2)`. This is a count, not a count of independent attempts.
- Great-circle distance: haversine formula using mean Earth radius 6,371.0088 km; it does not account for roads, borders, migration, or population density.
- Recurrence: `P(≥1 success after N attempts)=1−(1−p)^N`, assuming independent attempts and constant `p`.
- Attempts to target `q`: `ceil(ln(1−q)/ln(1−p))`; `p=0` and `q>0` is unreachable; `p<1` and `q=1` requires infinitely many attempts.
- Bayes teaching tool: `P(H|+) = P(+|H)P(H) / [P(+|H)P(H)+P(+|¬H)P(¬H)]`.
- Birthday collision tool assumes independent uniform categorical draws.

## Numerical representation

Count-derived probabilities are `Fraction` values and can be exported as exact numerator/denominator strings. Recurrence uses `log1p` and `expm1`; when a result is smaller than the representable float range it returns a `Decimal`, not zero. Display formatting uses scientific notation. A displayed exact rational is exact only under the stated finite dataset and sampling model, not necessarily an accurate representation of the real world.

## Unknowns, uncertainty, and interpretation

The included synthetic dataset has no sampling uncertainty because its toy counts are fixed, but its real-world relevance is nil. Imported source uncertainty and coverage are not automatically estimated. User-provided encounter and relationship values are sensitivity inputs, not empirical findings. Simulation intervals describe Monte Carlo sampling error under the Bernoulli model; they do not measure model or demographic uncertainty.

The recurrence tool does not treat births or all possible pairs as independent attempts. Pair opportunities can share people; a dependence-aware recurrence model would require an explicit relationship opportunity process. Literal recurrence of the same two identities and their exact circumstances is outside the implemented model.

## Reference example

For three distinct people with birth-year counts `{2000: 2, 2001: 1}`, there are `C(3,2)=3` unordered pairs. A one-year gap admits all 3, so the conditional probability is 1. A zero-year gap admits only the pair from 2000, so the probability is `1/3`. For recurrence, `p=1/2, N=2` gives `1−(1−1/2)²=3/4`.

