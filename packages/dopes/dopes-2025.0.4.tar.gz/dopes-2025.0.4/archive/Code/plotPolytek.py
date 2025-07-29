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



def lineOrMap(fp):
    with open(fp) as file:
        lines=file.readlines()
        if(lines[0][0]!="ï"):
            print(fp," has been detected to be a map type file")
            return 0
        else:
            print(fp," has been detected to be a line type file")
            return 1
    



def polyParsAndCorrect():  
    print("\nThe Polytec Parse And Correct routine expects all files to either be raw line or map files from the polytec")
    a=input("\nAre you sure all .txt files in the directory are from the polytec ? (y/n): ")
    if(a.lower()=='y'):
        print("\nStarting file parsing")
        files=glob.glob("*.txt")
        f_list=fileExtensionRemover(glob.glob("*.txt"))
        newpath=os.getcwd()+"\clean_polytec"+"\\"
        path_line=newpath+"\line\\"
        if not os.path.exists(path_line):
            os.makedirs(path_line)
        path_map=newpath+"\map\\"
        if not os.path.exists(path_map):
            os.makedirs(path_map)
        for i,fp in enumerate(files):
            if(lineOrMap(fp)==1):
                flag=0
                with open(fp) as file:
                    x=[]
                    z=[]
                    for line in file:
                        try:
                            if(isinstance(int(line[6]),int)):
                                values=line.replace('              ','0').split('\t')
                                x.append(float(values[0].replace(',','.')))
                                z.append(float(values[1].replace(',','.')))
                        except:
                            flag=1
                    if(flag):
                        print("currently running on: ",fp)
                        with open (path_line+f_list[i]+"_line_data_cleaned.txt",'w') as new_file:
                            for k in range(len(x)):
                                new_file.write(str(x[k])+" "+str(z[k])+"\n")
                    # print("Cleaned line data saved to: ",path_line)
            else:
                print("currently running on: ",fp)
                with open(fp) as file:
                    lines=file.readlines()
                    x=[]
                    y=[]
                    z=[]
                    for j in range(len(lines)):
                        values=lines[j].split()
                        x.append(float(values[0].replace(',','.')))
                        y.append(float(values[1].replace(',','.')))
                        z.append(float(values[2].replace(',','.')))
                                            
                     
                    with open (path_map+f_list[i]+"_map_data_cleaned.txt",'w') as new_file:
                        for k in range(len(x)):
                            new_file.write(str(x[k])+" "+str(y[k])+" "+str(z[k])+"\n")
                    # print("Cleaned map data saved to: ",path_map)
                
                
                
        print('\n---------------------------------------------------------------\n')        
        pyperclip3.copy("path "+newpath)
        print("\nOperation successful! Created path and path command copied to clipboard. Paste to move DesCar to the created directory\n")
    elif(a.lower()=='n'):
        print("\nPlease remove non polytec files before proceeding. Exiting ...")
    else:
        print("\nCommand not recognised. Exiting ...")
        
    
    
        

    

 
def deflection():
    print("\n!!Attention: The deflection routine will take the pressure information into the name of the polytec line measurement. File name should not contain numbers except the pressure info. For instance 0.5kpa, 0.5_kpa, my_measure_0.5kpa will all work but 20231127_0.5Kpa or 0.5Kpa(1) will not !!\n")
    newpath=os.getcwd()+"\deflection_data"+"\\"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    files=glob.glob("*.txt")
    x_peak=[]
    y_peak=[]
    for i,fp in enumerate(files):
        print("currently running on: ",files[i])
        x_peak.append(float(re.findall(r'\d+',files[i])[0])) #re.findall allows to find letters in a string
        with open(fp) as file:
            x = []
            y = []
            for line in file:
                values = line.split()
                # x.append(float(values[0]))
                y.append(float(values[1])) 
            y_peak.append(y[np.argmax(y)])
        
        
    sort=np.argsort(x_peak)
    x=[]
    y=[]
    for k in range(len(sort)):
        x.append(x_peak[sort[k]])
        y.append(y_peak[sort[k]])
            
    with open (newpath+"deflection_data.txt",'w') as file:
        for j in range(len(x)):
            file.write(str(x[j])+" "+str(y[j])+"\n")
    print('\n---------------------------------------------------------------\n')        
    pyperclip3.copy("path "+newpath)
    print("\nOperation successful! Created path and path command copied to clipboard. Paste to move DesCar to the created directory\n")


      
            
def dCycle():

    newpath=os.getcwd()+"\looped_data\\"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    
      
    print("\n!!Attention: files should be named up1, down1, up2, ... for this routine to work!! Automating checking starting ...\n")
    flag=0
    try:
        files=glob.glob("*.txt")
        flag=0
        for i in range(len(files)):
            if((files[i][:2]=="up")):
                if(isinstance(int(files[i][2]),int) and len(files[i])==7):
                    print(files[i]," detected. Format ok")
                else:
                    print(files[i]," detected. !!Wrong format!! Starting auto correction attempt ... ")
                    os.rename(os.getcwd()+"\\"+str(files[i]),os.getcwd()+"\\"+str(files[i][:3]+".txt"))
            elif(files[i][:4]=="down"):
                if(isinstance(int(files[i][4]),int) and len(files[i])==9):
                    print(files[i]," detected. Format ok")
                else:
                    print(files[i]," detected. !!Wrong format!! Starting auto correction attempt ... ")
                    os.rename(os.getcwd()+"\\"+str(files[i]),os.getcwd()+"\\"+str(files[i][:5]+".txt"))
    except:
        print("\nError in data interpretation loop. Exiting...")
        flag=1
    if(flag==0):
        try:
            shift_x=0
            shift_y=0

            with open("up1.txt") as file:
                print("Working on up1")
                x_temp=[]
                y_temp=[]  
                for line in file:
                    values = line.split()
                    x_temp.append(float(values[0]))
                    y_temp.append(float(values[1]))
                sort=np.argsort(x_temp)
                x=[]
                y=[]
                for k in range(len(sort)):
                    x.append(x_temp[sort[k]])
                    y.append(y_temp[sort[k]])
                # shift_x=x[-1]
                shift_y=y[-1]
                with open (newpath+"up1.txt",'w') as new_file:
                    for k in range(len(x)):
                        new_file.write(str(x[k])+" "+str(y[k])+"\n")

            counter=1
            for i in range(len(files)):
                if(i==0):
                    print("Skipping up1 (already done)")
                elif(i%2==0 and i!=0):
                   with open("up"+str(counter)+".txt") as file:
                        print("Working on: \"up"+str(counter)+".txt\".")
                        # print("Working on: \"up"+str(counter)+".txt\". (i="+str(i)+" and Counter="+str(counter)+")")
                        x_temp=[]
                        y_temp=[]  
                        for line in file:
                            values = line.split()
                            x_temp.append(float(values[0]))
                            y_temp.append(float(values[1]))
                        sort=np.argsort(x_temp)
                        x=[]
                        y=[]
                        for k in range(len(sort)):
                            x.append(x_temp[sort[k]])
                            y.append(y_temp[sort[k]]) 
                        # shift_x=shift_x-x[0]
                        shift_y=shift_y-y[0]
                        for j in range(len(x)):
                            # x[j]=x[j]+shift_x
                            y[j]=y[j]+shift_y
                        # shift_x=x[-1]
                        shift_y=y[-1]
                        with open (newpath+"up"+str(counter)+".txt",'w') as new_file:
                            for k in range(len(x)):
                                new_file.write(str(x[k])+" "+str(y[k])+"\n") 
                elif(i%2==1):
                    with open("down"+str(counter)+".txt") as file:
                        print("Working on: \"down"+str(counter)+".txt\".")
                        # print("Working on: \"down"+str(counter)+".txt\". (i="+str(i)+" and Counter="+str(counter)+")")
                        x_temp=[]
                        y_temp=[]  
                        for line in file:
                            values = line.split()
                            x_temp.append(float(values[0]))
                            y_temp.append(float(values[1]))
                        sort=np.argsort(x_temp)
                        x=[]
                        y=[]
                        for k in range(len(sort)):
                            x.append(x_temp[sort[k]])
                            y.append(y_temp[sort[k]])
                        # shift_x=shift_x-x[-1]
                        shift_y=shift_y-y[-1]
                        for j in range(len(x)):
                            # x[j]=x[j]+(shift_x)
                            y[j]=y[j]+(shift_y)
                        # shift_x=x[0]
                        shift_y=y[0]
                        with open (newpath+"down"+str(counter)+".txt",'w') as new_file:
                            for k in range(len(x)):
                                new_file.write(str(x[k])+" "+str(y[k])+"\n")
                        counter=counter+1
                    
                else:
                    print("Should not happen")
                    
            print('\n---------------------------------------------------------------\n')        
            pyperclip3.copy("path "+newpath)
            print("\nOperation successful! Created path and path command copied to clipboard. Paste to move DesCar to the created directory\n")
            
        except:
            print("\nError in main loop. Name correction attempts might have failed if initial names were wrong or data format are wrong. Exiting...")
    
        