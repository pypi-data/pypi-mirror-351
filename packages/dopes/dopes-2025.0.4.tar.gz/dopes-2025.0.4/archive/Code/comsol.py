from filePath import * 
import cmd #cmd in small letters is the name of the module. do cmd.Cmd.any_function() to run a function from the class from the module
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import glob
from plotRaman import  *
import os
import numpy as np
from material import *
import pandas as pd
import pyperclip3



def comsolClean():
    print("\nThe comsolClean routine expects all files to be raw column comsol export")
    a=input("\nAre you sure all .txt files in the directory are raw column comsol export ? (y/n): ")
    if(a.lower()=='y'):
        newpath=os.getcwd()+"\\cleaned_comsol"+"\\"
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        files=glob.glob("*.txt")
        f_list=fileExtensionRemover(glob.glob("*.txt"))
        for i,fp in enumerate(files):
            print("Working on \"",files[i],"\"")
            data_list=[]
            with open(fp) as file: 
                for line in file:
                    if(line[0]!='%'):
                        values = [float(val) for val in line.strip().split()]
                        data_list.append(values)    
                x=[]
                for j in range(len(data_list[0])):
                    y=[]
                    for l in range(len(data_list)):
                        if(j==0):
                            x.append(float(data_list[l][j]))
                        else:
                            y.append(float(data_list[l][j]))
                    if(j!=0):
                        with open (newpath+f_list[i]+".txt",'w') as file1:
                            for m in range(len(x)):
                                file1.write(str(x[m])+" "+str(y[m])+"\n") 
        print('\n---------------------------------------------------------------\n')        
        pyperclip3.copy("path "+newpath)
        print("\nOperation successful! Created path and path command copied to clipboard. Paste to move DesCar to the created directory\n")
                         
    elif(a.lower()=='n'):
        print("\nPlease remove non raw column comsol export files before proceeding. Exiting ...")
    else:
        print("\nCommand not recognised. Exiting ...")               