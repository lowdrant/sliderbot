"""
Sliderbot simulation CLI. Currently a unit test
"""
from argparse import ArgumentParser

import matplotlib.pyplot as plt
from numpy import arange, asarray, zeros_like
from scipy.integrate import odeint

from eqmech import get_dynam, solve_dynam
from helpers import *
from motor import Motor

N = 3


def myplot(t, y, r, L):
    """Plot sim output for time `t` and state `y`"""
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

    ipychk()


def create_parser():
    """functionalized for code folding"""
    parser = ArgumentParser('sliderbot simulator')
    parser.add_argument('--g', type=float, default=10,
                        help='gravitational accel, default:10')
    parser.add_argument('--r', type=float, default=1,
                        help='reaction wheel radius, default:1')
    parser.add_argument('--L', type=float, default=0.1,
                        help='pendulum length, default:0.1')
    parser.add_argument('--mp', type=float, default=1,
                        help='pendulum bob mass, default:1')
    parser.add_argument('--mc', type=float, default=1,
                        help='cart mass, default:1')
    parser.add_argument('--tf', type=float, default=1,
                        help='simulation runtime, default:1')
    parser.add_argument('--dt', type=float, default=0.01,
                        help='simulation timestep, default:0.01')
    parser.add_argument('--x0', type=str, default='0.1,0,0,0,0,0',
                        help='init cond CSV: phi,theta,x, phidot,thetadot,xdot, default:0.1,0,0,0,0,0')
    parser.add_argument('--fn', type=str, default=None,
                        help='filename of sliderbot ODE rawtext, default:None')
    parser.add_argument('--mtr', action='store_true',
                        help='use simple motor model')
    parser.add_argument('--full-mtr', action='store_true',
                        help='dynamic motor model')
    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    if args.full_mtr:
        raise NotImplementedError('Full motor model not implemented')
    t = arange(0, args.tf, args.dt)
    x0 = [float(v) for v in args.x0.replace(' ', '').split(',')]
    try:
        fun
    except NameError:
        sym, mats = solve_dynam(ret_mats=1)
        fun, sym = get_dynam(args.g, args.r, args.L, args.mp,
                             args.mc, eq=sym, ret_sym=1)

    mtr = Motor(1, 1, 1)

    def mtrsimple(t, x, v=0):
        """simple motor model"""
        i = mtr.v2i_ss(v)
        return mtr.torque(i)

    def f(t, x, u=0):
        """dynamics callable"""
        x = asarray(x)
        xdot = zeros_like(x)
        xdot[:N] = x[N:]
        if args.mtr:
            u = mtrsimple(t, x, u)
        xdot[N:] = fun(*x, u).squeeze()
        return xdot

    def ctl(t, x, r=0):
        """control loop callable"""
        err = r - x[0]
        errdot = r - x[N]
        u = 10 * err + errdot
        return f(t, x, u)

    y = odeint(ctl, x0, t, tfirst=1, args=(0.0,))
    myplot(t, y, args.r, args.L)
