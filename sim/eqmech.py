"""
Sliderbot mechanical dynamics construction
"""
__all__ = ['get_dynam', 'solve_dynam']
from pathlib import Path

from sympy import *

from helpers import *


def get_dynam(g, r, L, mp, mc, eq=None, printlog=True, ret_sym=False):
    """Construct numeric callable for sliderbot ODE
    INPUTS:
        g -- float -- gravitational acceleration
        r -- float -- pendulum length
        L -- float -- disk radius
        mp -- float -- disk mass
        mc -- float -- cart mass
        eq -- optional, filename or sympy equation --
        printlog -- optional, bool -- print status of solving, default:True
        ret_sym -- optional, bool -- return symbolic equation, default:False
    OUTPUTS:
        Callable
        Callable, symbolic equation if ret_sym==True

    """
    consts_dict = {'g': g, 'r': r, 'L': L, 'mp': mp, 'mc': mc}
    syms = symbols('phi theta x phidot thetadot xdot u')
    if eq is None:
        print('Solving sliderbot dynamics...')
        eq = solve_dynam()
    elif (eq is str) or (eq is Path):
        print(f'Loading sliderbot dynamics from {eq}')
        eq = loadeq(eq)
    print('Done!')
    eq = eq.subs(consts_dict)
    fun = lambdify(syms, eq, 'numpy')
    if ret_sym:
        return fun, eq
    return fun


def solve_dynam(ret_mats=False):
    """Solve for sliderbot mechanical dynamics
    INPUTS:
        ret_mats -- bool, optional -- return component matrices, default:False
    OUTPUTS:
        Vector ODE
        Vector ODE, (D,Cqdot,G,B) if ret_mats==True


    Pedantically, the equations describe two masses attached to the end
    of the pendulum, but their mass distibution is such that this is equivalent
    to a disk of mass M and radius L.
    """
    init_printing()
    N, M = 3, 4
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
    x1 = r * sin(phi) + L * cos(phi - theta) + x
    x2 = r * sin(phi) - L * cos(phi - theta) + x
    y1 = r * cos(phi) - L * sin(phi - theta)
    y2 = r * cos(phi) + L * sin(phi - theta)
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
    # - observe that:
    #     KE := qdot.T @ D @ qdot
    #     qdot := (phidot, thetadot, xdot).T
    # - so we can treat KE as a polynomial where the coefficients of the
    #   polynomial are the entries of D;
    D = zeros(N, N)
    for i in range(N):
        D[i, i] = KE.coeff(qdot[i]**2)
    D[0, 1] = KE.coeff(phi.diff(t) * theta.diff(t)) / 2
    D[0, 2] = KE.coeff(phi.diff(t) * x.diff(t)) / 2
    D[1, 2] = KE.coeff(theta.diff(t) * x.diff(t)) / 2
    D[1, 0] = D[0, 1]
    D[2, 0] = D[0, 2]
    D[2, 1] = D[1, 2]
    assert expand(qdot.T * D * qdot)[0] == expand(KE), 'inertia matrix error'

    # Gravity, Coriolis, Input Matrix
    G = PE.diff(q)
    Ccor = diff(D * qdot, q.T).reshape(N, N).tomatrix().T * qdot
    Cfug = diff(qdot.T * D * qdot, q.T).reshape(1, N).tomatrix().T / 2
    Cqdot = Ccor - Cfug
    B = Matrix([0, symbols('u') / (mp * L**2), 0])

    # Convert to Vars for Numeric Solving
    sd = {phi: 'phi', theta: 'theta', x: 'x', phi.diff(
        t): 'phidot', theta.diff(t): 'thetadot', x.diff(t): 'xdot'}
    D, Cqdot, G, B = D.subs(sd), Cqdot.subs(sd), G.subs(sd), B.subs(sd)
    Dinv = D.inv()
    fun = simplify(-Dinv * Cqdot - Dinv * G + Dinv * B)
    if ret_mats:
        return fun, (D, Cqdot, G, B)
    return fun
