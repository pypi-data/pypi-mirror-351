from random import choice
from typing import Any

import astropy.units as u
import numpy as np
from astropy.wcs import WCS
from dkist_fits_specifications.utils.spec_processors.polarimetric_requiredness import (
    POLARIMETRIC_HEADER_REQUIREMENTS,
)

from ..dataset import key_function
from .core import Spec214Dataset, Spec214Schema


class BaseDLNIRSPDataset(Spec214Dataset):
    """
    A base class for DL-NIRSP datasets.
    """

    def __init__(
        self,
        n_mosaic_repeats,
        n_stokes,
        time_delta,
        *,
        linewave,
        array_shape=(100, 100, 100),
    ):
        if not n_mosaic_repeats:
            raise NotImplementedError(
                "Support for less than 4D DLNIRSP datasets is not implemented."
            )

        array_shape = list(array_shape)

        dataset_shape_rev = list(array_shape) + [n_mosaic_repeats]
        if n_stokes > 1:
            dataset_shape_rev += [n_stokes]

        # These keys need to be passed to super().__init__ so the file schema is updated with the correct
        # polarimetric requiredness
        polarimetric_keys = self.get_polarimetric_keys(n_stokes)

        super().__init__(
            dataset_shape_rev[::-1],
            array_shape,
            time_delta=time_delta,
            instrument="dlnirsp",
            **polarimetric_keys,
        )

        self.add_constant_key("DTYPE1", "SPATIAL")
        self.add_constant_key("DPNAME1", "spatial x")
        self.add_constant_key("DWNAME1", "helioprojective longitude")
        self.add_constant_key("DUNIT1", "arcsec")

        self.add_constant_key("DTYPE2", "SPATIAL")
        self.add_constant_key("DPNAME2", "spatial y")
        self.add_constant_key("DWNAME2", "helioprojective latitude")
        self.add_constant_key("DUNIT2", "arcsec")

        self.add_constant_key("DTYPE3", "SPECTRAL")
        self.add_constant_key("DPNAME3", "wavelength")
        self.add_constant_key("DWNAME3", "wavelength")
        self.add_constant_key("DUNIT3", "nm")

        self.add_constant_key("DTYPE4", "TEMPORAL")
        self.add_constant_key("DPNAME4", "mosaic repeat")
        self.add_constant_key("DWNAME4", "time")
        self.add_constant_key("DUNIT4", "s")

        if n_stokes > 1:
            self.add_constant_key("DTYPE5", "STOKES")
            self.add_constant_key("DPNAME5", "stokes")
            self.add_constant_key("DWNAME5", "stokes")
            self.add_constant_key("DUNIT5", "")
            self.stokes_file_axis = 0

        self.add_constant_key("LINEWAV", linewave.to_value(u.nm))

        for key, value in polarimetric_keys.items():
            self.add_constant_key(key, value)

        # TODO: What is this value??
        self.plate_scale = (
            10 * u.arcsec / u.pix,
            10 * u.arcsec / u.pix,
            1 * u.nm / u.pix,
        )
        self.n_stokes = n_stokes

    def get_polarimetric_keys(self, n_stokes) -> dict[str, Any]:
        """
        Given the number of stokes parameters, update the header to correspond to polarimetric or non-polarimetric data.
        """
        pol_key_requirements = POLARIMETRIC_HEADER_REQUIREMENTS["dl-nirsp"]

        # Just a dummy schema so we can generate values.
        # Pass in some dummy keys just to avoid a ton of logger output. These will make the schema initially
        # polarimetric, but it has to be something and this way we avoid worrying about the types of the key values.
        dummy_pol_keys = {k: choice(v) for k, v in pol_key_requirements.items()}
        file_schema = Spec214Schema(
            instrument="dlnirsp",
            naxis=3,
            dnaxis=4,
            deaxes=2,
            daaxes=2,
            nspeclns=1,
            **dummy_pol_keys,
        )
        polarimetric_keys = dict()
        for key, polarimetric_choices in pol_key_requirements.items():
            if n_stokes > 1:
                value = choice(polarimetric_choices)

            else:
                key_schema = file_schema[key]
                value = key_schema.generate_value()
                while value in polarimetric_choices:
                    # Keep trying until we get something non-polarimetric
                    value = key_schema.generate_value()

            polarimetric_keys[key] = value

        return polarimetric_keys


class SimpleDLNIRSPDataset(BaseDLNIRSPDataset):
    """
    A simple five dimensional DLNIRSP dataset with a HPC grid aligned to the pixel axes.
    """

    name = "dlnirsp-simple"

    @property
    def non_temporal_file_axes(self):
        if self.n_stokes > 1:
            # This is the index in file shape so third file dimension
            return (0,)
        return super().non_temporal_file_axes

    @property
    def data(self):
        return np.random.random(self.array_shape)

    @property
    def fits_wcs(self):
        if self.array_ndim != 3:
            raise ValueError(
                "DLNIRSP dataset generator expects a three dimensional FITS WCS."
            )

        w = WCS(naxis=self.array_ndim)
        w.wcs.crpix = (
            self.array_shape[2] / 2,
            self.array_shape[1] / 2,
            self.array_shape[0] / 2,
        )
        w.wcs.crval = 0, 0, 0
        w.wcs.cdelt = [self.plate_scale[i].value for i in range(self.array_ndim)]
        w.wcs.cunit = "arcsec", "arcsec", "nm"
        w.wcs.ctype = "HPLN-TAN", "HPLT-TAN", "AWAV"
        w.wcs.pc = np.identity(self.array_ndim)
        return w


class MosaicedDLNIRSPDataset(SimpleDLNIRSPDataset):
    name = "dlnirsp-mosaiced"

    def __init__(
        self,
        n_mosaic_repeats,
        n_X_tiles,
        n_Y_tiles,
        n_stokes,
        time_delta,
        *,
        linewave,
        array_shape=(100, 100, 100),
    ):
        super().__init__(
            n_mosaic_repeats=n_mosaic_repeats,
            n_stokes=n_stokes,
            time_delta=time_delta,
            linewave=linewave,
            array_shape=array_shape,
        )

        if n_X_tiles * n_Y_tiles == 1:
            raise ValueError(
                "The mosaic is a single position. Use a different class for this."
            )

        if n_mosaic_repeats == 1 and ((n_X_tiles > 1) ^ (n_Y_tiles > 1)):
            raise ValueError(
                "Trying to use a mosaicing class to move the temporal loop to either the X or Y tile loop. Use a different class for this."
            )

        self.mosaic_shape = (n_X_tiles, n_Y_tiles)

        num_mosaic_axes = 1

        self.add_constant_key("MAXIS1", n_X_tiles)
        if n_Y_tiles > 1:
            num_mosaic_axes += 1
            self.add_constant_key("MAXIS2", n_Y_tiles)

        self.add_constant_key("MAXIS", num_mosaic_axes)

        n_pos = n_X_tiles * n_Y_tiles
        self.files_shape = (*self.files_shape, n_pos)
        self.files_ndim = len(self.files_shape)
        self.n_files = int(np.prod(self.files_shape))

        # Make random CRPIX[12] and CRVAL[12] arrays
        rng = np.random.default_rng()
        self.mosaic_crpix_values = rng.random((n_X_tiles, n_Y_tiles, 2)) * 100 - 50.0
        self.mosaic_crval_values = rng.random((n_X_tiles, n_Y_tiles, 2)) * 200 - 100.0
        self.tile_crval_move_amount = rng.random()
        self.mosaic_crval_move_amount = rng.random() * 5.0

    @property
    def current_mosaic_repeat(self) -> int:
        return self.file_index[-2]

    @property
    def current_mosaic_index(self) -> int:
        return self.file_index[-1]

    @property
    def current_mosaic_position(self) -> tuple[int, int]:
        return np.unravel_index(self.current_mosaic_index, self.mosaic_shape, order="C")

    @key_function(
        "MINDEX1",
        "MINDEX2",
        "DLCSTPX",
        "DLCSTPY",
    )
    def moasic_keys(self, key: str):
        current_mosaic_position = self.current_mosaic_position
        if key in ["MINDEX1", "DLCSTPX"]:
            return current_mosaic_position[0] + 1

        if key in ["MINDEX2", "DLCSTPY"]:
            return current_mosaic_position[1] + 1

        raise ValueError(f"Could not figure out what to do with {key = }")

    @property
    def fits_wcs(self):
        if self.array_ndim != 3:
            raise ValueError(
                "DLNIRSP dataset generator expects a three dimensional FITS WCS."
            )

        X_tile, Y_tile = self.current_mosaic_position
        w = WCS(naxis=self.array_ndim)
        w.wcs.crpix = (
            self.mosaic_crpix_values[X_tile, Y_tile, 0],
            self.mosaic_crpix_values[X_tile, Y_tile, 1],
            self.array_shape[0] / 2,
        )
        # Yes, the CRVALs will change every time the instrument moves
        # They will NOT be the same for the same mosaic tile if it is observed later
        w.wcs.crval = (
            self.mosaic_crval_values[X_tile, Y_tile, 0]
            + self.current_mosaic_index * self.tile_crval_move_amount
            + self.current_mosaic_repeat * self.mosaic_crval_move_amount,
            self.mosaic_crval_values[X_tile, Y_tile, 1]
            + self.current_mosaic_index * self.tile_crval_move_amount
            + self.current_mosaic_repeat * self.mosaic_crval_move_amount,
            0.0,
        )
        w.wcs.cdelt = [self.plate_scale[i].value for i in range(self.array_ndim)]
        w.wcs.cunit = "arcsec", "arcsec", "nm"
        w.wcs.ctype = "HPLN-TAN", "HPLT-TAN", "AWAV"
        w.wcs.pc = np.identity(self.array_ndim)
        return w
