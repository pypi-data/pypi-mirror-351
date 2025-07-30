import numpy as np
from numba import njit


@njit
def fz_thread_profile(pnt, a=1.0):
    y = pnt[1]
    if abs(y) > 2*a:
        return y / 2 / a
    x = pnt[0] * 2 * np.pi
    p = a / (-0.5 * np.sin(x) + 2**-20 - 2**-19 * np.sign(np.sin(x)))
    q = y / (np.sin(x) + 2**-20 + 2**-19 * np.sign(np.sin(x))) - 1
    return -p / 2 - np.sign(np.sin(x)) * (max(0, (p / 2) ** 2 - q)) ** 0.5


@njit
def fz_thread(pnt, radius, n=1, profile_depth=1.0, a=1.0):
    x, y, z = pnt
    ang = -np.atan2(y, x)
    r = (x**2 + y**2) ** 0.5
    r_arg = (r - radius)/profile_depth
    z_arg = z + n * ang / 2 / np.pi
    return profile_depth * fz_thread_profile((z_arg, r_arg), a)

