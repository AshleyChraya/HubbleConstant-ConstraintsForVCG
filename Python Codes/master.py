import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from math import pow
from scipy.integrate import quad
from cobaya.run import run
from getdist.mcsamples import MCSamplesFromCobaya
import getdist.plots as gdplt
import argparse  # Commandline input
from collections import OrderedDict as odict


plt.rcParams["figure.figsize"] = (20, 18)

directory = "/media/ash/1tb/github/HubbleConstant-ConstraintsForVCG/"
plt.style.use(f"{directory}standard.mplstyle")

parser = argparse.ArgumentParser()
parser.add_argument(
    "-Data",
    type=str,
    default="pantheon",
    help="Put either pantheon or gw or both for plotting together or pantheonGW for joint likelihood",
)
parser.add_argument(
    "-likelihood",
    type=str,
    default="gaussian",
    help="Put either gaussian or nongaussian for GWs likelihood",
)

args = parser.parse_args()


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

    return zhel, zSNe, muobs, Cinverse, Dstat


def GWdata():
    name = np.array(
        [
            "GW190521",
            "GW190706_222641",
            "GW190413_134308",
            "GW190514_065416",
            "GW190719_215514",
            "GW190521",
            "GW190909_114149",
            "GW190413_052954",
            "GW190803_022701",
            "GW190731_140936",
            "GW190727_060333",
            "GW190620_030421",
            "GW190421_213856",
            "GW170729",
            "GW190602_175927",
            "GW190527_092055",
            "GW190519_153544",
            "GW190424_180648",
            "GW190929_012149",
            "GW190828_063405",
            "GW190701_203306",
            "GW190513_205428",
            "GW170823",
            "GW190517_055101",
            "GW190915_235702",
            "GW190828_065509",
            "GW190408_181802",
            "GW190910_112807",
            "GW190512_180714",
            "GW190503_185404",
            "GW190521_074359",
            "GW170818",
            "GW151012",
            "GW170809",
            "GW170104",
            "GW190728_064510",
            "GW190708_232457",
            "GW190630_185205",
            "GW190720_000836",
            "GW190707_093326",
            "GW190930_133541",
            "GW190412",
            "GW190924_021846",
            "GW170814",
            "GW151226",
            "GW150914",
            "GW190426_152155",
            "GW200115_042309",
            "GW170608",
            "GW200105_162426",
            "GW190814",
            "GW190425",
            "GW170817",
        ]
    )

    full_DL_GW = np.array(
        [
            [5300.0, 2400, -2600],
            [4420.0, 2590, -1930],
            [4450, 2480, -2120],
            [4130.0, 2650, -2170],
            [3940.0, 2590, -2000],
            [3920.0, 2190, -1950],
            [3770.0, 3270, -2220],
            [3550.0, 2270, -1660],
            [3270.0, 1950, -1580],
            [3300.0, 2390, -1720],
            [3300.0, 1540, -1500],
            [2810.0, 1680, -1310],
            [2880.0, 1370, -1380],
            [2840.0, 1400, -1360],
            [2690.0, 1790, -1120],
            [2490.0, 2480, -1240],
            [2530.0, 1830, -920],
            [2200.0, 1580, -1160],
            [2130.0, 3650, -1050],
            [2130.0, 660, -930],
            [2060.0, 760, -730],
            [2060.0, 880, -800],
            [1940.0, 970, -900],
            [1860.0, 1620, -840],
            [1620.0, 710, -610],
            [1600.0, 620, -600],
            [1550.0, 400, -600],
            [1460.0, 1030, -580],
            [1430.0, 550, -550],
            [1450.0, 690, -630],
            [1240.0, 400, -570],
            [1060.0, 420, -380],
            [1080.0, 550, -490],
            [1030.0, 320, -390],
            [990.0, 440, -430],
            [870.0, 260, -370],
            [880.0, 330, -390],
            [890.0, 560, -370],
            [790.0, 690, -320],
            [770.0, 380, -370],
            [760.0, 360, -320],
            [740.0, 140, -170],
            [570.0, 220, -220],
            [600.0, 150, -220],
            [450.0, 180, -190],
            [440.0, 150, -170],
            [370.0, 180, -160],
            [300.0, 150, -100],
            [320.0, 120, -110],
            [280.0, 110, -110],
            [241.0, 41, -45],
            [159.0, 69, -72],
            [40.0, 7, -15],
        ]
    )
    full_Z_GW = np.array(
        [
            [0.82, 0.28, -0.34],
            [0.71, 0.32, -0.27],
            [0.71, 0.31, -0.30],
            [0.67, 0.33, -0.31],
            [0.64, 0.33, -0.29],
            [0.64, 0.28, -0.28],
            [0.62, 0.41, -0.33],
            [0.59, 0.29, -0.24],
            [0.55, 0.26, -0.24],
            [0.55, 0.31, -0.26],
            [0.55, 0.21, -0.22],
            [0.49, 0.23, -0.20],
            [0.49, 0.19, -0.21],
            [0.49, 0.19, -0.21],
            [0.47, 0.25, -0.17],
            [0.44, 0.34, -0.20],
            [0.44, 0.25, -0.14],
            [0.39, 0.23, -0.19],
            [0.38, 0.49, -0.17],
            [0.38, 0.10, -0.15],
            [0.37, 0.11, -0.12],
            [0.37, 0.13, -0.13],
            [0.35, 0.15, -0.15],
            [0.34, 0.24, -0.14],
            [0.3, 0.11, -0.10],
            [0.3, 0.10, -0.10],
            [0.29, 0.06, -0.10],
            [0.28, 0.16, -0.10],
            [0.27, 0.09, -0.10],
            [0.27, 0.11, -0.11],
            [0.24, 0.07, -0.10],
            [0.21, 0.07, -0.07],
            [0.21, 0.09, -0.09],
            [0.2, 0.05, -0.07],
            [0.2, 0.08, -0.08],
            [0.18, 0.05, -0.07],
            [0.18, 0.06, -0.07],
            [0.18, 0.10, -0.07],
            [0.16, 0.12, -0.06],
            [0.16, 0.07, -0.07],
            [0.15, 0.06, -0.06],
            [0.15, 0.03, -0.03],
            [0.12, 0.04, -0.04],
            [0.12, 0.03, -0.04],
            [0.09, 0.04, -0.04],
            [0.09, 0.03, -0.03],
            [0.08, 0.04, -0.03],
            [0.07, 0.03, -0.02],
            [0.07, 0.02, -0.02],
            [0.06, 0.02, -0.02],
            [0.053, 0.009, -0.010],
            [0.04, 0.01, -0.02],
            [0.01, 0.00, -0.00],
        ]
    )
    # Number of events
    a = name.size

    # Defining arrays
    dldata_GW = np.zeros(a)
    dlUP = np.zeros(a)
    dlLOW = np.zeros(a)
    dlTOP = np.zeros(a)
    dlBOTTOM = np.zeros(a)
    dmtop = np.zeros(a)
    dmbottom = np.zeros(a)
    Z_GW = np.zeros(a)
    dmth_GW = np.zeros(a)
    dmdata_GW = np.zeros(a)
    dlth_GW = np.zeros(a)
    dmtoperr = np.zeros(a)
    dmbottomerr = np.zeros(a)
    # defining variables for index of the above arrays
    b = c = d = e = f = h = k = l = m = x = y = p = q = r = s = 0
    # extracting redshifts and DL from the full data
    for i in full_Z_GW:
        Z_GW[e] += i[0]
        e += 1
    for i in full_DL_GW:
        dldata_GW[b] += i[0]
        b += 1
    for i in dldata_GW:
        dmdata_GW[h] += 5 * np.log(i, 10) + 25
        h += 1
    for i in full_DL_GW:
        dlUP[c] += i[0] + i[1]
        c += 1
    for i in full_DL_GW:
        dlLOW[d] += i[0] + i[2]
        d += 1
    label1 = {
        "Event_Name": name,
        "Z_GW": Z_GW,
        "dLdata_GW": dldata_GW,
        "DMdata_GW": dmdata_GW,
        "DL_Uplimit": dlUP,
        "DL_Lowlimit": dlLOW,
    }
    data_GW = pd.DataFrame(label1)
    data_GWTC3 = pd.read_excel(r"/media/ash/1tb/github/HubbleConstant-ConstraintsForVCG/oldGW.xlsx")
    data_GWTC3.index = np.arange(53, 88)

    mucollect = [data_GW.Z_GW, data_GWTC3.redshift]
    z1 = pd.concat(mucollect)

    namecollect = [data_GW.Event_Name, data_GWTC3.Event_Name_GWTC3]
    finalevents = pd.concat(namecollect)

    dlcollect = [data_GW.dLdata_GW, data_GWTC3.luminosity_distance]
    finaldl1 = pd.concat(dlcollect)

    dlupcollect = [data_GW.DL_Uplimit, data_GWTC3.luminosity_distance_upper]
    finaldlup1 = pd.concat(dlupcollect)

    dllowcollect = [data_GW.DL_Lowlimit, data_GWTC3.luminosity_distance_lower]
    finaldllow1 = pd.concat(dllowcollect)
    label2 = {
        "EventName": finalevents,
        "ZGW": z1,
        "dLdataGW": finaldl1,
        "DLUplimit": finaldlup1,
        "DLLowlimit": finaldllow1,
    }
    Final_GW = pd.DataFrame(label2)
    sort_data_GW = Final_GW.sort_values(by=["ZGW"], ignore_index=True)

    z = sort_data_GW.ZGW
    finaldl = sort_data_GW.dLdataGW
    finaldlup = sort_data_GW.DLUplimit
    finaldllow = sort_data_GW.DLLowlimit
    a = finalevents.size

    # Defining arrays
    dlTOP = np.zeros(a)
    dlBOTTOM = np.zeros(a)
    dmtop = np.zeros(a)
    dmbottom = np.zeros(a)
    dmth3_GW = np.zeros(a)
    mu = np.zeros(a)
    dlth3_GW = np.zeros(a)
    dmtoperr = np.zeros(a)
    dmbottomerr = np.zeros(a)
    # defining variables for index of the above arrays
    f = h = k = l = m = x = y = p = q = r = s = 0

    for i in finaldl:
        mu[h] += 5 * np.log(i, 10) + 25
        h += 1
    for i in finaldlup:
        dmtop[f] += 5 * np.log(i, 10) + 25
        f += 1
    for i in finaldllow:
        dmbottom[k] += 5 * np.log(i, 10) + 25
        k += 1
    # upper and lower differences for errors
    for (i, j) in zip(mu, dmtop):
        dmtoperr[r] += j - i
        r += 1
    for (i, j) in zip(mu, dmbottom):
        dmbottomerr[s] += i - j
        s += 1

    return z, mu, dmbottomerr, dmtoperr


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


def likelihood(omega_m, n, H0):

    if args.Data in ["pantheon", "both", "pantheongw"]:

        zhel, zSNe, muobs, Cinverse, Dstat = SNdata()

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
            loglikely_PS = -1.0e100
        else:
            loglikely_PS = -0.5 * chi2_SNe

        return loglikely_PS

    if args.Data in ["gw", "both", "pantheongw"]:
        z, mu, dmbottomerr, dmtoperr = GWdata()

        sigma = np.zeros(len(z))

        # DL theoretical from VCG model
        def D_l(z, omega_m, n, h0):
            def int_func(x):
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

            g = quad(int_func, 0, z)
            return (1 + z) * g[0] * (ckm / H0)

        # Calculate the value of mu_theory
        mu_th = 5 * np.log(D_l(z, omega_m, n, H0), 10) + 25

        # We now defile a likelihood function as given in the notes
        # If the value comes out to be less than zero, set it to a very very small likelyhood
        # Temporary variable to store mu(observation)- mu(theory)
        dmu = np.empty(len(z))
        if args.likelihood == "nongaussian":

            if omega_m <= 0.0 or omega_m >= 1 or H0 < 0:
                loglikely_GW = -1.0e100
            else:
                for i in range(len(z)):  # if data point lower than theoretical: take bottom error
                    # if data point above th : take upper error
                    dmu[i] = mu[i] - mu_th
                    if dmu[i] > 0:
                        sigma[i] = dmbottomerr[i]
                    else:
                        sigma[i] = dmtoperr[i]
                loglikely_GW = -0.5 * np.sum(dmu**2 / sigma**2)

                return loglikely_GW

        if args.likelihood == "gaussian":

            if omega_m <= 0.0 or omega_m >= 1 or H0 < 0:
                loglikely_GW = -1.0e100
            else:
                for i in range(len(z)):  # (Average of asymetrical errors)
                    dmu[i] = mu[i] - mu_th
                    sigma[i] = (dmbottomerr[i] + dmtoperr[i]) / 2
                loglikely = -0.5 * np.sum(dmu**2 / sigma**2)

                return loglikely_GW

    if args.Data == "pantheongw":

        return loglikely_PS + loglikely_GW


def mcmc(likelihood):

    guess = [0.3, 1.2, 70]
    omega_m, n, H0 = guess
    sigma = 5
    parameters = ["omega_m", "n", "H0"]
    info = {"likelihood": {"agostini": likelihood}}

    info["params"] = odict(
        [
            [
                "omega_m",
                {
                    "prior": {"dist": "norm", "loc": 0.12, "scale": sigma * 0.02},
                    "ref": omega_m,
                    "latex": r"\Omega_m",
                    "proposal": 0.001,
                },
            ],
            [
                "n",
                {
                    "prior": {"dist": "norm", "loc": 1.26, "scale": sigma * 0.26},
                    "ref": n,
                    "latex": r"n",
                    "proposal": 0.001,
                },
            ],
            [
                "H0",
                {
                    "prior": {"dist": "norm", "loc": 70.4, "scale": sigma * 69.8},
                    "ref": H0,
                    "latex": r"H_0",
                    "proposal": 0.001,
                },
            ],
        ]
    )
    info["sampler"] = {
        "mcmc": {
            "burn_in": 300,
            "max_samples": 10000000,
            "Rminus1_stop": 0.1,
            "Rminus1_cl_stop": 0.1,
            "learn_proposal": True,
        }
    }

    updated_info, sampler = run(info)
    return parameters, updated_info, sampler


def plot(likelihood):

    if args.Data in ["pantheon", "gw", "pantheongw"]:
        parameters, updated_info, sampler = mcmc(likelihood)
        gdsamples = MCSamplesFromCobaya(updated_info, sampler.products()["sample"], ignore_rows=0.3)
        gdplot = gdplt.getSubplotPlotter(width_inch=5)
        gdplot.triangle_plot(gdsamples, ["omega_m", "n", "H0"], filled=True)

        mean = gdsamples.getMeans()[: len(parameters)]
        sigma = np.sqrt(np.array(gdsamples.getVars()[: len(parameters)]))

        return mean, sigma

    if args.Data == "both":
        args.Data = "gw"
        parameters_GW, updated_info_GW, sampler_GW = mcmc(likelihood)
        gdsamples_GW = MCSamplesFromCobaya(updated_info_GW, sampler_GW.products()["sample"], ignore_rows=0.3)
        args.Data = "pantheon"
        parameters_PS, updated_info_PS, sampler_PS = mcmc(likelihood)
        gdsamples_PS = MCSamplesFromCobaya(updated_info_PS, sampler_PS.products()["sample"], ignore_rows=0.3)

        g = gdplt.get_subplot_plotter()
        g.settings.figure_legend_frame = False
        g.settings.alpha_filled_add = 0.4
        g.settings.title_limit_fontsize = 14
        g.triangle_plot(
            [gdsamples_PS, gdsamples_GW],
            ["omega_m", "n", "H0"],
            filled=True,
            legend_labels=["Pantheon Sample", "GWTC-3"],
            legend_loc="upper right",
            line_args=[{"lw": 2, "ls": "--", "color": "red"}, {"lw": 2, "color": "darkblue"}],
            contour_colors=["red", "darkblue"],
            #     title_limit=1, # first title limit (for 1D plots) is 68% by default
            #     markers={'h0':0})
        )


def chisq():
    zhel, zSNe, muobs, Cinverse, Dstat = SNdata()  # To collect data from SN dataset

    collection, col, dmth_SN = (np.array([[]]), np.array([]), np.array([]))
    h = 0.698
    c = 3 * 10**5
    for omega_m in np.linspace(0.01, 0.25, 10):
        print(f"starting Omega_m loop {omega_m}")
        for n in np.linspace(-1, 4, 10):
            for redshift in zSNe:
                g = quad(integrand, 0, redshift, args=(omega_m, n))
                dl1 = (1 + redshift) * g[0]  # Capital DL which is dimensionless
                dm = 5.0 * np.log10(dl1) - 5 * np.log10(h) + 42.38  # or =5log(xx,10)+42.38
                dmth_SN = np.append(dmth_SN, dm)

            C2 = np.sum(1 / Dstat**2)
            C1 = np.sum((dmth_SN - muobs) / (Dstat**2))

            partial = np.sum((dmth_SN - muobs) / Dstat) ** 2

            chi_sq = partial + (C1 / C2) * (C1 + (2 * np.log(10) / 5)) - (2 * np.log(h))
            col = np.append(col, chi_sq)
            if n == -1:
                collection = np.array([[chi_sq, omega_m, n]])
            else:
                collection = np.append(collection, np.array([[chi_sq, omega_m, n]]), axis=0)
            dlth_SN, dmth_SN = (np.array([]), np.array([]))
    print(collection)
    sigma1 = []

    minchi = min(col)
    for i in collection:
        if i[0] == np.min(col):
            print("Minimum Chi sq value is", i, "\n")
            minimum = i

    for i in collection:  # https://ned.ipac.caltech.edu/level5/Wall2/Wal3_4.html
        if i[0] <= np.min(col) + 2.3:  # for significance of 0.68, chi sq value inc by 2.30 from minimum
            sigma1.append(i)
    print(sigma1)
    omega1sigma = sigma1[:, 1]
    n1sigma = sigma1[:, 2]
    omegalowersigma1 = np.max(minimum[1] - np.array(omega1sigma))
    omegauppersigma1 = np.max(np.array(omega1sigma) - minimum[1])
    nlowersigma1 = np.max(minimum[2] - np.array(n1sigma))
    nuppersigma1 = np.max(np.array(n1sigma) - minimum[2])
    print(omegalowersigma1, omegauppersigma1, nlowersigma1, nuppersigma1)
    om1sigma = (omegauppersigma1 + omegalowersigma1) / 2
    n1sigma = (nuppersigma1 + nlowersigma1) / 2

    return minchi, om1sigma, n1sigma


if __name__ == "__main__":
    omega_b0 = 0.0000245
    omega_r0 = 0.02
    ckm = 299792.458
    H0 = 70
    # print(likelihood(omega_m=0.12, n=1.25, H0=70))
    plot(likelihood)
    plt.show()
