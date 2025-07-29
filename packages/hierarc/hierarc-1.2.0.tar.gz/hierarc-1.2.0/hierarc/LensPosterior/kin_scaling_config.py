import numpy as np
from hierarc.Likelihood.kin_scaling import KinScalingParamManager


class KinScalingConfig(KinScalingParamManager):
    """Class to manage the anisotropy model and parameters for the Posterior
    processing."""

    def __init__(
        self,
        anisotropy_model,
        r_eff,
        gamma_in_scaling=None,
        log_m2l_scaling=None,
        gamma_pl_scaling=None,
        gamma_pl_mean=None,
    ):
        """

        :param anisotropy_model: type of stellar anisotropy model. Supported are 'OM' and 'GOM' or 'const',
         see details in lenstronomy.Galkin module
        :param r_eff: half-light radius of the deflector galaxy
        :param gamma_in_scaling: array of gamma_in parameter to be interpolated (optional, otherwise None)
        :param log_m2l_scaling: array of log_m2l parameter to be interpolated (optional, otherwise None)
        :param gamma_pl_scaling: array of power-law density profile slopes to be interpolated (optional, otherwise None)
        :param gamma_pl_mean: mean gamma_pl upon which the covariances are calculated
        """
        self._r_eff = r_eff
        self._anisotropy_model = anisotropy_model
        self._param_name_list = []

        if self._anisotropy_model == "OM":
            self._ani_param_array = [np.array([0.1, 0.2, 0.5, 1, 2, 5])]
            # used for r_ani OsipkovMerritt anisotropy description
            self._param_name_list = ["a_ani"]
        elif self._anisotropy_model == "GOM":
            self._ani_param_array = [
                np.array([0.1, 0.2, 0.5, 1, 2, 5]),
                np.array([0, 0.5, 0.8, 1]),
            ]
            self._param_name_list = ["a_ani", "beta_inf"]
        elif self._anisotropy_model == "const":
            self._ani_param_array = [
                np.linspace(-0.49, 1, 7)
            ]  # used for constant anisotropy description
            self._param_name_list = ["a_ani"]
        elif self._anisotropy_model == "NONE":
            self._param_name_list = []
        else:
            raise ValueError(
                "anisotropy model %s not supported." % self._anisotropy_model
            )
        self._gamma_in_scaling = gamma_in_scaling
        self._log_m2l_scaling = log_m2l_scaling
        self._gamma_pl_scaling = gamma_pl_scaling
        self._gamma_pl_mean = gamma_pl_mean

        if gamma_in_scaling is not None:
            self._param_name_list.append("gamma_in")
            self._ani_param_array.append(np.array(gamma_in_scaling))
        if log_m2l_scaling is not None:
            self._param_name_list.append("log_m2l")
            self._ani_param_array.append(np.array(log_m2l_scaling))
        if gamma_pl_scaling is not None:
            self._param_name_list.append("gamma_pl")
            self._ani_param_array.append(np.array(gamma_pl_scaling))
        KinScalingParamManager.__init__(
            self, j_kin_scaling_param_name_list=self._param_name_list
        )

    @property
    def kwargs_anisotropy_base(self):
        """

        :return: keyword arguments of base anisotropy model configuration
        """
        if self._anisotropy_model == "OM":
            a_ani_0 = 1
            r_ani = a_ani_0 * self._r_eff
            kwargs_anisotropy_0 = {"r_ani": r_ani}
        elif self._anisotropy_model == "GOM":
            a_ani_0 = 1
            r_ani = a_ani_0 * self._r_eff
            beta_inf_0 = 1
            kwargs_anisotropy_0 = {"r_ani": r_ani, "beta_inf": beta_inf_0}
        elif self._anisotropy_model == "const":
            a_ani_0 = 0.1
            kwargs_anisotropy_0 = {"beta": a_ani_0}
        else:
            raise ValueError(
                "anisotropy model %s not supported." % self._anisotropy_model
            )
        return kwargs_anisotropy_0

    @property
    def kwargs_lens_base(self):
        """

        :return: keyword arguments of lens model parameters that are getting interpolated
        """
        kwargs_base = {}
        if "gamma_in" in self._param_name_list:
            kwargs_base["gamma_in"] = np.mean(self._gamma_in_scaling)
        if "log_m2l" in self._param_name_list:
            kwargs_base["log_m2l"] = np.mean(self._log_m2l_scaling)
        if "gamma_pl" in self._param_name_list:
            kwargs_base["gamma_pl"] = self._gamma_pl_mean
        return kwargs_base

    @property
    def kin_scaling_param_array(self):
        """

        :return: numpy array of kinematic scaling parameter values to be explored, list of 1D arrays
        """
        return self._ani_param_array

    @property
    def param_name_list(self):
        """List of parameters in same order as interpolated.

        :return:
        """
        return self._param_name_list

    def anisotropy_kwargs(self, a_ani=None, beta_inf=None):
        """

        :param a_ani: anisotropy parameter
        :param beta_inf: anisotropy at infinity (only used for 'GOM' model)
        :return: list of anisotropy keyword arguments for GalKin module
        """

        if self._anisotropy_model == "OM":
            r_ani = a_ani * self._r_eff
            kwargs_anisotropy = {"r_ani": r_ani}
        elif self._anisotropy_model == "GOM":
            r_ani = a_ani * self._r_eff
            kwargs_anisotropy = {"r_ani": r_ani, "beta_inf": beta_inf}
        elif self._anisotropy_model == "const":
            kwargs_anisotropy = {"beta": a_ani}
        else:
            raise ValueError(
                "anisotropy model %s not supported." % self._anisotropy_model
            )
        return kwargs_anisotropy
