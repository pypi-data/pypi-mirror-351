#!/usr/bin/env python3

from numpy import array, pi

from stalk import ParameterStructure
from stalk.io import XyzGeometry

from params import forward, backward, relax_pyscf


# Let us initiate a ParameterStructure object that implements the parametric mappings
params_init = array([1.8, 1.11, 109 * pi / 180])
elem = ['C'] + ['Cl'] + 3 * ['H']
structure = ParameterStructure(
    forward=forward,
    backward=backward,
    params=params_init,
    elem=elem,
    units='A'
)

outfile = 'relax.xyz'
try:
    geom = XyzGeometry({'suffix': outfile}).load('./')
except FileNotFoundError:
    new_params = relax_pyscf(structure, outfile)
    geom = XyzGeometry({'suffix': outfile}).load('./')
# end try
new_params = structure.map_forward(geom.get_pos())
print(structure.params)
print(new_params)
structure_relax = structure.copy(params=new_params)
