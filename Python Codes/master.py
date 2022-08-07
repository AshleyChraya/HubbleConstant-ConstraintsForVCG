import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from math import sqrt, pow
from scipy.integrate import quad
from cobaya.run import run
from getdist.mcsamples import MCSamplesFromCobaya
import getdist.plots as gdplt
from collections import OrderedDict as odict


plt.rcParams["figure.figsize"] = (20, 18)

directory = "/media/ash/1tb/github/HubbleConstant-ConstraintsForVCG/"
plt.style.use(f"{directory}standard.mplstyle")

# Reading SN Pantheon data
def SNdata():
    # Covariance data
    InverseCmat = pd.read_csv(
        f"{directory}AVGCfrom1to1048ORD.txt", sep="\t", header=None
    )  # import the matrices from SNe (Cmat) where C is the complete Coariance matrix from Dstat and Csys already inverted
    # Cov = Dstat + Csyst;  statistical matrix Dstat only has the diagonal components, it includes the distance error of each SNIa
    # Csys is the systematic covariance for each SNIa
    Cinverse = np.array(InverseCmat)
    Cmat = np.linalg.inv(Cinverse)  # Inverse of the inverse =  Cov
    Dstatinverse = np.diag(
        Cinverse
    )  # extract only the diagonal statistical uncertainties for SNe = Dstat (Dstat, see Scolnic et al. 2018)
    Dstat = np.diag(Cmat) ** 1 / 2  # Diagonal elements

    # SNe data
    SNdata = pd.read_csv(f"{directory}AVGdeltamulcfrom1to1048ORD.txt", sep="\t")
    # Columns are muobs	zHD	zhel  mu-M  mu-M_err
    SNdata = SNdata.sort_values(by=["zHD"])
    zSNe = SNdata["zHD"].to_numpy()
    zhel = SNdata["zhel"].to_numpy()  # zhel is the heliocentric redshift
    muobs = SNdata["muobs"].to_numpy()  # The mu_observed of the SNe are already in Mpc

    return zhel, zSNe, muobs, Cinverse


# Defining part which comes inside integeration of distance Luminosity
def integrand(x, omega_m, n):
    return 1 / (
        pow((1 + x), 2)
        * (
            omega_r0
            + (omega_b0 / (1 + x))
            + (
                (1 - omega_b0 - omega_r0)
                * ((omega_m * (1 + x) ** 6) + (1 - omega_m) * (1 + x) ** n) ** (0.5)
                / (1 + x) ** (4)
            )
        )
        ** (0.5)
    )


def likelihood(zSNe, omega_m, n, H0):

    ckm = 299792.458
    H0 = 70
    zhel, zSNe, muobs, Cinverse = SNdata()

    coefSNe = (ckm / H0) * (1 + zhel)

    d_parSNe = np.array([])
    for i in zSNe:
        Integ = quad(integrand, 0, i, args=(omega_m, n))  # Integration in DL formula
        d_parSNe = np.append(d_parSNe, Integ[0])

    dSNe = np.array(coefSNe * d_parSNe)  # Distance Luminosity in Mpc
    logdl_thSNe = np.log10(dSNe)
    muthSNe = 5 * logdl_thSNe + 25  # Theoretical distance modulus
    Deltamu = muobs - muthSNe
    chi2_SNe = np.matmul(Deltamu, np.matmul(Cinverse, Deltamu))

    if omega_m <= 0.0 or H0 < 0:  # If the value comes out to be less than zero, set it to small likelyhood
        loglikely = -1.0e100
    else:
        loglikely = -0.5 * chi2_SNe

    return loglikely


def mcmc(likelihood):
    chisq = []

    guess = [0.3, 1.2, 70]
    omega_m, n, H0 = guess
    sigma = 5
    parameters = ["omega_m", "n", "H0"]
    info_PS = {"likelihood": {"agostini": likelihood}}

    info_PS["params"] = odict(
        [
            [
                "omega_m",
                {
                    "prior": {"dist": "norm", "loc": 0.11, "scale": sigma * chisq},
                    "ref": omega_m,
                    "latex": r"\Omega_m",
                    "proposal": 0.001,
                },
            ],
            [
                "n",
                {
                    "prior": {"dist": "norm", "loc": 1.25, "scale": sigma * chisq},
                    "ref": n,
                    "latex": r"n",
                    "proposal": 0.001,
                },
            ],
            [
                "H0",
                {
                    "prior": {"dist": "norm", "loc": 70.4, "scale": sigma * chisq},
                    "ref": H0,
                    "latex": r"H_0",
                    "proposal": 0.001,
                },
            ],
        ]
    )
    info_PS["sampler"] = {
        "mcmc": {
            "burn_in": 300,
            "max_samples": 10000000,
            "Rminus1_stop": 0.1,
            "Rminus1_cl_stop": 0.1,
            "learn_proposal": True,
        }
    }

    updated_info_PS, sampler_PS = run(info_PS)

    gdsamples_PS = MCSamplesFromCobaya(updated_info_PS, sampler_PS.products()["sample"], ignore_rows=0.3)
    gdplot = gdplt.getSubplotPlotter(width_inch=5)
    gdplot.triangle_plot(gdsamples_PS, ["omega_m", "n", "H0"], filled=True)

    mean = gdsamples_PS.getMeans()[: len(parameters)]
    sigma = np.sqrt(np.array(gdsamples_PS.getVars()[: len(parameters)]))

    return mean, sigma


def chisq():
    zhel, zSNe, muobs, Cinverse = SNdata()
    chi_sq = []

    collection = []
    col = []
    dlth_SN, dmth_SN, chi_sq = (np.zeros(len(z)), np.zeros(len(z)), np.zeros(len(z)))
    a = 0
    b = 0
    h = 0.698
    c = 3 * 10**5
    for omega_m in np.linspace(0.01, 0.25, 40):
        for n in np.linspace(-1, 4, 40):
            for redshift in zSNe:
                g = quad(integrand, 0, redshift, args=(omega_m, n))
                dl1 = (1 + redshift) * g[0] # Capital DL which is dimensionless
                dlth_SN[b] += dl1
                dmth_SN[a] += 5.0 * np.log10(dl1) - 5 * np.log10(h) + 42.38  # or =5log(xx,10)+42.38
                a += 1
                b += 1
                sort_data_SN["DMchi"] = dmth_SN
            a = 0
            b = 0
            C2 = 0
            C1 = 0
            for i in sort_data_SN.Error_DM_SN:
                C2 += 1 / i**2
            sort_data_SN["dC1"] = (sort_data_SN["DMchi"] - sort_data_SN["DMdata_SN"]) / (
                sort_data_SN["Error_DM_SN"] ** 2
            )
            for i in sort_data_SN["dC1"]:
                C1 += i
            del sort_data_SN["dC1"]
            chi_sq_part1 = 0
            sort_data_SN["Part1"] = (
                (sort_data_SN["DMchi"] - sort_data_SN["DMdata_SN"]) / sort_data_SN["Error_DM_SN"]
            ) ** 2
            for i in sort_data_SN.Part1:
                chi_sq_part1 += i
            del sort_data_SN["Part1"]
            chi_sq = chi_sq_part1 + (C1 / C2) * (C1 + (2 * np.log(10) / 5)) - (2 * log(h))
            col.append(chi_sq)
            np_array = np.asarray(col)
            collection.append([chi_sq, omega_m, n])
            dlth_SN = np.zeros(len(z))
            dmth_SN = np.zeros(len(z))
            del sort_data_SN["DMchi"]

    print(len(collection))
    sigma1 = []
    sigma2 = []
    for i in collection:
        if i[0] == min(col):
            print("Minimum Chi sq value is", i, "\n")
            minimum = i
    for i in collection:  # https://ned.ipac.caltech.edu/level5/Wall2/Wal3_4.html
        if i[0] <= min(col) + 2.3:  # for significance of 0.68, chi sq value inc by 2.30 from minimum
            sigma1.append(i)
    omega_ = [row[1] for row in sigma1]
    n_ = [row[2] for row in sigma1]
    omegalowersigma1 = np.max(minimum[1] - np.array(omega_))
    omegauppersigma1 = np.max(np.array(omega_) - minimum[1])
    nlowersigma1 = np.max(minimum[2] - np.array(n_))
    nuppersigma1 = np.max(np.array(n_) - minimum[2])

    for i in collection:
        if i[0] <= min(col) + 4.61:
            # for significance of 0.96, chi sq value inc by 4.61 from minimum
            sigma2.append(i)
    omega_ = [row[1] for row in sigma2]
    n_ = [row[2] for row in sigma2]
    omegalowersigma2 = np.max(minimum[1] - np.array(omega_))
    omegauppersigma2 = np.max(np.array(omega_) - minimum[1])
    nlowersigma2 = np.max(minimum[2] - np.array(n_))
    nuppersigma2 = np.max(np.array(n_) - minimum[2])

    print("1 sigma + Error in omega", omegauppersigma1)
    print("1 sigma - Error in omega", omegalowersigma1)
    print("1 sigma + Error in n", nuppersigma1)
    print("1 sigma - Error in n", nlowersigma1)
    print("2 sigma + Error in omega", omegauppersigma2)
    print("2 sigma - Error in omega", omegalowersigma2)
    print("2 sigma + Error in n", nuppersigma2)
    print("2 sigma - Error in n", nlowersigma2)


omega_b0 = 0.0000245
omega_r0 = 0.02
