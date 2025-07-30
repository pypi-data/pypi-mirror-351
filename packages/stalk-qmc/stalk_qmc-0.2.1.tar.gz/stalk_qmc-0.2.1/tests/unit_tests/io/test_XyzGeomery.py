from numpy import loadtxt, array
from pytest import raises
from stalk.io.XyzGeometry import XyzGeometry
from stalk.params import GeometryResult
from stalk.params.ParameterStructure import ParameterStructure
from stalk.util.util import match_to_tol
from ..assets.h2o import pos_H2O, elem_H2O


def test_XyzGeometry_load():

    # default args: (suffix: relax.xyz)
    loader = XyzGeometry()

    # Test failing to load a file (default suffix: relax.xyz)
    with raises(FileNotFoundError):
        loader = XyzGeometry().load('tests/unit_tests/assets/pwscf_relax')
    # end with

    # Test loading a reference file
    res = loader.load('tests/unit_tests/assets/pwscf_relax', suffix='relax_bohr.xyz')
    res_dbl = loader.load('tests/unit_tests/assets/pwscf_relax', suffix='relax_bohr.xyz', c_pos=2.0)

    assert isinstance(res, GeometryResult)
    assert isinstance(res_dbl, GeometryResult)

    # For reference, just copy the load function for testing redundancy
    el_ref, x, y, z = loadtxt('tests/unit_tests/assets/pwscf_relax/relax_bohr.xyz', dtype=str, unpack=True, skiprows=2)
    pos = array([x, y, z], dtype=float)

    for el, el1, el2 in zip(el_ref, res.get_elem(), res_dbl.get_elem()):
        assert el == el1 and el == el2
    # end for
    for x, x1, x2 in zip(pos[0], res.get_pos()[:, 0], res_dbl.get_pos()[:, 0]):
        assert match_to_tol(x, x1, 1e-8) and match_to_tol(2 * x, x2, 1e-8)
    # end for
    for y, y1, y2 in zip(pos[1], res.get_pos()[:, 1], res_dbl.get_pos()[:, 1]):
        assert match_to_tol(y, y1, 1e-8) and match_to_tol(2 * y, y2, 1e-8)
    # end for
    for z, z1, z2 in zip(pos[2], res.get_pos()[:, 2], res_dbl.get_pos()[:, 2]):
        assert match_to_tol(z, z1, 1e-8) and match_to_tol(2 * z, z2, 1e-8)
    # end for
    assert res.get_axes() is None
    assert res_dbl.get_axes() is None
# end def


def test_XyzGeometry_write(tmp_path):
    # default args: (suffix: relax.xyz)
    writer = XyzGeometry()
    s = ParameterStructure(
        pos=pos_H2O,
        elem=elem_H2O
    )
    writer.write(s, tmp_path)

    # To test out, load the file and compare
    loader = XyzGeometry({'suffix': 'structure.xyz'})
    res = loader.load(tmp_path)
    for el_ref, el in zip(elem_H2O, res.get_elem()):
        assert el_ref == el
    # end for
    for pos_ref, pos in zip(pos_H2O, res.get_pos()):
        assert match_to_tol(pos_ref, pos)
    # end for

# end def
