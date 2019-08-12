import numpy as np


def get_crossing(xa, ya, xb, yb, xc, yc, xd, yd):
    a = np.matrix(
        [
            [xb - xa, -(xd - xc)],
            [yb - ya, -(yd - yc)]
        ]
    )
    delta = np.linalg.det(a)
    if np.fabs(delta) < 1e-6:
        print(delta)
        return None
    c = np.matrix(
        [
            [xc - xa, -(xd - xc)],
            [yc - ya, -(yd - yc)]
        ]
    )
    d = np.matrix(
        [
            [xb - xa, xc - xa],
            [yb - ya, yc - ya]
        ]
    )
    lamb = np.linalg.det(c) / delta
    miu = np.linalg.det(d) / delta
    if 1 >= lamb >= 0 and 0 <= miu <= 1:
        x = xc + miu * (xd - xc)
        y = yc + miu * (yd - yc)
        return (x, y)
    else:
        return None


point = get_crossing(0, 0, 320, 320, 0, 320, 320, 0)
print point
