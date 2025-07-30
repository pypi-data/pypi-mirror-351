"""
this file contains tests which verify that inventory generation works.

Because this file leads to a circular test-time dependency between
dkist-inventory and the simulator, these tests are in their own file which is
conditionally skipped depending on the version of the dkist-inventory package.

If you make large changes to dkist-inventory and the simulator which need to be
co-versioned you should bump the major version number of dkist-inventory and
update the skip directive here.

This means that incremental changes to the simulator have unit tests which
verify inventory generation doesn't fail spectacularly.
"""
import astropy.units as u
import dkist_inventory
import numpy as np
import pytest
from astropy.wcs import WCS
from dkist_inventory.header_parsing import HeaderParser
from dkist_inventory.inventory import extract_inventory
from packaging.version import Version

from dkist_data_simulator.dataset import key_function
from dkist_data_simulator.spec214 import Spec214Dataset
from dkist_data_simulator.spec214.cryo import (
    SimpleCryonirspCIDataset,
    SimpleCryonirspSPDataset,
)
from dkist_data_simulator.spec214.dlnirsp import (
    MosaicedDLNIRSPDataset,
    SimpleDLNIRSPDataset,
)
from dkist_data_simulator.spec214.vbi import MosaicedVBIBlueDataset, SimpleVBIDataset
from dkist_data_simulator.spec214.visp import SimpleVISPDataset
from dkist_data_simulator.spec214.vtf import SimpleVTFDataset


class DatasetTest214(Spec214Dataset):
    @property
    def fits_wcs(self):
        w = WCS(naxis=2)
        w.wcs.crpix = self.array_shape[1] / 2, self.array_shape[0] / 2
        w.wcs.crval = 0, 0
        w.wcs.cdelt = 1, 1
        w.wcs.cunit = "arcsec", "arcsec"
        w.wcs.ctype = "HPLN-TAN", "HPLT-TAN"
        w.wcs.pc = np.identity(self.array_ndim)
        return w

    @property
    def data(self):
        return np.random.random(self.array_shape)

    @key_function("FRAMEWAV")
    def framewav(self, key: str):
        """
        Add a random framewav around the line centre
        """
        return (np.random.random() - 0.5) * 100


def inventory_version_skip(version):
    """
    Return a pytest mark based on a version of dkist-inventory.

    This is just pytest.mark.skipif but for a dynamic version.
    """
    return pytest.mark.skipif(
        Version(dkist_inventory.__version__) < Version(version),
        reason=f"dkist-inventory must have a version higher than {version}",
    )


@pytest.mark.parametrize(
    "ds",
    (
        pytest.param(
            DatasetTest214(
                dataset_shape=(2, 2, 40, 50), array_shape=(40, 50), time_delta=10
            ),
            id="DatasetTest214",
        ),
        pytest.param(
            SimpleVISPDataset(
                n_maps=2, n_steps=3, n_stokes=4, time_delta=10, linewave=500 * u.m
            ),
            id="SimpleVISPDataset-polarized",
        ),
        pytest.param(
            SimpleVISPDataset(
                n_maps=2, n_steps=3, n_stokes=0, time_delta=10, linewave=500 * u.m
            ),
            id="SimpleVISPDataset",
        ),
        pytest.param(
            SimpleVBIDataset(n_time=2, time_delta=10, linewave=400 * u.nm),
            id="SimpleVBIDataset",
        ),
        pytest.param(
            SimpleVTFDataset(
                n_wave=2, n_repeats=3, n_stokes=4, time_delta=10, linewave=400 * u.nm
            ),
            id="SimpleVTFDataset-polarized",
        ),
        pytest.param(
            SimpleVTFDataset(
                n_wave=2, n_repeats=3, n_stokes=0, time_delta=10, linewave=400 * u.nm
            ),
            id="SimpleVTFDataset",
        ),
        pytest.param(
            SimpleCryonirspSPDataset(
                n_meas=1,
                n_steps=3,
                n_maps=3,
                n_stokes=4,
                time_delta=10,
                linewave=500 * u.m,
            ),
            id="SimpleCryonirspSPDataset-polarized-single-meas",
            marks=inventory_version_skip("0.18.dev0"),
        ),
        pytest.param(
            SimpleCryonirspSPDataset(
                n_meas=2,
                n_steps=3,
                n_maps=3,
                n_stokes=4,
                time_delta=10,
                linewave=500 * u.m,
            ),
            id="SimpleCryonirspSPDataset-polarized-multiple-meas",
            marks=inventory_version_skip("0.18.dev0"),
        ),
        pytest.param(
            SimpleCryonirspSPDataset(
                n_meas=1,
                n_steps=3,
                n_maps=3,
                n_stokes=1,
                time_delta=10,
                linewave=500 * u.m,
            ),
            id="SimpleCryonirspSPDataset-single-meas",
            marks=inventory_version_skip("0.18.dev0"),
        ),
        pytest.param(
            SimpleCryonirspSPDataset(
                n_meas=2,
                n_steps=3,
                n_maps=3,
                n_stokes=1,
                time_delta=10,
                linewave=500 * u.m,
            ),
            id="SimpleCryonirspSPDataset-multiple-meas",
            marks=inventory_version_skip("0.18.dev0"),
        ),
        pytest.param(
            SimpleCryonirspCIDataset(
                n_meas=1,
                n_steps=3,
                n_maps=3,
                n_stokes=4,
                time_delta=10,
                linewave=500 * u.m,
            ),
            id="SimpleCryonirspCIDataset-polarized-single-meas",
            marks=inventory_version_skip("0.18.dev0"),
        ),
        pytest.param(
            SimpleCryonirspCIDataset(
                n_meas=2,
                n_steps=3,
                n_maps=3,
                n_stokes=4,
                time_delta=10,
                linewave=500 * u.m,
            ),
            id="SimpleCryonirspCIDataset-polarized-multiple-meas",
            marks=inventory_version_skip("0.18.dev0"),
        ),
        pytest.param(
            SimpleCryonirspCIDataset(
                n_meas=1,
                n_steps=3,
                n_maps=3,
                n_stokes=1,
                time_delta=10,
                linewave=500 * u.m,
            ),
            id="SimpleCryonirspCIDataset-single-meas",
            marks=inventory_version_skip("0.18.dev0"),
        ),
        pytest.param(
            SimpleCryonirspCIDataset(
                n_meas=2,
                n_steps=3,
                n_maps=3,
                n_stokes=1,
                time_delta=10,
                linewave=500 * u.m,
            ),
            id="SimpleCryonirspCIDataset-multiple-meas",
            marks=inventory_version_skip("0.18.dev0"),
        ),
        pytest.param(
            SimpleDLNIRSPDataset(
                n_mosaic_repeats=3, n_stokes=4, time_delta=10, linewave=400 * u.nm
            ),
            id="SimpleDLNIRSPDataset-polarized",
            marks=inventory_version_skip("0.18.dev0"),
        ),
        pytest.param(
            SimpleDLNIRSPDataset(
                n_mosaic_repeats=3, n_stokes=0, time_delta=10, linewave=400 * u.nm
            ),
            id="SimpleDLNIRSPDataset",
            marks=inventory_version_skip("0.18.dev0"),
        ),
        pytest.param(
            MosaicedVBIBlueDataset(n_time=2, time_delta=10, linewave=400 * u.nm),
            id="MosaicedVBIBlueDataset",
            marks=inventory_version_skip("1.4.0.dev0"),
        ),
        pytest.param(
            MosaicedDLNIRSPDataset(
                n_mosaic_repeats=3,
                n_X_tiles=2,
                n_Y_tiles=2,
                n_stokes=4,
                time_delta=1,
                linewave=1083 * u.nm,
                array_shape=(10, 10, 10),
            ),
            id="MosaicedDLNIRSPDataset",
            marks=inventory_version_skip("1.4.0.dev0"),
        ),
    ),
)
def test_generate_214(ds):
    headers = ds.generate_headers()

    # Assert that the datasets generated here pass through gwcs generation and inventory creation.
    # This is the most minimal sanity check possible.

    filenames = [f"{i}.fits" for i in range(len(headers))]
    header_parser = HeaderParser.from_headers(headers, filenames=filenames)
    inv = extract_inventory(header_parser)
    assert isinstance(inv, dict)
