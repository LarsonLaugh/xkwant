import numpy as np
import scipy
import time
import matplotlib.pyplot as plt
from xkwant.batch import *
from xkwant.physics import *
from xkwant.utils import *
from xkwant.templates import *

##########################
###### Tests for Templates
def test_doubledirac_mkhbar_4t():
    from xkwant.device import Hbar

    geop = dict(a=1, lx_leg=30, ly_leg=30, lx_neck=15, ly_neck=15)
    ham_sys = dict(ws=0.1, vs=0.3, invs=0, hybs=0.1)
    ham_lead = dict(wl=0.1, vl=0.3, invl=0, hybl=0.1)
    fsyst = doubledirac_mkhbar_4t(geop, ham_sys, ham_lead, True)
    kwant.plotter.bands(fsyst.leads[0], momenta=np.linspace(-3,3,100))


def test_gappeddirac_mkhbar_4t():
    from xkwant.device import Hbar

    geop = dict(a=1, lx_leg=30, ly_leg=30, lx_neck=15, ly_neck=15)
    ham_sys = dict(ts=0, ws=0.1, vs=0.3, ms=0.05, Wdis=0, ds = 0.1)
    ham_lead = dict(tl=0, wl=0.1, vl=0.3, ml=0.05, dl = 0.1)
    fsyst = gappeddirac_mkhbar_4t(geop, ham_sys, ham_lead, True)
    kwant.plotter.bands(fsyst.leads[0], momenta=np.linspace(-1,1,100))  
##########################

def test_hbar_from_cmodel():
    from xkwant.device import Hbar

    geop = dict(lx_leg=20, ly_leg=20, lx_neck=10, ly_neck=10)
    bhz_continuum = """
        + mu * kron(sigma_0, sigma_0)
        + M * kron(sigma_0, sigma_z)
        - B * (k_x**2 + k_y**2) * kron(sigma_0, sigma_z) - D * (k_x**2 + k_y**2) * kron(sigma_0, sigma_0)
        + A * (k_x * kron(sigma_z, sigma_x) + k_y * kron(sigma_0, sigma_y))
    """
    hbar_from_cmodel = Hbar(geop)
    ham_params = dict(A=0.09, B=-0.18, D=-0.065, M=-0.02, mu=0)
    lead_params = ham_params
    hbar_from_cmodel.build_byfill(bhz_continuum, ham_params)
    print(hbar_from_cmodel)
    [
        hbar_from_cmodel.attach_lead_byfill(bhz_continuum, lead_params, pos)
        for pos in ["bl", "br", "tl", "tr"]
    ]
    hbar_from_cmodel.set_ham_params(ham_params)
    print(hbar_from_cmodel)
    kwant.plotter.bands(hbar_from_cmodel.finalized().leads[0])


def test_hbar_from_mk():
    geop = dict(lx_leg=20, ly_leg=20, lx_neck=10, ly_neck=10)
    ham_sys = dict(ts=tk, ws=0, vs=0.1, ms=0.05, Wdis=0, a=1)
    ham_lead = dict(tl=tk, wl=0, vl=0, ml=0.05)

    hbar_from_mk_4t = mkhbar_4t(geop, ham_sys, ham_lead, False)
    print(hbar_from_mk_4t)
    hbar_from_mk_6t = mkhbar_6t(geop, ham_sys, ham_lead, False)
    print(hbar_from_mk_6t)


def test_batch():
    lamd = np.linspace(0, 80, 2)
    Iin = 10e-9  # A
    target_density = 0.01
    geop = dict(lx_leg=20, ly_leg=20, lx_neck=10, ly_neck=10)
    ham_sys = dict(ts=tk, ws=0, vs=0.1, ms=0.05, Wdis=0, a=1)
    ham_lead = dict(tl=tk, wl=0, vl=0, ml=0.05)
    energy_range = np.linspace(0, 0.15, 6)
    print(
        list(
            density_to_energy(
                *varyx_idos(
                    mkhbar_4t, geop, ham_sys, ham_lead, "vs", xvalue, energy_range
                ),
                target_density,
            )
            for xvalue in (l / 1e3 for l in lamd)
        )
    )
    print(
        list(
            density_to_energy(
                *varyx_idos(
                    mkhbar_6t, geop, ham_sys, ham_lead, "vs", xvalue, energy_range
                ),
                target_density,
            )
            for xvalue in (l / 1e3 for l in lamd)
        )
    )
    print(
        *vary_energy_vvector_4t(
            mkhbar_4t(geop, ham_sys, ham_lead, False),
            energies=energy_range,
            ivector=[0, 0, Iin, -Iin],
        )
    )
    print(
        *vary_energy_vvector_6t(
            mkhbar_6t(geop, ham_sys, ham_lead, False),
            energies=energy_range,
            ivector=[0, 0, Iin, -Iin, 0, 0],
        )
    )
    rho_site, j_site = varyx_rho_j_energy_site(
        mkhbar_4t, geop, ham_sys, ham_lead, "vl", 0.1, 0.2
    )
    rho_site, j_site = varyx_rho_j_energy_site(
        mkhbar_4t, geop, ham_sys, ham_lead, ("vs", "vl"), (0.1, 0.1), 0.2
    )
    # print(rho_site)
    # print(j_site)


def test_get_dos_kpm():
    geop = dict(lx_leg=20, ly_leg=20, lx_neck=10, ly_neck=10)
    ham_sys = dict(ts=tk, ws=0, vs=0.1, ms=0.05, Wdis=0, a=1)
    ham_lead = dict(tl=tk, wl=0, vl=0, ml=0.05)

    hbar = mkhbar_4t(geop, ham_sys, ham_lead, False)
    energy_range = np.arange(0, 6, 0.02)
    # print("Results for get_idos")
    start_time = time.time()
    dos1 = get_dos(hbar, energy_range)
    split1_time = time.time()
    # print("Results for get_idos_kpm")
    dos2, energies = get_dos_kpm(hbar)
    split2_time = time.time()
    time1 = split1_time - start_time
    time2 = split2_time - split1_time
    print(time1, time2)
    plt.plot(energy_range, dos1)
    plt.plot(energies, dos2)
    plt.show()


def test_get_idos():
    N1, L = 36, 90
    # core parameters
    geop = dict(
        a=L / N1,
        lx_leg=int(N1),
        ly_leg=int(N1 / 6),
        lx_neck=int(N1 / 6),
        ly_neck=int(N1 / 6),
    )
    hamp_sys = dict(ts=0, ws=0.1 / 3, vs=0.1, ms=0.05, Wdis=0)
    hamp_lead = dict(tl=0, wl=0.1 / 3, vl=0.1, ml=0.05)

    hbar = mkhbar_4t(geop, hamp_sys, hamp_lead, finalized=False)
    energy_range = np.linspace(0, 0.05, 50)
    start_time = time.time()
    idos_wkpm, new_energy_range = get_idos(hbar, energy_range, use_kpm=True)
    split1_time = time.time()

    idos_wokpm, _ = get_idos(hbar, energy_range, use_kpm=False)
    split2_time = time.time()

    time1 = split1_time - start_time
    time2 = split2_time - split1_time
    print(time1, time2)
    # time1 = 0.09, time2 = 4.58 idos_wkpm is 50 times faster here.
    plt.scatter(new_energy_range, idos_wkpm, label="wkpm")
    plt.scatter(energy_range, idos_wokpm, label="wokpm")
    plt.legend()
    plt.show()


def test_add_peierls_phase():
    geop = dict(lx_leg=50, ly_leg=30, lx_neck=30, ly_neck=30)
    ham_sys = dict(ts=tk, ws=0, vs=0, ms=0.05, Wdis=0, a=1)
    ham_lead = dict(tl=tk, wl=0, vl=0, ml=0.05)
    hbar = mkhbar_b4t(geop, ham_sys, ham_lead, False)
    fsyst = hbar.finalized()
    energies = []
    bvalues = np.linspace(0, 0.1, 20)
    # for B in Bfields:
    #     ham_mat = self.hamiltonin_submatrix(params=dict(B=B), sparse=True)
    #     ev = sla.eigsh(ham_mat.tocsc(),k=num_ev,sigma=0,return_eigenvectors=False)
    #     energies.append(ev)
    for B in bvalues:
        h = fsyst.hamiltonian_submatrix(params=dict(B=B))
        # energies.append(sla.eigsh(h.tocsc(),k=100,sigma=0,return_eigenvectors=False))
        energies.append(scipy.linalg.eigvalsh(h))
    plt.plot(bvalues, energies)
    # kwant.plotter.bands(fsyst.leads[0])
    plt.show()


def test_tb_magnetic_field():
    lat = kwant.lattice.square(norbs=1)
    syst = kwant.Builder(kwant.TranslationalSymmetry((-1, 0)))

    def peierls(to_site, from_site, B):
        y = from_site.tag[1]
        return -1 * np.exp(-1j * B * y)

    syst[(lat(0, j) for j in range(-19, 20))] = 4
    syst[lat.neighbors()] = -1
    syst[kwant.HoppingKind((1, 0), lat)] = peierls
    syst = syst.finalized()

    fig, ax = plt.subplots(1, 1)
    ax.set_xlabel("momentum")
    ax.set_ylabel("energy")
    ax.set_ylim(0, 1)

    params = dict(B=0.1)

    kwant.plotter.bands(syst, ax=ax, params=params)
    plt.show()


if __name__ == "__main__":
    start_time = time.time()
    # test_batch()
    # test_dirac_vary_lambda()
    # test_get_idos()
    # test_doubledirac_mkhbar_4t()
    # test_hbar_from_cmodel()
    # test_add_peierls_phase()
    # test_tb_magnetic_field()
    test_gappeddirac_mkhbar_4t()
    end_time = time.time()
    print(end_time - start_time)
