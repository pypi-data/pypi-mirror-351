from filePath import * 
import cmd #cmd in small letters is the name of the module. do cmd.Cmd.any_function() to run a function from the class from the module
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import glob
from plotRaman import  *
import os
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
import re
import pyperclip3



def lorentz(x,x0,A,W):
    return 2*A/(np.pi*W)/(1+((x-x0)/(W/2))**2)
    #return A/(1+((x-x0)/(W/2))**2)
    



def peak_remover():
    #newpath=file_duplication()
    #temp_path=os.getcwd()
    #os.chdir(newpath)
    
    
    print("\nThe Raman Silicon Remove routine expects all files to be Raman data")
    a=input("\nAre you sure all .txt files in the directory are from the Raman ? (y/n): ")
    if(a.lower()=='y'):
        newpath=os.getcwd()+"\si_peak_removed"+"\\"
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        
        files = glob.glob("*.txt")
        f_list=fileExtensionRemover(glob.glob("*.txt"))
        for i,fp in enumerate(files):
            print("Removing silicon peak on: ",files[i])
            data=np.loadtxt(files[i])
            #data[:,1]=data[:,1]-np.min(data[:,1])
            f=interp1d(data[:,0],data[:,1])
            peak_x=np.linspace(515,525,100)
            win=5
            xmin=peak_x[np.argmax(f(peak_x))]-win
            xmax=peak_x[np.argmax(f(peak_x))]+win
            inter_x=np.linspace(xmin,xmax,1000)   
            inter_y=f(inter_x)
            inter_y=inter_y-np.min(inter_y)
            print("Detected peak at: [cm-1]",peak_x[np.argmax(f(peak_x))])
            
            p=curve_fit(lorentz, inter_x, inter_y, p0=[peak_x[np.argmax(f(peak_x))],np.max(f(peak_x)),5],maxfev=10000)[0]
            

            data[:,1]=f(data[:,0])-lorentz(data[:,0],p[0],p[1],p[2])-np.min(f(data[:,0]))
            
            
            with open (newpath+f_list[i]+" (Si peak removed).txt",'w') as file:
                for i in range(len(data[:,0])):
                    file.write(str(data[i,0])+" "+str(data[i,1])+"\n")
            
        print('\n---------------------------------------------------------------\n')        
        pyperclip3.copy("path "+newpath)
        print("\nOperation successful! Created path and path command copied to clipboard. Paste to move DesCar to the created directory\n")
            
        # print('\n---------------------------------------------------------------\n')      
        # print("Modified measurement without silicon peak saved to: ",newpath)  
    elif(a.lower()=='n'):
        print("\nPlease remove non Raman files before proceeding. Exiting ...")
    else:
        print("\nCommand not recognised. Exiting ...")
        
        
