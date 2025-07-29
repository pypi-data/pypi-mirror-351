from hierarc.Sampling.ParamManager.kin_param import KinParam
from hierarc.Sampling.ParamManager.cosmo_param import CosmoParam
from hierarc.Sampling.ParamManager.lens_param import LensParam
from hierarc.Sampling.ParamManager.source_param import SourceParam
from hierarc.Sampling.ParamManager.los_param import LOSParam


class ParamManager(object):
    """Class for managing the parameters involved."""

    def __init__(
        self,
        cosmology,
        ppn_sampling=False,
        rd_sampling=False,
        lambda_mst_sampling=False,
        lambda_mst_distribution="NONE",
        anisotropy_sampling=False,
        anisotropy_model="OM",
        anisotropy_distribution="NONE",
        anisotropy_parameterization="beta",
        gamma_in_sampling=False,
        gamma_in_distribution="NONE",
        log_m2l_sampling=False,
        log_m2l_distribution="NONE",
        lambda_ifu_sampling=False,
        lambda_ifu_distribution="NONE",
        alpha_lambda_sampling=False,
        beta_lambda_sampling=False,
        alpha_gamma_in_sampling=False,
        alpha_log_m2l_sampling=False,
        gamma_pl_num=0,
        gamma_pl_global_sampling=False,
        gamma_pl_global_dist="NONE",
        sigma_v_systematics=False,
        sne_apparent_m_sampling=False,
        sne_distribution="GAUSSIAN",
        z_apparent_m_anchor=0.1,
        log_scatter=False,
        los_sampling=False,
        los_distributions=None,
        kwargs_lower_cosmo=None,
        kwargs_upper_cosmo=None,
        kwargs_fixed_cosmo=None,
        kwargs_lower_lens=None,
        kwargs_upper_lens=None,
        kwargs_fixed_lens=None,
        kwargs_lower_kin=None,
        kwargs_upper_kin=None,
        kwargs_fixed_kin=None,
        kwargs_lower_source=None,
        kwargs_upper_source=None,
        kwargs_fixed_source=None,
        kwargs_lower_los=None,
        kwargs_upper_los=None,
        kwargs_fixed_los=None,
    ):
        """

        :param cosmology: string describing cosmological model
        :param ppn_sampling: post-newtonian parameter sampling
        :param rd_sampling: sound horizon at drag epoch sampling (used only if the BAOLIkelihood is used)
        :param lambda_mst_sampling: bool, if True adds a global mass-sheet transform parameter in the sampling
        :param lambda_mst_distribution: string, distribution function of the MST transform
        :param lambda_ifu_sampling: bool, if True samples a separate lambda_mst for a second (e.g. IFU) data set
        independently
        :param alpha_lambda_sampling: bool, if True samples a parameter alpha_lambda, which scales lambda_mst linearly
         according to a predefined quantity of the lens
        :param beta_lambda_sampling: bool, if True samples a parameter beta_lambda, which scales lambda_mst linearly
         according to a predefined quantity of the lens
        :param lambda_ifu_distribution: string, distribution function of the lambda_ifu parameter
        :param anisotropy_sampling: bool, if True adds a global stellar anisotropy parameter that alters the single lens
         kinematic prediction
        :param anisotropy_distribution: string, indicating the distribution function of the anisotropy model
        :param gamma_in_sampling: bool, if True samples gNFW inner slope parameter
        :param gamma_in_distribution: string, distribution function of the gamma_in parameter
        :param log_m2l_sampling: bool, if True samples the mass-to-light ratio of the stars in logarithmic scale
        :param log_m2l_distribution: string, distribution function of the log_m2l parameter
        :param alpha_gamma_in_sampling: bool, if True samples a parameter alpha_gamma_in, which scales gamma_in linearly
            according to a predefined quantity of the lens
        :param alpha_log_m2l_sampling: bool, if True samples a parameter alpha_log_m2l, which scales log_m2l linearly
            according to a predefined quantity of the lens
        :param gamma_pl_num: int, number of power-law density slopes being sampled (to be assigned to individual lenses)
        :param gamma_pl_global_sampling: if sampling a global power-law density slope distribution
        :type gamma_pl_global_sampling: bool
        :param gamma_pl_global_dist: distribution of global gamma_pl distribution ("GAUSSIAN" or "NONE")
        :param sne_apparent_m_sampling: boolean, if True, samples/queries SNe unlensed magnitude distribution
         (not intrinsic magnitudes but apparent!)
        :param sne_distribution: string, apparent non-lensed brightness distribution (in linear space).
         Currently supports:
         'GAUSSIAN': Gaussian distribution
        :param sigma_v_systematics: bool, if True samples paramaters relative to systematics in the velocity dispersion
         measurement
        :param log_scatter: boolean, if True, samples the Gaussian scatter amplitude in log space (and thus flat prior in log)
        :param los_sampling: if sampling of the parameters should be done
        :type los_sampling: bool
        :param los_distributions: list of line of sight distributions to be sampled
        :type los_distributions: list of str
        :param kwargs_fixed_los: fixed arguments in sampling
        :type kwargs_fixed_los: list of dictionaries for each los distribution
        :param anisotropy_parameterization: model of parameterization (currently for constant anisotropy),
         ["beta" or "TAN_RAD"] supported
        :type anisotropy_parameterization: str
        """
        self._kin_param = KinParam(
            anisotropy_sampling=anisotropy_sampling,
            anisotropy_model=anisotropy_model,
            distribution_function=anisotropy_distribution,
            log_scatter=log_scatter,
            sigma_v_systematics=sigma_v_systematics,
            kwargs_fixed=kwargs_fixed_kin,
            anisotropy_parameterization=anisotropy_parameterization,
        )
        self._cosmo_param = CosmoParam(
            cosmology=cosmology,
            ppn_sampling=ppn_sampling,
            rd_sampling=rd_sampling,
            kwargs_fixed=kwargs_fixed_cosmo,
        )
        self._lens_param = LensParam(
            lambda_mst_sampling=lambda_mst_sampling,
            lambda_mst_distribution=lambda_mst_distribution,
            lambda_ifu_sampling=lambda_ifu_sampling,
            lambda_ifu_distribution=lambda_ifu_distribution,
            gamma_in_sampling=gamma_in_sampling,
            gamma_in_distribution=gamma_in_distribution,
            log_m2l_sampling=log_m2l_sampling,
            log_m2l_distribution=log_m2l_distribution,
            alpha_lambda_sampling=alpha_lambda_sampling,
            beta_lambda_sampling=beta_lambda_sampling,
            alpha_gamma_in_sampling=alpha_gamma_in_sampling,
            alpha_log_m2l_sampling=alpha_log_m2l_sampling,
            gamma_pl_num=gamma_pl_num,
            gamma_pl_global_sampling=gamma_pl_global_sampling,
            gamma_pl_global_dist=gamma_pl_global_dist,
            log_scatter=log_scatter,
            kwargs_fixed=kwargs_fixed_lens,
        )
        self._source_param = SourceParam(
            sne_apparent_m_sampling=sne_apparent_m_sampling,
            sne_distribution=sne_distribution,
            z_apparent_m_anchor=z_apparent_m_anchor,
            kwargs_fixed=kwargs_fixed_source,
        )
        self._los_param = LOSParam(
            los_sampling=los_sampling,
            los_distributions=los_distributions,
            kwargs_fixed=kwargs_fixed_los,
        )
        self._kwargs_upper_cosmo, self._kwargs_lower_cosmo = (
            kwargs_upper_cosmo,
            kwargs_lower_cosmo,
        )
        self._kwargs_upper_lens, self._kwargs_lower_lens = (
            kwargs_upper_lens,
            kwargs_lower_lens,
        )
        self._kwargs_upper_kin, self._kwargs_lower_kin = (
            kwargs_upper_kin,
            kwargs_lower_kin,
        )
        self._kwargs_upper_source, self._kwargs_lower_source = (
            kwargs_upper_source,
            kwargs_lower_source,
        )
        self._kwargs_upper_los, self._kwargs_lower_los = (
            kwargs_upper_los,
            kwargs_lower_los,
        )

    @property
    def num_param(self):
        """Number of parameters being sampled.

        :return: integer
        """
        return len(self.param_list())

    def param_list(self, latex_style=False):
        """

        :param latex_style: bool, if True returns strings in latex symbols, else in the convention of the sampler
        :return: list of the free parameters being sampled in the same order as the sampling
        """
        list_param = []
        list_param += self._cosmo_param.param_list(latex_style=latex_style)
        list_param += self._lens_param.param_list(latex_style=latex_style)
        list_param += self._kin_param.param_list(latex_style=latex_style)
        list_param += self._source_param.param_list(latex_style=latex_style)
        list_param += self._los_param.param_list(latex_style=latex_style)
        return list_param

    def args2kwargs(self, args):
        """

        :param args: sampling argument list
        :return: keyword argument list with parameter names
        """
        i = 0
        kwargs_cosmo, i = self._cosmo_param.args2kwargs(args, i=i)
        kwargs_lens, i = self._lens_param.args2kwargs(args, i=i)
        kwargs_kin, i = self._kin_param.args2kwargs(args, i=i)
        kwargs_source, i = self._source_param.args2kwargs(args, i=i)
        kwargs_los, i = self._los_param.args2kwargs(args, i=i)
        return kwargs_cosmo, kwargs_lens, kwargs_kin, kwargs_source, kwargs_los

    def kwargs2args(
        self,
        kwargs_cosmo=None,
        kwargs_lens=None,
        kwargs_kin=None,
        kwargs_source=None,
        kwargs_los=None,
    ):
        """

        :param kwargs_cosmo: keyword argument list of parameters for cosmology sampling
        :param kwargs_lens: keyword argument list of parameters for lens model sampling
        :param kwargs_kin: keyword argument list of parameters for kinematic sampling
        :param kwargs_source: keyword arguments of parameters of source brightness
        :param kwargs_los: keyword arguments of parameters of the line of sight
        :return: sampling argument list in specified order
        """
        args = []
        args += self._cosmo_param.kwargs2args(kwargs_cosmo)
        args += self._lens_param.kwargs2args(kwargs_lens)
        args += self._kin_param.kwargs2args(kwargs_kin)
        args += self._source_param.kwargs2args(kwargs_source)
        args += self._los_param.kwargs2args(kwargs_los)
        return args

    def cosmo(self, kwargs_cosmo):
        """

        :param kwargs_cosmo: keyword arguments of parameters (can include others not used for the cosmology)
        :return: cosmology
        :rtype: ~astropy.cosmology instance
        """
        return self._cosmo_param.cosmo(kwargs_cosmo)

    @property
    def param_bounds(self):
        """

        :return: argument list of the hard bounds in the order of the sampling
        """
        lower_limit = self.kwargs2args(
            kwargs_cosmo=self._kwargs_lower_cosmo,
            kwargs_lens=self._kwargs_lower_lens,
            kwargs_kin=self._kwargs_lower_kin,
            kwargs_source=self._kwargs_lower_source,
            kwargs_los=self._kwargs_lower_los,
        )
        upper_limit = self.kwargs2args(
            kwargs_cosmo=self._kwargs_upper_cosmo,
            kwargs_lens=self._kwargs_upper_lens,
            kwargs_kin=self._kwargs_upper_kin,
            kwargs_source=self._kwargs_upper_source,
            kwargs_los=self._kwargs_upper_los,
        )
        return lower_limit, upper_limit
