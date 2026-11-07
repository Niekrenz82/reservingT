# Reserving methods: the math

This note explains the three methods in `src/reservingt/`: Chain Ladder, Bornhuetter-Ferguson and Cape Cod. The code follows these formulas directly.

## Notation

- $n$: number of accident years (rows) and development years (columns). The triangle is square.
- $C_{i,j}$: cumulative loss for accident year $i$ at development year $j$ (0-indexed, $i + j \le n-1$ for observed cells).
- $X_{i,j}$: incremental loss, $X_{i,j} = C_{i,j} - C_{i,j-1}$ with $X_{i,0} = C_{i,0}$.
- $L_i = C_{i,\,n-1-i}$: latest observed cumulative loss for accident year $i$.
- $\hat{C}_{i}$: ultimate loss for accident year $i$.
- $R_i = \hat{C}_{i} - L_i$: reserve for accident year $i$. The total reserve is $\sum_i R_i$.

Cumulative and incremental forms carry the same information. The app converts between them with the formulas above, and the methods expect cumulative data.

## 1. Chain Ladder

**Development factors.** The factor from development year $j$ to $j+1$ is the ratio of column sums, taken over the accident years that have both columns observed:

$$
f_j = \frac{\sum_{i=0}^{n-j-2} C_{i,\,j+1}}{\sum_{i=0}^{n-j-2} C_{i,\,j}}, \qquad j = 0, \dots, n-2
$$

**Cumulative development factor.** From development year $j$ to ultimate:

$$
\mathrm{CDF}_j = \prod_{k=j}^{n-2} f_k, \qquad \mathrm{CDF}_{n-1} = 1
$$

**Ultimate and reserve.** Each accident year is developed from its latest observed value:

$$
\hat{C}_i = L_i \cdot \mathrm{CDF}_{\,n-1-i}, \qquad R_i = L_i \,(\mathrm{CDF}_{\,n-1-i} - 1)
$$

The code fills the lower triangle with $C_{i,j} = C_{i,j-1} \cdot f_{j-1}$, and the last column is the ultimate.

*Reference:* Friedland (2010), Ch. 2; Wüthrich & Merz (2008), Sec. 2.

## 2. Bornhuetter-Ferguson

Chain Ladder projects the latest loss forward, so a recent year with little data gets a volatile ultimate. Bornhuetter-Ferguson blends the projection with an a priori expected ultimate $P_i$ (the prior). The share of the ultimate that is still unreported is $1 - 1/\mathrm{CDF}$:

$$
\hat{C}_i = L_i + \left(1 - \frac{1}{\mathrm{CDF}_{\,n-1-i}}\right) P_i
$$

The reserve is $R_i = \hat{C}_i - L_i = \left(1 - \frac{1}{\mathrm{CDF}}\right) P_i$.

Where the prior is the Chain Ladder ultimate, $P_i = L_i \cdot \mathrm{CDF}$, the formula returns the Chain Ladder ultimate exactly. The test `test_bf_with_cl_ultimates_as_prior_returns_cl_ultimates` checks this.

*Reference:* Bornhuetter & Ferguson (1972); Friedland (2010), Ch. 3.

## 3. Cape Cod (Stanard-Bühlmann)

Cape Cod gets its prior from the data instead of asking for one. An exposure $E_i$ (for example premium) is given for each accident year. One expected loss ratio (ELR) is estimated from the whole triangle:

$$
\mathrm{ELR} = \frac{\sum_i L_i}{\sum_i E_i / \mathrm{CDF}_{\,n-1-i}}
$$

Each accident year's prior is its exposure times the ELR, $P_i = \mathrm{ELR} \cdot E_i$. The ultimate is then the Bornhuetter-Ferguson formula with that prior:

$$
\hat{C}_i = L_i + \left(1 - \frac{1}{\mathrm{CDF}_{\,n-1-i}}\right) \mathrm{ELR} \cdot E_i
$$

Intuition: the denominator is the expected reported loss at the valuation date, if every year had the same loss ratio. Dividing by it gives the ELR that makes the observed losses match the expected reported losses.

The code uses `1 / CDF` as the percent developed for each accident year. It returns this as `percent_developed`, together with `elr`.

*Reference:* Stanard (1985); Friedland (2010), Ch. 4.

## Summary

| Method | Prior | Ultimate |
|---|---|---|
| Chain Ladder | none | $L_i \cdot \mathrm{CDF}$ |
| Bornhuetter-Ferguson | given per year, $P_i$ | $L_i + (1 - 1/\mathrm{CDF})\,P_i$ |
| Cape Cod | $\mathrm{ELR} \cdot E_i$, with ELR from the triangle | $L_i + (1 - 1/\mathrm{CDF})\,\mathrm{ELR}\cdot E_i$ |

## References

- Bornhuetter, R. L., & Ferguson, R. E. (1972). The Actuary and IBNR. *Proceedings of the Casualty Actuarial Society*, 59, 181–195.
- Friedland, J. (2010). *Estimating Unpaid Claims Using Basic Techniques* (3rd ed.). Casualty Actuarial Society. Free from the CAS website.
- Mack, T. (1993). Distribution-free calculation of the standard error of chain ladder reserve estimates. *ASTIN Bulletin*, 23(2), 213–225.
- Stanard, J. N. (1985). A simulation test of prediction errors of loss reserve estimation techniques. *Proceedings of the Casualty Actuarial Society*, 72, 124–148.
- Wüthrich, M. V., & Merz, M. (2008). *Stochastic Claims Reserving Methods in Insurance*. Wiley.

Mack (1993) gives a standard error for the Chain Ladder reserve. It is not implemented in this repo.
