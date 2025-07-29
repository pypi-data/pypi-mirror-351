import copy

from hierarc.Likelihood.hierarchy_likelihood import LensLikelihood


class LensSampleLikelihood(object):
    """Class to evaluate the likelihood of a cosmology given a sample of angular
    diameter posteriors Currently this class does not include possible covariances
    between the lens samples."""

    def __init__(self, kwargs_lens_list, normalized=False, kwargs_global_model=None):
        """

        :param kwargs_lens_list: keyword argument list specifying the arguments of the LensLikelihood class
        :param normalized: bool, if True, returns the normalized likelihood, if False, separates the constant prefactor
         (in case of a Gaussian 1/(sigma sqrt(2 pi)) ) to compute the reduced chi2 statistics
        :param kwargs_global_model: arguments of global distribution parameters for initialization of
         ParamManager() class
        """
        if kwargs_global_model is None:
            kwargs_global_model = {}
        self._lens_list = []
        self._gamma_pl_num = 0
        gamma_pl_index = 0

        gamma_pl_global_sampling = kwargs_global_model.get(
            "gamma_pl_global_sampling", False
        )

        for kwargs_lens in kwargs_lens_list:
            gamma_pl_index_ = None
            if "kin_scaling_param_list" in kwargs_lens and not gamma_pl_global_sampling:
                kin_scaling_param_list = kwargs_lens["kin_scaling_param_list"]
                if "gamma_pl" in kin_scaling_param_list:
                    self._gamma_pl_num += 1
                    gamma_pl_index_ = copy.deepcopy(gamma_pl_index)
                    gamma_pl_index += 1
            kwargs_lens_ = self._merge_global2local_settings(
                kwargs_global_model=kwargs_global_model, kwargs_lens=kwargs_lens
            )
            self._lens_list.append(
                LensLikelihood(
                    gamma_pl_index=gamma_pl_index_,
                    normalized=normalized,
                    **kwargs_lens_
                )
            )

    def log_likelihood(
        self,
        cosmo,
        kwargs_lens=None,
        kwargs_kin=None,
        kwargs_source=None,
        kwargs_los=None,
        verbose=False,
    ):
        """

        :param cosmo: astropy.cosmology instance
        :param kwargs_lens: keywords of the parameters of the lens model
        :param kwargs_kin: keyword arguments of the kinematic model
        :param kwargs_source: keyword argument of the source model (such as SNe)
        :param kwargs_los: line of sight keyword argument list
        :param verbose: If true, prints intermediate outputs of likelihood calculation
        :type verbose: bool
        :return: log likelihood of the combined lenses
        """
        log_likelihood = 0
        for lens in self._lens_list:
            log_likelihood += lens.lens_log_likelihood(
                cosmo=cosmo,
                kwargs_lens=kwargs_lens,
                kwargs_kin=kwargs_kin,
                kwargs_source=kwargs_source,
                kwargs_los=kwargs_los,
                verbose=verbose,
            )
        return log_likelihood

    def num_data(self):
        """Number of data points across the lens sample.

        :return: integer
        """
        num = 0
        for lens in self._lens_list:
            num += lens.num_data()
        return num

    def info(self):
        """

        :return:
        """
        print("number of lenses: ", len(self._lens_list))
        print("number of data points: ", self.num_data())
        for lens in self._lens_list:
            lens.info()

    @property
    def gamma_pl_num(self):
        """Number of power-law density slope parameters being sampled on individual
        lenses.

        :return: number of power-law density slope parameters being sampled on
            individual lenses
        """
        return self._gamma_pl_num

    @staticmethod
    def _merge_global2local_settings(kwargs_global_model, kwargs_lens):
        """

        :param kwargs_global_model: dictionary of global model settings and distribution functions
        :param kwargs_lens: specific settings of an individual lens
        :return: joint dictionary that overwrites global with local parameters (if needed) and only keeps the relevant
         arguments that an individual lens likelihood needs
        :rtype: dict
        """
        kwargs_global_model_ = {}
        for key in _input_param_list:
            if key in kwargs_global_model:
                kwargs_global_model_[key] = kwargs_global_model[key]
        kwargs_global_model_subset = copy.deepcopy(kwargs_global_model_)
        return {**kwargs_global_model_subset, **kwargs_lens}


_input_param_list = [
    "anisotropy_model",
    "anisotropy_sampling",
    "anisotropy_distribution",
    "anisotropy_parameterization",
    "los_distributions",
    "lambda_mst_distribution",
    "gamma_in_sampling",
    "gamma_in_distribution",
    "log_m2l_sampling",
    "log_m2l_distribution",
    "alpha_lambda_sampling",
    "beta_lambda_sampling",
    "alpha_gamma_in_sampling",
    "alpha_log_m2l_sampling",
    "gamma_pl_global_sampling",
    "gamma_pl_global_dist",
    "log_scatter",
]
