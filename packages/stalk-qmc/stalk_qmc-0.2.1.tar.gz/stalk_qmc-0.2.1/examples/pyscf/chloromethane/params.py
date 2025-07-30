#!/usr/bin/env python3

from numpy import array, sin, cos, ndarray, pi, arcsin
from scipy.optimize import minimize

from pyscf import dft
from pyscf import gto
from pyscf.geomopt.geometric_solver import optimize
from pyscf.gto.mole import tofile

from stalk.params.util import bond_angle, mean_distances, distance, mean_param
from stalk import ParameterStructure
from stalk.params import PesFunction


# Natural forward mapping using bond lengths and angles
def forward(pos: ndarray):
    pos = pos.reshape(-1, 3)  # make sure of the shape
    # for easier comprehension, list particular atoms
    C = pos[0]
    Cl = pos[1]
    H0 = pos[2]
    H1 = pos[3]
    H2 = pos[4]

    r_CCl = distance(C, Cl)
    r_CH = mean_distances([
        (C, H0),
        (C, H1),
        (C, H2),
    ])
    a = mean_param([
        bond_angle(H0, C, H1, units='rad'),
        bond_angle(H1, C, H2, units='rad'),
        bond_angle(H2, C, H0, units='rad'),
    ], tol=1e-5)
    params = [r_CCl, r_CH, a]
    return params
# end def


# Backward mapping: produce array of atomic positions from parameters
def backward(params: ndarray):
    r_CCl = params[0]
    r_CH = params[1]
    a = params[2]
    aux_ang = 2 * pi / 3

    def p_aux(p):
        z = abs(p[0])
        xy = abs(p[1])
        r0 = array([0.0, 0.0, 0.0])
        ra = array([xy, 0.0, z])
        rb = array([xy * cos(aux_ang), xy * sin(aux_ang), z])
        a_this = bond_angle(ra, r0, rb, units='rad')
        r_this = distance(r0, ra)
        return (a_this - a)**2 + (r_this - r_CH)**2
    # end def

    p = minimize(p_aux, x0=[0.4, r_CH], tol=1e-9).x
    z = p[0]
    xy = p[1]
    if z < 0:
        print('z is negative!', a * 180 / pi, r_CH, z, xy)
    # end if
    # place atoms on a hexagon in the xy-directions
    C = [0.0, 0.0, 0.0]
    Cl = [0.0, 0.0, -r_CCl]
    H0 = [xy, 0.0, z]
    H1 = [xy * cos(aux_ang), xy * sin(aux_ang), z]
    H2 = [xy * cos(-aux_ang), xy * sin(-aux_ang), z]
    pos = array([C, Cl, H0, H1, H2])
    return pos
# end def


def kernel_pyscf(structure: ParameterStructure):
    atom = []
    for el, pos in zip(structure.elem, structure.pos):
        atom.append([el, tuple(pos)])
    # end for
    mol = gto.Mole()
    mol.atom = atom
    mol.verbose = 3
    mol.basis = 'ccpvdz'
    mol.unit = 'A'
    mol.ecp = 'ccecp'
    mol.charge = 0
    mol.spin = 0
    mol.symmetry = False
    mol.build()

    mf = dft.RKS(mol)
    return mf
# end def


def relax_pyscf(structure: ParameterStructure, outfile='relax.xyz', xc='pbe'):
    mf = kernel_pyscf(structure=structure)
    mf.xc = xc
    mf.kernel()
    mol_eq = optimize(mf, maxsteps=100)
    # Write to external file
    tofile(mol_eq, outfile, format='xyz')
# end def


def pes_pyscf(structure: ParameterStructure, xc='pbe', **kwargs):
    print(f'Computing: {structure.label} ({xc})')
    mf = kernel_pyscf(structure=structure)
    mf.xc = xc
    e_scf = mf.kernel()
    return e_scf, 0.0
# end def


pes_pbe = PesFunction(pes_pyscf, {'xc': 'pbe'})
pes_b3lyp = PesFunction(pes_pyscf, {'xc': 'b3lyp'})
