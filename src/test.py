#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy


items = {}

for i in xrange(10):
    items.update({i: {'z': i}})

print items

def alg(a, v):
    b = copy.deepcopy(a)
    a.append(v)

    maxV = max(a)


def main():
    pass

if __name__ == '__main__':
    main()
