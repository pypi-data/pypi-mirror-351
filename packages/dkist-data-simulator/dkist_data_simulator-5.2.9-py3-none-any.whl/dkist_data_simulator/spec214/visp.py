from random import choice
from typing import Any

import astropy.units as u
import numpy as np
from astropy.wcs import WCS
from dkist_fits_specifications.utils.spec_processors.polarimetric_requiredness import (
    POLARIMETRIC_HEADER_REQUIREMENTS,
)

from .core import Spec214Dataset, Spec214Schema, TimeVaryingWCSGenerator


class BaseVISPDataset(Spec214Dataset):
    """
    A base class for VISP datasets.
    """

    def __init__(
        self,
        n_maps,
        n_steps,
        n_stokes,
        time_delta,
        *,
        linewave,
        detector_shape=(1000, 2560),
        slit_width=0.06 * u.arcsec,
        raster_step=None,
    ):
        array_shape = [1] + list(detector_shape)
        dataset_shape = [n_steps] + list(detector_shape)

        if n_maps > 1:
            dataset_shape = [n_maps] + dataset_shape
        if n_stokes > 1:
            dataset_shape = [n_stokes] + dataset_shape

        # These keys need to be passed to super().__init__ so the file schema is updated with the correct
        # polarimetric requiredness
        polarimetric_keys = self.get_polarimetric_keys(n_stokes)

        super().__init__(
            dataset_shape,
            array_shape,
            time_delta=time_delta,
            instrument="visp",
            **polarimetric_keys,
        )

        self.linewave = linewave
        self.plate_scale = 0.06 * u.arcsec / u.pix
        self.spectral_scale = 0.01 * u.nm / u.pix
        self.slit_width = slit_width
        self.raster_step = raster_step if raster_step is not None else slit_width / 2
        self.n_stokes = n_stokes
        self.n_steps = n_steps
        self.n_maps = n_maps

        # This key isn't actually the slit width in arcsec, it's in micro-meters
        # I am not sure if there is a key which is the angular slit width?!
        # self.add_constant_key("VSPWID", self.slit_width.to_value(u.arcsec))
        self.add_constant_key("VSPSLTSS", self.raster_step.to_value(u.arcsec))

        self.add_constant_key("DTYPE1", "SPATIAL")
        self.add_constant_key("DTYPE2", "SPECTRAL")
        self.add_constant_key("DTYPE3", "SPATIAL")
        self.add_constant_key("DPNAME1", "slit position")
        self.add_constant_key("DPNAME2", "wavelength")
        self.add_constant_key("DPNAME3", "raster position")
        self.add_constant_key("DWNAME1", "helioprojective latitude")
        self.add_constant_key("DWNAME2", "wavelength")
        self.add_constant_key("DWNAME3", "helioprojective longitude")
        self.add_constant_key("DUNIT1", "arcsec")
        self.add_constant_key("DUNIT2", "nm")
        self.add_constant_key("DUNIT3", "arcsec")

        next_index = 4
        if n_maps > 1:
            self.add_constant_key(f"DTYPE{next_index}", "TEMPORAL")
            self.add_constant_key(f"DPNAME{next_index}", "scan number")
            self.add_constant_key(f"DWNAME{next_index}", "time")
            self.add_constant_key(f"DUNIT{next_index}", "s")
            next_index += 1

        if n_stokes > 1:
            self.add_constant_key(f"DTYPE{next_index}", "STOKES")
            self.add_constant_key(f"DPNAME{next_index}", "stokes")
            self.add_constant_key(f"DWNAME{next_index}", "stokes")
            self.add_constant_key(f"DUNIT{next_index}", "")
            self.stokes_file_axis = 0

        self.add_constant_key("LINEWAV", linewave.to_value(u.nm))

        for key, value in polarimetric_keys.items():
            self.add_constant_key(key, value)

    def get_polarimetric_keys(self, n_stokes) -> dict[str, Any]:
        """
        Given the number of stokes parameters, update the header to correspond to polarimetric or non-polarimetric data.
        """
        pol_key_requirements = POLARIMETRIC_HEADER_REQUIREMENTS["visp"]

        # Just a dummy schema so we can generate values.
        # Pass in some dummy keys just to avoid a ton of logger output. These will make the schema initially
        # polarimetric, but it has to be something and this way we avoid worrying about the types of the key values.
        dummy_pol_keys = {k: choice(v) for k, v in pol_key_requirements.items()}
        file_schema = Spec214Schema(
            instrument="visp",
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

    def calculate_raster_crpix(self):
        """
        A helper method to calculate the crpix3 value for a frame.

        The summit provides headers where CDELT3 is not the slitwidth but the
        angular raster step.  Therefore we generate crpix3 values which are -1
        less per raster step.
        """
        # These are 0 indexed
        raster_index = self.file_index[-1]
        # We want the pixel number to start high (the reference pixel is to the right, and end low (to the left)
        raster_pixel_number = ((self.n_steps / 2) - raster_index) * u.pix
        return (1 * u.pix + raster_pixel_number).to_value(u.pix)


class SimpleVISPDataset(BaseVISPDataset):
    """
    A VISP cube with regular raster spacing.
    """

    name = "visp-simple"

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
                "VISP dataset generator expects a three dimensional FITS WCS."
            )

        w = WCS(naxis=self.array_ndim)
        w.wcs.crpix = (
            self.array_shape[2] / 2,
            self.array_shape[1] / 2,
            self.calculate_raster_crpix(),
        )
        w.wcs.crval = 0, self.linewave.to_value(u.nm), 0
        w.wcs.cdelt = (
            self.plate_scale.to_value(u.arcsec / u.pix),
            self.spectral_scale.to_value(u.nm / u.pix),
            self.raster_step.to_value(u.arcsec),
        )
        w.wcs.cunit = "arcsec", "nm", "arcsec"
        w.wcs.ctype = "HPLT-TAN", "AWAV", "HPLN-TAN"
        w.wcs.pc = np.identity(self.array_ndim)
        return w


class TimeDependentVISPDataset(SimpleVISPDataset):
    """
    A version of the ViSP dataset where the CRVAL and PC matrix change with time.
    """

    name = "visp-time-dependent"

    def __init__(
        self,
        n_maps,
        n_steps,
        n_stokes,
        time_delta,
        *,
        linewave,
        detector_shape=(1000, 2560),
        slit_width=0.06 * u.arcsec,
        raster_step=None,
        pointing_shift_rate=10 * u.arcsec / u.s,
        rotation_shift_rate=0.5 * u.deg / u.s,
        rotation_angle=-2 * u.deg,
    ):
        super().__init__(
            n_maps,
            n_steps,
            n_stokes,
            time_delta,
            linewave=linewave,
            detector_shape=detector_shape,
            slit_width=slit_width,
            raster_step=raster_step,
        )

        self.wcs_generator = TimeVaryingWCSGenerator(
            cunit=(u.arcsec, u.nm, u.arcsec),
            ctype=("HPLT-TAN", "WAVE", "HPLN-TAN"),
            crval=(0, self.linewave.to_value(u.nm), 0),
            rotation_angle=rotation_angle,
            crpix=(
                self.array_shape[2] / 2,
                self.array_shape[1] / 2,
                self.calculate_raster_crpix,
            ),
            cdelt=(
                self.plate_scale.to_value(u.arcsec / u.pix),
                self.spectral_scale.to_value(u.nm / u.pix),
                self.raster_step.to_value(u.arcsec),
            ),
            pointing_shift_rate=u.Quantity([pointing_shift_rate, pointing_shift_rate]),
            rotation_shift_rate=rotation_shift_rate,
            jitter=False,
            static_axes=[1],
        )

    @property
    def fits_wcs(self):
        return self.wcs_generator.generate_wcs(self.time_index * self.time_delta * u.s)
