import io
import os
import shutil
import subprocess
import sys
from os.path import exists

import numpy as np
import csv
import vtk
from math import floor, log10
from vtkmodules.util.numpy_support import vtk_to_numpy
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import Toolbox
import matplotlib.pyplot as plt


SolDirec = os.path.join(os.getcwd() + "\\" + "solution", "") #Solution directory
IniDirec = os.path.join(os.getcwd() + "\\" + "initialisation", "") #Initialisation directory
Solfile = "K_Site_1mm_solved.pvd" #Solution .pvd file
Inifile = "K_Site_1mm_initialised.pvd" #Initialisation .pvd file
t = [0, 480, 960, 1440, 1680, 1920, 2160, 2400, 2640] #step time

SolVariables = ["Points", "Area", "Density", "Density Transfer Rate 0", "Pressure", "Temperature Gas", "Temperature Liquid",
                "Thermal Conductivity", "Weighted Temperature", "Specific Mass Transfer"]
IniVariables = ["Volume"]

Check_SolFile = Toolbox.check_file_exist(SolDirec, Solfile)
# print(Check_SolFile)

Check_IniFile = Toolbox.check_file_exist(IniDirec, Inifile)
# print(Check_IniFile)

Solpvd_data = Toolbox.pvd_read(SolDirec, Solfile, )
# print(Solpvd_data[0][1])

Inipvd_data = Toolbox.pvd_read(IniDirec, Inifile, )
# print(Inipvd_data)

for t_i in t:

    Solvtk_data = Toolbox.read_vtk(Solpvd_data[t_i][1], Solpvd_data[t_i][2], SolVariables, )
    Inivtk_data = Toolbox.read_vtk(Inipvd_data[0][1], Inipvd_data[0][2], IniVariables, )
    time_step = float(Solpvd_data[t_i][0])
    Coordinates = Solvtk_data[0]
    Area = Solvtk_data[1]
    Density = Solvtk_data[2]
    Density_Transfer_Rate_0 = Solvtk_data[3]
    Presssure = Solvtk_data[4]
    Temperature_Gas = Solvtk_data[5]
    Temperature_liquid = Solvtk_data[6]
    Thermal_Conductivity = Solvtk_data[7]
    Weighted_Temperature = Solvtk_data[8]
    Specific_Mass_Transfer = Solvtk_data[9]
    Volume = Inivtk_data[0]

    # with np.printoptions(threshold=sys.maxsize):
        # print("Points", Coordinates)
        # print("Area", Area)
        # print("Density", Density)
        # print("Density Tranfer Rate 0", Density_Transfer_Rate_0)
        # print("Pressure", Presssure)
        # print("Temperature Gas", Temperature_Gas)
        # print("Temperature liquid", Temperature_liquid)
        # print("Thermal Conductivity", Thermal_Conductivity)
        # print("Weighted Temperature", Weighted_Temperature)
        # print("Specific Mass Transfer", Specific_Mass_Transfer)
        # print("Volume", Volume)

    mass_flow_rate = []
    Coordinate_x = []
    Nrow = Coordinates.shape[0]

    for i in range(Nrow):
        if abs(Density_Transfer_Rate_0[i]) > 0:  #Node where there is phase change
            mass_flow_rate.append(Density_Transfer_Rate_0[i] * Volume[i])
            Coordinate_x.append(Coordinates[i,0]) #Extract the x coordinate


    mass_flow_rate = np.array(mass_flow_rate)
    Coordinate_x = np.array(Coordinate_x)

    order = np.argsort(Coordinate_x, axis=0)
    Coordinate_x_sorted = Coordinate_x[order]
    mass_flow_rate_sorted = mass_flow_rate[order]
    # print(mass_flow_rate_x_sorted)

    data = np.column_stack((Coordinate_x_sorted, mass_flow_rate_sorted))
    np.savetxt(f"mass_flow_rate_data_{time_step:.4f}s.csv", data, delimiter=",", header="x[m],m_dot[kg/m^2]", comments="")

    # m2 = []
    # Coordx = []

    # for i in range(Nrow):
    #     if abs(Specific_Mass_Transfer[i]) > 0:
    #         m2.append(Specific_Mass_Transfer[i] * Area[i])
    #         Coordx.append(Coordinates[i,0])

    # m2 = np.array(m2)
    # Coordx = np.array(Coordx)
    # order1 = np.argsort(Coordx, axis=0)
    # Coordx_sorted = Coordx[order1]
    # m2_sorted = m2[order1]

plt.plot(Coordinate_x_sorted, mass_flow_rate_sorted, label = f"Density trans at {time_step:.3f} s")
# plt.plot(Coordx_sorted, m2_sorted, label = "Specific m")

plt.xlabel("Horizontal distance, x [m]")
plt.ylabel("Mass flow rate, mdot [kg/m^2]")
plt.legend()
plt.grid(True)
plt.show()


