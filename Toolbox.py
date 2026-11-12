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
import RunTools


##################################################################################################################################################
# FILE HANDLING
##################################################################################################################################################

def check_file_exist(_directory, _file):
    """
    Checks if a file exists at the passed directory.

    :param _directory: Directory where the file is.
    :type _directory: str
    :param _file: Name of the file to be read.
    :type _file: str
    :return: True if the file exists else false.
    """

    if not (os.path.exists(_directory) and os.path.isdir(_directory)):
        print('ERROR: Requested file path, ' + _directory + ' does not exist.')
        sys.stdout.flush()
        return False
    if not os.path.exists(_directory + _file):
        print('ERROR: Requested file, ' + _file + ' does not exist.')
        sys.stdout.flush()
        return False
    else:
        return True



def pvd_read(_directory, _file, _is_stead=False):
    """
    Reads the supplied .pvd file and creates a list of all vtu (or pvtu in parallel) files returns the time, directory and vtu(pvtu) file names.

    :param _directory: Directory where the pvd file to be read is.
    :type _directory: str
    :param _file: Name of the pvd file to be read (note: include the .pvd file extension to the name).
    :type _file: str
    :param _is_stead: Whether a steady-simulation was requested.
    :type _is_stead: bool
    :return: An array where each row is a .vtu or .pvtu read from the .pvd file: [[time, direc, .vtufilename], [time, direc, .vtufilename], ...]
    """

    if not os.path.isdir(_directory):
        IOError("ERROR: Directory does not exists")

    if not check_file_exist(_directory, _file):
        IOError('Could not find ' + _file + ' in ' + _directory)

    # Change the directory, this so the file paths are correct.
    current_directory = os.path.join(os.getcwd(), "")
    os.chdir(_directory)

    # Parse the .pvd file
    tree = ET.parse(_file)
    root = tree.getroot()

    # List to hold the filenames of the .pvtu/.vtu files
    file_list = []

    # Function to recursively find file attributes
    def find_files(element):
        if element.tag.endswith('DataSet') or element.tag.endswith('Collection'):
            file_name = element.get('file')
            timestep = element.get('timestep')
            if file_name:
                directory_path, file = os.path.split(file_name)
                file_list.append([timestep, _directory + os.path.join(directory_path.replace("/", "\\"), ""), file])

        # Recursively check child elements
        for child in element:
            find_files(child)

    # Start searching from the root
    find_files(root)
    os.chdir(current_directory)
    return file_list


def read_vtk(_directory, _file, _field_name_list, _parallel_node_state_string='Parallel Communication Flag'):
    """
    Read vtk files and get field data for the specified in field names, where pvtu's are used delete slave node data (unless told not to).

    :param _directory: Directory where the .pvtu or .vtu is in.
    :type _directory: str
    :param _file: vtk filename, must be either .vtu or .pvtu
    :type _file: str
    :param _field_name_list: Data point field names, must be in an exact match for the names in the vtk file. Node co-ordinates are referenced via 'Points'.
    :type _field_name_list: list(str).
    :param _parallel_node_state_string: The name of the field which contains the parallel node state of each node in vtk, the set '' to not delete slaves.
    :type _parallel_node_state_string: str.
    :return: The data fields from the read vtk file for all cores.
    """

    if not os.path.isdir(_directory):
        raise IOError("Directory does not exist")

    if not check_file_exist(_directory, _file):
        IOError('Could not find ' + _file + ' in ' + _directory)

    if not (isinstance(_field_name_list, list)):
        raise TypeError("fieldNames must be a list, eg [fieldName0, fieldName1]")

    is_pvtu = _file.split(".")[1] == 'pvtu'
    if not (is_pvtu or _file.split(".")[1] == 'vtu'):
        raise IOError(_file + " is not a .vtu or .pvtu.")

    vtk_data = []
    if is_pvtu:
       reader = vtk.vtkXMLPUnstructuredGridReader()
    else:
       reader = vtk.vtkXMLUnstructuredGridReader() 
    reader.SetFileName(_directory + _file)
    reader.Update()
    unstructured_grid = reader.GetOutput()
    clean_filter = vtk.vtkCleanUnstructuredGrid()
    clean_filter.SetInputData(unstructured_grid)
    clean_filter.Update()            
    # Get the cleaned data
    vtk_output = clean_filter.GetOutput()
    for i_field, field in enumerate(_field_name_list):
        current_data = vtk_to_numpy(vtk_output.GetPointData().GetArray(field)) \
            if not field == 'Points' else vtk_to_numpy(vtk_output.GetPoints().GetData())
       
        if not len(_field_name_list) == len(vtk_data):
            vtk_data.append(current_data)
        else:
            vtk_data[i_field] = np.concatenate((vtk_data[i_field], current_data))
    return vtk_data


##################################################################################################################################################
