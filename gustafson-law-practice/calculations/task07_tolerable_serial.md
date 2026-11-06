# Task 07 - Maximum Tolerable Serial Fraction

Given P = 8,192, requirement S(P) >= 7,500.

## Derivation
S(P) = P - alpha(P-1) >= S_req
-alpha(P-1) >= S_req - P
alpha(P-1) <= P - S_req          (multiply by -1, inequality flips)
alpha <= (P - S_req)/(P - 1)

## Numeric result
alpha_max = (8192 - 7500) / (8192 - 1) = 692 / 8191 = **0.084483**  (~ 8.448 %)

## Verification
S(P) at alpha_max = 8192 - 0.084482969 x 8191 = 7500.0000  (exactly 7500).
At alpha = 0.09: S = 7454.81 < 7500 -> fails. At alpha = 0.08: S = 7536.72 -> passes.

Implied efficiency floor: E >= 7500/8192 = 0.9155.
