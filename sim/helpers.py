"""
Misc helper functions
"""
__all__ = ['ipychk', 'saveeq', 'loadeq', 'q2c']
import matplotlib.pyplot as plt
from numpy import c_, cos, newaxis, r_, sin, zeros_like
from sympy import sympify


def ipychk():
    """If ipython session, enable interactive plotting. Else `plt.show()`"""
    try:
        get_ipython()
        plt.ion()
    except NameError:
        plt.ioff()
        plt.show()


def saveeq(fn, eq):
    """Save equation to textfile. Will overwrite file.
    INPUTS:
        fn -- filename to save eq
        eq -- sympy equation
    OUTPUTS:
        Return value of file.write
    """
    with open(fn, 'w') as f:
        ret = f.write(str(eq))
    return ret


def loadeq(fn):
    """Load equation from text file.
    INPUTS:
        fn -- filename
    OUTPUTS:
        sympy equation
    """
    with open(fn, 'r') as f:
        eq = f.read()
    return sympify(eq)


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
