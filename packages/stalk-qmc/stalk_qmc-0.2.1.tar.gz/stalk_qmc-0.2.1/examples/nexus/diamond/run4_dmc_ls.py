#!/usr/bin/env python3

from matplotlib import pyplot as plt

from stalk import LineSearchIteration

from params import pes_dmc
from run2_surrogate import surrogate

interactive = __name__ == "__main__"

# Run a snapshot job to sample effective variance w.r.t relative DMC samples
var_eff = pes_dmc.get_var_eff(
    structure=surrogate.structure,
    path='dmc_var_eff',
    samples=10,
    interactive=interactive,
)
# Add var_eff to DMC arguments
pes_dmc.args['var_eff'] = var_eff

# Then generate line-search iteration object based on the shifted surrogate
dmc_ls = LineSearchIteration(
    surrogate=surrogate,
    path='dmc_ls',
    pes=pes_dmc,
)
# Propagate the parallel line-search (compute values, analyze, then move on) 4 times
#   add_sigma = True means that target errorbars are used to simulate random noise
for i in range(3):
    dmc_ls.propagate(i, interactive=interactive)
    if interactive:
        print(dmc_ls)
        dmc_ls.pls(i).plot()
        plt.show()
    # end if
# end for
# Evaluate the latest eqm structure
dmc_ls.pls().evaluate_eqm(interactive=interactive)

# Print the line-search performance
if interactive:
    print(dmc_ls)
# end if
