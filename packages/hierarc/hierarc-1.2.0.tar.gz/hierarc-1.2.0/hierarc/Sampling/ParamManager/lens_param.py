import numpy as np


class LensParam(object):
    """Manages the lens model covariant parameters."""

    def __init__(
        self,
        lambda_mst_sampling=False,
        lambda_mst_distribution="NONE",
        lambda_ifu_sampling=False,
        lambda_ifu_distribution="NONE",
        gamma_in_sampling=False,
        gamma_in_distribution="NONE",
        log_m2l_sampling=False,
        log_m2l_distribution="NONE",
        alpha_lambda_sampling=False,
        beta_lambda_sampling=False,
        alpha_gamma_in_sampling=False,
        alpha_log_m2l_sampling=False,
        gamma_pl_num=0,
        gamma_pl_global_sampling=False,
        gamma_pl_global_dist="NONE",
        kwargs_fixed=None,
        log_scatter=False,
    ):
        """

        :param lambda_mst_sampling: bool, if True adds a global mass-sheet transform parameter in the sampling
        :param lambda_mst_distribution: string, distribution function of the MST transform
        :param lambda_ifu_sampling: bool, if True samples a separate lambda_mst for a
            second (e.g. IFU) data set independently
        :param lambda_ifu_distribution: string, distribution function of the lambda_ifu parameter
        :param gamma_in_sampling: bool, if True samples the inner slope of the GNFW profile
        :param gamma_in_distribution: string, distribution function of the inner
            slope of the GNFW profile
        :param log_m2l_sampling: bool, if True samples the mass to light ratio of
            the stars in logarithmic scale
        :param log_m2l_distribution: string, distribution function of the logarithm of mass to
            light ratio of the lens
        :param kappa_ext_sampling: bool, if True samples a global external convergence
            parameter
        :param kappa_ext_distribution: string, distribution function of the kappa_ext
            parameter
        :param alpha_lambda_sampling: bool, if True samples a parameter alpha_lambda, which scales lambda_mst linearly
            according to a predefined quantity of the lens
        :param beta_lambda_sampling: bool, if True samples a parameter beta_lambda, which scales lambda_mst linearly
            according to a predefined quantity of the lens
        :param alpha_gamma_in_sampling: bool, if True samples a parameter alpha_gamma_in, which scales gamma_in linearly
        :param alpha_log_m2l_sampling: bool, if True samples a parameter alpha_log_m2l, which scales log_m2l linearly
        :param gamma_pl_num: int, number of power-law density slopes being sampled (to be assigned to individual lenses)
        :param gamma_pl_global_sampling: if sampling a global power-law density slope distribution
        :type gamma_pl_global_sampling: bool
        :param gamma_pl_global_dist: distribution of global gamma_pl distribution ("GAUSSIAN" or "NONE")
        :param log_scatter: boolean, if True, samples the Gaussian scatter amplitude in log space (and thus flat prior
         in log)
        :param kwargs_fixed: keyword arguments that are held fixed through the sampling
        """
        self._lambda_mst_sampling = lambda_mst_sampling
        self._lambda_mst_distribution = lambda_mst_distribution
        self._lambda_ifu_sampling = lambda_ifu_sampling
        self._lambda_ifu_distribution = lambda_ifu_distribution
        self._gamma_in_sampling = gamma_in_sampling
        self._gamma_in_distribution = gamma_in_distribution
        self._log_m2l_sampling = log_m2l_sampling
        self._log_m2l_distribution = log_m2l_distribution
        self._alpha_lambda_sampling = alpha_lambda_sampling
        self._beta_lambda_sampling = beta_lambda_sampling
        self._alpha_gamma_in_sampling = alpha_gamma_in_sampling
        self._alpha_log_m2l_sampling = alpha_log_m2l_sampling
        self._gamma_pl_num = gamma_pl_num
        self._gamma_pl_global_sampling = gamma_pl_global_sampling
        self._gamma_pl_global_dist = gamma_pl_global_dist

        self._log_scatter = log_scatter
        if kwargs_fixed is None:
            kwargs_fixed = {}
        self._kwargs_fixed = kwargs_fixed

    def param_list(self, latex_style=False):
        """

        :param latex_style: bool, if True returns strings in latex symbols, else in the convention of the sampler
        :return: list of the free parameters being sampled in the same order as the sampling
        """
        list = []
        if self._lambda_mst_sampling is True:
            if "lambda_mst" not in self._kwargs_fixed:
                if latex_style is True:
                    list.append(r"$\overline{\lambda}_{\rm int}$")
                else:
                    list.append("lambda_mst")
            if self._lambda_mst_distribution == "GAUSSIAN":
                if "lambda_mst_sigma" not in self._kwargs_fixed:
                    if latex_style is True:
                        if self._log_scatter is True:
                            list.append(r"$\log_{10}\sigma(\lambda_{\rm int})$")
                        else:
                            list.append(r"$\sigma(\lambda_{\rm int})$")
                    else:
                        list.append("lambda_mst_sigma")
        if self._lambda_ifu_sampling is True:
            if "lambda_ifu" not in self._kwargs_fixed:
                if latex_style is True:
                    list.append(r"$\lambda_{\rm ifu}$")
                else:
                    list.append("lambda_ifu")
            if self._lambda_ifu_distribution == "GAUSSIAN":
                if "lambda_ifu_sigma" not in self._kwargs_fixed:
                    if latex_style is True:
                        if self._log_scatter is True:
                            list.append(r"$\log_{10}\sigma(\lambda_{\rm ifu})$")
                        else:
                            list.append(r"$\sigma(\lambda_{\rm ifu})$")
                    else:
                        list.append("lambda_ifu_sigma")
        if self._gamma_in_sampling:
            if "gamma_in" not in self._kwargs_fixed:
                if latex_style is True:
                    list.append(r"$\gamma_{\rm in}$")
                else:
                    list.append("gamma_in")
            if self._gamma_in_distribution == "GAUSSIAN":
                if "gamma_in_sigma" not in self._kwargs_fixed:
                    if latex_style is True:
                        if self._log_scatter is True:
                            list.append(r"$\log_{10}\sigma(\gamma_{\rm in})$")
                        else:
                            list.append(r"$\sigma(\gamma_{\rm in})$")
                    else:
                        list.append("gamma_in_sigma")
        if self._log_m2l_sampling is True:
            if "log_m2l" not in self._kwargs_fixed:
                if latex_style is True:
                    list.append(r"$\Upsilon_{\rm stars}$")
                else:
                    list.append("log_m2l")
            if self._log_m2l_distribution == "GAUSSIAN":
                if "log_m2l_sigma" not in self._kwargs_fixed:
                    if latex_style is True:
                        if self._log_scatter is True:
                            list.append(r"$\log_{10}\sigma(\Upsilon_{\rm stars})$")
                        else:
                            list.append(r"$\sigma(\Upsilon_{\rm stars})$")
                    else:
                        list.append("log_m2l_sigma")
        if self._alpha_lambda_sampling is True:
            if "alpha_lambda" not in self._kwargs_fixed:
                if latex_style is True:
                    list.append(r"$\alpha_{\lambda}$")
                else:
                    list.append("alpha_lambda")
        if self._beta_lambda_sampling is True:
            if "beta_lambda" not in self._kwargs_fixed:
                if latex_style is True:
                    list.append(r"$\beta_{\lambda}$")
                else:
                    list.append("beta_lambda")
        if self._alpha_gamma_in_sampling is True:
            if "alpha_gamma_in" not in self._kwargs_fixed:
                if latex_style is True:
                    list.append(r"$\alpha_{\gamma_{\rm in}}$")
                else:
                    list.append("alpha_gamma_in")
        if self._alpha_log_m2l_sampling is True:
            if "alpha_log_m2l" not in self._kwargs_fixed:
                if latex_style is True:
                    list.append(r"$\alpha_{\Upsilon_{\rm stars}}$")
                else:
                    list.append("alpha_log_m2l")
        for i in range(self._gamma_pl_num):
            if latex_style is True:
                list.append(r"$\gamma_{\rm pl %i}$" % i)
            else:
                list.append("gamma_pl_%s" % i)
        if self._gamma_pl_global_sampling is True:
            if "gamma_pl_mean" not in self._kwargs_fixed:
                if latex_style is True:
                    list.append(r"$\overline{\gamma}_{\rm pl}$")
                else:
                    list.append("gamma_pl_mean")
            if self._gamma_pl_global_dist == "GAUSSIAN":
                if "gamma_pl_sigma" not in self._kwargs_fixed:
                    if latex_style is True:
                        list.append(r"$\sigma(\gamma_{\rm pl, global})$")
                    else:
                        list.append("gamma_pl_sigma")
        return list

    def args2kwargs(self, args, i=0):
        """

        :param args: sampling argument list
        :return: keyword argument list with parameter names
        """
        kwargs = {}
        if self._lambda_mst_sampling is True:
            if "lambda_mst" in self._kwargs_fixed:
                kwargs["lambda_mst"] = self._kwargs_fixed["lambda_mst"]
            else:
                kwargs["lambda_mst"] = args[i]
                i += 1
            if self._lambda_mst_distribution == "GAUSSIAN":
                if "lambda_mst_sigma" in self._kwargs_fixed:
                    kwargs["lambda_mst_sigma"] = self._kwargs_fixed["lambda_mst_sigma"]
                else:
                    if self._log_scatter is True:
                        kwargs["lambda_mst_sigma"] = 10 ** (args[i])
                    else:
                        kwargs["lambda_mst_sigma"] = args[i]
                    i += 1
        if self._lambda_ifu_sampling is True:
            if "lambda_ifu" in self._kwargs_fixed:
                kwargs["lambda_ifu"] = self._kwargs_fixed["lambda_ifu"]
            else:
                kwargs["lambda_ifu"] = args[i]
                i += 1
            if self._lambda_ifu_distribution == "GAUSSIAN":
                if "lambda_ifu_sigma" in self._kwargs_fixed:
                    kwargs["lambda_ifu_sigma"] = self._kwargs_fixed["lambda_ifu_sigma"]
                else:
                    if self._log_scatter is True:
                        kwargs["lambda_ifu_sigma"] = 10 ** (args[i])
                    else:
                        kwargs["lambda_ifu_sigma"] = args[i]
                    i += 1
        if self._gamma_in_sampling is True:
            if "gamma_in" in self._kwargs_fixed:
                kwargs["gamma_in"] = self._kwargs_fixed["gamma_in"]
            else:
                kwargs["gamma_in"] = args[i]
                i += 1
            if self._gamma_in_distribution == "GAUSSIAN":
                if "gamma_in_sigma" in self._kwargs_fixed:
                    kwargs["gamma_in_sigma"] = self._kwargs_fixed["gamma_in_sigma"]
                else:
                    if self._log_scatter is True:
                        kwargs["gamma_in_sigma"] = 10 ** (args[i])
                    else:
                        kwargs["gamma_in_sigma"] = args[i]
                    i += 1
        if self._log_m2l_sampling is True:
            if "log_m2l" in self._kwargs_fixed:
                kwargs["log_m2l"] = self._kwargs_fixed["log_m2l"]
            else:
                kwargs["log_m2l"] = args[i]
                i += 1
            if self._log_m2l_distribution == "GAUSSIAN":
                if "log_m2l_sigma" in self._kwargs_fixed:
                    kwargs["log_m2l_sigma"] = self._kwargs_fixed["log_m2l_sigma"]
                else:
                    if self._log_scatter is True:
                        kwargs["log_m2l_sigma"] = 10 ** (args[i])
                    else:
                        kwargs["log_m2l_sigma"] = args[i]
                    i += 1
        if self._alpha_lambda_sampling is True:
            if "alpha_lambda" in self._kwargs_fixed:
                kwargs["alpha_lambda"] = self._kwargs_fixed["alpha_lambda"]
            else:
                kwargs["alpha_lambda"] = args[i]
                i += 1
        if self._beta_lambda_sampling is True:
            if "beta_lambda" in self._kwargs_fixed:
                kwargs["beta_lambda"] = self._kwargs_fixed["beta_lambda"]
            else:
                kwargs["beta_lambda"] = args[i]
                i += 1
        if self._alpha_gamma_in_sampling is True:
            if "alpha_gamma_in" in self._kwargs_fixed:
                kwargs["alpha_gamma_in"] = self._kwargs_fixed["alpha_gamma_in"]
            else:
                kwargs["alpha_gamma_in"] = args[i]
                i += 1
        if self._alpha_log_m2l_sampling is True:
            if "alpha_log_m2l" in self._kwargs_fixed:
                kwargs["alpha_log_m2l"] = self._kwargs_fixed["alpha_log_m2l"]
            else:
                kwargs["alpha_log_m2l"] = args[i]
                i += 1
        if self._gamma_pl_num > 0:
            gamma_pl_list = []
            for k in range(self._gamma_pl_num):
                gamma_pl_list.append(args[i])
                i += 1
            kwargs["gamma_pl_list"] = gamma_pl_list
        if self._gamma_pl_global_sampling is True:
            if "gamma_pl_mean" in self._kwargs_fixed:
                kwargs["gamma_pl_mean"] = self._kwargs_fixed["gamma_pl_mean"]
            else:
                kwargs["gamma_pl_mean"] = args[i]
                i += 1
            if self._gamma_pl_global_dist == "GAUSSIAN":
                if "gamma_pl_sigma" in self._kwargs_fixed:
                    kwargs["gamma_pl_sigma"] = self._kwargs_fixed["gamma_pl_sigma"]
                else:
                    kwargs["gamma_pl_sigma"] = args[i]
                    i += 1

        return kwargs, i

    def kwargs2args(self, kwargs):
        """

        :param kwargs: keyword argument list of parameters
        :return: sampling argument list in specified order
        """
        args = []
        if self._lambda_mst_sampling is True:
            if "lambda_mst" not in self._kwargs_fixed:
                args.append(kwargs["lambda_mst"])
            if self._lambda_mst_distribution == "GAUSSIAN":
                if "lambda_mst_sigma" not in self._kwargs_fixed:
                    if self._log_scatter is True:
                        args.append(np.log10(kwargs["lambda_mst_sigma"]))
                    else:
                        args.append(kwargs["lambda_mst_sigma"])
        if self._lambda_ifu_sampling is True:
            if "lambda_ifu" not in self._kwargs_fixed:
                args.append(kwargs["lambda_ifu"])
            if self._lambda_ifu_distribution == "GAUSSIAN":
                if "lambda_ifu_sigma" not in self._kwargs_fixed:
                    if self._log_scatter is True:
                        args.append(np.log10(kwargs["lambda_ifu_sigma"]))
                    else:
                        args.append(kwargs["lambda_ifu_sigma"])
        if self._gamma_in_sampling is True:
            if "gamma_in" not in self._kwargs_fixed:
                args.append(kwargs["gamma_in"])
            if self._gamma_in_distribution == "GAUSSIAN":
                if "gamma_in_sigma" not in self._kwargs_fixed:
                    if self._log_scatter is True:
                        args.append(np.log10(kwargs["gamma_in_sigma"]))
                    else:
                        args.append(kwargs["gamma_in_sigma"])
        if self._log_m2l_sampling is True:
            if "log_m2l" not in self._kwargs_fixed:
                args.append(kwargs["log_m2l"])
            if self._log_m2l_distribution == "GAUSSIAN":
                if "log_m2l_sigma" not in self._kwargs_fixed:
                    if self._log_scatter is True:
                        args.append(np.log10(kwargs["log_m2l_sigma"]))
                    else:
                        args.append(kwargs["log_m2l_sigma"])
        if self._alpha_lambda_sampling is True:
            if "alpha_lambda" not in self._kwargs_fixed:
                args.append(kwargs["alpha_lambda"])
        if self._beta_lambda_sampling is True:
            if "beta_lambda" not in self._kwargs_fixed:
                args.append(kwargs["beta_lambda"])
        if self._alpha_gamma_in_sampling is True:
            if "alpha_gamma_in" not in self._kwargs_fixed:
                args.append(kwargs["alpha_gamma_in"])
        if self._alpha_log_m2l_sampling is True:
            if "alpha_log_m2l" not in self._kwargs_fixed:
                args.append(kwargs["alpha_log_m2l"])
        if self._gamma_pl_num > 0:
            for i in range(self._gamma_pl_num):
                args.append(kwargs["gamma_pl_list"][i])
        if self._gamma_pl_global_sampling is True:
            if "gamma_pl_mean" not in self._kwargs_fixed:
                args.append(kwargs["gamma_pl_mean"])
            if self._gamma_pl_global_dist == "GAUSSIAN":
                if "gamma_pl_sigma" not in self._kwargs_fixed:
                    args.append(kwargs["gamma_pl_sigma"])
        return args
