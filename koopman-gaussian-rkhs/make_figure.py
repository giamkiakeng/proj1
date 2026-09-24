"""Figure 1 of paper.tex: admissible times for Example 6.1.

For A_beta = [[-1, beta], [0, -1]] and B = C = I, Theorem 4.1 of paper.tex says
K^t H_I is contained in H_I exactly when D_t >= 0, where (Example 6.1)

    D_t = [[3(1-e) + beta^2 (1 - e(1+2t+3t^2)),  beta (1 - e(1+3t))],
           [beta (1 - e(1+3t)),                  3(1-e)          ]],   e = exp(-2t).

For beta <= 6 this holds for every t >= 0 (Theorem 4.4). For beta > 6 the script
computes, on a grid of beta, the set of t in (0, T_MAX] with D_t >= 0, checks that it
is an interval [t_1(beta), T_MAX], and finds t_1(beta) by bisection on det D_t. For
t >= T_MAX, D_t > 0 follows from the bound in the proof of Theorem 5.1(c)
(checked below). The output is fig_admissible_times.pdf.

Run:  python3 make_figure.py
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

T_MAX = 40.0
BLUE = "#2a78d6"        # data hue (validated with the dataviz palette validator)
INK = "#0b0b0b"         # primary text
INK_2 = "#52514e"       # secondary text / reference lines



def D_entries(t, beta):
    e = np.exp(-2 * t)
    d11 = 3 * (1 - e) + beta ** 2 * (1 - e * (1 + 2 * t + 3 * t ** 2))
    d12 = beta * (1 - e * (1 + 3 * t))
    d22 = 3 * (1 - e)
    return d11, d12, d22


def lam_min(t, beta):
    d11, d12, d22 = D_entries(t, beta)
    return 0.5 * (d11 + d22 - np.sqrt((d11 - d22) ** 2 + 4 * d12 ** 2))


def det_D(t, beta):
    d11, d12, d22 = D_entries(t, beta)
    return d11 * d22 - d12 ** 2


def t1(beta):
    """Smallest t > 0 with D_t >= 0; verifies that {D_t >= 0} is an interval on the grid."""
    grid = np.linspace(1e-5, T_MAX, 200_001)
    ok = lam_min(grid, beta) >= -1e-12
    first = np.argmax(ok)
    assert ok[first] and np.all(ok[first:]), f"admissible set is not an interval for beta={beta}"
    assert first > 0, f"D_t >= 0 already at the first grid point for beta={beta}"
    lo, hi = grid[first - 1], grid[first]
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if det_D(mid, beta) < 0 else (lo, mid)
    return 0.5 * (lo + hi)


def tail_bound_ok(beta):
    """Rigorous tail: for t >= T_MAX, ||e^{A_beta t}|| <= (1 + beta t) e^{-t}, which is decreasing on [1, oo),
    so sup_{t >= T_MAX} ||e^{At}||^2 <= ((1 + beta T_MAX) e^{-T_MAX})^2; Theorem 5.1(c) needs this to be
    <= lam_min(P)/lam_max(P) with P = I + 4 Sigma = [[3 + beta^2, beta], [beta, 3]]."""
    P = np.array([[3 + beta ** 2, beta], [beta, 3]])
    ev = np.linalg.eigvalsh(P)
    return bool(((1 + beta * T_MAX) * np.exp(-T_MAX)) ** 2 <= ev[0] / ev[1])


betas = np.linspace(6.0, 14.0, 321)[1:]
t1s = np.array([t1(b) for b in betas])
assert all(tail_bound_ok(b) for b in betas)
assert np.all(np.diff(t1s) > 0), "t_1(beta) is expected to increase on this range"
print(f"t_1(beta): beta=6.025 -> {t1s[0]:.4f}, beta=7 -> {np.interp(7, betas, t1s):.4f}, "
      f"beta=8 -> {np.interp(8, betas, t1s):.4f}, beta=14 -> {t1s[-1]:.4f}")
for b in (7.0, 8.0):
    print(f"  t_1({b:g}) by direct bisection: {t1(b):.6f}")

# ---------------------------------------------------------------------------- figure
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["cmr10", "DejaVu Serif"],
    "mathtext.fontset": "cm",
    "axes.unicode_minus": False,
    "axes.formatter.use_mathtext": True,
    "font.size": 9,
    "hatch.linewidth": 0.6,
    "hatch.color": INK_2,
    "pdf.fonttype": 42,      # embed TrueType fonts (journals reject Type 3)
    "ps.fonttype": 42,
})

fig, ax = plt.subplots(figsize=(5.0, 2.7))
Y_MAX = 0.8
bx = np.concatenate([[0.0, 6.0], betas])
upper = np.full_like(bx, Y_MAX)
lower = np.concatenate([[0.0, 0.0], t1s])

# admissible region {(beta, t): K^t H_I subset H_I}
ax.fill_between(bx, lower, upper, color=BLUE, alpha=0.14, linewidth=0,
                label=r"$K^tH_I\subset H_I$ (Theorem 4.1)")
# part of it guaranteed by the sufficient condition (1.3) of [PSWPN]: beta <= 4
ax.fill_between([0, 4], [0, 0], [Y_MAX, Y_MAX], facecolor="none", edgecolor=INK_2, hatch="////",
                linewidth=0, label=r"covered by condition (1.3)")
# boundary t = t_1(beta)
ax.plot(betas, t1s, color=BLUE, linewidth=1.5, solid_capstyle="round")
ax.plot([6.0, betas[0]], [0.0, t1s[0]], color=BLUE, linewidth=1.5)

# thresholds beta = 4 (condition (1.3)) and beta = 6 (condition (1.5))
for x in (4.0, 6.0):
    ax.axvline(x, color=INK_2, linewidth=0.6)

# direct labels (sparing)
ax.text(11.0, 0.18, "not invariant", ha="center", va="center", color=INK)
ax.text(11.0, 0.68, "invariant", ha="center", va="center", color=INK)
bl = 9.0
ax.annotate(r"$t=t_1(\beta)$", xy=(bl, np.interp(bl, betas, t1s)), xytext=(7.6, 0.66),
            color=INK, ha="center", va="center",
            arrowprops=dict(arrowstyle="-", color=INK_2, linewidth=0.6, shrinkA=4, shrinkB=0))

ax.set_xlim(0, 14)
ax.set_ylim(0, Y_MAX)
ax.set_xlabel(r"$\beta$")
ax.set_ylabel(r"$t$", rotation=0, labelpad=8)
ax.set_xticks(range(0, 15, 2))
ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8])
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
for side in ("left", "bottom"):
    ax.spines[side].set_linewidth(0.6)
    ax.spines[side].set_color(INK_2)
ax.tick_params(colors=INK_2, width=0.6, labelcolor=INK)
ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=2, frameon=False, fontsize=8.5,
          handlelength=1.8, borderaxespad=0.0, columnspacing=1.6)

fig.tight_layout()
fig.savefig("fig_admissible_times.pdf")
fig.savefig("fig_admissible_times.png", dpi=200)
print("wrote fig_admissible_times.pdf / .png")
