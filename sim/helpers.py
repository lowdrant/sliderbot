"""
Misc helper functions
"""
__all__ = ['ipychk', 'saveeq', 'loadeq']
import matplotlib.pyplot as plt
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
