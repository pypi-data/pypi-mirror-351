from typing import Callable

import astropy.units as u
import numpy as np
import pytest
from astropy.table import Table
from dkist_fits_specifications.spec214 import load_processed_spec214
from dkist_header_validator import spec214_validator

from dkist_data_simulator.spec214.cryo import (
    SimpleCryonirspCIDataset,
    SimpleCryonirspSPDataset,
    TimeDependentCryonirspCIDataset,
    TimeDependentCryonirspSPDataset,
)
from dkist_data_simulator.spec214.dlnirsp import (
    MosaicedDLNIRSPDataset,
    SimpleDLNIRSPDataset,
)
from dkist_data_simulator.spec214.vbi import (
    MosaicedVBIBlueDataset,
    SimpleVBIDataset,
    TimeDependentVBIDataset,
)
from dkist_data_simulator.spec214.visp import (
    SimpleVISPDataset,
    TimeDependentVISPDataset,
)
from dkist_data_simulator.spec214.vtf import SimpleVTFDataset


def test_vbi_mosaic():
    ds = MosaicedVBIBlueDataset(n_time=2, time_delta=10, linewave=400 * u.nm)
    headers = ds.generate_headers()
    h_table = Table(headers)

    # Assert that between index 1 and 2 we have 9 unique positions
    tile_grouped = h_table.group_by(("MINDEX1", "MINDEX2"))
    assert len(tile_grouped.groups) == 9

    for tile in tile_grouped.groups:
        assert (tile["CRVAL1"] == tile["CRVAL1"][0]).all()
        assert (tile["CRVAL2"] == tile["CRVAL2"][0]).all()
        assert (tile["CRPIX1"] == tile["CRPIX1"][0]).all()
        assert (tile["CRPIX2"] == tile["CRPIX2"][0]).all()

    assert (h_table["MAXIS"] == 2).all()
    assert (h_table["MAXIS1"] == 3).all()
    assert (h_table["MAXIS2"] == 3).all()

    # Assert some things about each timestep
    time_grouped = h_table.group_by(("DINDEX3"))
    assert len(time_grouped.groups) == 2

    for time in time_grouped.groups:
        assert not (time["CRPIX1"] == time["CRPIX1"][0]).all()
        assert not (time["CRPIX2"] == time["CRPIX2"][0]).all()
        assert not (time["MINDEX1"] == time["MINDEX1"][0]).all()
        assert not (time["MINDEX2"] == time["MINDEX2"][0]).all()


def test_time_varying_vbi():
    ds = TimeDependentVBIDataset(n_time=5, time_delta=10, linewave=400 * u.nm)
    headers = ds.generate_headers()
    h_table = Table(headers)

    constant_keys = ["CRPIX1", "CRPIX2", "CTYPE1", "CTYPE2", "CUNIT1", "CUNIT2"]
    varying_keys = ["CRVAL1", "CRVAL2", "PC1_1", "PC1_2", "PC2_1", "PC2_2"]

    for key in constant_keys:
        assert (h_table[key] == h_table[0][key]).all()

    for key in varying_keys:
        assert not (h_table[key] == h_table[0][key]).all()


def test_vbi_single_frame():
    ds = MosaicedVBIBlueDataset(n_time=1, time_delta=10, linewave=400 * u.nm)
    headers = ds.generate_headers()
    h_table = Table(headers)

    assert "DINDEX3" not in h_table.colnames

    assert len(headers) == 9
    # Assert that between index 1 and 2 we have 9 unique positions
    tile_grouped = h_table.group_by(("MINDEX1", "MINDEX2"))
    assert len(tile_grouped.groups) == 9

    for tile in tile_grouped.groups:
        assert (tile["CRVAL1"] == tile["CRVAL1"][0]).all()
        assert (tile["CRVAL2"] == tile["CRVAL2"][0]).all()
        assert (tile["CRPIX1"] == tile["CRPIX1"][0]).all()
        assert (tile["CRPIX2"] == tile["CRPIX2"][0]).all()

    assert (h_table["MAXIS"] == 2).all()
    assert (h_table["MAXIS1"] == 3).all()
    assert (h_table["MAXIS2"] == 3).all()

    # Assert some things about all the headers (we only have one timestep)
    assert not (h_table["MINDEX1"] == h_table["MINDEX1"][0]).all()
    assert not (h_table["MINDEX2"] == h_table["MINDEX2"][0]).all()
    assert not (h_table["CRPIX1"] == h_table["CRPIX1"][0]).all()
    assert not (h_table["CRPIX2"] == h_table["CRPIX2"][0]).all()


def test_time_varying_visp():
    ds = TimeDependentVISPDataset(3, 4, 1, 10, linewave=500 * u.nm)
    headers = ds.generate_headers()
    h_table = Table(headers)

    crval1 = h_table["CRVAL1"]
    crval2 = h_table["CRVAL2"]
    crval3 = h_table["CRVAL3"]

    keys = []
    for i in range(1, 4):
        for j in range(1, 4):
            keys.append(f"PC{i}_{j}")

    pc = np.array([np.array(h_table[key]) for key in keys]).reshape(
        (3, 3, len(h_table))
    )
    # Check the PC value is the same along the wave axis
    assert np.allclose(pc[1, 1, 0], pc[1, 1, :])
    assert not np.allclose(pc[:, :, 0:1], pc)

    assert not np.allclose(crval1[0], crval1)
    assert np.allclose(crval2[0], crval2)
    assert not np.allclose(crval3[0], crval3)


def test_vtf_stokes_time():
    ds = SimpleVTFDataset(
        n_wave=2, n_repeats=2, n_stokes=4, time_delta=10, linewave=500 * u.nm
    )

    # assert ds.non_temporal_file_axes == (0,)
    # ds._index = 5
    # assert ds.time_index == 1

    # ds._index = 0
    headers = Table(ds.generate_headers())
    time = np.unique(headers["DATE-AVG"])
    assert time.shape == (4,)


def test_visp_4d():
    ds = SimpleVISPDataset(
        n_steps=2, n_maps=1, n_stokes=4, time_delta=10, linewave=500 * u.nm
    )

    headers = Table(ds.generate_headers())
    assert headers[0]["DTYPE4"] == "STOKES"
    assert "DTYPE5" not in headers.colnames

    ds = SimpleVISPDataset(
        n_steps=2, n_maps=2, n_stokes=1, time_delta=10, linewave=500 * u.nm
    )

    headers = Table(ds.generate_headers())
    assert headers[0]["DTYPE4"] == "TEMPORAL"
    assert "DTYPE5" not in headers.colnames


@pytest.mark.parametrize(
    "n_meas, n_maps, n_stokes",
    [
        pytest.param(1, 3, 4, id="Single meas, Multi map, Stokes"),
        pytest.param(2, 3, 4, id="Multi meas, Multi map, Stokes"),
        pytest.param(1, 1, 4, id="Single meas, Single map, Stokes"),
        pytest.param(2, 1, 4, id="Multi meas, Single map, Stokes"),
        pytest.param(1, 3, 1, id="Single meas, Multi map, no Stokes"),
        pytest.param(2, 3, 1, id="Multi meas, Multi map, no Stokes"),
        pytest.param(1, 1, 1, id="Single meas, Single map, no Stokes"),
        pytest.param(2, 1, 1, id="Multi meas, Single map, no Stokes"),
    ],
)
@pytest.mark.parametrize(
    "cryo_dataset",
    [
        pytest.param(SimpleCryonirspSPDataset, id="SP Dataset"),
        pytest.param(SimpleCryonirspCIDataset, id="CI Dataset"),
    ],
)
def test_simple_cryo(cryo_dataset: Callable, n_meas: int, n_maps: int, n_stokes: int):
    """
    Given: A simple Cryo SP or CI dataset
    When: Making a dataset
    Then: The correct numbers of dataset axes are created
    """
    n_steps = 2
    ds = cryo_dataset(
        n_meas=n_meas,
        n_steps=n_steps,
        n_maps=n_maps,
        n_stokes=n_stokes,
        time_delta=10,
        linewave=1083 * u.nm,
    )
    if isinstance(ds, SimpleCryonirspSPDataset):
        dtype1_value = "SPECTRAL"
        scan_step_value = "SPATIAL"
    else:
        dtype1_value = "SPATIAL"
        scan_step_value = "TEMPORAL"

    headers = Table(ds.generate_headers())
    assert headers[0]["DTYPE1"] == dtype1_value
    assert headers[0]["DNAXIS1"] == headers[0]["NAXIS1"]
    assert headers[0]["DTYPE2"] == "SPATIAL"
    assert headers[0]["DNAXIS2"] == headers[0]["NAXIS2"]
    axis_num = 3
    if n_meas > 1:
        # measurement axis
        assert headers[0][f"DTYPE{axis_num}"] == "TEMPORAL"
        assert headers[0][f"DNAXIS{axis_num}"] == n_meas
        axis_num += 1
        # scan step axis
        assert headers[0][f"DTYPE{axis_num}"] == scan_step_value
        assert headers[0][f"DNAXIS{axis_num}"] == n_steps
    else:
        # scan step axis
        assert headers[0][f"DTYPE{axis_num}"] == scan_step_value
        assert headers[0][f"DNAXIS{axis_num}"] == n_steps
    if n_maps > 1:
        axis_num += 1
        # map scan axis
        assert headers[0][f"DTYPE{axis_num}"] == "TEMPORAL"
        assert headers[0][f"DNAXIS{axis_num}"] == n_maps
    if n_stokes > 1:
        axis_num += 1
        # stokes axis
        assert headers[0][f"DTYPE{axis_num}"] == "STOKES"
        assert headers[0][f"DNAXIS{axis_num}"] == 4
        assert headers[0][f"DINDEX{axis_num}"] in range(5)
    assert headers[0]["DAAXES"] == 2
    assert headers[0]["DNAXIS"] == axis_num
    assert headers[0]["DEAXES"] == axis_num - 2
    assert f"DNAXIS{axis_num + 1}" not in headers.columns
    assert f"DTYPE{axis_num + 1}" not in headers.colnames


@pytest.mark.parametrize(
    "ds_cls", (SimpleCryonirspSPDataset, TimeDependentCryonirspSPDataset)
)
def test_cryo_sp_crpix3(ds_cls):
    n_raster = 11
    ds = ds_cls(
        1,
        n_raster,
        1,
        1,
        time_delta=0.1,
        linewave=500 * u.nm,
        slit_width=0.1 * u.arcsec,
        raster_step=0.5 * u.arcsec,
    )
    headers = ds.generate_headers()
    h_table = Table(headers)

    pixel_delta = ((ds.raster_step / 1 * u.pix) / ds.slit_width).to_value(u.pix)
    # We expect the CRPIX3 value to go from
    # (n_raster / 2) * -pixel_delta to (n_raster / 2) * pixel_delta
    center_pix = round((n_raster - 1) / 2)
    start = center_pix * -pixel_delta
    end = center_pix * pixel_delta
    CRPIX3 = h_table["CRPIX3"]
    assert np.allclose(CRPIX3[0], start)
    assert np.allclose(CRPIX3[-1], end)


@pytest.mark.parametrize(
    "ds_cls", (SimpleCryonirspCIDataset, TimeDependentCryonirspCIDataset)
)
def test_cryo_ci_rastering(ds_cls):
    n_raster = 11
    ds = ds_cls(1, n_raster, 1, 1, 0.9, linewave=100 * u.nm, raster_step=0.5 * u.arcsec)
    headers = ds.generate_headers()
    h_table = Table(headers)

    pixel_delta = ((ds.raster_step) / ds.plate_scale).to_value(u.pix)
    # We expect the CRPIX1 value to go from
    # (n_raster / 2) * -pixel_delta to (n_raster / 2) * pixel_delta
    center_pix = round((n_raster - 1) / 2)
    start = center_pix * -pixel_delta
    end = center_pix * pixel_delta
    CRPIX1 = h_table["CRPIX1"]
    assert np.allclose(CRPIX1[0], start)
    assert np.allclose(CRPIX1[-1], end)


def test_time_varying_cryo_sp():
    ds = TimeDependentCryonirspSPDataset(
        n_meas=1, n_steps=2, n_maps=3, n_stokes=4, time_delta=10, linewave=500 * u.nm
    )
    headers = ds.generate_headers()
    h_table = Table(headers)

    crval1 = h_table["CRVAL1"]
    crval2 = h_table["CRVAL2"]
    crval3 = h_table["CRVAL3"]

    keys = []
    for i in range(1, 4):
        for j in range(1, 4):
            keys.append(f"PC{i}_{j}")

    pc = np.array([np.array(h_table[key]) for key in keys]).reshape(
        (ds.array_ndim, ds.array_ndim, len(h_table))
    )
    # Check the PC value is the same along the wave axis
    assert np.allclose(pc[0, 0, 0], pc[0, 0, :])
    assert not np.allclose(pc[:, :, 0:1], pc)

    assert np.allclose(crval1[0], crval1)
    assert not np.allclose(crval2[0], crval2)
    assert not np.allclose(crval3[0], crval3)


def test_stokes_static_cryo_sp():
    ds = SimpleCryonirspSPDataset(
        n_meas=4, n_steps=2, n_maps=3, n_stokes=4, time_delta=10, linewave=500 * u.nm
    )
    headers = ds.generate_headers()
    h_table = Table(headers)

    # Sanity check that the indicies in all the files actually vary
    for n in range(3, headers[0]["DNAXIS"] + 1):
        assert not (h_table[f"DINDEX{n}"][0] == h_table[f"DINDEX{n}"]).all()

    # Santity check that stokes is last
    assert headers[0]["DTYPE6"] == "STOKES"
    # Test that STOKES for a given index all have the same time
    # For the first index in raster, map and measurement extract the header rows
    stokes_1 = h_table[np.all([h_table[f"DINDEX{d}"] == 0 for d in [3, 4, 5]], axis=0)]
    # We should have 4 headers
    assert len(stokes_1) == 4
    # Check that all the stokes profiles have the same time
    assert (stokes_1["DATE-AVG"][0] == stokes_1["DATE-AVG"]).all()


def test_time_varying_cryo_ci():
    ds = TimeDependentCryonirspCIDataset(
        n_meas=1, n_steps=2, n_maps=3, n_stokes=4, time_delta=10, linewave=500 * u.nm
    )
    headers = ds.generate_headers()
    h_table = Table(headers)

    constant_keys = ["CRPIX1", "CRPIX2", "CTYPE1", "CTYPE2", "CUNIT1", "CUNIT2"]
    varying_keys = ["CRVAL1", "CRVAL2", "PC1_1", "PC1_2", "PC2_1", "PC2_2"]

    for key in constant_keys:
        assert (h_table[key] == h_table[0][key]).all()

    for key in varying_keys:
        assert not (h_table[key] == h_table[0][key]).all()


def test_time_varying_visp_crpix3():
    n_raster = 10
    ds = TimeDependentVISPDataset(1, n_raster, 1, 10, linewave=500 * u.nm)
    headers = ds.generate_headers()
    h_table = Table(headers)

    # We expect the CRPIX3 value to go from n_raster / 2 to n_raster / 2
    # but we have to compensate for the fact that in FITS convention 1 is the
    # "midpoint" of this range
    start = n_raster / 2 + 1
    end = -1 * (n_raster / 2 - 1)
    assert np.allclose(h_table["CRPIX3"], np.arange(start, end, -1))


def test_dlnirsp_mosaic():
    n_X_tiles = 2
    n_Y_tiles = 3
    ds = MosaicedDLNIRSPDataset(
        n_mosaic_repeats=3,
        n_X_tiles=n_X_tiles,
        n_Y_tiles=n_Y_tiles,
        n_stokes=4,
        time_delta=10,
        linewave=400 * u.nm,
        array_shape=(10, 10, 10),
    )
    headers = ds.generate_headers()
    h_table = Table(headers)

    n_pos = n_X_tiles * n_Y_tiles

    # Assert that between index 1 and 2 we have 9 unique positions
    tile_grouped = h_table.group_by(("MINDEX1", "MINDEX2"))
    assert len(tile_grouped.groups) == n_pos

    for tile in tile_grouped.groups:
        assert not (tile["CRVAL1"] == tile["CRVAL1"][0]).all()
        assert not (tile["CRVAL2"] == tile["CRVAL2"][0]).all()
        assert (tile["CRPIX1"] == tile["CRPIX1"][0]).all()
        assert (tile["CRPIX2"] == tile["CRPIX2"][0]).all()

    assert (h_table["MAXIS"] == 2).all()
    assert (h_table["MAXIS1"] == n_X_tiles).all()
    assert (h_table["MAXIS2"] == n_Y_tiles).all()

    # Assert some things about each timestep
    time_grouped = h_table.group_by(("DINDEX4"))
    assert len(time_grouped.groups) == 3

    for time in time_grouped.groups:
        # Don't test the 3rd (wavelength) axis, because we expect that to be the same
        assert not (time["CRPIX1"] == time["CRPIX1"][0]).all()
        assert not (time["CRPIX2"] == time["CRPIX2"][0]).all()
        assert not (time["MINDEX1"] == time["MINDEX1"][0]).all()
        assert not (time["MINDEX2"] == time["MINDEX2"][0]).all()


@pytest.mark.parametrize(
    "dataset_class, non_stokes_args",
    [
        pytest.param(
            SimpleCryonirspSPDataset,
            {
                "n_meas": 1,
                "n_steps": 2,
                "n_maps": 1,
                "time_delta": 0.5,
                "linewave": 1083.0 * u.nm,
            },
            id="Cryo SP",
        ),
        pytest.param(
            SimpleCryonirspCIDataset,
            {
                "n_meas": 1,
                "n_steps": 2,
                "n_maps": 1,
                "time_delta": 0.5,
                "linewave": 1083.0 * u.nm,
            },
            id="Cryo CI",
        ),
        pytest.param(
            SimpleDLNIRSPDataset,
            {"n_mosaic_repeats": 1, "time_delta": 0.5, "linewave": 1083.0 * u.nm},
            id="DL-NIRSP",
        ),
        pytest.param(
            SimpleVISPDataset,
            {"n_maps": 1, "n_steps": 1, "time_delta": 0.5, "linewave": 630.0 * u.nm},
            id="ViSP",
        ),
    ],
)
@pytest.mark.parametrize(
    "n_stokes",
    [pytest.param(1, id="non-polarimetric"), pytest.param(4, id="polarimetric")],
)
def test_polarimetric_headers(dataset_class, non_stokes_args, n_stokes):
    """
    Given: A dataset that is either polarimetric (n_stokes > 1) or non-polarimetric (n_stokes == 1)
    When: Checking the requiredness of some polarimetric 214 keys
    Then: The keys are required for polarimetric datasets and not required for non-polarimetric datasets

    I.e., test that changing n_stokes correctly updates the header so it is identified as [non-]polarimetric
    """
    args = non_stokes_args | {"n_stokes": n_stokes}
    ds = dataset_class(**args)
    header = ds.header()

    if n_stokes > 1:
        expected_required = True
    else:
        expected_required = False

    # We use ["pac"]["POL_SENS"] as a sentinel key for basically no reason
    spec_schema = load_processed_spec214(glob="pac", **header)["pac"]
    assert (
        spec_schema["POL_SENS"].get("required", not expected_required)
        == expected_required
    )


@pytest.mark.parametrize(
    "dataset_class, class_args",
    [
        pytest.param(
            SimpleCryonirspSPDataset,
            {
                "n_meas": 1,
                "n_steps": 2,
                "n_maps": 1,
                "n_stokes": 4,
                "time_delta": 0.5,
                "linewave": 1083.0 * u.nm,
            },
            id="Cryo SP",
        ),
        pytest.param(
            SimpleCryonirspCIDataset,
            {
                "n_meas": 1,
                "n_steps": 2,
                "n_maps": 1,
                "n_stokes": 4,
                "time_delta": 0.5,
                "linewave": 1083.0 * u.nm,
            },
            id="Cryo CI",
        ),
        pytest.param(
            SimpleDLNIRSPDataset,
            {
                "n_mosaic_repeats": 1,
                "n_stokes": 4,
                "time_delta": 0.5,
                "linewave": 1083.0 * u.nm,
            },
            id="DL-NIRSP",
        ),
        pytest.param(
            SimpleVBIDataset,
            {"n_time": 1, "time_delta": 0.5, "linewave": 630.0 * u.nm},
            id="VBI",
        ),
        pytest.param(
            SimpleVISPDataset,
            {
                "n_maps": 1,
                "n_steps": 1,
                "n_stokes": 4,
                "time_delta": 0.5,
                "linewave": 630.0 * u.nm,
            },
            id="ViSP",
        ),
        pytest.param(
            SimpleVTFDataset,
            {
                "n_wave": 1,
                "n_repeats": 1,
                "n_stokes": 4,
                "time_delta": 0.5,
                "linewave": 630.0 * u.nm,
            },
            id="VTF",
        ),
    ],
)
def test_required_only_headers_validate(dataset_class, class_args):
    """
    Given: A Simple 214 dataset for a specific instrument
    When: Creating a header with only the required keywords
    Then: The header successfully validates
    """
    ds = dataset_class(**class_args)
    header = ds.header(required_only=True)
    spec214_validator.validate(header)


def test_expected_only_includes_required():
    """
    Given: A header generated with `required=False, expected=True`
    When: Valdiating the header
    Then: The header validates because required keys were generated
    """
    ds = SimpleVBIDataset(n_time=1, time_delta=0.5, linewave=0.0 * u.nm)
    header = ds.header(expected_only=True, required_only=False)
    spec214_validator.validate(header)
