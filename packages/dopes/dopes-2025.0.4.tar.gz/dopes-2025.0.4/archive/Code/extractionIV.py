from filePath import * 
import cmd #cmd in small letters is the name of the module. do cmd.Cmd.any_function() to run a function from the class from the module
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import glob
from plotRaman import  *
import os
import numpy as np
import pyperclip3
from material import *




def resistance(path,aRange):
    try:
        with open(path) as file:
            data=np.loadtxt(file)
            v=data[:,0]
            i=data[:,1]
            r=np.polyfit(i[v>aRange],v[v>aRange],1)[0]
        return r
    except:
        print('\n---------------------------------------------------------------\n')
        print("\nError in resistance polyfit. Exiting...\n")




# def rPressure():
    # newpath=os.getcwd()+"\resistance"+"\\"
    # if not os.path.exists(newpath):
        # os.makedirs(newpath)
    # a=int(input(""))
    # b=input("On what voltage range would you like to compute the resistance (coma separated): ").split(",")
    # b[0]=float(b[0])
    # b[1]=float(b[1])
    # files=glob.glob("*.txt")
    # f_list=fileExtensionRemover(glob.glob("*.txt"))
    # pData=[]
    # for i in range(len(files):
        # pData.append()
    
    # for i,fp in enumerate(files):
        # r.append(float(f_list[i][]))


def rPressure():
    try:
        print("\n!!Attention: The resistanceP routine will take the pressure information into the name of the file. File name should not contain numbers except the pressure info. For instance 0.5kpa, 0.5_kpa, my_measure_0.5kpa will all work but 20231127_0.5Kpa or 0.5Kpa(1) will not !!\n")
        newpath=os.getcwd()+"\\resistance"+"\\"
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        files=glob.glob("*.txt")
        b=float(input("What starting voltage do you want to use to compute the resistance: "))
        x_temp=[]
        y_temp=[]
        for i,fp in enumerate(files):
            print("currently running on: ",files[i])
            x_temp.append(float(re.findall(r'\d+',files[i])[0])) #re.findall allows to find letters in a string
            path=os.getcwd()+"\\"+files[i]
            y_temp.append(resistance(path,b))
        sort=np.argsort(x_temp)
        x=[]
        y=[]
        for k in range(len(sort)):
            x.append(x_temp[sort[k]])
            y.append(y_temp[sort[k]])
                
        with open (newpath+"resistance_data.txt",'w') as file:
            for j in range(len(x)):
                file.write(str(x[j])+" "+str(y[j])+"\n")
        print('\n---------------------------------------------------------------\n')        
        pyperclip3.copy("path "+newpath)
        print("\nOperation successful! Created path and path command copied to clipboard. Paste to move DesCar to the created directory\n")
    except:
        print('\n---------------------------------------------------------------\n')
        print("\nError in main loop. Check manual entries. Exiting...\n")


