import matplotlib.pyplot as plt
import sympy as sm
from numpy import *
from numpy.linalg import pinv
from scipy.integrate import odeint
from sympy import (Derivative, Function, Matrix, expand, init_printing,
                   simplify, symarray, symbols, trigsimp)

N = 3


def get_dynam():
    """symbolically compute dynamics eqns"""
    init_printing()
    M = 4
    t, r, L, mp, mc, g = symbols('t r L mp mc g')

    # Coordinates
    phi = Function('phi')
    phi = phi(t)
    theta = Function('theta')
    theta = theta(t)
    x = Function('x')
    x = x(t)
    q = Matrix([phi, theta, x])
    qdot = q.diff(t)

    # Kinematics
    x1 = r * sm.sin(phi) + L * sm.cos(phi - theta) + x
    x2 = r * sm.sin(phi) - L * sm.cos(phi - theta) + x
    y1 = r * sm.cos(phi) - L * sm.sin(phi - theta)
    y2 = r * sm.cos(phi) + L * sm.sin(phi - theta)
    p = Matrix([x1, y1, x2, y2])
    J = p.diff(q.T).reshape(N, M).tomatrix().T
    v = J * qdot

    # Energy
    KEc = mc * x.diff(t)**2 / 2
    KEp = mp * (x1.diff(t)**2 + y1.diff(t)**2 +
                x2.diff(t)**2 + y2.diff(t)**2) / 2
    KE = expand(simplify(expand(KEp + KEc)))
    PE = mp / 2 * g * (y1 + y2)

    # Build Inertia Matrix
    # - qdot = (phidot, thetadot, xdot).T
    D = sm.zeros(N, N)
    for i in range(N):
        D[i, i] = KE.coeff(qdot[i]**2)
    D[0, 1] = KE.coeff(phi.diff(t) * theta.diff(t)) / 2
    D[0, 2] = KE.coeff(phi.diff(t) * x.diff(t)) / 2
    D[1, 2] = KE.coeff(theta.diff(t) * x.diff(t)) / 2
    D[1, 0] = D[0, 1]
    D[2, 0] = D[0, 2]
    D[2, 1] = D[1, 2]
    assert expand(qdot.T * D * qdot)[0] == expand(KE), 'inertia matrix error'
    # Dynamics Matrices
    G = PE.diff(q)
    Ccor = sm.diff(D * qdot, q.T).reshape(N, N).tomatrix().T * qdot
    Cfug = sm.diff(qdot.T * D * qdot, q.T).reshape(1, N).tomatrix().T / 2
    Cqdot = Ccor - Cfug
    B = Matrix([0, 1 / (mp * L**2), 0])

    # Represent in Terms of Variables
    sd = {phi: 'phi', theta: 'theta', x: 'x', phi.diff(
        t): 'phidot', theta.diff(t): 'thetadot', x.diff(t): 'xdot'}
    D, Cqdot, G, B = D.subs(sd), Cqdot.subs(sd), G.subs(sd), B.subs(sd)
    return D, Cqdot, G, B


def q2c(phi, theta, x, r, L):
    """coords to xy
    `plt.plot(*q2c(args))` should work out of the box
    OUT:
        (x,y)
        x := (xorigin, xpivot, x1, xpivot, x2)
    """
    x1 = r * sin(phi) + L * cos(phi - theta) + x
    x2 = r * sin(phi) - L * cos(phi - theta) + x
    y1 = r * cos(phi) - L * sin(phi - theta)
    y2 = r * cos(phi) + L * sin(phi - theta)
    xp = (x1 + x2) / 2
    yp = (y1 + y2) / 2
    x = c_[x, xp, x1, xp, x2]  # vstack([[x, xp, x1, xp, x2]])
    y = c_[zeros_like(yp), yp, y1, yp, y2]
    return r_[x[newaxis], y[newaxis]]


if __name__ == '__main__':
    g, r, L, mp, mc = 10, 1, 0.1, 1, 1
    try:
        Dn, Gn, Bn, Cqdotn
        print('Using precomputed eqns')
    except NameError:
        print('Deriving matrices...')
        D, Cqdot, G, B = get_dynam()
        print('Done!')
        print('Substituting constants...')
        sd = {'g': g, 'r': r, 'L': L, 'mp': mp, 'mc': mc}
        D, Cqdot, G, B = D.subs(sd), Cqdot.subs(sd), G.subs(sd), B.subs(sd)
        print('Done!')
        print('Lambdifying...')
        syms = symbols('phi theta x phidot thetadot xdot u')
        Dinv = D.inv()
        fun = simplify(-Dinv * Cqdot - Dinv * G + Dinv * B * syms[-1])
        Dn = sm.lambdify(syms, D, 'numpy')
        Cqdotn = sm.lambdify(syms, Cqdot, 'numpy')
        Gn = sm.lambdify(syms, G, 'numpy')
        Bn = sm.lambdify(syms, B, 'numpy')
        print('Done!')

    def f(t, x, u=0):
        x = asarray(x)
        xdot = zeros_like(x)
        xdot[:N] = x[N:]
        Dinv = pinv(Dn(*x, u))
        Cqdot = Cqdotn(*x, u)
        G = Gn(*x, u)
        B = Bn(*x, u)
        xdot[N:] = (Dinv @ (B * u - Cqdot - G)).squeeze()
        return xdot

    def ctl(t, x, r=0):
        err = r - x[0]
        errdot = r - x[N]
        u = 10 * err + errdot
        return f(t, x, u)

    tf = 1
    t = linspace(0, tf, 100 * tf)
    x0 = [0.1, 0, 0, 0, 0, 0]
    y = odeint(ctl, x0, t, tfirst=1, args=(0.0,))
    xy = q2c(*y.T[:N], r, L)

    f = plt.figure(1)
    f.clf()
    ax1 = f.add_subplot(231)
    ax2 = f.add_subplot(234, sharex=ax1)
    ax3 = plt.subplot2grid((2, 2), (0, 1), rowspan=2, colspan=2, fig=f)
    ax2.set_xlabel('t [sec]')
    ax3.set_xlabel('x')
    ax3.set_ylabel('y')

    ax1.plot(t, y[:, 0], '-', label='$\\phi$')
    ax1.plot(t, y[:, N], '-', label='$\\dot{\\phi}$')
    ax1.plot(t, y[:, 2], '-', label='$x$')
    ax1.plot(t, y[:, 5], '-', label='$\\dot{x}$')

    ax2.plot(t, y[:, 0] - y[:, 1], '-', label='$\\phi-\\theta$')
    ax2.plot(t, y[:, 1], '-', label='$\\theta$')
    ax2.plot(t, y[:, N + 1], '-', label='$\\dot{\\theta}$')

    ax3.plot(*xy[..., 2], '-', label='mass 1', c='tab:orange')
    ax3.plot(*xy[..., -1], '-', label='mass 2', c='tab:green')
    ax3.plot(*xy[..., 1], '-', label='pivot', c='tab:blue', lw=3)
    ax3.plot(*xy[..., 0], '-', label='base', c='k', lw=3)
    ax3.plot(*xy[:, [0, -1], 1], 'X', c='tab:blue', ms=10)
    ax3.plot(*xy[:, [0, -1], 2], 'X', c='tab:orange', ms=10)
    ax3.plot(*xy[:, [0, -1], -1], 'X', c='tab:green', ms=10)
    ax3.plot(*xy[:, [0, -1], 0], 'kX', ms=10)

    for ax in f.axes:
        ax.grid()
        ax.legend(loc='center right')

    ax3.set_aspect('equal')
    # f.suptitle('PD controller')

    try:
        get_ipython()
        plt.ion()
    except NameError:
        plt.ioff()
        plt.show()
