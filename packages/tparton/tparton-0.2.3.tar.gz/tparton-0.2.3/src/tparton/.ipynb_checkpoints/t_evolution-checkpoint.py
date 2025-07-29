# Copyright Congzhou M Sha 2024
import numpy as np
from scipy.integrate import simpson
from numpy._core.multiarray import interp
from scipy.integrate import odeint
from scipy.special import spence

def evolve(
    pdf,
    Q0_2=0.16,
    Q2=5.0,
    l_QCD=0.25,
    n_f=3,
    n_t=100,
    n_z=500,
    morp='plus',
    order=2,
    logScale=False,
    verbose=False,
    Q0_2_a=91.1876 ** 2,
    a0=0.118 / 4 / np.pi,
    alpha_num=True
):
    '''
    Evolve the transversity PDF
    ***************************
    Parameters:
        pdf: array-like
            the input first moment (assumed to be at x
            evenly distributed on [0, 1] inclusive)

        Q0_2: float
            initial Q^2

        Q2: float
            final evolved Q^2

        l_QCD: float
            QCD energy scale

        n_f: int
            number of flavors

        n_t: int
            number of time steps

        n_z: int
            the number of z steps to take in integral

        morp: 'plus' or 'minus'
            type of pdf (plus or minus type)

        order: int
            1: first-order
            2: second-order

        logScale: bool
            z is log scaled if True

        verbose: bool
            print progress if True
    '''
    # Calculate the color constants
    if pdf.shape[-1] == 1:
        xs = np.linspace(0, 1, len(pdf))
    else:
        xs, pdf = pdf[:, 0], pdf[:, 1]
    print(xs, pdf)
    sign = 1 if morp == 'plus' else -1
    lnlam = 2 * np.log(l_QCD)

    pi = np.pi
    CF = 4 / 3
    CG = 3
    TR = 1/2
    beta0 = 11 / 3 * CG - 4 / 3 * TR * n_f
    beta1 = 34 / 3 * CG ** 2 - 10 / 3 * CG * n_f - 2 * CF * n_f

    tmin = np.log(Q0_2)
    tmax = np.log(Q2)
    ts = np.linspace(tmin, tmax, n_t)

    def alp2pi(t):
        dlnq2 = t - lnlam
        alpha = 4 * pi / beta0 / dlnq2
        alpha_factor = 1 if order == 1 else (1 - beta1 * np.log(dlnq2) / beta0**2 / dlnq2)
        alpha_factor /= (2 * pi)
        return alpha_factor * alpha
    
    alp2pi = alp2pi(ts)
    
    if order == 2:
        ode = lambda x, a: -beta0 * a * a - beta1 * a * a * a
    else:
        ode = lambda x, a: -beta0 * a * a

    # SciPy requires that the times be monotonic
    less = ts < np.log(Q0_2_a)
    ts_less = ts[less]
    ts_greater =ts[~less]

    alp2pi_num_less = odeint(ode, a0, [np.log(Q0_2_a)] + list(ts_less[::-1]), tfirst=True).flatten() * 2
    alp2pi_num_less = alp2pi_num_less[-1:0:-1]
    alp2pi_num_greater = odeint(ode, a0, [np.log(Q0_2_a)] + list(ts_greater), tfirst=True).flatten() * 2
    alp2pi_num_greater = alp2pi_num_greater[1:]
    alp2pi_num = list(alp2pi_num_less) + list(alp2pi_num_greater)

    if alpha_num:
        alp2pi = alp2pi_num


    def splitting(z):
        # Calculate the splitting functions
        p0 = CF * 2 * z / (1 - z+1e-100)
        p0pf = -CF * 2 / (1 - z+1e-100)

        z1 = 1 / (1 + z)
        z2 = z / (1 + z)
        dln1 = np.log(z1)
        dln2 = np.log(z2)
        # SciPy convention for Spence (aka dilogarithm) differs from paper
        s2 = -spence(z2) + spence(z1) - (dln1 ** 2 - dln2 ** 2) * 0.5

        if order == 2:
            omz = 1 - z
            lnz = np.log(z)
            lno = np.log(omz+1e-100)
            dP0 = 2 * z / (omz+1e-100)
            pp1 = 1 - z - (3 / 2 + 2 * lno) * lnz * dP0
            pp2 = -omz + (67/9 + 11/3 * lnz + lnz**2 - pi**2 / 3) * dP0
            pp3 = (-lnz - 5/3) * dP0
            pp4 = -omz + 2 * s2 * 2 * -z / (1 + z)

            # Eq. 43 in Vogelsang
            dpqq = CF * CF * pp1 + CF * CG * 0.5 * pp2 + 2 / 3 * CF * TR * n_f * pp3

            # Eq. 44 in Vogelsang
            dpqqb = CF * (CF-CG / 2) * pp4
            p1 = dpqq + sign * dpqqb
            p1[0] = 0
        else:
            p1 = 0
        omz = 1 - z

        # The plus function contributions upon integration for the entire range of z in [x, 1]
        # f(1) in Eq. A.8
        # These terms correspond to -f(1)/(1-z) in Eq. A.8
        p2plus = -(67/9-pi**2/3) * 2 / (omz+1e-100)
        p3plus = 5 / 3 * 2 / (omz+1e-100)
        p1pf = CF * CG / 2 * p2plus + 2 / 3 * CF * TR * n_f * p3plus

        p0[-1] = 0
        p0pf[-1] = 0
        if order == 2:
            p1[-1] = 0
            p1pf[-1] = 0

        # The zero order plus and delta function contributions to the integrals
        plus0 = CF * 2
        del0 = CF * 3/2

        if order == 2:
            zta = 1.2020569031595943
            # The delta function contributions for the entire range of z in [x, 1]
            del1 = CF * CF * (3 / 8 - pi**2 / 2 + 6 * zta) + \
                CF * CG / 2 * (17 / 12 + 11 * pi**2 /9 - 6 * zta) - \
                2 / 3 * CF * TR * n_f * (1 / 4 + pi**2 / 3)
            # p2pl, p3pl correspond to the f(1) in Eq. A.8
            p2pl = (67 / 9 - pi**2/3) * 2
            p3pl = -5 / 3 * 2
            plus1 = CF * CG / 2 * p2pl + 2 / 3 * CF * TR * n_f * p3pl
        else:
            plus1 = 0
            del1 = 0
        return p0, p1, p0pf, p1pf, plus0, del0, plus1, del1

    def integrate(pdf, i, z, alp):
        if len(z) == 0:
            return 0
        p0, p1, p0pf, p1pf, plus0, del0, plus1, del1 = splitting(z)
        p0[-1] = p0pf[-1] = 0
        if order == 2:
            p1[-1] = p1pf[-1] = 0

        # Implement Eq. A.5 in Hirai
        # The interp function interpolates pdf(x / z)
        # In the FORTRAN code, the first part of this equation is not divided by z
        func = ((p0 + (alp * p1 if order == 2 else 0)) * interp(xs[i] / z, xs, pdf)) + \
            (p0pf + (alp * p1pf if order == 2 else 0)) * pdf[i]

        lno = np.log(1 - xs[i])
        estimate = simpson(func, x=z) + (plus0 * lno + del0) * pdf[i]
        if order == 2:
            estimate += alp * (plus1 * lno + del1) * pdf[i]

        return estimate

    dt = (tmax - tmin) / n_t
    res = np.copy(pdf)

    for i, (t, alp) in enumerate(zip(ts, alp2pi)):
        if verbose:
            print(i+1, ' of ', len(ts), 'time steps')
        inc = np.array([integrate(res, index, \
            np.power(10, np.linspace(np.log10(xs[index]), 0, n_z + 1)) if logScale else np.linspace(xs[index], 1, n_z + 1), \
                alp) for index in range(1, len(xs)-1)])
        inc = np.pad(inc, 1)
        res += dt * inc * alp
    return np.stack((xs, res))


def main():
    import argparse, sys
    parser = argparse.ArgumentParser(description='Evolution of the nonsinglet transversity PDF, according to the DGLAP equation.')
    parser.add_argument('type',action='store',type=str,help='The method you chose')
    parser.add_argument('input', action='store', type=str,
                    help='The CSV file containing (x,x*PDF(x)) pairs on each line. If only a single number on each line, we assume a linear spacing for x between 0 and 1 inclusive')
    parser.add_argument('Q0sq', action='store', type=float, help='The starting energy scale in units of GeV^2')
    parser.add_argument('Qsq', action='store', type=float, help='The ending energy scale in units of GeV^2')
    parser.add_argument('--morp',  action='store', nargs='?', type=str, default='plus', help='The plus vs minus type PDF (default \'plus\')')
    parser.add_argument('-o', action='store', nargs='?', type=str, default='out.dat', help='Output file for the PDF, stored as (x,x*PDF(x)) pairs.')
    parser.add_argument('-l', metavar='l_QCD', nargs='?', action='store', type=float, default=0.25, help='The QCD scale parameter (default 0.25 GeV^2). Only used when --alpha_num is False.')
    parser.add_argument('--nf', metavar='n_f', nargs='?', action='store', type=int, default=5, help='The number of flavors (default 5)')
    parser.add_argument('--nc', metavar='n_c', nargs='?', action='store', type=int, default=3, help='The number of colors (default 3)')
    parser.add_argument('--order', metavar='order', nargs='?', action='store', type=int, default=2, help='1: leading order, 2: NLO DGLAP (default 2)')
    parser.add_argument('--nt', metavar='n_t', nargs='?', action='store', type=int, default=100, help='Number of steps to numerically integrate the DGLAP equations (default 100)')
    parser.add_argument('--nz', metavar='n_z', nargs='?', action='store', type=int, default=1000, help='Number of steps for numerical integration (default 1000)')
    parser.add_argument('--logScale', nargs='?', action='store', type=bool, default=True, help='True if integration should be done on a log scale (default True)')
    parser.add_argument('--delim', nargs='?', action='store', type=str, default=' ', help='Delimiter for data file (default \' \'). If given without an argument, then the delimiter is whitespace (i.e. Mathematica output.)')
    parser.add_argument('--alpha_num', metavar='alpha_num', nargs='?', action='store', type=bool, default=True, help='Set to use the numerical solution for the strong coupling constant, numerically evolved at LO or NLO depending on the --order parameter.')
    parser.add_argument('--Q0sqalpha', metavar='Q0sqalpha', nargs='?', action='store', type=float, default=91.1876**2, help='The reference energy squared at which the strong coupling constant is known. Default is the squared top quark mass. Use in conjunction with --a0. Only used when --alpha_num is True.')
    parser.add_argument('--a0', metavar='a0', nargs='?', action='store', type=float, default=0.118 / 4 / np.pi, help='The reference value of the strong coupling constant a = alpha / (4 pi) at the corresponding reference energy --Q0sqalpha. Default is 0.118 / (4 pi), at energy Q0sqalpha = top quark mass squared. Only used when --alpha_num is True.')
    parser.add_argument('-v', nargs='?', action='store', type=bool, default=False, help='Verbose output (default False)')


    args = parser.parse_args()
    f = args.input
    if args.delim is None:
        pdf = np.genfromtxt(f)
        args.delim = ' '
    else:
        pdf = np.genfromtxt(f, delimiter=args.delim)
    Q0sq = args.Q0sq
    Qsq = args.Qsq
    morp = args.morp
    l = args.l
    nf = args.nf
    nc = args.nc
    order = args.order
    nt = args.nt
    nz = args.nz
    logScale = args.logScale
    alpha_num = args.alpha_num
    Q0sqalpha = args.Q0sqalpha
    a0 = args.a0
    verbose = args.v

    res = evolve(pdf,
        Q0_2=Q0sq,
        Q2=Qsq,
        l_QCD=l,
        n_f=nf,
        n_t=nt,
        n_z=nz,
        morp=morp,
        order=order,
        logScale=logScale,
        verbose=verbose,
        alpha_num=alpha_num,
        Q0_2_a=Q0sqalpha,
        a0=a0
    )

    np.savetxt(args.o, res.T, delimiter=args.delim)
    if verbose:
        print(res)

if __name__ == '__main__':
    main()
