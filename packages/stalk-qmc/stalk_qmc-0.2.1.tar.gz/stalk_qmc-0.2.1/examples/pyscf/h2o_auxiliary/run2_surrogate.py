#!/usr/bin/env python

from stalk import TargetParallelLineSearch
from matplotlib import pyplot as plt

from params import pes_pbe
from run1_hessian import hessian


surrogate_file = 'surrogate.p'
surrogate = TargetParallelLineSearch(
    path='surrogate/',
    fit_kind='pf3',
    load=surrogate_file,
    structure=hessian.structure,
    hessian=hessian,
    pes=pes_pbe,
    window_frac=0.5,
    M=15
)
surrogate.bracket_target_biases()

epsilon_p = [0.02, 0.02]
surrogate.optimize(
    epsilon_p=epsilon_p,
    fit_kind='pf3',
    M=7,
    N=400,
    reoptimize=False,
    write=surrogate_file,
)
print(surrogate)
