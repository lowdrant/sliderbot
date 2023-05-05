"""
Motor dynamics

A. Hughes and B. Drury, "Electric Motors and Drives," ISBN: 978-0-08-102615-1
"""
__all__ = ['Motor']


class Motor:
    """DC Motor parameter storage class. Provides some basic calculation
    helpers.

    __call__ method is an ODE on armature current

    INPUTS:
        L -- float -- motor inductance
        R -- float -- coil resistance
        k -- float -- motor constant
    """

    def __init__(self, L, R, k):
        self.L, self.R, self.k = L, R, k

    def __call__(self, I, V, w):
        E = self.k * w
        Idot = (V - (self.R * I + E)) / self.L
        return Idot

    def torque(self, I):
        """motor current to torque"""
        return self.k * I

    def emf(self, w):
        """shaft speed to internal EMF"""
        return self.k * w

    def v2i_ss(self, V):
        """steady-state current calculation"""
        return V / self.R
