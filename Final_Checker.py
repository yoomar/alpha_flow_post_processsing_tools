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
t = [2880]

SolVariables = ["Points", "Area", "Temperature Gas", "Temperature Liquid", "Thermal Conductivity",
                 "Weighted Temperature", "Internal Wall Heat Flux", "Turbulent Viscosity Ratio", "Density Transfer Rate 0"]
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
    Turbulent_Viscosity_Ratio = Solvtk_data[7]
    Density_Transfer_Rate_0 = Solvtk_data[8]
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
    Wall_Coord_x = []
    Int_Wall_Heat_Flux = []
    mu_r_wall = []
    mu_r_int = []
    Coordinate_x = [] 
    Coordinate_y = [] 

    for i in range(Nrow):
        if abs(Internal_Wall_Heat_Flux[i]) > 0: 
            Int_Wall_Heat_Flux.append(Internal_Wall_Heat_Flux[i]) #Extracting the internal wall heat fluxes
            Wall_Coord_y.append(Coordinates[i,1]) #Extracting the y coordinates of the wall
            Wall_Coord_x.append(Coordinates[i,0]) #Extracting the x coordinates of the wall
            mu_r_wall.append(Turbulent_Viscosity_Ratio[i]) #Extracting the turbulent viscosity ratio along the wall

        if abs(Density_Transfer_Rate_0[i]) > 0:
            mu_r_int.append(Turbulent_Viscosity_Ratio[i]) #Extracting the turbulent viscosity ratio along the interface
            Coordinate_x.append(Coordinates[i,0]) #Extract the x coordinate
            Coordinate_y.append(Coordinates[i,1]) #Extract the y coordinate

    Wall_Coord_y = np.array(Wall_Coord_y)
    Wall_Coord_x = np.array(Wall_Coord_x)
    Int_Wall_Heat_Flux = np.array(Int_Wall_Heat_Flux)
    mu_r_wall = np.array(mu_r_wall)

    mu_r_int = np.array(mu_r_int)
    Coordinate_x = np.array(Coordinate_x) 
    Coordinate_y = np.array(Coordinate_y)

    order = np.argsort(-Wall_Coord_y, axis=0) #Descending order
    Wall_Coord_y_sorted = Wall_Coord_y[order]
    Wall_Coord_x_sorted = Wall_Coord_x[order]
    Int_Wall_Heat_Flux_sorted = Int_Wall_Heat_Flux[order]
    mu_r_wall_sorted = mu_r_wall[order]

    Wall_Coord_y_sorted = np.flip(Wall_Coord_y_sorted + Wall_Coord_y_sorted[0]) #Making the bottom of tank y = 0 
    Wall_Coord_x_sorted = np.flip(Wall_Coord_x_sorted)
    Int_Wall_Heat_Flux_sorted = np.flip(Int_Wall_Heat_Flux_sorted)
    mu_r_wall_sorted = np.flip(mu_r_wall_sorted)

    order_int = np.argsort(Coordinate_x, axis=0)
    mu_r_int_sorted = mu_r_int[order_int]
    Coordinate_x_sorted = Coordinate_x[order_int]
    Coordinate_y_sorted = Coordinate_y[order_int]

    # data = np.column_stack((Int_Wall_Heat_Flux_sorted, Wall_Coord_y_sorted))
    # np.savetxt(f"Int_Wall_Heat_Flux_data_{time_step:.4f}s.csv", data, delimiter=",", header="Qwi[W/m^2],y[m]", comments="")

# plt.plot(Int_Wall_Heat_Flux_sorted, Wall_Coord_y_sorted)
# plt.xlabel("Internal wall heat flux, Qwi [W/m^2]")
# plt.ylabel("Vertical height, y [m]")
# plt.show()

Q_f = 0
N = Wall_Coord_y_sorted.shape[0]

for i in range(N):
    if i == 0:
        delta_y = (Wall_Coord_y_sorted[i] + Wall_Coord_y_sorted[i + 1])/2
    if i == N - 1:
        delta_y = (Wall_Coord_y_sorted[i] + Wall_Coord_y_sorted[i - 1])/2
    else:
        delta_y = (Wall_Coord_y_sorted[i + 1] - Wall_Coord_y_sorted[i - 1])/2

    Q_f = Q_f + (2 * np.pi * Wall_Coord_x_sorted[i] * delta_y * Int_Wall_Heat_Flux_sorted[i])

print(Q_f)