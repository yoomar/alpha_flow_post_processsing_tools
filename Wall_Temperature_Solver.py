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

SolDirec = os.path.join("C:\\Users\\NTSKOP001\\Downloads\\output_3mm_Boil_Para_Real_Gas_90kPa_Rev4\\visualisation\\solution", "")
IniDirec = os.path.join("C:\\Users\\NTSKOP001\\Downloads\\output_3mm_Boil_Para_Real_Gas_90kPa_Rev4\\visualisation\\initialisation", "")
Solfile = "K_Site_3mm_solved.pvd" #Solution .pvd file
Inifile = "K_Site_3mm_initialised.pvd" #Initialisation .pvd file
t = [201]

SolVariables = ["Points", "Area", "Temperature Gas", "Temperature Liquid",
                 "Thermal Conductivity", "Weighted Temperature", "Internal Wall Heat Flux"]
IniVariables = ["Volume"]

Check_SolFile = Toolbox.check_file_exist(SolDirec, Solfile)
# print(Check_SolFile)

Check_IniFile = Toolbox.check_file_exist(IniDirec, Inifile)
# print(Check_IniFile)

Solpvd_data = Toolbox.pvd_read(SolDirec, Solfile, )
# print(Solpvd_data[0])

Inipvd_data = Toolbox.pvd_read(IniDirec, Inifile, )
# print(Inipvd_data)

for t_i in t:
    Solvtk_data = Toolbox.read_vtk(Solpvd_data[t_i][1], Solpvd_data[t_i][2], SolVariables, )
    Inivtk_data = Toolbox.read_vtk(Inipvd_data[0][1], Inipvd_data[0][2], IniVariables, )

    Coordinates = Solvtk_data[0]
    time_step = float(Solpvd_data[t_i][0])
    Area = Solvtk_data[1]
    Temperature_Gas = Solvtk_data[2]
    Temperature_liquid = Solvtk_data[3]
    Thermal_Conductivity = Solvtk_data[4]
    Weighted_Temperature = Solvtk_data[5]
    Internal_Wall_Heat_Flux = Solvtk_data[6]
    Volume = Inivtk_data[0]

    # with np.printoptions(threshold=sys.maxsize):
        # print("Points", Coordinates)
        # print("Area", Area)
        # print("Temperature Gas", Temperature_Gas)
        # print("Temperature liquid", Temperature_liquid)
        # print("Thermal Conductivity", Thermal_Conductivity)
        # print("Weighted Temperature", Weighted_Temperature)
        # print("Internal Wall Heat Flux", Internal_Wall_Heat_Flux)
        # print("Volume", Volume)

    Nrow = Coordinates.shape[0]
    Wall_Coord_y = []
    Wall_Temperature = []

    for i in range(Nrow):
        if abs(Internal_Wall_Heat_Flux[i]) > 0: 
            Wall_Temperature.append(Weighted_Temperature[i]) #Extracting the wall temperature
            Wall_Coord_y.append(Coordinates[i,1]) #Extracting the y coordinates of the wall

    Wall_Coord_y = np.array(Wall_Coord_y)
    Wall_Temperature = np.array(Wall_Temperature)

    order = np.argsort(-Wall_Coord_y, axis=0)
    Wall_Coord_y_sorted = Wall_Coord_y[order]
    Wall_Temperature_sorted = Wall_Temperature[order]

    data = np.column_stack((Wall_Coord_y_sorted, Wall_Temperature_sorted))
    np.savetxt(f"Wall_Temperature_data_{time_step:.4f}s.csv", data, delimiter=",", header="y[m], T[K]", comments="")

plt.plot(Wall_Temperature_sorted, Wall_Coord_y_sorted)
plt.xlabel("Wall Temperature, T [K]")
plt.ylabel("Vertical height, y [m]")
plt.show()
