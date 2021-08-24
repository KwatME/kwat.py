from .drop import drop


def drop_until(da, ax=None, **ke):

    sh1 = da.shape

    if ax is None:

        ax = int(sh1[0] < sh1[1])

    re = False

    while True:

        da = drop(da, ax, **ke)

        sh2 = da.shape

        if re and sh1 == sh2:

            return da

        sh1 = sh2

        if ax == 0:

            ax = 1

        elif ax == 1:

            ax = 0

        re = True
