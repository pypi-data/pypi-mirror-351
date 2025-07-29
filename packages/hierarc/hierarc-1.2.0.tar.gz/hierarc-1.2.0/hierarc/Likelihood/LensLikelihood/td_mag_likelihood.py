import numpy as np
from lenstronomy.Util import constants as const
from lenstronomy.Util.data_util import magnitude2cps


class TDMagLikelihood(object):
    """Likelihood of time delays and magnification likelihood.

    This likelihood uses linear flux units and linear lensing magnifications.
    """

    def __init__(
        self,
        time_delay_measured,
        cov_td_measured,
        amp_measured,
        cov_amp_measured,
        fermat_diff,
        magnification_model,
        cov_model,
        magnitude_zero_point=20,
    ):
        """

        :param time_delay_measured: array, relative time delays (relative to the first image) [days]
        :param cov_td_measured: 2d array, error covariance matrix of time delay measurement [days^2]
        :param amp_measured: array, amplitudes of measured fluxes of image positions
        :param cov_amp_measured: 2d array, error covariance matrix of the measured amplitudes
        :param fermat_diff: mean Fermat potential differences (relative to the first image) in arcsec^2
        :param magnification_model: mean magnification of the model prediction
        :param cov_model: 2d array (length relative time delays + image amplitudes); model fermat potential differences
         and lensing magnification covariances
        :param magnitude_zero_point: magnitude zero point for which the image amplitudes and covariance matrix are
        defined
        """

        self._data_vector = np.append(time_delay_measured, amp_measured)
        self._cov_td_measured = np.array(cov_td_measured)
        self._cov_amp_measured = np.array(cov_amp_measured)
        # check sizes of covariances matches
        n_tot = len(self._data_vector)
        self._n_td = len(time_delay_measured)
        self._n_amp = len(amp_measured)
        assert self._n_td == len(cov_td_measured)
        assert self._n_amp == len(cov_amp_measured)
        assert n_tot == len(cov_model)
        # merge data covariance matrices from time delay and image amplitudes
        self._cov_data = np.zeros((n_tot, n_tot))
        self._cov_data[: self._n_td, : self._n_td] = self._cov_td_measured
        self._cov_data[self._n_td :, self._n_td :] = self._cov_amp_measured
        # self._fermat_diff = fermat_diff   # in units arcsec^2
        self._fermat_unit_conversion = (
            const.Mpc / const.c / const.day_s * const.arcsec**2
        )
        # self._mag_model = mag_model
        self._model_tot = np.append(fermat_diff, magnification_model)
        self._cov_model = cov_model
        self.num_data = n_tot
        self._magnitude_zero_point = magnitude_zero_point

    def log_likelihood(self, ddt, mu_intrinsic):
        """

        :param ddt: time-delay distance (physical Mpc)
        :param mu_intrinsic: intrinsic brightness of the source (already incorporating the inverse MST transform)
        :return: log likelihood of the measured magnified images given the source brightness
        """
        model_vector, cov_tot = self._model_cov(ddt, mu_intrinsic)
        # invert matrix
        try:
            cov_tot_inv = np.linalg.inv(cov_tot)
        except:
            return -np.inf
        # difference to data vector
        delta = self._data_vector - model_vector
        # evaluate likelihood
        lnlikelihood = -delta.dot(cov_tot_inv.dot(delta)) / 2.0
        sign_det, lndet = np.linalg.slogdet(cov_tot)
        lnlikelihood -= 1 / 2.0 * (self.num_data * np.log(2 * np.pi) + lndet)
        return lnlikelihood

    def _model_cov(self, ddt, mu_intrinsic):
        """Combined covariance matrix of the data and model when marginialized over the
        Gaussian model uncertainties in the Fermat potential and magnification.

        :param ddt: time-delay distance (physical Mpc)
        :param mu_intrinsic: intrinsic brightness of the source (already incorporating
            the inverse MST transform)
        :return: model vector, combined covariance matrix
        """
        # compute model predicted magnified image amplitude and time delay
        amp_intrinsic = magnitude2cps(
            magnitude=mu_intrinsic, magnitude_zero_point=self._magnitude_zero_point
        )
        model_scale = np.append(
            ddt * self._fermat_unit_conversion * np.ones(self._n_td),
            amp_intrinsic * np.ones(self._n_amp),
        )
        model_vector = model_scale * self._model_tot
        # scale model covariance matrix with model_scale vector (in quadrature)
        cov_model = model_scale * (self._cov_model * model_scale).T
        # combine data and model covariance matrix
        cov_tot = self._cov_data + cov_model
        return model_vector, cov_tot
