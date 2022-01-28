import numpy as np


def add_integration_dim(func):
    def wrapper(*args):
        print(func(*args))
        return func()[None, :] if np.ndim(func()) == 2 else func()
    return wrapper


@add_integration_dim
def primary(fuck):
    print(fuck)
    return np.zeros((40, 50))


if __name__ == '__main__':
    p = primary('asdf')
    print(p.shape)

