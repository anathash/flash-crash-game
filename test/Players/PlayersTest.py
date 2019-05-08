import unittest

from numpy import sort


def to_string_list(orders):
    l = []
    for item in orders:
        l.append(list(sort(list(map(lambda x: str(x), item)))))
    l.sort(key=lambda x: (len(x), x[0]))
    return l


if __name__ == '__main__':
    unittest.main()


