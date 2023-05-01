import matplotlib.pyplot as plt
from numpy import *
from scipy.integrate import odeint

from eqmech import get_dynam

N = 3


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
        fun
        print('Using precomputed eqns...')
    except NameError:
        fun, sym = get_dynam(g, r, L, mp, mc, ret_sym=1)
        print(fun, sym)

    def f(t, x, u=0):
        x = asarray(x)
        xdot = zeros_like(x)
        xdot[:N] = x[N:]
        xdot[N:] = fun(*x, u).squeeze()
        return xdot

    def ctl(t, x, r=0):
        err = r - x[0]
        errdot = r - x[N]
        u = 10 * err + errdot
        return f(t, x, u)

    tf = 10
    t = linspace(0, tf, 100 * tf)
    x0 = [0.1, 0, 0, 0, 0, 0]
    y = odeint(f, x0, t, tfirst=1, args=(0.0,))
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
