from filePath import * 
import cmd #cmd in small letters is the name of the module. do cmd.Cmd.any_function() to run a function from the class from the module
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import glob
from plotRaman import  *
import os
import numpy as np
from material import *
import re 
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
import pyperclip3






def ramanMapCleanAndAvg():
    newpath=os.getcwd()+"\\corrected_raman_map"+"\\"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    files=glob.glob("*.txt")
    f_list=fileExtensionRemover(glob.glob("*.txt"))
    flag=0
    a=float(input("How much data point do you have in the map?: "))
    for i,fp in enumerate(files):
        print("Working on \"",files[i],"\"")
        with open(fp) as file:
            for line in file:
                if(line[0]!='#'):
                    if(flag==1):
                        y_temp=np.zeros(len(line.split()))
                        y_temp=line.split()
                        y_temp2=y_temp[2:]
                        for k in range(len(y_temp2)):
                                y[k]=y[k]+float(y_temp2[k])
                    else:
                        x=np.zeros(len(line.split()))
                        y=np.zeros(len(line.split()))
                        x=line.split()
                        flag=1
            y=y/a
            with open (newpath+f_list[i]+"_corrected_map.txt",'w') as file:
                for j in range(len(x)):
                    file.write(str(x[j])+" "+str(y[j])+"\n")
    print('\n---------------------------------------------------------------\n')        
    pyperclip3.copy("path "+newpath)
    print("\nOperation successful! Created path and path command copied to clipboard. Paste to move DesCar to the created directory\n")





def ramanSiliconPressure():
    newpath=os.getcwd()+"\\raman_peak_shift"+"\\"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    files=glob.glob("*.txt")
    x_pressure=[]
    y_1peak_pos=[]
    y_2peak_pos1=[]
    y_2peak_pos2=[]
    error=[]
    for i,fp in enumerate(files):
        with open(fp) as file:
            print("Working on ","\"",files[i],"\"")
            x_temp = []
            y_temp = []
            for line in file:
                values = line.split()
                x_temp.append(float(values[0]))
                y_temp.append(float(values[1]))
            
            try:
                y_1peak_pos.append(find_1peak(x_temp,y_temp)) #LO
                y_2peak_pos1.append(find_2peaks(x_temp,y_temp)[0]) #TO
                y_2peak_pos2.append(find_2peaks(x_temp,y_temp)[1]) #LO
                x_pressure.append(float(re.findall(r'\d+',files[i])[0]))
            except:
                print("\n!!Fit error!!",files[i],"was skipped\n")

                
            
    sort=np.argsort(x_pressure)

    x=[]
    y=[]
    for k in range(len(sort)):
        x.append(x_pressure[sort[k]])
        y.append(y_1peak_pos[sort[k]])   
    with open (newpath+"raman_peak_lorentzian1.txt",'w') as file:
        for j in range(len(x)):
            file.write(str(x[j])+" "+str(y[j])+"\n")
    
    with open (newpath+"LO_Ferran_Urena_and_all_uniAxial.txt",'w') as file:
        for j in range(len(x)):
            file.write(str(x[j])+" "+str((520.7-y[j])/(343))+"\n")
    
    with open (newpath+"LO_Nicolas_Roisin_and_all_uniAxial.txt",'w') as file:
        for j in range(len(x)):
            file.write(str(x[j])+" "+str((520.7-y[j])/(175.77))+"\n")
            
    
    
            
    
    
    x1=[]
    y1=[]
    for k in range(len(sort)):
        x1.append(x_pressure[sort[k]])
        y1.append(y_2peak_pos1[sort[k]])   
    with open (newpath+"raman_peak1_lorentzian2.txt",'w') as file:
        for j in range(len(x1)):
            file.write(str(x1[j])+" "+str(y1[j])+"\n")
     
    # with open (newpath+"LO_Ferran_Urena_and_all(TP).txt",'w') as file:
        # for j in range(len(x1)):
            # file.write(str(x1[j])+" "+str((520.7-y1[j])/(485))+"\n")
    
    # with open (newpath+"LO_Nicolas_Roisin_and_all(TP).txt",'w') as file:
        # for j in range(len(x1)):
            # file.write(str(x1[j])+" "+str((520.7-y1[j])/(400))+"\n")    
            
            
            
    x2=[]
    y2=[]        
    for k in range(len(sort)):
        x2.append(x_pressure[sort[k]])
        y2.append(y_2peak_pos2[sort[k]])   
    # with open (newpath+"TO_Ferran_Urena_and_all(TP).txt",'w') as file:
        # for j in range(len(x2)):
            # file.write(str(x2[j])+" "+str((520.7-y2[j])/(485))+"\n")
    
    
    # with open (newpath+"TO_Nicolas_Roisin_and_all(TP).txt",'w') as file:
        # for j in range(len(x2)):
            # file.write(str(x2[j])+" "+str((520.7-y2[j])/(400))+"\n")
            
    with open (newpath+"raman_peak2_lorentzian2.txt",'w') as file:
        for j in range(len(x2)):
            file.write(str(x2[j])+" "+str(y2[j])+"\n")
            
    print('\n---------------------------------------------------------------\n')        
    pyperclip3.copy("path "+newpath)
    print("\nOperation successful! Created path and path command copied to clipboard. Paste to move DesCar to the created directory\n")
    
   
#Code bellow from Nicolas Roisin. PhD student uclouvain 2023      
            

def lorentzian( x, a,b,c ):
    return b * c**2 / ( c**2 + ( x - a )**2)

 

def lorentzian2( x, a1,b1,c1,a2,b2,c2  ):
    return b1 * c1**2 / ( c1**2 + ( x - a1 )**2)+b2 * c2**2 / ( c2**2 + ( x - a2 )**2)



#We here try to detect a single peak. A single peak would be mainly the LO (LL 20231212)

#We do a quadratic interpolation of the Raman spectrum then we detect the max. The >450 is to take the median and remove the baseline.
# Taking >450 removes some weird effect that can appear bellow 450 

def find_1peak(x,y):
    x=np.array(x)
    y=np.array(y)
    x_interp=np.linspace(x[0],x[-1],10000)
    # y=y-np.median(y[(x<500) & (x>480)])
    y=y-np.median(y[(x>450)])
    y=y/np.max(y)
    f = interp1d(x, y,kind='quadratic')   
    x0=x_interp[f(x_interp)==np.max(f(x_interp[x_interp>450]))][0]
    p1=curve_fit(lorentzian,x_interp,f(x_interp),p0=[x0,0.7,1],bounds=[(515,0,0.5),(525,1,3)],maxfev=10000)[0]
    return p1[0] #returns the position only
    # return p1 #returns the position, height and width

#We here try to find two peaks: LO and TO. The LO is the one that moves the less compared to the 520.7 original position of the peak. The TO moves away to
# the left of this position. Not always possible to find it. Under high levels of strain the two peaks do separate. Not so much with smaller levels of deformation
# p2[0] => TO and p2[3] => LO (LL 20231212)

#We do a quadratic interpolation of the Raman spectrum then we detect the max. The >450 is to take the median and remove the baseline.
# Taking >450 removes some weird effect that can appear bellow 450 

def find_2peaks(x,y):
    x=np.array(x)
    y=np.array(y)
    x_interp=np.linspace(x[0],x[-1],10000)
    y=y-np.median(y[x<450])
    y=y/np.max(y)
    f = interp1d(x, y,kind='quadratic')   
    x0=x_interp[f(x_interp)==np.max(f(x_interp[x_interp>450]))][0]
    p2=curve_fit(lorentzian2,x_interp,f(x_interp),p0=[x0-0.1,0.7,1,x0+0.1,0.7,1],bounds=[(515,0,0.5,515,0,0.5),(525,1,3,525,1,3)],maxfev=10000)[0]
    return p2[0],p2[3]




#We do a quadratic interpolation of the Raman spectrum then we detect the max. The >450 is to take the median and remove the baseline.
# Taking >450 removes some weird effect that can appear bellow 450 

def find_peak_max(x,y):
    x=np.array(x)
    y=np.array(y)
    x_interp=np.linspace(x[0],x[-1],10000)
    # y=y-np.median(y[(x<500) & (x>480)])
    y=y-np.median(y[(x>450)]) 
    y=y/np.max(y)
    f = interp1d(x, y,kind='quadratic')   
    x0=x_interp[f(x_interp)==np.max(f(x_interp[x_interp>450]))][0]
    return x0