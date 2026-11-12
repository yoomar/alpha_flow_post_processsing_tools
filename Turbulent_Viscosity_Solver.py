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


# SolDirec = os.path.join(os.getcwd() + "\\" + "solution", "") #Solution directory
# IniDirec = os.path.join(os.getcwd() + "\\" + "initialisation", "") #Initialisation directory
# Solfile = "K_Site_1mm_solved.pvd" #Solution .pvd file
# Inifile = "K_Site_1mm_initialised.pvd" #Initialisation .pvd file
# t = [0, 480, 960, 1440, 1680, 1920, 2160, 2400, 2640] #step time

SolDirec = os.path.join("C:\\Users\\NTSKOP001\\Downloads\\output_1mm_Ideal_Gas\\visualisation\\solution", "")
IniDirec = os.path.join("C:\\Users\\NTSKOP001\\Downloads\\output_1mm_Ideal_Gas\\visualisation\\initialisation", "")
Solfile = "K_Site_1mm_solved.pvd" #Solution .pvd file
Inifile = "K_Site_1mm_initialised.pvd" #Initialisation .pvd file
# t = [2880]
t = [0, 480, 960, 1440, 1680, 1920, 2160, 2400, 2640] #step time

SolVariables = ["Points", "Area", "Density Transfer Rate 0", "Internal Wall Heat Flux", "Turbulent Viscosity Ratio"]
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
    Density_Transfer_Rate_0 = Solvtk_data[2]
    Internal_Wall_Heat_Flux = Solvtk_data[3]
    Turbulent_Viscosity_Ratio = Solvtk_data[4]
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

    Int_Coord_x = []
    Wall_Coord_y = []
    Int_turbulent_viscosity_ratio = []
    Wall_turbulent_viscosity_ratio = []
    Nrow = Coordinates.shape[0]

    for i in range(Nrow):
        if abs(Density_Transfer_Rate_0[i]) > 0: 
            Int_Coord_x.append(Coordinates[i,0]) #Extract the x coordinate along the interface
            Int_turbulent_viscosity_ratio.append(Turbulent_Viscosity_Ratio[i]) #Turbulent viscosity ratio along the interface

        if abs(Internal_Wall_Heat_Flux[i]) > 0:
            Wall_Coord_y.append(Coordinates[i,1]) #Extract the y coordinate along the wall
            Wall_turbulent_viscosity_ratio.append(Turbulent_Viscosity_Ratio[i]) #Turbulent viscosity ratio along the wall


    Int_Coord_x = np.array(Int_Coord_x)
    Int_turbulent_viscosity_ratio = np.array(Int_turbulent_viscosity_ratio)
    Wall_Coord_y = np.array(Wall_Coord_y)
    Wall_turbulent_viscosity_ratio = np.array(Wall_turbulent_viscosity_ratio)

    order1 = np.argsort(Int_Coord_x, axis=0)
    Int_Coord_x_sorted = Int_Coord_x[order1]
    Int_turbulent_viscosity_ratio_sorted = Int_turbulent_viscosity_ratio[order1]

    order2 = np.argsort(Wall_Coord_y, axis=0)
    Wall_Coord_y_sorted = Wall_Coord_y[order2]
    Wall_turbulent_viscosity_ratio_sorted = Wall_turbulent_viscosity_ratio[order2]

    data1 = np.column_stack((Int_Coord_x_sorted, Int_turbulent_viscosity_ratio_sorted))
    np.savetxt(f"Int_turbulent_viscosity_ratio_data_{time_step:.4f}s.csv", data1, delimiter=",", header="x[m],turbulent mu ratio", comments="")

    data2 = np.column_stack((Wall_turbulent_viscosity_ratio_sorted, Wall_Coord_y_sorted))
    np.savetxt(f"Wall_turbulent_viscosity_ratio_data_{time_step:.4f}s.csv", data2, delimiter=",", header="turbulent mu ratio, y[m]", comments="")


plt.plot(Int_Coord_x_sorted, Int_turbulent_viscosity_ratio_sorted, label = f"Interface turbulent viscosity at {time_step:.3f} s")
plt.xlabel("Horizontal distance, x [m]")
plt.ylabel("Turbulent Viscosity ratio")
plt.legend()
# plt.grid(True)
plt.show()

plt.plot(Wall_turbulent_viscosity_ratio_sorted, Wall_Coord_y_sorted, label = f"Wall Turbulent viscosity at {time_step:.3f} s")
plt.xlabel("Turbulent Viscosity ratio")
plt.ylabel("Vertical height, y [m]")
plt.legend()
# plt.grid(True)
plt.show()

