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

SolVariables = ["Points", "Area", "Internal Wall Heat Flux", "Velocity", "Weighted Temperature"]
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
    Internal_Wall_Heat_Flux = Solvtk_data[2]
    Velocity = Solvtk_data[3]
    Weighted_Temperature = Solvtk_data[4]
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

    Wall_Coord_Adj_y = []
    Wall_Coord_y = []
    Adj_Wall_Vel = []
    Wall_Delta_Temp = []
    Nrow = Coordinates.shape[0]

    for i in range(Nrow):
        if abs(Internal_Wall_Heat_Flux[i]) > 0: 
            if Coordinates[i,1] >= 0: #Vapour side of the tank
                Wall_Coord_Adj_y.append(Coordinates[i+1, 1]) #Extract the y coordinate adjacent to the wall
                Wall_Coord_y.append(Coordinates[i,1]) #Extract the y coordinate along the wall
                Adj_Wall_Vel.append(np.sqrt((Velocity[i+1,0])**2 + (Velocity[i+1,1])**2)) #Extract the velocity adjacent to the wall
                Wall_Delta_Temp.append((Weighted_Temperature[i+1]) - (Weighted_Temperature[i])) #Delta T along the wall

            if Coordinates[i,1] < 0: #Liquid side of the tank
                Wall_Coord_Adj_y.append(Coordinates[i-1, 1]) #Extract the y coordinate adjacent to the wall
                Wall_Coord_y.append(Coordinates[i,1]) #Extract the y coordinate along the wall
                Adj_Wall_Vel.append(np.sqrt((Velocity[i-1,0])**2 + (Velocity[i-1,1])**2)) #Extract the velocity adjacent to the wall
                Wall_Delta_Temp.append((Weighted_Temperature[i-1]) - (Weighted_Temperature[i])) #Delta T along the wall


    Wall_Coord_Adj_y = np.array(Wall_Coord_Adj_y)
    Adj_Wall_Vel = np.array(Adj_Wall_Vel)
    Wall_Coord_y = np.array(Wall_Coord_y)
    Wall_Delta_Temp = np.array(Wall_Delta_Temp)

    order1 = np.argsort(Wall_Coord_Adj_y, axis=0)
    Wall_Coord_Adj_y_sorted = Wall_Coord_Adj_y[order1]
    Adj_Wall_Vel_sorted = Adj_Wall_Vel[order1]

    order2 = np.argsort(Wall_Coord_y, axis=0)
    Wall_Coord_y_sorted = Wall_Coord_y[order2]
    Wall_Delta_Temp_sorted = Wall_Delta_Temp[order2]

    data1 = np.column_stack((Adj_Wall_Vel_sorted, Wall_Coord_Adj_y_sorted))
    np.savetxt(f"Adj_Wall_Velocity_data_{time_step:.4f}s.csv", data1, delimiter=",", header="v[m/s],y[m]", comments="")

    data2 = np.column_stack((Wall_Delta_Temp_sorted, Wall_Coord_y_sorted))
    np.savetxt(f"Wall_delta_temp_data_{time_step:.4f}s.csv", data2, delimiter=",", header="Delta T[K], y[m]", comments="")


plt.plot(Adj_Wall_Vel_sorted, Wall_Coord_Adj_y_sorted, label = f"Adj Wall Vel at {time_step:.3f} s")
plt.xlabel("Velocity magnitude, v [m/s]")
plt.ylabel("Vertical height, y [m]")
plt.legend()
# plt.grid(True)
plt.show()

plt.plot(Wall_Delta_Temp_sorted, Wall_Coord_y_sorted, label = f"Wall delta Temp at {time_step:.3f} s")
plt.xlabel("Wall Delta T [K]")
plt.ylabel("Vertical height, y [m]")
plt.legend()
# plt.grid(True)
plt.show()

