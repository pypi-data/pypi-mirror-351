from abc import ABC, abstractmethod
from random import choice
from typing import Any, Callable

import astropy.units as u
import numpy as np
from astropy.wcs import WCS
from dkist_fits_specifications.utils.spec_processors.polarimetric_requiredness import (
    POLARIMETRIC_HEADER_REQUIREMENTS,
)

from .core import Spec214Dataset, Spec214Schema, TimeVaryingWCSGenerator


class CryonirspDatasetBase(Spec214Dataset):
    def add_main_axis_header_keys(
        self, n_meas: int, n_steps: int, n_maps: int, n_stokes: int
    ) -> None:
        first_axis_num = 1
        next_axis_num = self._add_first_axis(axis_num=first_axis_num)
        next_axis_num = self._add_helioprojective_longitude_axis(axis_num=next_axis_num)
        multiple_measurements = n_meas > 1
        if multiple_measurements:
            next_axis_num = self._add_measurement_axis(n_meas, next_axis_num)
        next_axis_num = self._add_scan_step_axis(n_steps, axis_num=next_axis_num)
        if n_maps > 1:
            next_axis_num = self._add_map_scan_axis(n_maps, axis_num=next_axis_num)
        if n_stokes > 1:
            next_axis_num = self._add_stokes_axis(axis_num=next_axis_num)
        self._add_wavelength_headers()
        num_axes = next_axis_num - 1
        self._add_common_headers(num_axes=num_axes)

    @property
    @abstractmethod
    def _longitude_pixel_name(self) -> str:
        """Return the descriptive name for the longitudinal axis."""
        pass

    @property
    @abstractmethod
    def _add_first_axis(self) -> Callable:
        """Return the add method for the first axis."""
        pass

    def _get_polarimetric_keys(self, n_stokes: int) -> dict[str, Any]:
        """
        Given the number of stokes parameters, update the header to correspond to polarimetric or non-polarimetric data.
        """
        pol_key_requirements = POLARIMETRIC_HEADER_REQUIREMENTS["cryo-nirsp"]

        # Just a dummy schema so we can generate values.
        # Pass in some dummy keys just to avoid a ton of logger output. These will make the schema initially
        # polarimetric, but it has to be something and this way we avoid worrying about the types of the key values.
        dummy_pol_keys = {k: choice(v) for k, v in pol_key_requirements.items()}
        file_schema = Spec214Schema(
            instrument="cryonirsp",
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

    def _add_helioprojective_longitude_axis(self, axis_num: int) -> int:
        """Add header keys for the spatial helioprojective longitude axis."""
        self.add_constant_key(f"DNAXIS{axis_num}", self.data_shape[0])
        self.add_constant_key(f"DTYPE{axis_num}", "SPATIAL")
        self.add_constant_key(f"DPNAME{axis_num}", self._longitude_pixel_name)
        self.add_constant_key(f"DWNAME{axis_num}", "helioprojective longitude")
        self.add_constant_key(f"DUNIT{axis_num}", "arcsec")
        next_axis = axis_num + 1
        return next_axis

    def _add_measurement_axis(self, n_meas: int, axis_num: int) -> int:
        """Add header keys related to multiple measurements."""
        self.add_constant_key(f"DNAXIS{axis_num}", n_meas)
        self.add_constant_key(f"DTYPE{axis_num}", "TEMPORAL")
        self.add_constant_key(f"DPNAME{axis_num}", "measurement number")
        self.add_constant_key(f"DWNAME{axis_num}", "time")
        self.add_constant_key(f"DUNIT{axis_num}", "s")
        next_axis = axis_num + 1
        return next_axis

    @abstractmethod
    def _add_scan_step_axis(self, n_steps: int, axis_num: int) -> int:
        pass

    def _add_map_scan_axis(self, n_maps: int, axis_num: int) -> int:
        """Add header keys for the temporal map scan axis."""
        self.add_constant_key("CNNMAPS", n_maps)
        self.add_constant_key(f"DNAXIS{axis_num}", n_maps)
        self.add_constant_key(f"DTYPE{axis_num}", "TEMPORAL")
        self.add_constant_key(f"DPNAME{axis_num}", "scan number")
        self.add_constant_key(f"DWNAME{axis_num}", "time")
        self.add_constant_key(f"DUNIT{axis_num}", "s")
        next_axis = axis_num + 1
        return next_axis

    def _add_stokes_axis(self, axis_num: int) -> int:
        """Add header keys for the stokes polarization axis."""
        self.add_constant_key(f"DNAXIS{axis_num}", 4)
        self.add_constant_key(f"DTYPE{axis_num}", "STOKES")
        self.add_constant_key(f"DPNAME{axis_num}", "stokes")
        self.add_constant_key(f"DWNAME{axis_num}", "stokes")
        self.add_constant_key(f"DUNIT{axis_num}", "")
        next_axis = axis_num + 1
        self.stokes_file_axis = axis_num - len(self.dataset_shape)
        return next_axis

    def _add_wavelength_headers(self) -> None:
        """Add header keys related to the observing wavelength."""
        self.add_constant_key("WAVEUNIT", -9)  # nanometers
        self.add_constant_key("WAVEREF", "Air")

    def _add_common_headers(self, num_axes: int) -> None:
        """Add header keys that are common to both SP and CI."""
        self.add_constant_key("DNAXIS", num_axes)
        self.add_constant_key("DAAXES", 2)  # Spatial, spatial
        self.add_constant_key("DEAXES", num_axes - 2)  # Total - detector axes
        self.add_constant_key("LEVEL", 1)
        # Binning headers
        nbin1 = nbin2 = 1
        self.add_constant_key("NBIN1", nbin1)
        self.add_constant_key("NBIN2", nbin2)
        # Leaving them separate in case we ever want to have different binnings
        self.add_constant_key("NBIN", nbin1 * nbin2)


class CryonirspSPDatasetBase(CryonirspDatasetBase, ABC):
    """
    A base class for Cryo-NIRSP SP datasets.
    """

    def __init__(
        self,
        n_meas: int,
        n_steps: int,
        n_maps: int,
        n_stokes: int,
        time_delta: float,
        *,
        linewave: float,
        #                         (spatial, spectral)
        detector_shape: (int, int) = (1024, 1022),
        slit_width=0.06 * u.arcsec,
        raster_step=None,
    ):
        # [1] is for the implicit wavelength axis
        array_shape = [1] + list(detector_shape)

        dataset_shape_rev = list(detector_shape)[::-1]
        if n_meas > 1:
            dataset_shape_rev += [n_meas]
        dataset_shape_rev += [n_steps]
        if n_maps > 1:
            dataset_shape_rev += [n_maps]
        if n_stokes > 1:
            dataset_shape_rev += [n_stokes]

        # These keys need to be passed to super().__init__ so the file schema is updated with the correct
        # polarimetric requiredness
        polarimetric_keys = self._get_polarimetric_keys(n_stokes)

        super().__init__(
            tuple(dataset_shape_rev[::-1]),
            tuple(array_shape),
            time_delta=time_delta,
            instrument="cryonirsp",
            **polarimetric_keys,
        )

        self.add_main_axis_header_keys(
            n_meas=n_meas, n_steps=n_steps, n_maps=n_maps, n_stokes=n_stokes
        )

        for key, value in polarimetric_keys.items():
            self.add_constant_key(key, value)

        # TODO: Is this correct?
        self.add_constant_key("LINEWAV", linewave.to_value(u.nm))
        self.linewave = linewave

        # TODO: Numbers
        self.plate_scale = 0.06 * u.arcsec / u.pix
        self.spectral_scale = 0.01 * u.nm / u.pix
        self.slit_width = slit_width
        self.n_stokes = n_stokes
        self.n_steps = n_steps
        self.raster_step = raster_step if raster_step is not None else self.slit_width

        self.add_constant_key("CNP1DSS", self.raster_step.to_value(u.arcsec))

    @property
    def _longitude_pixel_name(self) -> str:
        """Return the descriptive name for the longitudinal axis."""
        return "spatial along slit"

    @property
    def _add_first_axis(self) -> Callable:
        """Return the add method for the first axis."""
        return self._add_spectral_axis

    def _add_spectral_axis(self, axis_num):
        self.add_constant_key(f"DNAXIS{axis_num}", self.data_shape[1])
        self.add_constant_key(f"DTYPE{axis_num}", "SPECTRAL")
        self.add_constant_key(f"DPNAME{axis_num}", "dispersion axis")
        self.add_constant_key(f"DWNAME{axis_num}", "wavelength")
        self.add_constant_key(f"DUNIT{axis_num}", "nm")
        next_axis = axis_num + 1
        return next_axis

    def _add_scan_step_axis(self, n_steps, axis_num: int) -> int:
        """Add header keys for the spatial scan step axis."""
        self.add_constant_key(f"DNAXIS{axis_num}", n_steps)
        self.add_constant_key(f"DTYPE{axis_num}", "SPATIAL")
        self.add_constant_key(f"DPNAME{axis_num}", "map scan step number")
        self.add_constant_key(f"DWNAME{axis_num}", "helioprojective latitude")
        self.add_constant_key(f"DUNIT{axis_num}", "arcsec")
        next_axis = axis_num + 1
        return next_axis

    def calculate_raster_crpix(self):
        """
        A helper method to calculate the crpix3 value for a frame.

        Unlike VISP, in cryo the stepping is represented by changes in
        CRPIX3, where a 1px offset is 1 unit of CDELT3 away from the
        CRVAL3 reference coordinate.
        """
        if self.n_steps == 1:
            return 1
        scan_mid_pix = round((self.dataset_shape[-3] - 1) / 2) * u.pix
        rel_pix_ind = self.file_index[-1] * u.pix - scan_mid_pix
        pix_delta = (self.raster_step / 1 * u.pix) / self.slit_width
        step_pix_shift = pix_delta * rel_pix_ind.to_value(u.pix)
        return step_pix_shift.to_value(u.pix)


class CryonirspCIDatasetBase(CryonirspDatasetBase, ABC):
    """
    A base class for Cryo-NIRSP datasets.
    """

    def __init__(
        self,
        n_meas: int,
        n_steps: int,
        n_maps: int,
        n_stokes: int,
        time_delta: float,
        *,
        linewave: float,
        #                            (long, lat)
        detector_shape: (int, int) = (2046, 2048),
        raster_step: u.Quantity[u.arcsec] = None,
    ):
        if n_maps < 1:
            raise ValueError("Having fewer than one map just doesn't make sense.")

        if n_steps <= 1:
            raise NotImplementedError(
                "Support for Cryo CI data with fewer than two raster steps is not supported."
            )

        array_shape = tuple(detector_shape)

        dataset_shape_rev = list(detector_shape)[::-1]
        if n_meas > 1:
            dataset_shape_rev += [n_meas]
        dataset_shape_rev += [n_steps]
        if n_maps > 1:
            dataset_shape_rev += [n_maps]
        if n_stokes > 1:
            dataset_shape_rev += [n_stokes]

        polarimetric_keys = self._get_polarimetric_keys(n_stokes)

        super().__init__(
            tuple(dataset_shape_rev[::-1]),
            tuple(array_shape),
            time_delta=time_delta,
            instrument="cryonirsp",
            **polarimetric_keys,
        )

        self.add_main_axis_header_keys(
            n_meas=n_meas, n_steps=n_steps, n_maps=n_maps, n_stokes=n_stokes
        )

        for key, value in polarimetric_keys.items():
            self.add_constant_key(key, value)

        self.add_constant_key("LINEWAV", linewave.to_value(u.nm))
        self.linewave = linewave

        self.plate_scale = 0.06 * u.arcsec / u.pix
        self.raster_step = raster_step
        self.n_stokes = n_stokes

    @property
    def _longitude_pixel_name(self) -> str:
        """Return the descriptive name for the longitudinal axis."""
        return "helioprojective longitude"

    @property
    def _add_first_axis(self) -> Callable:
        """Return the add method for the first axis."""
        return self._add_helioprojective_latitude_axis

    def _add_helioprojective_latitude_axis(self, axis_num: int) -> int:
        """Add header keys for the spatial helioprojective latitude axis."""
        self.add_constant_key(f"DNAXIS{axis_num}", self.data_shape[1])
        self.add_constant_key(f"DTYPE{axis_num}", "SPATIAL")
        self.add_constant_key(f"DPNAME{axis_num}", "helioprojective latitude")
        self.add_constant_key(f"DWNAME{axis_num}", "helioprojective latitude")
        self.add_constant_key(f"DUNIT{axis_num}", "arcsec")
        next_axis = axis_num + 1
        return next_axis

    def _add_scan_step_axis(self, n_steps: int, axis_num: int) -> int:
        """Add header keys for the scan step axis."""
        self.add_constant_key(f"DNAXIS{axis_num}", n_steps)
        self.add_constant_key(f"DTYPE{axis_num}", "TEMPORAL")
        self.add_constant_key(f"DPNAME{axis_num}", "map scan step number")
        self.add_constant_key(f"DWNAME{axis_num}", "time")
        self.add_constant_key(f"DUNIT{axis_num}", "s")
        next_axis = axis_num + 1
        return next_axis

    def calculate_raster_crpix(self):
        """
        A helper method to calculate the crpix1 value for a frame.

        This helper is for the CI, where the CRPIX1 changes over the raster (as CI follows the slit of SP).
        CRPIX1 changes by raster_step / CDELT1 pixels per step
        """
        if self.raster_step is None:
            return self.array_shape[0] / 2
        scan_mid_pix = round((self.dataset_shape[-3] - 1) / 2) * u.pix
        rel_pix_ind = self.file_index[-1] * u.pix - scan_mid_pix
        pix_delta = (self.raster_step) / self.plate_scale
        step_pix_shift = pix_delta * rel_pix_ind.to_value(u.pix)
        return step_pix_shift.to_value(u.pix)


class SimpleCryonirspSPDataset(CryonirspSPDatasetBase):
    """
    A five dimensional Cryo cube with regular raster spacing.
    """

    name = "cryo-sp-simple"

    @property
    def non_temporal_file_axes(self):
        if self.n_stokes > 1:
            # See above, Stokes is the first axis in dataset_shape
            return (self.stokes_file_axis,)
        return super().non_temporal_file_axes

    @property
    def data(self):
        return np.random.random(self.array_shape)

    @property
    def fits_wcs(self):
        if self.array_ndim != 3:
            raise ValueError(
                "Cryo SP dataset generator expects a three dimensional FITS WCS."
            )

        w = WCS(naxis=self.array_ndim)
        w.wcs.crpix = (
            self.array_shape[2] / 2,
            self.array_shape[1] / 2,
            self.calculate_raster_crpix(),
        )
        # TODO: linewav is not a good centre point
        w.wcs.crval = self.linewave.to_value(u.nm), 0, 0
        w.wcs.cdelt = (
            self.spectral_scale.to_value(u.nm / u.pix),
            self.plate_scale.to_value(u.arcsec / u.pix),
            self.slit_width.to_value(u.arcsec),
        )
        w.wcs.cunit = "nm", "arcsec", "arcsec"
        w.wcs.ctype = "AWAV", "HPLT-TAN", "HPLN-TAN"
        w.wcs.pc = np.identity(self.array_ndim)
        return w


class SimpleCryonirspCIDataset(CryonirspCIDatasetBase):
    """
    A CI dataset where pointing does not vary
    """

    name = "cryo-ci-simple"

    @property
    def non_temporal_file_axes(self):
        if self.n_stokes > 1:
            # See above, Stokes is the first axis in dataset_shape
            return (self.stokes_file_axis,)
        return super().non_temporal_file_axes

    @property
    def data(self):
        return np.random.random(self.array_shape)

    @property
    def fits_wcs(self):
        if self.array_ndim != 2:
            raise ValueError(
                "Cryo CI dataset generator expects a two dimensional FITS WCS."
            )

        w = WCS(naxis=self.array_ndim)
        w.wcs.crpix = (
            self.calculate_raster_crpix(),
            self.array_shape[0] / 2,
        )
        w.wcs.crval = 0, 0
        w.wcs.cdelt = [self.plate_scale.to_value(u.arcsec / u.pix) for _ in range(2)]
        w.wcs.cdelt = [self.plate_scale.to_value(u.arcsec / u.pix) for _ in range(2)]
        w.wcs.cunit = "arcsec", "arcsec"
        w.wcs.ctype = "HPLN-TAN", "HPLT-TAN"
        w.wcs.pc = np.identity(self.array_ndim)

        return w


class TimeDependentCryonirspSPDataset(SimpleCryonirspSPDataset):
    """
    A version of the Cryo SP dataset where the CRVAL and PC matrix change with time.
    """

    name = "cryo-sp-time-dependent"

    def __init__(
        self,
        n_meas: int,
        n_steps: int,
        n_maps: int,
        n_stokes: int,
        time_delta: float,
        *,
        linewave: float,
        detector_shape: (int, int) = (1024, 1024),
        pointing_shift_rate=10 * u.arcsec / u.s,
        rotation_shift_rate=0.5 * u.deg / u.s,
        slit_width=0.06 * u.arcsec,
        raster_step=None,
    ):
        super().__init__(
            n_meas=n_meas,
            n_maps=n_maps,
            n_steps=n_steps,
            n_stokes=n_stokes,
            time_delta=time_delta,
            linewave=linewave,
            detector_shape=detector_shape,
            slit_width=slit_width,
            raster_step=raster_step,
        )

        self.wcs_generator = TimeVaryingWCSGenerator(
            cunit=(u.nm, u.arcsec, u.arcsec),
            ctype=("WAVE", "HPLT-TAN", "HPLN-TAN"),
            crval=(self.linewave.to_value(u.nm), 900, 900),
            rotation_angle=-2 * u.deg,
            crpix=(
                self.array_shape[2] / 2,
                self.array_shape[1] / 2,
                self.calculate_raster_crpix,
            ),
            cdelt=(
                self.spectral_scale.to_value(u.nm / u.pix),
                self.plate_scale.to_value(u.arcsec / u.pix),
                self.slit_width.to_value(u.arcsec),
            ),
            pointing_shift_rate=u.Quantity([pointing_shift_rate, pointing_shift_rate]),
            rotation_shift_rate=rotation_shift_rate,
            jitter=False,
            static_axes=[0],
        )

    @property
    def fits_wcs(self):
        return self.wcs_generator.generate_wcs(self.time_index * self.time_delta * u.s)


class TimeDependentCryonirspCIDataset(SimpleCryonirspCIDataset):
    """
    A version of the Cryo CI dataset where the CRVAL and PC matrix change with time.
    """

    name = "cryo-ci-time-dependent"

    def __init__(
        self,
        n_meas: int,
        n_steps: int,
        n_maps: int,
        n_stokes: int,
        time_delta: float,
        *,
        linewave: float,
        detector_shape: (int, int) = (2048, 2048),
        pointing_shift_rate=10 * u.arcsec / u.s,
        rotation_shift_rate=0.5 * u.deg / u.s,
        raster_step=None,
    ):
        super().__init__(
            n_meas=n_meas,
            n_maps=n_maps,
            n_steps=n_steps,
            n_stokes=n_stokes,
            time_delta=time_delta,
            linewave=linewave,
            detector_shape=detector_shape,
            raster_step=raster_step,
        )

        self.wcs_generator = TimeVaryingWCSGenerator(
            cunit=(u.arcsec, u.arcsec),
            ctype=("HPLT-TAN", "HPLN-TAN"),
            crval=(0, 0),
            rotation_angle=-2 * u.deg,
            crpix=(self.calculate_raster_crpix, self.array_shape[0] / 2),
            cdelt=[self.plate_scale.to_value(u.arcsec / u.pix) for _ in range(2)],
            pointing_shift_rate=u.Quantity([pointing_shift_rate, pointing_shift_rate]),
            rotation_shift_rate=rotation_shift_rate,
            jitter=False,
        )

    @property
    def fits_wcs(self):
        return self.wcs_generator.generate_wcs(self.time_index * self.time_delta * u.s)
