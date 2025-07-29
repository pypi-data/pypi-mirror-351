# Copyright Congzhou M Sha 2024
import mpmath as mp
import numpy as np
from scipy.interpolate import interp1d as interp
from mpmath import invertlaplace, mpc, pi, zeta, psi, euler as euler_gamma

mp.dps = 15
zeta2 = zeta(2)
zeta3 = zeta(3)

def constants(CG, n_f):
    NC = CG
    CF = (NC * NC - 1) / NC / 2
    TR = 1/2
    Tf= TR * n_f
    beta0 = 11 / 3 * CG - 4 / 3 * TR * n_f
    beta1 = 34 / 3 * CG ** 2 - 10 / 3 * CG * n_f - 2 * CF * n_f
    return NC, CF, TR, Tf, beta0, beta1

psi0 = lambda s: psi(0,s)
psi_p = lambda s: psi(1,s)
psi_pp = lambda s: psi(2,s)

# Special functions which analytically continue the zeta function
S_1 = lambda n: euler_gamma + psi0(n+1)
S_2 = lambda n: zeta2 - psi_p(n+1)
S_3 = lambda n: zeta3 + 0.5 * psi_pp(n+1)

etaN = lambda n, eta: 1 if eta == 1 else mp.power(eta, n)

def S_p1(n, f):
    return 0.5 * (
        (1 + f) * S_1(n/2) + (1 - f) * S_1((n-1)/2))

def S_p2(n, f):
    return 0.5 * (
        (1 + f) * S_2(n/2) + (1 - f) * S_2((n-1)/2))

def S_p3(n, f):
    return 0.5 * (
        (1 + f) * S_3(n/2) + (1 - f) * S_3((n-1)/2))

G = lambda n: psi0((n+1)/2) - psi0(n/2)

def Stilde(n, f):
    temp = -5/8 * zeta3
    term = f
    term *= S_1(n) / n / n - zeta2/2 * G(n) + \
        mp.quad(lambda t: mp.power(t, n-1) * mp.polylog(2, t) / (1 + t), [0, 1])
    return temp + term

def mellin(f, s):
    return mp.quad(lambda t: mp.power(t, s-1) * f(t), [0, 1])

def inv_mellin(f, x, degree=5, verbose=True):
    res = invertlaplace(f, -mp.log(x), method='cohen', degree=degree)
    if verbose:
        print(x, x*res)
    return res

def evolve(
    pdf,
    Q0_2=0.16,
    Q2=5.0,
    l_QCD=0.25,
    n_f=5,
    CG=3,
    morp='minus',
    order=2,
    n_x=200,
    verbose=False,
    Q0_2_a=91.1876**2,
    a0=0.118 / 4 / pi,
    alpha_num=True,
    degree=5,
):
    '''
    Evolve the transversity PDF
    ***************************
    Parameters:
        pdf: 1D or 2D array-like
            the input first moment. If 1D, assumed to be at x
            evenly distributed on [0, 1] inclusive.

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

        verbose: bool
            control the verbosity
    '''

    if pdf.shape[-1] == 1:
        xs = np.linspace(0, 1, len(pdf))
    else:
        xs, pdf = pdf[:, 0], pdf[:, 1]
    pdf = pdf / (xs + 1e-100)
    pdf[0] = 0
    pdf_fun = interp(xs, pdf, fill_value=0, assume_sorted=True)
    pdf = lambda x: mp.mpf(pdf_fun(float(x)).item())

    eta = 1 if morp == 'plus' else -1

    # Calculate the color constants
    NC, CF, TR, Tf, beta0, beta1 = constants(CG, n_f)
    if order == 1:
        beta1 = 0

    # Corresponds to MDTP_qq_LO
    LO_splitting_function_moment = lambda n: CF * (1.5 - 2 * S_1(n))
    # Corresponds to MDTP_qq_NLO
    def NLO_splitting_function_moment(n):
        f = etaN(n, eta)
        return \
            CF * CF * (
                3 / 8
                + (1-eta) / (n * (n + 1))
                - 3 * S_2(n)
                - 4 * S_1(n) * (S_2(n) - S_p2(n, f))
                - 8 * Stilde(n, f)
                + S_p3(n, f)
            ) + \
            0.5 * CF * NC * (
                17 / 12
                - (1 - eta) / (n * (n + 1))
                - 134 / 9 * S_1(n)
                + 22 / 3 * S_2(n)
                + 4 * S_1(n) * (2 * S_2(n) - S_p2(n, f))
                + 8 * Stilde(n, f)
                - S_p3(n, f)
            ) + \
            2 / 3 * CF * Tf * (
                -1 / 4
                + 10 / 3 * S_1(n)
                - 2 * S_2(n)
            )

    if order == 1:
        NLO_splitting_function_moment = lambda n: 0

    def alpha_S(Q2):
        ln_Q2_L_QCD = mp.log(Q2) - 2 * mp.log(l_QCD)
        ln_ln_Q2_L_QCD = mp.log(ln_Q2_L_QCD)
        alpha_S = 4 * pi / beta0 / ln_Q2_L_QCD
        if order == 2:
            alpha_S -= 4 * pi * beta1 / mp.power(beta0, 3) * ln_ln_Q2_L_QCD / ln_Q2_L_QCD / ln_Q2_L_QCD
        return alpha_S
        
    def alpha_S_num(Q2):
        if order == 2:
            ode = lambda x, a: -beta0 * a * a - beta1 * a * a * a
        else:
            ode = lambda x, a: -beta0 * a * a
        if Q2 < Q0_2_a:
            ode_fixed = lambda x, a: -ode(x, a)
            f = mp.odefun(ode_fixed, -mp.log(Q0_2_a), a0)
            return f(-np.log(Q2)) * 4 * pi
        else:
            f = mp.odefun(ode, mp.log(Q0_2_a), a0)
            return f(np.log(Q2)) * 4 * pi
    
    if alpha_num:
        alpha_S = alpha_S_num

    alpha_S_Q0_2 = alpha_S(Q0_2)
    alpha_S_Q2 = alpha_S(Q2)
    def evolveMoment(n, pdf_m):
        total = 1
        total += (alpha_S_Q0_2 - alpha_S_Q2) / pi / beta0 * (NLO_splitting_function_moment(n) - beta1 / 2 / beta0 * LO_splitting_function_moment(n))
        total *= mp.power(alpha_S_Q2 / alpha_S_Q0_2, -2 / beta0 * LO_splitting_function_moment(n)) * pdf_m
        return total

    if n_x > 0:
        xs = np.linspace(0, 1, n_x+2)
    xs = xs[1:-1]

    # Perform Mellin transform
    pdf_m = lambda s: mellin(pdf, s)
    # Evolve moments
    pdf_evolved_m = lambda s: mpc(evolveMoment(s, pdf_m(s)))
    # Invert Mellin transform
    pdf_evolved = np.array([inv_mellin(pdf_evolved_m, x, degree=degree, verbose=verbose).__complex__().real for x in xs])
    xs = np.pad(xs, 1)
    xs[-1] = 1
    pdf_evolved = np.pad(pdf_evolved, 1)
    pdf_evolved = np.stack((xs, np.array(xs) * np.array(pdf_evolved)))
    print('Done!')
    return pdf_evolved

def main():
    import argparse, sys
    parser = argparse.ArgumentParser(description='Evolution of the nonsinglet transversity PDF, using Vogelsang\'s moment method.')
    parser.add_argument('type',action='store',type=str,help='The method you chose')
    parser.add_argument('input', action='store', type=str,
                    help='The CSV file containing (x,x*PDF(x)) pairs on each line. If only a single number on each line, we assume a linear spacing for x between 0 and 1 inclusive')
    parser.add_argument('Q0sq', action='store', type=float, help='The starting energy scale in units of GeV^2')
    parser.add_argument('Qsq', action='store', type=float, help='The ending energy scale in units of GeV^2')
    parser.add_argument('--morp', nargs='?', action='store', type=str, default='plus', help='The plus vs minus type PDF (default is \'plus\')')
    parser.add_argument('-o', action='store', nargs='?', type=str, default='out.dat', help='Output file for the PDF, stored as (x,x*PDF(x)) pairs.')
    parser.add_argument('-l', metavar='l_QCD', nargs='?', action='store', type=float, default=0.25, help='The QCD scale parameter (default 0.25 GeV^2). Only used when --alpha_num is False.')
    parser.add_argument('--n_f', metavar='n_f', nargs='?', action='store', type=int, default=5, help='The number of flavors (default 5)')
    parser.add_argument('--nc', metavar='n_c', nargs='?', action='store', type=int, default=3, help='The number of colors (default 3)')
    parser.add_argument('--order', metavar='order', nargs='?', action='store', type=int, default=2, help='1: leading order, 2: NLO DGLAP (default 2)')
    parser.add_argument('--nx', metavar='n_x', nargs='?', action='store', type=int, default=-1, help='The number of x values to sample the evolved PDF (default -1). If left at -1, will sample at input xs.')
    parser.add_argument('--alpha_num', metavar='alpha_num', nargs='?', action='store', type=bool, default=True, help='Set to use the numerical solution for the strong coupling constant, numerically evolved at LO or NLO depending on the --order parameter.')
    parser.add_argument('--Q0sqalpha', metavar='Q0sqalpha', nargs='?', action='store', type=float, default=91.1876**2, help='The reference energy squared at which the strong coupling constant is known. Default is the squared top quark mass. Use in conjunction with --a0. Only used when --alpha_num is True.')
    parser.add_argument('--a0', metavar='a0', nargs='?', action='store', type=float, default=0.118 / 4 / np.pi, help='The reference value of the strong coupling constant a = alpha / (4 pi) at the corresponding reference energy --Q0sqalpha. Default is 0.118 / (4 pi), at energy Q0sqalpha = top quark mass squared. Only used when --alpha_num is True.')
    parser.add_argument('--delim', nargs='?', action='store', type=str, default=' ', help='Delimiter for the output (default \' \'). If given without an argument, then the delimiter is whitespace (i.e. Mathematica output.)')
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
    n_f = args.n_f
    nc = args.nc
    order = args.order
    nx = args.nx
    alpha_num = args.alpha_num
    Q0sqalpha = args.Q0sqalpha
    a0 = args.a0
    verbose = args.v

    res = evolve(pdf,
        Q0_2=Q0sq,
        Q2=Qsq,
        l_QCD=l,
        n_f=n_f,
        CG=nc,
        morp=morp,
        order=order,
        n_x=nx,
        verbose=verbose,
        alpha_num=alpha_num,
        Q0_2_a=Q0sqalpha,
        a0=a0
    )

    np.savetxt(args.o, res.T, delimiter=args.delim)

if __name__ == '__main__':
    main()
