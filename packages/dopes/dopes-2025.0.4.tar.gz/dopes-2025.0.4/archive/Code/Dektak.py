from filePath import * 
from interpolate import *
import cmd #cmd in small letters is the name of the module. do cmd.Cmd.any_function() to run a function from the class from the module
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import glob
# from plotRaman import  *
import os
import numpy as np
from material import *

from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import re
import pyperclip3





def dektakClean():
    newpath=os.getcwd()+"\cleaned_dektak\\"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    print("\nStarting file parsing")
    files=glob.glob("*.txt")
    f_list=fileExtensionRemover(glob.glob("*.txt"))
    for i,fp in enumerate(files):
        flag=0
        with open(fp) as file:
            x=[]
            y=[]
            for line in file:
                try:
                    if(isinstance(int(line[0]),int)):
                        values=line.split(",")
                        x.append(float(values[0]))
                        y.append(float(values[1]))
                except:
                    flag=1
            if(flag):
                print("Succesful text rejection on: ",files[i])
                with open (newpath+f_list[i]+".txt",'w') as new_file:
                    for k in range(len(x)):
                        new_file.write(str(x[k])+" "+str(y[k])+"\n") 
    print('\n---------------------------------------------------------------\n')        
    pyperclip3.copy("path "+newpath)
    print("\nOperation successful! Created path and path command copied to clipboard. Paste to move DesCar to the created directory\n")
            
                
                
