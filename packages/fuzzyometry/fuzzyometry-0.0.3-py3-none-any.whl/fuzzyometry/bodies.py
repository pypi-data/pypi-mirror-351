from numba import njit
import numpy as np


@njit
def _fz_cuboid_or(p, s):
    x, y, z = p
    w, l, h = s
    d = (
        min(w - x, w + x, 0) ** 2
        + min(l - y, l + y, 0) ** 2
        + min(h - z, h + z, 0) ** 2
    ) ** 0.5
    return d


@njit
def _fz_corner_ir_2d(x, y):
    if x > 2 * y:
        return -y
    if y > 2 * x:
        return -x
    return -2 / 7 * (x + y) - ((-2 / 7 * (x + y)) ** 2 - (x**2 + y**2) / 7) ** 0.5


@njit
def _fz_corner_ir_3d(x, y, z):
    p = -4 / 11 * (x + y + z)
    q = (x**2 + y**2 + z**2) / 11
    if (p / 2) ** 2 - q < 0:
        return 2
    return -(-p / 2 + ((p / 2) ** 2 - q) ** 0.5)


@njit
def _fz_cuboid_ir(p, s):
    x, y, z = p
    w, l, h = s
    xd = min(w - x, w + x)
    yd = min(l - y, l + y)
    zd = min(h - z, h + z)
    r = _fz_corner_ir_3d(xd, yd, zd)
    if -2 * r < max(xd, yd, zd):
        return max(
            _fz_corner_ir_2d(xd, yd), _fz_corner_ir_2d(yd, zd), _fz_corner_ir_2d(xd, zd)
        )
    return r


@njit
def fz_cuboid(pnt, dimensions, r=0.):
    #s = [e / 2 - r for e in dimensions]
    s = np.array(dimensions) /2. - r
    x, y, z = pnt
    w, l, h = s
    xd = min(w - x, w + x)
    yd = min(l - y, l + y)
    zd = min(h - z, h + z)
    if 0 > min(xd, yd, zd):
        return _fz_cuboid_or(pnt, s) - r
    return _fz_cuboid_ir(pnt, s) - r


@njit
def fz_circle(p, r):
    x, y = p[:2]
    return (x**2 + y**2) ** 0.5 - r


@njit
def fz_sphere(p, r):
    x, y, z = p[:3]
    return (x**2 + y**2 + z**2) ** 0.5 - r
