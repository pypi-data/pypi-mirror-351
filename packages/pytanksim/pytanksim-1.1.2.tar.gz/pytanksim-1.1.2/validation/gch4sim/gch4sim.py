# -*- coding: utf-8 -*-
# This file is a part of the python package pytanksim.
#
# Copyright (c) 2024 Muhammad Irfan Maulana Kusdhany, Kyushu University
#
# pytanksim is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import pytanksim as pts
import matplotlib.pyplot as plt
import CoolProp as CP
import numpy as np
import scipy as sp
import itertools
import scienceplots
import matplotlib.transforms as mtransforms

cng_capacity_mass = 2.74877 * 75
cng_density = CP.CoolProp.PropsSI("D", 'T', 300, 'P', 24.82113E6,
                                  'NaturalGasSample.mix')
tankvol = cng_capacity_mass/cng_density

mix = CP.AbstractState("HEOS", 'NaturalGasSample.mix')
mix.update(CP.PT_INPUTS, 24.82113E6, 300)
cp = mix.cpmass()
cv = mix.cvmass()
rho = mix.rhomass()
mu = mix.viscosity()
gam = cp/cv
crit_rat = (2/(gam+1))**(gam/(gam-1))
mdot = 5 * 2.567/60
D = 6


def residual(d):
    # Calculate diameter of orifice to allow CNG refueling rate similar to
    # conventional refueling stations.
    Re = 4*mdot/(np.pi*mu*D*1E-3)
    beta = d/D
    fact = (19000*beta/Re)**0.8
    C = 0.5961 + 0.0261 * (beta**2) - 0.216 * (beta ** 8) + \
        0.000521*((10E6*beta/Re)**0.7) + (0.0188 + 0.0063 * fact) *\
        (beta**3.5) * \
        max([(10E6/Re)**0.3, 22.7-4700*(Re/10E6)]) \
        + (0.043+0.08-0.123) * (1-0.11*fact) * (beta**4)/(1-beta**4) \
        + 0.011 * (0.75-beta) * max([2.8-D/25.4, 0])
    pr = 24.82113E6
    A = np.pi*((d*1E-3/2)**2)
    Cd = C / (np.sqrt(1-(beta**4)))
    mdotcalc = Cd * A * np.sqrt(gam * pr * rho *
                                ((2/(gam+1))**((gam+1)/(gam-1))))
    return mdotcalc-mdot


d = sp.optimize.root_scalar(residual, bracket=[1E-1, 5]).root
beta = d/D

fluid_name_list = ["Hydrogen&Methane"] * 5 + ["Methane", "Hydrogen"]
h2_comp_list = np.array([0.05, 0.15, 0.25, 0.35, 0.45])
ch4_comp_list = 1 - h2_comp_list

for ind, name in enumerate(fluid_name_list):
    fracs = [h2_comp_list[ind], ch4_comp_list[ind]] \
        if name == "Hydrogen&Methane" else None
    fluid = pts.StoredFluid(fluid_name=name,
                            EOS="HEOS",
                            mole_fractions=fracs)
    fluid.backend.specify_phase(CP.iphase_gas)
    pr = 24.82113E6
    Tr = 300
    A = np.pi * ((d * 1E-3 / 2)**2)
    fluid.backend.update(CP.PT_INPUTS, pr, Tr)
    cp = fluid.backend.cpmass()
    cv = fluid.backend.cvmass()
    rho = fluid.backend.rhomass()
    mu = fluid.backend.viscosity()
    gam = cp/cv
    ent = fluid.backend.hmolar()
    crit_rat = (2/(gam+1))**(gam/(gam-1))
    fluid = pts.StoredFluid(fluid_name=name,
                            EOS="PR",
                            mole_fractions=fracs)
    fluid.backend.specify_phase(CP.iphase_gas)
    tank = pts.StorageTank(volume=tankvol,
                            stored_fluid=fluid,
                            vent_pressure=24.82113E6,
                            min_supply_pressure=100)

    def mass_flow_in(p, T, t):     
        def C(mdot):
            # Calculate the coefficient of discharge
            Re = 4*mdot/(np.pi*mu*D*1E-3)
            if Re == 0:
                return 0.5961
            else:
                fact = (19000*beta/Re)**0.8
                return 0.5961 + 0.0261 * (beta**2) - 0.216 * (beta ** 8) + \
                    0.000521*((10E6*beta/Re)**0.7) + (0.0188 + 0.0063 * fact) *\
                    (beta**3.5) * max([(10E6/Re)**0.3, 22.7-4700*(Re/10E6)]) \
                    + (0.043+0.08-0.123) * (1-0.11*fact) *\
                    (beta**4)/(1-beta**4) + 0.011 * (0.75-beta) * \
                    max([2.8-D/25.4, 0])

        def mdot(C, p):
            # Calculate mass flow rate based on the coefficient of discharge
            Cd = C / np.sqrt(1-beta**4)
            if p > pr:
                p = pr
            if p/pr <= crit_rat:
                return Cd * A * np.sqrt(gam * pr * rho *
                                        ((2/(gam+1))**((gam+1)/(gam-1))))
            else:
                return Cd * A * np.sqrt(2 * pr * rho * (gam/(gam-1)) *
                                        ((p/pr)**(2/gam)-(p/pr)**(
                                            (gam+1)/gam)))

        def root(mdottry, p):
            Ctry = C(mdottry)
            mcalc = mdot(Ctry, p)
            return mdottry-mcalc
        # Calculate the mass flow rate recursively
        return sp.optimize.root_scalar(root, p, bracket=[0, 3]).root

    boundary_flux = pts.BoundaryFlux(
        mass_flow_in=mass_flow_in,
        enthalpy_in=ent
        )

    simulation_params = pts.SimParams(init_temperature=300,
                                      init_pressure=101325,
                                      final_time=60*30)

    simulation_fluid = pts.generate_simulation(
        storage_tank=tank,
        boundary_flux=boundary_flux,
        simulation_params=simulation_params,
        simulation_type="Default")

    results = simulation_fluid.run()
    filename = name+".csv" if name != "Hydrogen&Methane" else \
        str(h2_comp_list[ind])+"H2"+str(ch4_comp_list[ind])+"CH4.csv"
    results.to_csv(filename)

plt.style.use(["science", "nature"])
small = 8.3
medium = 9.3
plt.rcParams.update({
    "text.usetex": True,
    "font.family": 'Helvetica'
})
plt.rc('font', size=medium)         
plt.rc('axes', labelsize=medium)   
plt.rc('xtick', labelsize=small)   
plt.rc('ytick', labelsize=small)   
plt.rc('legend', fontsize=small)   


fig1, ax1 = plt.subplots(2, figsize=(3.543, 3.543 * 5/3))
fig2, ax2 = plt.subplots(3, figsize=(3.543, 3.543 * 2.5))

palette = itertools.cycle(["#8e463a",
                           "#71b54a",
                           "#9349cd",
                           "#c59847",
                           "#7b8cd1",
                           "#d14f38",
                           "#56a5a1",
                           "#cc4d97",
                           "#56733f",
                           "#593e78",
                           "#c07685"])
linestyles = itertools.cycle(["solid",
                              "dashdot",
                              "dashed",
                              "dotted",
                              (0, (5, 10)),
                              (0, (3, 10, 1, 10)),
                              (0, (3, 5, 1, 5, 1, 5))])

for ind, name in enumerate(fluid_name_list):
    color = next(palette)
    linestyle = next(linestyles)
    filename = name+".csv" if name != "Hydrogen&Methane" else \
        str(h2_comp_list[ind])+"H2"+str(ch4_comp_list[ind])+"CH4.csv"
    results, tank, params = pts.SimResults.from_csv(filename, True)
    df = results.df
    labelname = "Pure " + name if name != "Hydrogen&Methane" else \
        str(int(100*h2_comp_list[ind])) + ":" \
        + str(int(100*ch4_comp_list[ind])) + \
        " H$_2$:CH$_4$"
    if name == "Hydrogen":
        eneden = 33.3
    elif name == "Methane":
        eneden = 13.9
    else:
        eneden = h2_comp_list[ind]*33.3 + ch4_comp_list[ind] * 13.9
    ax1[0].plot(df["t"], df["p"]/1E6, label=labelname, color=color,
                linestyle=linestyle)
    ax1[1].plot(df["t"], df["T"], label=labelname, color=color,
                linestyle=linestyle)
    ax2[0].plot(df["t"], df["min_dot"], label=labelname, color=color,
                linestyle=linestyle)
    ax2[1].plot(df["t"], df["mg"]+df["ms"], label=labelname, color=color,
                linestyle=linestyle)
    ax2[2].plot(df["t"], eneden*(df["mg"]+df["ms"])/1000, label=labelname,
                color=color, linestyle=linestyle)


ax1[1].annotate('Initial Cooling',
            xy=(30, 280), xycoords='data',
            xytext=(600, 285), textcoords='data',
            arrowprops=dict(shrink=0, width=1, headwidth=4, 
                            headlength=5,
                            facecolor='gray', edgecolor='gray'),
            horizontalalignment='right', verticalalignment='center')

ax1[1].annotate('Initial Heating',
            xy=(30, 375), xycoords='data',
            xytext=(600, 420), textcoords='data',
            arrowprops=dict(shrink=0, width=1, headwidth=4, 
                            headlength=5,
                            facecolor='gray', edgecolor='gray'),
            horizontalalignment='right', verticalalignment='center')

ax1[1].hlines(y=300, xmin=-200, xmax=1000, color="gray", linestyle="dashed")
ax1[1].text(500, 310, "Starting Temperature", color="gray", fontsize=small)
ax1[1].set_xlim(-50, 900)

for ind, ax in enumerate(ax1):
    label = r"\textbf{"+chr(ord('`')+(ind+1))+".)" + "}"
    trans = mtransforms.ScaledTranslation(-30/72, 3/72, fig1.dpi_scale_trans)
    ax.text(0.0, 1.0, label, transform=ax.transAxes + trans,
            fontsize='medium', va='bottom', fontfamily='serif', weight="bold")

for ind, ax in enumerate(ax2):
    label = r"\textbf{"+chr(ord('`')+(ind+1))+".)" + "}"
    trans = mtransforms.ScaledTranslation(-30/72, 3/72, fig2.dpi_scale_trans)
    ax.text(0.0, 1.0, label, transform=ax.transAxes + trans,
            fontsize='medium', va='bottom', fontfamily='serif', weight="bold")

ax1[0].set_ylabel("Pressure (MPa)")
ax1[1].set_ylabel("Temperature (K)")
ax1[0].set_xlabel("Time (s)")
ax1[1].set_xlabel("Time (s)")
ax1[0].legend()
ax2[0].set_ylabel("Mass Flow Rate (kg/s)")
ax2[1].set_ylabel("Fuel Stored (kg)")
ax2[2].set_ylabel("Energy Stored (MWh)")
ax2[0].set_xlabel("Time (s)")
ax2[1].set_xlabel("Time (s)")
ax2[2].set_xlabel("Time (s)")
handles, labels = ax2[0].get_legend_handles_labels()
fig2.legend(handles, labels, loc="lower center", ncol=2)
fig1.savefig("CH4fig1.jpeg", dpi=1000)
fig2.savefig("CH4fig2.jpeg", dpi=1000)
