#!/usr/bin/env python3

from yateto import *

def add(generator, dim, nbf, Nbf, nq, Nq):
    J = Tensor('J', (Nq,))
    G = Tensor('G', (dim, dim, Nq))
    K = Tensor('K', (Nbf,))
    W = Tensor('W', (Nq,))
    E = Tensor('E', (Nbf, Nq))
    Em = Tensor('Em', (Nq, Nbf))
    D_xi = Tensor('D_xi', (Nbf, dim, Nq))
    D_x = Tensor('D_x', D_xi.shape())
    A = Tensor('A', (Nbf, Nbf))

    generator.add('assembleVolume', [
        D_x['kiq'] <= G['eiq'] * D_xi['keq'],
        A['kl'] <= J['q'] * W['q'] * K['m'] * Em['qm'] * D_x['kiq'] * D_x['liq']
    ])

    g = Tensor('g', (dim, dim, nq))
    n = Tensor('n', (dim, nq))
    nl = Tensor('nl', (nq,))
    w = Tensor('w', (nq,))
    e = [Tensor('e({})'.format(x), (Nbf, nq)) for x in range(2)]
    em = [Tensor('em({})'.format(x), (nq, Nbf)) for x in range(2)]
    d_xi = [Tensor('d_xi({})'.format(x), (Nbf, dim, nq)) for x in range(2)]
    d_x = [Tensor('d_x({})'.format(x), (Nbf, dim, nq)) for x in range(2)]
    a = [[Tensor('a({},{})'.format(x, y), (Nbf, Nbf)) for y in range(2)] for x in range(2)]
    c0 = [Scalar('c0{}'.format(x)) for x in range(2)]
    c1 = [Scalar('c1{}'.format(x)) for x in range(2)]
    c2 = [Scalar('c2{}'.format(x)) for x in range(2)]

    def surface(x, y):
        return a[x][y]['kl'] <= c0[y] * w['q'] * d_x[x]['kiq'] * n['iq'] * e[y]['lq'] + \
                                c1[x] * w['q'] * d_x[y]['liq'] * n['iq'] * e[x]['kq'] + \
                                c2[abs(y-x)] * w['q'] * e[x]['kq'] * e[y]['lq'] * nl['q']

    surfaceKernelsLocal = [
        d_x[0]['kiq'] <= K['m'] * em[0]['qm'] * g['eiq'] * d_xi[0]['keq'],
        surface(0, 0)
    ]
    surfaceKernelsNeighbour = [
        d_x[1]['kiq'] <= K['m'] * em[1]['qm'] * g['eiq'] * d_xi[1]['keq'],
        surface(0, 1),
        surface(1, 0),
        surface(1, 1)]
    generator.add('assembleFacetLocal', surfaceKernelsLocal)
    generator.add('assembleFacetNeighbour', surfaceKernelsNeighbour)

    b = Tensor('b', (Nbf,))
    F = Tensor('F', (Nq,))
    generator.add('rhsVolume', b['k'] <= J['q'] * W['q'] * E['kq'] * F['q'])

    f = Tensor('f', (nq,))
    generator.add('rhsFacet', b['k'] <= \
            c1[0] * w['q'] * K['m'] * em[0]['qm'] * g['eiq'] * d_xi[0]['keq'] * n['iq'] * f['q'] + \
            c2[0] * w['q'] * e[0]['kq'] * nl['q'] * f['q'])

