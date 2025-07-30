#!/usr/bin/env python3

from pytest import raises
from numpy import isnan

from stalk.util.util import match_to_tol
from stalk.nexus.NexusPes import NexusPes
from stalk.nexus.NexusStructure import NexusStructure

from ..assets.test_jobs import nxs_generic_pes, TestLoader
from ..assets.h2o import pes_H2O, pos_H2O, elem_H2O

__author__ = "Juha Tiihonen"
__email__ = "tiihonen@iki.fi"
__license__ = "BSD-3-Clause"


def test_NexusPes(tmp_path):

    s = NexusStructure(
        label='label',
        pos=pos_H2O,
        elem=elem_H2O,
        units='A'
    )

    # Test empty (should fail)
    with raises(TypeError):
        NexusPes()
    # end with

    # 1a: Test successful generation of jobs
    pes = NexusPes(
        nxs_generic_pes,
        args={'pes_variable': 'h2o'},
        loader=TestLoader()
    )
    assert not pes.disable_failed
    assert not pes.bundle_jobs
    pes.evaluate(s, path=str(tmp_path) + '/nosigma', sigma=0.0)
    assert s.generated
    assert len(s.jobs) == 1
    assert s.finished
    assert s.analyzed
    E_original = pes_H2O(pos_H2O)[0]
    assert match_to_tol(s.value, E_original)
    assert match_to_tol(s.error, 0.0)
    # 1b: Test successful generation of jobs with noise
    sigma = 0.1
    s.reset_value()
    pes.evaluate(s, path=str(tmp_path) + '/sigma', sigma=sigma, add_sigma=True)
    # The value must have shifted
    assert not match_to_tol(s.value, E_original)
    assert match_to_tol(s.error, 0.1)
    # 1c: Test unsuccessful loading of jobs
    s.reset_value()
    pes.loader = TestLoader(args={'produce_fail': True})
    pes.evaluate(s, path=str(tmp_path) + '/fail', sigma=0.0)
    assert isnan(s.value)
    assert s.enabled
    assert match_to_tol(s.error, 0.0)
    # 1d: Test disabling of failed jobs
    s.reset_value()
    pes.disable_failed = True
    pes.evaluate(s, path=str(tmp_path) + '/disable_fail')
    assert not s.enabled

    # 2: Test evaluate all
    sigmas = [0.1, 0.2, 0.3, 0.4]
    s2a = s.copy(pos=pos_H2O * 0.9, label='s2a')
    s2eqm1 = s.copy(pos=pos_H2O, label='eqm')
    s2b = s.copy(pos=pos_H2O * 1.1, label='s2b')
    s2eqm2 = s.copy(pos=pos_H2O, label='eqm')
    structures = [s2a, s2eqm1, s2b, s2eqm2]
    pes.evaluate_all(
        structures,
        path=str(tmp_path) + '/eval_all',
        sigmas=sigmas,
        add_sigma=True
    )
    assert all([s.generated for s in structures[:-1]])
    assert all([s.analyzed for s in structures[:-1]])
    assert match_to_tol([s.error for s in structures], sigmas)
    # TODO: not sure if this behavior is good
    assert not structures[-1].generated
    assert not structures[-1].analyzed

    # 3: Test bundle
    sigmas = [0.1, 0.2]
    pes_bundle = NexusPes(
        nxs_generic_pes,
        args={'pes_variable': 'fail'},
        loader=TestLoader(),
        bundle_jobs=True
    )
    assert pes_bundle.bundle_jobs
    s1 = s.copy(pos=pos_H2O * 0.9, label='bundle1')
    s2 = s.copy(pos=pos_H2O * 1.1, label='bundle2')
    structures_bundle = [s1, s2]
    pes.evaluate_all(
        structures_bundle,
        path=str(tmp_path) + '/bundle',
        sigmas=sigmas,
        add_sigma=True
    )
    assert all([s.generated for s in structures_bundle])
    assert all([s.analyzed for s in structures_bundle])
    assert match_to_tol([s.error for s in structures_bundle], sigmas)

# end def
