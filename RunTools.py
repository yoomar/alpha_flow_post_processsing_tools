'''
Description: Module for running and Compiling Elemental bin data

'''

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
from vtk.util.numpy_support import vtk_to_numpy
import xml.etree.ElementTree as ET
workDirec = '../workdirec'


########################################################################################################################
# BLOCK 1: Binary Handling Functions                                                                                   #
########################################################################################################################

def copy_binary(asourDirec, adestDirec, abinaName, afinalBinaName = None):
    # Check that the source, destination paths, and file exists - then copies the file over.
    if not (os.path.exists(asourDirec) and os.path.isdir(asourDirec)):
        print('ERROR: Requested binary path, ' + asourDirec + ' does not exist.')
        sys.stdout.flush()
        return False
    if not (os.path.exists(adestDirec) and os.path.isdir(adestDirec)):
        print('ERROR: Requested binary path, ' + adestDirec + ' does not exist.')
        sys.stdout.flush()
        return False
    if not os.path.exists(asourDirec + abinaName):
        print('ERROR: Requested binary, ' + abinaName + ' does not exist.')
        sys.stdout.flush()
        return False
    else:
        print('Copying binary ' + abinaName + '...')
        sys.stdout.flush()
        if afinalBinaName is None:
            afinalBinaName = abinaName
        shutil.copy(asourDirec + abinaName, adestDirec + afinalBinaName)
        os.system("chmod a+x " + adestDirec + afinalBinaName)
    return True


def run_binary(arunDirec, abinaName, abinaArgu):
    """
    Runs a binary with the name abinaName from the run directory arunDirec. The function will return true if the binary exited with state 0. If an error ocour
    the function returns false. The function will return to the directory from which it was called.
    :param arunDirec: The directory the binary must be run from
    :param abinaName: The name of the binary to be run.
    :param abinaArgu: Arguments for the binary.
    :return: True if the binary was located and run successfully, else false.
    """

    # Record starting directory.
    startDirec = os.getcwd()

    # Check that the binary exists at the source path and that the run directory exists, then copy the binary over.
    if not (os.path.exists(arunDirec) and os.path.isdir(arunDirec)):
        print('ERROR: Requested run directory, ' + arunDirec + ' does not exist.')
        sys.stdout.flush()
        return False
    if not (os.path.exists(arunDirec + abinaName)):
        print('ERROR: ' + abinaName + ' binary missing in ' + arunDirec)
        sys.stdout.flush()
        return False

    # Running binary
    print("Running " + abinaName + abinaArgu + "...")
    sys.stdout.flush()
    os.chdir(arunDirec)

    with io.open('run.log', 'wb') as outstr:
        process = subprocess.Popen('./' + abinaName + abinaArgu, shell=True, stdout=outstr)
        process.wait()
        sys.stdout.flush()

    os.chdir(startDirec)
    if process.returncode != 0:
        print('Binary returned with non-zero exit code, ' + str(process.returncode))
        return False
    else:
        return True


def run_mpi_binary(arunDirec, abinaName, abinaArgu, amcore):
    """
    Runs a binary with the name abinaName from the run directory arunDirec with MPI. The function will return true if the binary exited with state 0. If an
    error ocour the function returns false. The function will return to the directory from which it was called.
    :param arunDirec: The directory the binary must be run from
    :param abinaName: The name of the binary to be run.
    :param abinaArgu: Arguments for the binary.
    :param amcore: Number of cores used for mpi, i.e. argument for -np
    :return: True if the binary was located and run successfully, else false.
    """

    # Record starting directory.
    startDirec = os.getcwd()

    # Check that the binary exists at the source path and that the run directory exists, then copy the binary over.
    if not (os.path.exists(arunDirec) and os.path.isdir(arunDirec)):
        print('ERROR: Requested run directory, ' + arunDirec + ' does not exist.')
        sys.stdout.flush()
        return False
    if not (os.path.exists(arunDirec + abinaName)):
        print('ERROR: ' + abinaName + ' binary missing in ' + arunDirec)
        sys.stdout.flush()
        return False

    # Running binary with mpi
    print("Running mpirun -np " + str(amcore) + ' ' + abinaName + ' ' + abinaArgu + "...")
    sys.stdout.flush()
    os.chdir(arunDirec)
    mpirun = 'mpirun -np ' + str(amcore) + ' ' + abinaName + ' ' + abinaArgu
    with io.open('run.log', 'wb') as outstr:
        process = subprocess.Popen(mpirun, shell=True, stdout=outstr)
        process.wait()
        sys.stdout.flush()

    os.chdir(startDirec)
    if process.returncode != 0:
        print('Binary returned with non-zero exit code, ' + str(process.returncode))
        return False
    else:
        return True

########################################################################################################################
# BLOCK 2: File Handling Functions                                                                                     #
########################################################################################################################


def CheckFileExist(adirec, afile):
    """
    Checks if a file exists at the passed directory.
    :param adirec: Directory where the file is.
    :param afile: Name of the file to be read.
    :return: True if the file exists else false.
    """
    if not (os.path.exists(adirec) and os.path.isdir(adirec)):
        print('ERROR: Requested file path, ' + adirec + ' does not exist.')
        sys.stdout.flush()
        return False
    if not os.path.exists(adirec + afile):
        print(adirec + afile)
        print('ERROR: Requested file, ' + afile + ' does not exist.')
        sys.stdout.flush()
        return False
    else:
        return True


def CopyFile(asourDirec, adestDirec, afileName, afinalFileName = None):
    """
    Copies a file from the source directory to the destination directory. The file name can be changed if desired. This function will ensure that all the paths
    do exist and that the program does not exit due to a missing file. This function will overwrite any existing files at the destination with its name.
    :param asourDirec: The directory where the file to be copied can be found.
    :param adestDirec: The directory where the file is to be copied to.
    :param afileName: Name of the file to be copied, at the source directory.
    :param afinalFileName: Name of the file once copied, if defaulted to be the source name.
    :return: True if the file was copied successfully else false.
    """

    # Check that the source, destination paths, and file exists - then copies the file over.
    if not CheckFileExist(asourDirec, afileName):
        return False
    if not (os.path.exists(adestDirec) and os.path.isdir(adestDirec)):
        print('ERROR: Requested file path, ' + adestDirec + ' does not exist.')
        sys.stdout.flush()
        return False
    else:
        print('Copying file ' + asourDirec + afileName + ' to ' + adestDirec + afinalFileName + '...')
        sys.stdout.flush()
        if afinalFileName is None:
            afinalFileName = afileName
        shutil.copy(asourDirec + afileName, adestDirec + afinalFileName)
    return True


def ReadFile(adirec, afile):
    """
    Reads a file and returns an array where each line is an element in the array. The function will check that the directory and file exist before reading.
    :param adirec: Directory where the file to be read is.
    :param afile: Name of the file to be read.
    :return: False if the function failed to read the file, otherwise an array where each element is a line of the file.
    """
    if not CheckFileExist(adirec, afile):
        return False
    else:
        print('Reading file ' + adirec + afile + '...')
        fileData = []
        with open(adirec + afile, 'r') as fileRead:
            for line in fileRead:
                fileData.append(line)
        return fileData


def LineRepla(adirec, afile, akeyWord, aline):
    """
    Reads a file and and replaces lines when the passed key word is found in the line. (You do not need to add the new line in the aline argument)
    :param adirec: Directory where the file to changed is.
    :param afile: Name of the file to be changed.
    :param akeyWord: The exact key word which will trigger the line to be replaced.
    :param aline: The new line to replace the line where the key word is found.
    :return: True if the file was successfully opened and line replaced, else false. Note: if no keyword is found the function will still return true.
    """

    if not CheckFileExist(adirec, afile):
        return False
    else:
        # Open the file for reading, and a temp file for writing.
        print('Updating ' + afile + '...')
        tempFileName = adirec + afile + '.TEMP'
        readFile = open(adirec + afile, 'r')
        writeFile = open(tempFileName, 'w')

        # Look for the key word and replace if found.
        for line in readFile:
            wordlst = line.split() # Split line into strings
            if akeyWord.strip() in wordlst: # Strip the keyword of any leading or trailing spaces
                line = aline + '\n'
            writeFile.write(line)


        # Close the files and move the temp file to the original file
        readFile.close()
        writeFile.close()
        os.remove(adirec + afile)
        os.rename(tempFileName, adirec + afile)

        return True


################################################################################################################################################################
# BLOCK 2: File Handling Functions                                                                                                                             #
################################################################################################################################################################

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


def copy_file(_source_direc, _destination_directory, _file_name, _final_file_name=None):
    """
    Copies a file from the source directory to the destination directory. The File Name can be changed if desired. This function will ensure that all the paths
    do exist and that the program does not exit due to a missing file. This function will overwrite any existing files at the destination with its name.

    :param _source_direc: The directory where the file to be copied can be found.
    :type _source_direc: str
    :param _destination_directory: The directory where the file is to be copied to.
    :type _destination_directory: str
    :param _file_name: Name of the file to be copied, at the source directory.
    :type _file_name: str
    :param _final_file_name: Name of the file once copied, if defaulted to be the source name.
    :type _final_file_name: str
    :return: True if the file was copied successfully else false.
    """

    # Check that the source, destination paths, and file exists - then copies the file over.
    if not check_file_exist(_source_direc, _file_name):
        return False
    if not (os.path.exists(_destination_directory) and os.path.isdir(_destination_directory)):
        print('ERROR: Requested file path, ' + _destination_directory + ' does not exist.')
        sys.stdout.flush()
        return False
    else:
        print('Copying file ' + _source_direc + _file_name + ' to ' + _destination_directory + _final_file_name + '...')
        sys.stdout.flush()
        if _final_file_name is None:
            _final_file_name = _file_name
        shutil.copy(_source_direc + _file_name, _destination_directory + _final_file_name)
    return True


def read_file(_directory, _file):
    """
    Reads a file and returns an array where each line is an element in the array. The function will check that the directory and file exist before reading.

    :param _directory: Directory where the file to be read is.
    :type _directory: str
    :param _file: Name of the file to be read.
    :type _file: str
    :return: False if the function failed to read the file, otherwise an array where each element is a line of the file.
    """
    if not check_file_exist(_directory, _file):
        return False
    else:
        print('Reading file ' + _directory + _file + '...')
        file_data = []
        with open(_directory + _file, 'r') as fileRead:
            for line in fileRead:
                file_data.append(line)
        return file_data


def line_replace(_directory, _file, _key_word, _new_line):
    """
    Reads a file and and replaces lines when the passed key word is found in the line. (You do not need to add the new line in the aline argument)

    :param _directory: Directory where the file to changed is.
    :type _directory: str
    :param _file: Name of the file to be changed.
    :type _file: str
    :param _key_word: The exact key word which will trigger the line to be replaced.
    :type _key_word: str
    :param _new_line: The new line to replace the line where the key word is found.
    :type _new_line: str
    :return: True if the file was successfully opened and line replaced, else false. Note: if no keyword is found the function will still return true.
    """

    if not check_file_exist(_directory, _file):
        return False
    else:
        # Open the file for reading, and a temp file for writing.
        print('Updating ' + _file + '...')
        temporary_file_name = _directory + _file + '.TEMP'
        read_file_name = open(_directory + _file, 'r')
        write_file_name = open(temporary_file_name, 'w')

        # Look for the key word and replace if found.
        for line in read_file_name:
            word_list = line.split()  # Split line into strings
            if _key_word.strip() in word_list:  # Strip the keyword of any leading or trailing spaces
                line = _new_line + '\n'
            write_file_name.write(line)

        # Close the files and move the temp file to the original file
        read_file_name.close()
        write_file_name.close()
        os.remove(_directory + _file)
        os.rename(temporary_file_name, _directory + _file)

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

    # Change ot directory, this so the file paths are correct.
    current_directory = os.getcwd()
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
                file_list.append([timestep, os.getcwd() + '/' + directory_path + '/', file])

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
        raise TypeError("feildNames must be a list, eg [fieldName0, feildName1]")

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

def CompBina(abinaExten, amcore):

    """
    Compiles any of Elemental's binaries using the MakeFile generated by cmake, which should be located in the build directory in the Elemental's source
    directory. The output and error stream are saved to a text file, compile.log. If the compilation fails, the contents of compile.log are returned, otherwise
    only a notification of success is returned.

    :param abinaExten: The name of the binary, used for output purposes.
    :param abinName: The name of the binary which is to be compiled.
    :return: True if compilation succeeded else false.
    """

    # Record current directory
    currDire = os.getcwd()

    # Set up standard write out
    compOut = 'Compiling ' + abinaExten + '...'
    print(compOut + " "),
    sys.stdout.flush()
    addedSpace = " "
    for ii in range(0, 50 - len(compOut)):
        addedSpace += " "

    # Set up a .log file
    filename = currDire + '/compile.log'
    if os.path.exists(filename):
        os.remove(filename)

    # Change to source directory and build project.
    os.chdir('/media/veracrypt1/Elem/build')
    with io.open(filename, 'wb') as writer:
        process = subprocess.Popen(str('make -j' + str(amcore) + ' Elemental'), shell=True, stdout=writer, stderr=writer)
        if process.wait() != 0:
            # Report failure and close the log writer.
            print('compile failed ')
            writer.close()

            # Open the log and write it to screen
            reader = open(filename, 'r')
            compLogCont = reader.read()
            print(compLogCont)

            # Change directory and return false
            os.chdir(currDire)
            return False

    # For successful builds, report results and move binary to the bin folder (renaming it in the process)
    print('compile complete ')
    shutil.move('/media/veracrypt1/Elem/build/bin/Elemental', currDire + './bin/Elemental' + abinaExten)
    os.chdir(currDire)
    return True


def buildNodeElemConn(elements, mnode):
    '''
    Reads Base mesh and generates basic data structures

    :param elements: Specific elements to which the connectr refrs to
    :param mnode: total number of connecting nodes
    :return:
    '''
    nodeElemConn = []
    nodeNodeConn = []

    # initalise to -1
    for inode in range(mnode):
        nodeElemConn.append([])
        nodeNodeConn.append([])

    ielem = 0
    for elem in elements:
        for inode in elem:
            nodeElemConn[inode].append(ielem)

            for iconnNode in elem:
                if iconnNode == inode:
                    continue
                else:
                    isfound = False
                    for iconnNodeinTable in nodeNodeConn[inode]:
                        if(iconnNodeinTable == iconnNode):
                            isfound = True
                            break
                    if isfound == False:
                        nodeNodeConn[inode].append(iconnNode)


        ielem = ielem + 1

    return nodeNodeConn, nodeElemConn


def Readfile(Direc, filename):
    '''
    Brief: Read file

    :param Direc: Directory to read from
    :param filename: filename to read from
    :return:
    '''
    if not os.path.isdir(Direc):
        print("Directory does not exists")
        return False
    if not os.path.isfile(Direc + '/' + filename):
        print("File does not exists")
        return False
    file = open(Direc + '/' + filename)
    return file.readlines()


def Find(contents, keyword):
    '''
    Brief: Find a keyword

    :param contents: data file
    :param keyword: string to be found
    :return: int n
    '''
    n = 0
    for line in contents:
        if keyword in line:
            return n
        else:
            n += 1


def FindValue(Direc, filename, keyword):
    file = open(Direc+'/'+filename)
    for line in file:
        if keyword in line:
            return line


def CopyResults(exisDirec, resultsDirec, files):
    '''
    :param exisDirec: Directory to copy from
    :param newDirec: New Directory to copy to
    :param filename: file to be copied
    :return: bool
    '''

     # Create resultsDirec if it does not exist
    if not os.path.isdir(resultsDirec):
        os.mkdir(resultsDirec)

    # Create Generic Test folder
    for file in files:
        if os.path.isdir(exisDirec + '/' + file):
            shutil.copytree(exisDirec +'/' + file, resultsDirec + '/' + file)
        else:
            print(exisDirec + '/' + file, resultsDirec + '/' + file)
            shutil.copy(exisDirec + '/' + file, resultsDirec + '/' + file)
    return True


def RemoveDirec(Direc):

    if os.path.isdir(Direc):
        shutil.rmtree(Direc)


def CreateDirec(Direc):

    if not os.path.isdir(Direc):
        os.mkdir(Direc)


def CSVwriter(filename, Data):
    with open(str(filename) + '.csv', mode='w') as file:
        file_writer = csv.writer(file, delimiter=',')
        for i in Data:
            file_writer.writerow(Data[i][0])

    file.close()


def sci_notation(num, decimal_digits=1, precision=None, exponent=None):
    """
    Returns a string representation of the scientific
    notation of the given number formatted for use with
    LaTeX or Mathtext, with specified number of significant
    decimal digits and precision (number of decimal digits
    to show). The exponent to be used can also be specified
    explicitly.
    """
    if exponent is None:
        exponent = int(floor(log10(abs(num))))
    coeff = round(num / float(10**exponent), decimal_digits)
    if precision is None:
        precision = decimal_digits

    return r"${0:.{2}f}\times10^{{{1:d}}}$".format(coeff, exponent, precision)


def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '|', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length*iteration//total)
    bar = fill*filledLength + '-'*(length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def strRepla(Direc, filename, oldstring, newstring):

    # Open file for reading and a temp file for writing
    tempFileName = Direc + '/' + filename + 'Temp'
    readFile = open(Direc + '/' + filename, 'r')
    writeFile = open(tempFileName, 'w')

    for line in readFile:
        if oldstring in line:
            line = newstring + "\n"
        writeFile.write(line)

    readFile.close()
    writeFile.close()
    os.remove(Direc + '/' + filename)
    os.rename(tempFileName, Direc + '/' + filename)
    return True


def read_csv_data(_directory_path, _file_name, _variable_list, _n_row = 1):
   file_path = _directory_path + '/' + _file_name
   header = np.genfromtxt(file_path, delimiter=',', dtype=str, max_rows=1)
   probe_data = np.genfromtxt(file_path, skip_header=1, delimiter=',')
   data = []
   data_index = []
   for i_data in range(len(_variable_list)):
    data_index.append(np.where(header == _variable_list[i_data])[0])
    data.append([])
   for i_row in range(len(probe_data)):
    if (i_row + 1)%_n_row == 0:
     for i_data, index_data in enumerate(data_index):
      data[i_data].append(probe_data[i_row][index_data][0])
   return data 

def find_second_maximum(lst):
    return sorted(set(lst), reverse=True)[1] if len(lst) > 1 else "List has less than two elements"

def apply_scaling_factor(_data, _off_set, _scaling_factor):
 scaled_data = []
 for i in range(len(_data)):
  scaled_data.append((_data[i] + _off_set)*_scaling_factor)
 return scaled_data

 def find_index(_time, _target_time):
    m_start = 0
    while _time[m_start] < _target_time:
        m_start += 1
    return m_start


def pressure_fit(_time, _pressure_start, _pressure_equilibrium, _alpha):
    return _pressure_equilibrium + ( _pressure_start - _pressure_equilibrium)*np.exp(-_alpha*_time)


def l2_norm_error(_pressure, _pressure_fit):
    return np.sqrt(np.sum(((_pressure - _pressure_fit)/_pressure)**2))


def temperature_fit(_pressure, _average_density, _gas_constant):
    return _pressure/(_average_density*_gas_constant)

def write_table_header(_directory_name, _file_name, _header):
  write_file = open(_directory_name + _file_name + '.tex', 'w')
  write_file.write('%!TEX root = ../main.tex \n')
  write_file.write('\\begin{adjustbox}{max width=\\textwidth}' + '\n')
  tabular_environment = 'l'  # expect at least one column
  header = ''
  for i in range(len(_header)):
   if _header[i] != '':
    header += _header[i] + ('&' if i != len(_header) - 1 else '\\\\ \n')
   if i > 0:
    tabular_environment += 'c'
  write_file.write('\\begin{tabular}{' + tabular_environment + '}' + '\n')
  write_file.write('\\hline \n')
  write_file.write(header)
  write_file.write('\\hline \n')


def write_table_entry(_directory_name, _file_name, _data):
 data_entry = ''
 for i in range(len(_data)):
  data_entry += _data[i] + ('&' if i != len(_data) - 1 else '\\\\ \n')
 write_file = open(_directory_name + _file_name + '.tex', 'a')
 write_file.write(data_entry)


def finalise_table(_directory_name, _file_name):
 write_file = open(_directory_name + _file_name + '.tex', 'a')
 write_file.write('\\hline \n')
 write_file.write('\\hline \n')
 write_file.write('\\end{tabular}' + '\n')
 write_file.write('\\end{adjustbox}' + '\n')
 write_file.close()


def print_progress_bar(iteration, total, prefix ='', suffix ='', decimals = 1, length = 100, fill ='|', printEnd ="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length*iteration//total)
    bar = fill*filledLength + '-'*(length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def sci_notation(num, decimal_digits=1, precision=None, exponent=None):
    """
    Returns a string representation of the scientific
    notation of the given number formatted for use with
    LaTeX or Mathtext, with specified number of significant
    decimal digits and precision (number of decimal digits
    to show). The exponent to be used can also be specified
    explicitly.
    """
    if exponent is None:
        exponent = int(floor(log10(abs(num))))
    coeff = round(num / float(10**exponent), decimal_digits)
    if precision is None:
        precision = decimal_digits

    return r"${0:.{2}f}\times10^{{{1:d}}}$".format(coeff, exponent, precision)
    

def format_seconds(seconds):
     # Calculate days, hours, minutes, seconds, and milliseconds
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    seconds, milliseconds = divmod(int(seconds * 1000), 1000)

    # Create a formatted string
    formatted_time = f"{int(days)}:" + '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
    
    return formatted_time


def convert_to_rgb_code(_i, _cmap, _n):
    cmap = plt.get_cmap(_cmap)
    color = cmap(float(_i) /_n)
    red = int(float(color[0])*255)
    green = int(float(color[1])*255)
    blue = int(float(color[2])*255)
    alpha = int(float(color[3])*255)
    return "#{:02X}{:02X}{:02X}{:02X}".format(red, green, blue, alpha)


def compute_nusselt_number(_conductivity_laminar, _conductivity_turbulent):
    return (_conductivity_laminar + _conductivity_turbulent)/_conductivity_laminar


def compute_reynolds_number(_density, _viscosity, _velocity, _characteristic_length):
    return _density*_velocity*_characteristic_length/_viscosity


def compute_turbulent_data(_work_directory, _is_skip_header):
    [time, viscosity_liquid_turbulent, thermal_conductivity_liquid_turbulent, velocity_liquid, area] = get_turbulent_data(_work_directory, _is_skip_header)

    return time, np.amax(viscosity_liquid_turbulent), np.amax(thermal_conductivity_liquid_turbulent), np.amax(velocity_liquid), area

def get_turbulent_data(_work_directory, _is_skip_header):
    turbulent_data = np.genfromtxt(_work_directory + "/mesh0/turbulent_data.csv", skip_header=_is_skip_header, delimiter=',')
    thermal_conductivity_liquid_turbulent = []
    viscosity_liquid_turbulent = []
    velocity_liquid = []
    area = []
    time = []
    for i_data in range(len(turbulent_data)):
        time.append(turbulent_data[i_data][0])
        viscosity_liquid_turbulent.append(turbulent_data[i_data][4])
        thermal_conductivity_liquid_turbulent.append(turbulent_data[i_data][5])
        velocity_liquid.append(turbulent_data[i_data][6])
        area.append(turbulent_data[i_data][-1])
    return time, viscosity_liquid_turbulent, thermal_conductivity_liquid_turbulent, velocity_liquid, area

def get_plic_area(_work_directory, _is_skip_header):
    plic_data = np.genfromtxt(_work_directory + "/mesh0/plic_data.csv", skip_header=_is_skip_header, delimiter=',')
    area = []
    time = []
    for i in range(len(plic_data)):
        time.append(plic_data[i][0])
        area.append(plic_data[i][2])
    return time, area
