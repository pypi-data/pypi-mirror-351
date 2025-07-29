import pytest
from hierarc.Likelihood.transformed_cosmography import TransformedCosmography
from lenstronomy.Util.data_util import magnitude2cps
import numpy.testing as npt


class TestTransformedCoismography(object):
    def setup_method(self):
        self.transform = TransformedCosmography()

    def test_displace_prediction(self):
        ddt, dd = 1, 1
        mag_source = 16
        magnitude_zero_point = 20
        amp_source = magnitude2cps(
            magnitude=mag_source, magnitude_zero_point=magnitude_zero_point
        )
        # case where nothing happens
        ddt_, dd_, mag_source_ = self.transform.displace_prediction(
            ddt, dd, gamma_ppn=1, lambda_mst=1, kappa_ext=0, mag_source=mag_source
        )
        assert ddt == ddt_
        assert dd == dd_
        assert mag_source_ == mag_source

        # case where kappa_ext is displaced
        kappa_ext = 0.1
        ddt_, dd_, mag_source_ = self.transform.displace_prediction(
            ddt,
            dd,
            gamma_ppn=1,
            lambda_mst=1,
            kappa_ext=kappa_ext,
            mag_source=mag_source,
        )
        assert ddt_ == ddt * (1 - kappa_ext)
        assert dd_ == dd
        amp_source_ = magnitude2cps(
            magnitude=mag_source_, magnitude_zero_point=magnitude_zero_point
        )
        npt.assert_almost_equal(
            amp_source_, amp_source / (1 - kappa_ext) ** 2, decimal=7
        )

        # case where lambda_mst is displaced
        lambda_mst = 0.9
        ddt_, dd_, mag_source_ = self.transform.displace_prediction(
            ddt,
            dd,
            gamma_ppn=1,
            lambda_mst=lambda_mst,
            kappa_ext=0,
            mag_source=mag_source,
        )
        assert ddt_ == ddt * lambda_mst
        assert dd == dd_
        amp_source_ = magnitude2cps(
            magnitude=mag_source_, magnitude_zero_point=magnitude_zero_point
        )
        npt.assert_almost_equal(amp_source_, amp_source / lambda_mst**2, decimal=7)
        # case for gamma_ppn
        gamma_ppn = 1.1
        ddt_, dd_, mag_source_ = self.transform.displace_prediction(
            ddt,
            dd,
            gamma_ppn=gamma_ppn,
            lambda_mst=1,
            kappa_ext=0,
            mag_source=mag_source,
        )
        assert ddt_ == ddt
        assert dd_ == dd * (1 + gamma_ppn) / 2.0
        assert mag_source_ == mag_source

    def test_displace_kappa_ext(self):
        ddt, dd = 1, 1
        kappa_ext = 0.1
        ddt_, dd_ = self.transform._displace_kappa_ext(ddt, dd, kappa_ext=kappa_ext)
        assert ddt_ == ddt * (1 - kappa_ext)
        assert dd == dd_

    def test_displace_ddt_gamma_pl(self):
        ddt = 10
        gamma_pl = 2.1
        transform = TransformedCosmography(gamma_pl_pivot=2, gamma_pl_ddt_slope=-0.1)
        ddt_ = transform._displace_gamma_pl(ddt, gamma_pl)
        npt.assert_almost_equal(ddt_, ddt + 0.1 * 0.1)


if __name__ == "__main__":
    pytest.main()
