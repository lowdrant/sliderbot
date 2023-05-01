"""
Sliderbot simulation CLI. Currently a unit test
"""
from argparse import ArgumentParser

import matplotlib.pyplot as plt
from numpy import arange, asarray, zeros_like
from scipy.integrate import odeint

from eqmech import get_dynam
from helpers import *

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


parser = ArgumentParser('sliderbot simulator')
parser.add_argument('--g', type=float, default=10,
                    help='gravitational accel, default:10')
parser.add_argument('--r', type=float, default=1,
                    help='reaction wheel radius, default:1')
parser.add_argument('--L', type=float, default=0.1,
                    help='pendulum length, default:0.1')
parser.add_argument('--mp', type=float, default=1,
                    help='pendulum bob mass, default:1')
parser.add_argument('--mc', type=float, default=1, help='cart mass, default:1')
parser.add_argument('--tf', type=float, default=10,
                    help='simulation runtime, default:10')
parser.add_argument('--dt', type=float, default=0.01,
                    help='simulation timestep, default:0.01')
parser.add_argument('--x0', type=str, default='0.1,0,0,0,0,0',
                    help='init cond CSV: phi,theta,x, phidot,thetadot,xdot, default:0.1,0,0,0,0,0')
parser.add_argument('--fn', type=str, default=None,
                    help='filename of sliderbot ODE rawtext, default:None')

if __name__ == '__main__':
    args = parser.parse_args()
    t = arange(0, args.tf, args.dt)
    x0 = [float(v) for v in args.x0.replace(' ', '').split(',')]
    fun, sym = get_dynam(args.g, args.r, args.L, args.mp,
                         args.mc, eq=args.fn, ret_sym=1)

    def f(t, x, u=0):
        """dynamics callable"""
        x = asarray(x)
        xdot = zeros_like(x)
        xdot[:N] = x[N:]
        xdot[N:] = fun(*x, u).squeeze()
        return xdot

    def ctl(t, x, r=0):
        """control loop callable"""
        err = r - x[0]
        errdot = r - x[N]
        u = 10 * err + errdot
        return f(t, x, u)

    y = odeint(f, x0, t, tfirst=1, args=(0.0,))
    myplot(t, y, args.r, args.L)