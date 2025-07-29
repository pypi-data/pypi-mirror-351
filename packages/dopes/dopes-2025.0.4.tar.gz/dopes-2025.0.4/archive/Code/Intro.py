from filePath import * 
import cmd #cmd in small letters is the name of the module. do cmd.Cmd.any_function() to run a function from the class from the module
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import glob
from plotRaman import  *
import os
import numpy as np




def intro():
    ve="2.12.2"
    date="09/08/24"
    print("\n-------------------------------------------")
    print("\nWelcome to DesCar version ",ve," ! (Uploaded: ",date,")")
    print("\nCurrently supported features:\n")
    print("\n-Generic plot routine: plot all, rifle or select with different graphic style (line, point, fancy, ...). Adding new designs should be intuitive. Possibility to set all plot generic parameter once and not at each run of a plot command")
    print("-Raman: automatic silicon peak removal, automatic raman peak display (NO auto peak detection in ",ve," but data from material propreties). Detection and lrtz fit of silicon peaks")
    print("-Stress: Theoretical thermal stress computation, theoretical stress compensation routine, Experimental thermal stress estimation based on the differential stoney equation.")
    print("-Automatic saving of results, easy path managment (changing save/file path one by one or at the same time),saving of new path to the clipboard, autoload at boot of last path used in previous descar session,Extension modifier (with global parameter modifier),File name modification")
    print("-Material mode: Puts DesCar in a configuration related to the selected material. Material data such as the Young modulus, the Poisson ratio, the Raman spectrum are available to the entire program in a .txt file. Allows for the easy addition of new materials in DesCar.")
    print("-Polytec: raw data cleaning to a neat column  xyz .txt type file, automatic detection of maximal deflection, automatic generation of delfection fct of P in a .txt")
    print("-Generic mathematical tool: normalisation routine, approximation to any desired order on any given range of the input data,sqrt approximation, averaging of multiple clean xy files, data modifier (col mult or add), polynomial leveling of curves")
    print("-Comsol: column type export data cleaning\n-Dektak file cleaning routine")
    print("-DesCar automation: ramanStrain (from map raman measurement to strain fct pressure plot),polytecDeflection (from polytec measurement to deflection fct pressure plot),setPlot allowing to set all plot parameter in one command")
    print("-Dektak file cleaning routine")
    print("-Generic file cleaning routine. Should work with any txt input files to output clean xyz column file")
    print("-Configuration log: DesCar remembers the last file and save path as well as plot configuration between sessions")
    # print("\n-------------------------------------------")
    # print("\nUpcoming work: The Polytec and Raman plot routines (all, rifle and select) are currently coded in the same exact way. The files are almost a copy paste of each other. The code should be rewritten so that rifle, all and select become the base routines and the machines (raman, polytec, ...) are taken as modifiers")
    print("\n-------------------------------------------")
    print("\nWork by Lahaye Loïc")
    print("\n-------------------------------------------")
    print("\nContributions: Nicolas Roisin for the extraction of silicon raman peaks based on Lorenztian fit")
    print("\n-------------------------------------------")
    print("\nType help or ? to list commands. Type help followed by the command to get help on the command\n")