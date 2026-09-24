"""Numerical cross-checks for solution.tex.

The theorems in solution.tex are proved analytically; nothing in the proofs
depends on this script. The script checks the matrix identities and the
explicit examples in floating point, and cross-checks the Fourier-side
formulas against Proposition 4.1 of Philipp, Schaller, Worthmann, Peitz and
Nueske (arXiv:2405.14429), whose derivation is independent (x-space Gaussian
integrals).

Notation follows the paper: k^C(x, y) = exp(-(x-y)^T C^{-2} (x-y)),
Sigma(t) = int_0^t e^{As} B B^T e^{A^T s} ds, C_t, tau_t as in (4.1).
New objects (solution.tex):
    D_t        = C^2 + 4 Sigma(t) - e^{At} C^2 e^{A^T t}
    N          = 4 B B^T - (A C^2 + C^2 A^T)
    Ctil_t^2   = e^{-At} (C^2 + 4 Sigma(t)) e^{-A^T t}
    tautil_t   = det C / det(C^2 + 4 Sigma(t))^{1/2}
    P_C        = C^2 + 4 Sigma            (A Hurwitz)

Run:  python3 verify.py
"""

import numpy as np
from scipy.integrate import quad_vec
from scipy.linalg import expm, solve_continuous_lyapunov, sqrtm

rng = np.random.default_rng(20260924)
RESULTS = []


def report(name, value, tol):
    ok = bool(value <= tol)
    RESULTS.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {value:.3e} (tol {tol:.0e})")


def spd(d, shift=0.5):
    R = rng.normal(size=(d, d))
    return R @ R.T + shift * np.eye(d)


def sigma_van_loan(A, B, t):
    """Sigma(t) = int_0^t e^{As} BB^T e^{A^T s} ds via Van Loan's block exponential (small t only)."""
    d = A.shape[0]
    H = np.zeros((2 * d, 2 * d))
    H[:d, :d] = -A
    H[:d, d:] = B @ B.T
    H[d:, d:] = A.T
    F = expm(H * t)
    return F[d:, d:].T @ F[:d, d:]


def sigma_t(A, B, t, h_max=0.25):
    """Sigma(t) by the recursion Sigma(s + h) = Sigma(h) + e^{Ah} Sigma(s) e^{A^T h}.

    Van Loan's formula alone cancels catastrophically for large t (it multiplies
    e^{-At} by e^{At}); on steps of length <= h_max it is accurate, and the
    recursion adds only positive semidefinite terms.
    """
    if t == 0:
        return np.zeros((A.shape[0], A.shape[0]))
    n = int(np.ceil(t / h_max))
    h = t / n
    S_h = sigma_van_loan(A, B, h)
    E = expm(A * h)
    S = S_h
    for _ in range(n - 1):
        S = S_h + E @ S @ E.T
    return S


def sym(X):
    return 0.5 * (X + X.T)


def D(A, B, C, t):
    E = expm(A * t)
    return sym(C @ C + 4 * sigma_t(A, B, t) - E @ C @ C @ E.T)


def lam_min(X):
    return np.linalg.eigvalsh(sym(X)).min()


def lam_max(X):
    return np.linalg.eigvalsh(sym(X)).max()


# ---------------------------------------------------------------------------
print("1. Sigma(t) (Van Loan steps + recursion) agrees with quadrature")
d, m = 3, 2
A = rng.normal(size=(d, d))
B = rng.normal(size=(d, m))
for t in (0.3, 1.7, 4.0):
    S_q = quad_vec(lambda s: expm(A * s) @ B @ B.T @ expm(A.T * s), 0, t,
                   epsabs=1e-13, epsrel=1e-12)[0]
    report(f"t={t}: max|Sigma - Sigma_quad| / max|Sigma_quad|",
           np.abs(sigma_t(A, B, t) - S_q).max() / np.abs(S_q).max(), 1e-10)

# ---------------------------------------------------------------------------
print("2. D_t = int_0^t e^{As} N e^{A^T s} ds  (arbitrary A, B, C; no Hurwitz assumption)")
for trial in range(3):
    d, m = 3, 2
    A = rng.normal(size=(d, d))
    B = rng.normal(size=(d, m))
    C = np.real(sqrtm(spd(d)))
    N = 4 * B @ B.T - (A @ C @ C + C @ C @ A.T)
    print(f"  trial {trial}: spectral abscissa of A = {np.linalg.eigvals(A).real.max():+.3f}")
    for t in (0.05, 0.8, 2.5):
        rhs = quad_vec(lambda s: expm(A * s) @ N @ expm(A.T * s), 0, t,
                       epsabs=1e-13, epsrel=1e-12)[0]
        scale = max(1.0, np.abs(rhs).max())
        report(f"trial {trial}, t={t}: rel. error", np.abs(D(A, B, C, t) - rhs).max() / scale, 1e-9)
    t = 1e-6
    report(f"trial {trial}: |D_t/t - N| at t=1e-6 (O(t) expected)",
           np.abs(D(A, B, C, t) / t - N).max() / max(1.0, np.abs(N).max()), 1e-4)

# ---------------------------------------------------------------------------
print("3. Hurwitz A: D_t = P_C - e^{At} P_C e^{A^T t}, P_C = C^2 + 4 Sigma")
d, m = 3, 1
A = rng.normal(size=(d, d))
A = A - (np.linalg.eigvals(A).real.max() + 0.7) * np.eye(d)       # Hurwitz
B = rng.normal(size=(d, m))
C = np.real(sqrtm(spd(d)))
Sig = solve_continuous_lyapunov(A, -B @ B.T)                         # A S + S A^T = -BB^T
P = C @ C + 4 * Sig
for t in (0.1, 1.0, 6.0):
    E = expm(A * t)
    report(f"t={t}: max|D_t - (P - e^At P e^A^Tt)|", np.abs(D(A, B, C, t) - (P - E @ P @ E.T)).max(), 1e-9)
report("A P_C + P_C A^T + N = 0", np.abs(A @ P + P @ A.T + 4 * B @ B.T - (A @ C @ C + C @ C @ A.T)).max(), 1e-9)

# ---------------------------------------------------------------------------
print("4. Kernel sections: Fourier-side formulas vs. Proposition 4.1 of the paper")


def ip_bumps(Cp, Cpp, y, yp):
    """<k^{C'}_y, k^{C'}_{y'}>_{H_{C''}} in closed form (requires 2C'^2 - C''^2 > 0)."""
    G = 2 * Cp @ Cp - Cpp @ Cpp
    diff = y - yp
    return (np.linalg.det(Cp) ** 2 / (np.linalg.det(Cpp) * np.sqrt(np.linalg.det(G)))
            * np.exp(-diff @ np.linalg.solve(G, diff)))


d, m = 2, 2
A = rng.normal(size=(d, d)) - 1.2 * np.eye(d)
B = rng.normal(size=(d, m))
C = np.real(sqrtm(spd(d)))
for t in (0.2, 0.9):
    E, Einv = expm(A * t), expm(-A * t)
    S = sigma_t(A, B, t)
    Ct = np.real(sqrtm(sym(Einv @ (C @ C + 2 * S) @ Einv.T)))          # paper (4.1)
    tau = np.linalg.det(C) / np.sqrt(np.linalg.det(C @ C + 2 * S))       # paper (4.1)
    Ctil = np.real(sqrtm(sym(Einv @ (C @ C + 4 * S) @ Einv.T)))        # solution.tex
    tautil = np.linalg.det(C) / np.sqrt(np.linalg.det(C @ C + 4 * S))    # solution.tex
    Z = rng.normal(size=(4, d))
    # Gram matrix of K^t k^C_{z_i} in H_{Ctil_t}, using K^t k^C_z = tau_t k^{C_t}_{e^{-At}z} (paper, Prop. 4.1)
    G_img = np.array([[tau ** 2 * ip_bumps(Ct, Ctil, Einv @ zi, Einv @ zj) for zj in Z] for zi in Z])
    G_src = np.array([[np.exp(-(zi - zj) @ np.linalg.solve(C @ C, zi - zj)) for zj in Z] for zi in Z])
    report(f"t={t}: max|<K k_zi, K k_zj>_Ctil - tautil k^C(zi,zj)|  (Theorem B isometry)",
           np.abs(G_img - tautil * G_src).max(), 1e-10)
    # ||K^t k^C_z||_C^2 : Fourier-side formula (Prop. 3 of solution.tex) vs paper-based value
    four = np.exp(-t * np.trace(A)) * np.linalg.det(C) / np.sqrt(np.linalg.det(2 * C @ C + 4 * S - E @ C @ C @ E.T))
    z = Z[0]
    paper = tau ** 2 * ip_bumps(Ct, C, Einv @ z, Einv @ z)
    report(f"t={t}: |Fourier formula - paper-based value| for ||K^t k_z||_C^2", abs(four - paper) / paper, 1e-10)

# ---------------------------------------------------------------------------
print("5. Monte Carlo check of Proposition 4.1 of the paper (transition law used above)")
d, m = 2, 2
A = np.array([[-1.0, 5.0], [0.0, -1.0]])
B = np.eye(2)
C = np.eye(2)
t = 0.4
E, Einv = expm(A * t), expm(-A * t)
S = sigma_t(A, B, t)
Ct2 = sym(Einv @ (C @ C + 2 * S) @ Einv.T)
tau = np.linalg.det(C) / np.sqrt(np.linalg.det(C @ C + 2 * S))
x, z = np.array([0.3, -0.2]), np.array([0.5, 0.4])
Zs = rng.multivariate_normal(np.zeros(2), S, size=2_000_000)
vals = np.exp(-np.sum((E @ x + Zs - z) ** 2, axis=1))                 # k^I(e^{At}x + Z, z)
mc, se = vals.mean(), vals.std() / np.sqrt(len(vals))
w = Einv @ z
exact = tau * np.exp(-(x - w) @ np.linalg.solve(Ct2, x - w))
print(f"  MC estimate {mc:.6f} +/- {se:.1e}, Prop. 4.1 value {exact:.6f}")
report("|MC - exact| / (5 standard errors)", abs(mc - exact) / (5 * se), 1.0)

# ---------------------------------------------------------------------------
print("6. Example A_beta = [[-1, beta], [0, -1]], B = C = I  (A Hurwitz, (A,B) controllable)")
B = np.eye(2)
C = np.eye(2)
for beta in (4.0, 5.0, 6.0, 7.0, 8.0):
    A = np.array([[-1.0, beta], [0.0, -1.0]])
    L = A @ C @ C + C @ C @ A.T
    cond_paper = lam_max(0.5 * L - B @ B.T) <= 1e-12            # (2.3)
    cond_sharp = lam_max(0.5 * L - 2 * B @ B.T) <= 1e-12        # (2.3#)
    ts = np.concatenate([np.linspace(1e-4, 0.05, 200), np.linspace(0.05, 12, 4000)])
    mins = np.array([lam_min(D(A, B, C, t)) for t in ts])
    is_bad = mins < -1e-12
    bad = ts[is_bad]
    # the grid points with D_t indefinite form an initial segment of the grid
    initial_segment = bool(np.all(is_bad[:is_bad.sum()])) if is_bad.any() else True
    paper_crit = np.array([lam_min(expm(-A * t) @ (C @ C + 2 * sigma_t(A, B, t)) @ expm(-A.T * t) - C @ C)
                           for t in ts[:50]]).min()
    print(f"  beta={beta:>3}: (2.3) {'holds' if cond_paper else 'FAILS'}, "
          f"(2.3#) {'holds' if cond_sharp else 'FAILS'}, "
          f"min_t lam_min(D_t) = {mins.min():+.3e}, "
          f"D_t indefinite for t in {'(none)' if bad.size == 0 else f'[{bad.min():.4f}, {bad.max():.4f}]'}"
          f"{'' if bad.size == 0 else (' (initial segment of grid)' if initial_segment else ' (NOT an initial segment)')}, "
          f"min lam_min(C_t^2 - C^2) on t <= {ts[49]:.4f}: {paper_crit:+.3e}")
    RESULTS.append(cond_sharp == (bad.size == 0) and initial_segment)

# closed form of D_t for this example (solution.tex, Example 6.1)
beta = 8.0
A = np.array([[-1.0, beta], [0.0, -1.0]])
for t in (0.3, 1.1, 4.0):
    e = np.exp(-2 * t)
    Dc = np.array([[3 * (1 - e) + beta ** 2 * (1 - e * (1 + 2 * t + 3 * t ** 2)), beta * (1 - e * (1 + 3 * t))],
                   [beta * (1 - e * (1 + 3 * t)), 3 * (1 - e)]])
    report(f"beta=8, t={t}: closed-form D_t vs numerical", np.abs(Dc - D(A, B, C, t)).max(), 1e-10)


def detD(t, beta=8.0):
    e = np.exp(-2 * t)
    d11 = 3 * (1 - e) + beta ** 2 * (1 - e * (1 + 2 * t + 3 * t ** 2))
    d12 = beta * (1 - e * (1 + 3 * t))
    d22 = 3 * (1 - e)
    return d11 * d22 - d12 ** 2


grid = np.linspace(1e-4, 40, 400001)
vals = detD(grid)
sign_changes = np.where(np.diff(np.sign(vals)) != 0)[0]
lo, hi = grid[sign_changes[0]], grid[sign_changes[0] + 1]
for _ in range(100):
    mid = 0.5 * (lo + hi)
    lo, hi = (mid, hi) if detD(mid) < 0 else (lo, mid)
print(f"  beta=8: det D_t changes sign {len(sign_changes)} time(s) on (0, 40]; root t_1 = {0.5 * (lo + hi):.6f}")
RESULTS.append(len(sign_changes) == 1)

# ---------------------------------------------------------------------------
print("7. Example with scalar noise: A = [[3/2, -2], [2, -2]], B = e_1, C = I")
A = np.array([[1.5, -2.0], [2.0, -2.0]])
B = np.array([[1.0], [0.0]])
C = np.eye(2)
print(f"  eigenvalues of A: {np.linalg.eigvals(A)}; rank[B, AB] = {np.linalg.matrix_rank(np.hstack([B, A @ B]))}")
L = A + A.T
print(f"  lam_max(L/2 - BB^T) = {lam_max(0.5 * L - B @ B.T):+.3f}  (> 0: (2.3) fails)")
print(f"  lam_max(L/2 - 2BB^T) = {lam_max(0.5 * L - 2 * B @ B.T):+.3f}  (<= 0: (2.3#) holds)")
mins = min(lam_min(D(A, B, C, t)) for t in np.linspace(1e-4, 10, 3000))
print(f"  min over t-grid of lam_min(D_t) = {mins:+.3e}")
RESULTS.append(np.linalg.eigvals(A).real.max() < 0 and lam_max(0.5 * L - B @ B.T) > 0
               and lam_max(0.5 * L - 2 * B @ B.T) <= 1e-12 and mins > -1e-12)

print()
print(f"{sum(RESULTS)}/{len(RESULTS)} checks passed")
