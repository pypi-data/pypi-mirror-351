#!/usr/bin/env python3

from numpy import array, pi

from stalk import ParameterStructure
from stalk.io import XyzGeometry

from params import forward, backward, relax_pyscf


# Let us initiate a ParameterStructure object that implements the parametric mappings
params_init = array([0.97, 104.0 / 180 * pi])
elem = ['O'] + 2 * ['H']
structure_natural = ParameterStructure(
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
    new_params = relax_pyscf(structure_natural, outfile)
    geom = XyzGeometry({'suffix': outfile}).load('./')
# end try
new_params = structure_natural.map_forward(geom.get_pos())
print(structure_natural.params)
print(new_params)
structure_relax = structure_natural.copy(params=new_params)
