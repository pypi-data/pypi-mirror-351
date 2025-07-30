#!/usr/bin/env python3

from matplotlib import pyplot as plt

from stalk import LineSearch

from params import pes_dmc
from run2_surrogate import surrogate

interactive = __name__ == "__main__"

structure_qmc = surrogate.structure.copy()
# Run a snapshot job to sample effective variance w.r.t relative DMC samples
var_eff = pes_dmc.get_var_eff(
    structure_qmc,
    path='dmc_var_eff',
    samples=10,
    interactive=interactive
)
pes_dmc.args['var_eff'] = var_eff

# Finally, perform line-search iteration based on surrogate settings and DMC PES
dmc_ls = LineSearch(
    path='dmc_ls',
    pes=pes_dmc,
    interactive=interactive,
    **surrogate.to_settings()
)

# Print the line-search performance
if interactive:
    print(dmc_ls)
    dmc_ls.plot()
    plt.show()
# end if
