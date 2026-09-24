"""Exact (symbolic) checks for paper.tex, complementing the floating-point checks in verify.py.

Every check below is an identity or inequality that the paper proves by hand; SymPy confirms it in
exact arithmetic. Nothing in the paper depends on this script.

Sections:
  S1  Gaussian integrals and constants: (2.1), (2.3), (2.4), the normalization in (2.5), Lemma 7.1.
  S2  One-dimensional model: the kernel-section formula of [PSWPN, proof of Prop. 4.1], the norm
      identity (3.4), Theorem 4.2 (isometry up to the factor tautilde_t), Proposition 7.5 (Gaussian m_t).
  S3  Example 6.1 (A_beta, B = C = I): Sigma(t), D_t, (4.2), Lambda_C, Sigma, P_C, Theorem 5.1(a),(b),
      Remark 4.5, thresholds beta <= 4 and beta <= 6, Corollary 1.2, the tail bound for beta <= 14.
  S4  Example 6.2 (scalar noise), including the stationary covariance and Theorem 5.1(b).
  S5  Matrix identities used in Section 4 and Remark 7.3, with generic symbolic 2x2 matrices.

Run:  python3 verify_symbolic.py      (SymPy >= 1.12)
"""

import sympy as sp

RESULTS = []


def check(name, ok):
    ok = bool(ok)
    RESULTS.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")


def is_zero(expr):
    return sp.simplify(sp.expand(expr)) == 0


def mat_is_zero(M):
    return all(is_zero(e) for e in M)


x, y, z, xi, eta = sp.symbols("x y z xi eta", real=True)
t, s, r = sp.symbols("t s r", positive=True)

# ------------------------------------------------------------------------------------------------
print("S1. Gaussian integrals and normalizing constants")
p = sp.symbols("p", positive=True)
lhs = sp.integrate(sp.exp(-p * x**2 - sp.I * xi * x), (x, -sp.oo, sp.oo), conds="none")
check("(2.1), d = 1:  int exp(-p x^2 - i xi x) dx = sqrt(pi/p) exp(-xi^2/(4p))",
      is_zero(lhs - sp.sqrt(sp.pi / p) * sp.exp(-xi**2 / (4 * p))))

c, c1, c2 = sp.symbols("c c1 c2", positive=True)
k_hat = sp.integrate(sp.exp(-(x - y)**2 / c**2 - sp.I * xi * x), (x, -sp.oo, sp.oo), conds="none")
kappa = sp.sqrt(sp.pi) * c                                   # kappa_C = pi^{d/2} det C, d = 1
w = lambda cc, v: sp.exp(cc**2 * v**2 / 4)                   # w_C(xi) = exp(xi^T C^2 xi / 4)
check("(2.3), d = 1:  FT of k^c_y is kappa_c e^{-i xi y} / w_c(xi)",
      is_zero(k_hat - kappa * sp.exp(-sp.I * xi * y) / w(c, xi)))
check("(2.4), d = 1:  int 1/w_c = (4 pi)^{1/2} / c",
      is_zero(sp.integrate(1 / w(c, xi), (xi, -sp.oo, sp.oo)) - sp.sqrt(4 * sp.pi) / c))
norm_k = (sp.integrate(sp.simplify(k_hat * sp.conjugate(k_hat)) * w(c, xi), (xi, -sp.oo, sp.oo))
          / (2 * sp.pi * kappa))
check("(2.5), d = 1:  ||k^c_y||_c^2 = k^c(y, y) = 1", is_zero(norm_k - 1))
d = sp.symbols("d", positive=True, integer=True)
detC = sp.symbols("detC", positive=True)
check("(2.5), general d:  (2 pi)^{-d} kappa_C^{-1} * kappa_C^2 * (4 pi)^{d/2}/det C = 1",
      is_zero(sp.powsimp((2 * sp.pi)**(-d) * sp.pi**(d / 2) * detC * (4 * sp.pi)**(d / 2) / detC, force=True) - 1))
check("Lemma 7.1, general d:  (2 pi)^{-d} pi^d 2^d = 1",
      is_zero(sp.powsimp((2 * sp.pi)**(-d) * sp.pi**d * 2**d, force=True) - 1))

yp = sp.symbols("yp", real=True)
G = 2 * c1**2 - c2**2
Gp = sp.symbols("Gp", positive=True)                         # stands for G = 2c1^2 - c2^2 > 0
kh1 = sp.sqrt(sp.pi) * c1 * sp.exp(-sp.I * xi * y) / w(c1, xi)
kh2 = sp.sqrt(sp.pi) * c1 * sp.exp(-sp.I * xi * yp) / w(c1, xi)
integrand = sp.simplify(kh1 * sp.conjugate(kh2) * w(c2, xi)).subs(c2**2, 2 * c1**2 - Gp)
ip = sp.integrate(sp.expand(integrand), (xi, -sp.oo, sp.oo), conds="none") / (2 * sp.pi * sp.sqrt(sp.pi) * c2)
target = c1**2 / (c2 * sp.sqrt(Gp)) * sp.exp(-(y - yp)**2 / Gp)
check("Lemma 7.1, d = 1:  <k^{c1}_y, k^{c1}_{y'}>_{c2} = c1^2/(c2 sqrt G) exp(-(y-y')^2/G), G = 2c1^2 - c2^2",
      is_zero(sp.simplify(ip - target)))

# ------------------------------------------------------------------------------------------------
print("S2. One-dimensional model: dX = a X dt + b dW, kernel matrix C = c > 0, t > 0")
a = sp.symbols("a", real=True)
sig = sp.symbols("sigma", positive=True)                     # sigma = Sigma(t) > 0 (b != 0, t > 0)
gauss_density = sp.exp(-y**2 / (2 * sig)) / sp.sqrt(2 * sp.pi * sig)
check("characteristic function:  int e^{i xi y} N(0, sigma)(dy) = exp(-sigma xi^2 / 2)",
      is_zero(sp.integrate(sp.exp(sp.I * xi * y) * gauss_density, (y, -sp.oo, sp.oo), conds="none")
              - sp.exp(-sig * xi**2 / 2)))
Kk = sp.integrate(sp.exp(-(sp.exp(a * t) * x + y - z)**2 / c**2) * gauss_density, (y, -sp.oo, sp.oo), conds="none")
ct2 = sp.exp(-2 * a * t) * (c**2 + 2 * sig)                  # C_t^2 of [PSWPN, (4.1)]
tau = c / sp.sqrt(c**2 + 2 * sig)
check("[PSWPN, proof of Prop. 4.1]:  K^t k^c_z = tau_t k^{C_t}_{e^{-at} z}  (x-space Gaussian convolution)",
      is_zero(sp.simplify(Kk - tau * sp.exp(-(x - sp.exp(-a * t) * z)**2 / ct2))))
g_hat = sp.integrate(tau * sp.exp(-(x - sp.exp(-a * t) * z)**2 / ct2 - sp.I * xi * x), (x, -sp.oo, sp.oo),
                     conds="none")
f_hat = sp.sqrt(sp.pi) * c * sp.exp(-sp.I * eta * z) / w(c, eta)
KtFT = sp.exp(-a * t) * f_hat.subs(eta, sp.exp(-a * t) * xi) * sp.exp(-sp.exp(-2 * a * t) * sig * xi**2 / 2)
check("(3.2), d = 1, f = k^c_z:  FT(K^t f)(xi) = e^{-ta} f^(e^{-at} xi) exp(-xi^2 e^{-2at} sigma / 2)",
      is_zero(sp.simplify(g_hat - KtFT)))
Dt = c**2 + 4 * sig - sp.exp(2 * a * t) * c**2
lhs34 = sp.simplify(g_hat * sp.conjugate(g_hat) * w(c, xi))
rhs34 = sp.exp(-a * t) * sp.simplify(f_hat * sp.conjugate(f_hat)) * w(c, eta) * sp.exp(-Dt * eta**2 / 4)
lhs34_sub = sp.simplify(lhs34.subs(xi, sp.exp(a * t) * eta) * sp.exp(a * t))   # xi = e^{at} eta, dxi = e^{at} deta
check("(3.4), d = 1, f = k^c_z:  integrands agree after xi = e^{at} eta", is_zero(sp.simplify(lhs34_sub - rhs34)))
ctil2 = sp.exp(-2 * a * t) * (c**2 + 4 * sig)                # Ctilde_t^2 of Theorem 4.2
ctil = sp.sqrt(ctil2)
norm_img = sp.integrate(sp.simplify(g_hat * sp.conjugate(g_hat) * sp.exp(ctil2 * xi**2 / 4)), (xi, -sp.oo, sp.oo),
                        conds="none") / (2 * sp.pi * sp.sqrt(sp.pi) * ctil)
check("Theorem 4.2, d = 1:  ||K^t k^c_z||^2 in H_{Ctilde_t} = tautilde_t = c / sqrt(c^2 + 4 sigma)",
      is_zero(sp.simplify(norm_img - c / sp.sqrt(c**2 + 4 * sig))))
phihat = lambda v: sp.sqrt(sp.pi) * c * sp.exp(-c**2 * v**2 / 4)
m_t = phihat(eta) * sp.exp(-sig * eta**2) / phihat(sp.exp(a * t) * eta)
check("Proposition 7.5, d = 1:  m_t(eta) = exp(-D_t eta^2 / 4)", is_zero(sp.simplify(m_t - sp.exp(-Dt * eta**2 / 4))))

# ------------------------------------------------------------------------------------------------
print("S3. Example 6.1: A = [[-1, beta], [0, -1]], B = C = I")
beta = sp.symbols("beta", nonnegative=True)
I2 = sp.eye(2)
A = sp.Matrix([[-1, beta], [0, -1]])
E = lambda tt: sp.exp(-tt) * sp.Matrix([[1, beta * tt], [0, 1]])
check("e^{At} = e^{-t} [[1, beta t], [0, 1]]  (sympy matrix exponential)", mat_is_zero((A * t).exp() - E(t)))
Sig_t = (E(s) * E(s).T).applyfunc(lambda e_: sp.integrate(e_, (s, 0, t)))
el = sp.exp(-2 * t)
check("elementary integrals: int_0^t s^k e^{-2s} ds, k = 0, 1, 2",
      is_zero(sp.integrate(sp.exp(-2 * s), (s, 0, t)) - (1 - el) / 2)
      and is_zero(sp.integrate(s * sp.exp(-2 * s), (s, 0, t)) - (1 - el * (1 + 2 * t)) / 4)
      and is_zero(sp.integrate(s**2 * sp.exp(-2 * s), (s, 0, t)) - (1 - el * (1 + 2 * t + 2 * t**2)) / 4))
D = I2 + 4 * Sig_t - E(t) * E(t).T
D_closed = sp.Matrix([[3 * (1 - el) + beta**2 * (1 - el * (1 + 2 * t + 3 * t**2)), beta * (1 - el * (1 + 3 * t))],
                      [beta * (1 - el * (1 + 3 * t)), 3 * (1 - el)]])
check("closed form of D_t (entries d_11, d_12 = d_21, d_22)", mat_is_zero(D - D_closed))
Lam = 4 * I2 - (A + A.T)
check("Lambda_C = [[6, -beta], [-beta, 6]]", mat_is_zero(Lam - sp.Matrix([[6, -beta], [-beta, 6]])))
check("(4.2): D_t = int_0^t e^{As} Lambda_C e^{A^T s} ds",
      mat_is_zero(D - (E(s) * Lam * E(s).T).applyfunc(lambda e_: sp.integrate(e_, (s, 0, t)))))
check("D_t = t Lambda_C + O(t^2):  lim_{t->0} D_t / t = Lambda_C",
      mat_is_zero((D / t).applyfunc(lambda e_: sp.limit(e_, t, 0)) - Lam))
check("dD_t/dt = e^{At} Lambda_C e^{A^T t}", mat_is_zero(D.diff(t) - E(t) * Lam * E(t).T))
Sig = Sig_t.applyfunc(lambda e_: sp.limit(e_, t, sp.oo))
check("Sigma = [[1/2 + beta^2/4, beta/4], [beta/4, 1/2]]",
      mat_is_zero(Sig - sp.Matrix([[sp.Rational(1, 2) + beta**2 / 4, beta / 4], [beta / 4, sp.Rational(1, 2)]])))
check("A Sigma + Sigma A^T = -B B^T", mat_is_zero(A * Sig + Sig * A.T + I2))
P = I2 + 4 * Sig
check("P_C = I + 4 Sigma = [[3 + beta^2, beta], [beta, 3]]", mat_is_zero(P - sp.Matrix([[3 + beta**2, beta], [beta, 3]])))
check("Theorem 5.1(a): D_t = P_C - e^{At} P_C e^{A^T t}", mat_is_zero(D - (P - E(t) * P * E(t).T)))
check("Theorem 5.1(b): A P_C + P_C A^T = [[-6, beta], [beta, -6]] = -Lambda_C",
      mat_is_zero(A * P + P * A.T - sp.Matrix([[-6, beta], [beta, -6]])) and mat_is_zero(A * P + P * A.T + Lam))
Q = I2 + 2 * Sig
check("A (I + 2 Sigma) + (I + 2 Sigma) A^T = [[-4, beta], [beta, -4]]",
      mat_is_zero(A * Q + Q * A.T - sp.Matrix([[-4, beta], [beta, -4]])))
Ct2 = E(-t) * (I2 + 4 * Sig_t) * E(-t).T
check("Remark 4.5: d/dt Ctilde_t^2 = e^{-At} Lambda_C e^{-A^T t}", mat_is_zero(Ct2.diff(t) - E(-t) * Lam * E(-t).T))
check("Corollary 4.3: Ctilde_t^2 - C^2 = e^{-At} D_t e^{-A^T t}", mat_is_zero(Ct2 - I2 - E(-t) * D * E(-t).T))
ev = (A + A.T).eigenvals()
check("eigenvalues of A + A^T are -2 + beta and -2 - beta", set(ev) == {beta - 2, -beta - 2})
bt = sp.symbols("b", real=True)                              # real copy of beta for the inequality solver
lam_max_half = (bt - 2) / 2                                  # largest eigenvalue of (A + A^T)/2 for beta >= 0
nonneg = sp.Interval(0, sp.oo)
check("(1.3) <=> (beta - 2)/2 <= 1 <=> beta <= 4   (beta >= 0)",
      sp.solve_univariate_inequality(lam_max_half <= 1, bt, relational=False).intersect(nonneg) == sp.Interval(0, 4))
check("(1.5) <=> (beta - 2)/2 <= 2 <=> beta <= 6   (beta >= 0)",
      sp.solve_univariate_inequality(lam_max_half <= 2, bt, relational=False).intersect(nonneg) == sp.Interval(0, 6))
check("Corollary 1.2 (beta = 5): eigenvalues of (A + A^T)/2 are 3/2 and -7/2",
      set(((A + A.T) / 2).subs(beta, 5).eigenvals()) == {sp.Rational(3, 2), sp.Rational(-7, 2)})
check("||K^t|| = e^{-t Tr A / 2} = e^t since Tr A = -2", A.trace() == -2)
# tail bound of Example 6.1: lam_min(P)/lam_max(P) >= 1/100 for 0 <= beta <= 14, and (1 + 14 t) e^{-t} < 1e-14 at t = 40
Tr, Det = P.trace(), P.det()
ratio_fn = sp.simplify(Det / Tr**2)                          # = r / (1 + r)^2 with r = lam_min / lam_max
check("Det(P)/Tr(P)^2 = (9 + 2 beta^2)/(6 + beta^2)^2 is decreasing in beta > 0 (so r is decreasing)",
      is_zero(ratio_fn - (9 + 2 * beta**2) / (6 + beta**2)**2)
      and sp.simplify(sp.diff(ratio_fn, beta) + 4 * beta * (beta**2 + 3) / (beta**2 + 6)**3) == 0)
evs14 = sorted(P.subs(beta, 14).eigenvals(), key=lambda v: float(v))
check("beta = 14: eigenvalues of P_C are 101 -+ 70 sqrt(2)",
      is_zero(evs14[0] - (101 - 70 * sp.sqrt(2))) and is_zero(evs14[1] - (101 + 70 * sp.sqrt(2))))
check("beta = 14: lam_min/lam_max >= 1/100 exactly  (<=> 9999^2 >= 2 * 7070^2)",
      9999**2 >= 2 * 7070**2 and sp.simplify(100 * evs14[0] - evs14[1]) == 9999 - 7070 * sp.sqrt(2))
check("(1 + 14 * 40) e^{-40} < 1e-14  (50-digit evaluation)", sp.N((1 + 14 * 40) * sp.exp(-40), 50) < sp.Float("1e-14", 50))
check("(1 + beta t) e^{-t} is decreasing for t >= 1 (derivative e^{-t}(beta - 1 - beta t) <= -e^{-t} < 0)",
      is_zero(sp.diff((1 + beta * t) * sp.exp(-t), t) - sp.exp(-t) * (beta - 1 - beta * t)))

# ------------------------------------------------------------------------------------------------
print("S4. Example 6.2: A = [[3/2, -2], [2, -2]], B = e_1, C = I")
A2 = sp.Matrix([[sp.Rational(3, 2), -2], [2, -2]])
B2 = sp.Matrix([1, 0])
BB = B2 * B2.T
check("Tr A = -1/2, det A = 1", A2.trace() == sp.Rational(-1, 2) and A2.det() == 1)
check("eigenvalues -1/4 +- i sqrt(15)/4",
      set(A2.eigenvals()) == {sp.Rational(-1, 4) + sp.I * sp.sqrt(15) / 4, sp.Rational(-1, 4) - sp.I * sp.sqrt(15) / 4})
check("A B = (3/2, 2)^T and det[B, AB] = 2",
      A2 * B2 == sp.Matrix([sp.Rational(3, 2), 2]) and sp.Matrix.hstack(B2, A2 * B2).det() == 2)
H2 = (A2 + A2.T) / 2
check("(A + A^T)/2 = diag(3/2, -2), BB^T = diag(1, 0)",
      H2 == sp.diag(sp.Rational(3, 2), -2) and BB == sp.diag(1, 0))
check("BB^T - (A + A^T)/2 = diag(-1/2, 2), so (1.3) fails", BB - H2 == sp.diag(sp.Rational(-1, 2), 2))
check("2BB^T - (A + A^T)/2 = diag(1/2, 2) >= 0, so (1.5) holds", 2 * BB - H2 == sp.diag(sp.Rational(1, 2), 2))
p11, p12, p22 = sp.symbols("p11 p12 p22")
S2 = sp.Matrix([[p11, p12], [p12, p22]])
sol = sp.solve(list(A2 * S2 + S2 * A2.T + BB), [p11, p12, p22], dict=True)[0]
Sig2 = S2.subs(sol)
check(f"stationary covariance Sigma = {Sig2.tolist()} is positive definite",
      Sig2[0, 0] > 0 and Sig2.det() > 0)
P2 = sp.eye(2) + 4 * Sig2
Lam2 = 4 * BB - (A2 + A2.T)
check("Theorem 5.1(b): A P_C + P_C A^T = -Lambda_C = diag(-1, -4) <= 0",
      A2 * P2 + P2 * A2.T == -Lam2 and Lam2 == sp.diag(1, 4))

# ------------------------------------------------------------------------------------------------
print("S5. Generic matrix identities (symbolic 2x2 matrices)")
a11, a12, a21, a22, b1, b2, q11, q12, q22, s11, s12, s22 = sp.symbols("a11 a12 a21 a22 b1 b2 q11 q12 q22 s11 s12 s22",
                                                                         real=True)
Ag = sp.Matrix([[a11, a12], [a21, a22]])
Bg = sp.Matrix([b1, b2])
C2g = sp.Matrix([[q11, q12], [q12, q22]])                    # C^2 (symmetric)
Sg = sp.Matrix([[s11, s12], [s12, s22]])                      # Sigma(t) (symmetric)
e1, e2 = sp.Matrix([eta, 0]), sp.Matrix([0, eta])
v = sp.Matrix(sp.symbols("v1 v2", real=True))
check("Theorem 4.2: -v^T Sigma v + v^T (C^2 + 4 Sigma) v / 4 = v^T C^2 v / 4",
      is_zero((-(v.T * Sg * v) + (v.T * (C2g + 4 * Sg) * v) / 4 - (v.T * C2g * v) / 4)[0]))
lhs_c = (Ag * (C2g / 2) + (C2g / 2) * Ag.T) / 2 - Bg * Bg.T
rhs_c = ((Ag * C2g + C2g * Ag.T) / 2 - 2 * Bg * Bg.T) / 2
check("Corollary 1.2: condition (1.3) for C/sqrt(2) is (1.5) divided by 2", mat_is_zero(lhs_c - rhs_c))
Einv = sp.Matrix(2, 2, sp.symbols("f11 f12 f21 f22", real=True))   # stands for e^{-At}
Ct2g = Einv * (C2g + 2 * Sg) * Einv.T
Ctil2g = Einv * (C2g + 4 * Sg) * Einv.T
check("Corollary 4.3: Ctilde_t^2 - C_t^2 = 2 e^{-At} Sigma(t) e^{-A^T t}", mat_is_zero(Ctil2g - Ct2g - 2 * Einv * Sg * Einv.T))
check("Remark 7.3: 2 C_t^2 - Ctilde_t^2 = e^{-At} C^2 e^{-A^T t}", mat_is_zero(2 * Ct2g - Ctil2g - Einv * C2g * Einv.T))
a_, b_, c_, e_ = sp.symbols("detP2 detP4 detC expTrA", positive=True)
# a_ = det(C^2 + 2 Sigma), b_ = det(C^2 + 4 Sigma), c_ = det C, e_ = e^{t Tr A}
det_Ct, det_Ctil, tau_, tautil_ = sp.sqrt(a_) / e_, sp.sqrt(b_) / e_, c_ / sp.sqrt(a_), c_ / sp.sqrt(b_)
check("Remark 7.3: (det Ctilde_t / det C_t) * tautilde_t = tau_t", is_zero(det_Ctil / det_Ct * tautil_ - tau_))
check("Remark 7.3: tau_t^2 (det C_t)^2 / (det Ctilde_t * det(e^{-At} C^2 e^{-A^T t})^{1/2}) = tautilde_t",
      is_zero(tau_**2 * det_Ct**2 / (det_Ctil * (c_ / e_)) - tautil_))

print()
print(f"{sum(RESULTS)}/{len(RESULTS)} symbolic checks passed")
