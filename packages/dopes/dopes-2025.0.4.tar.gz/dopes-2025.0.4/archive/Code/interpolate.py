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
import pyperclip3



def approximateOrder(order):
    if(order==""):
        try:
           order=int(input("\nOrder of approximation:" ))
        except:
            print("\nImproper order of approximation: Exiting ...\n")
            return None
    else:
        try:
           order=int(order)
        except:
            print("\nImproper order of approximation: Exiting ...\n")
            return None
    return order
            


def approximateRange():
    try:
        interpo_range=input("\nOn what range would you like to approximate ? (Enter for all range (not supported by level routine) or x_min,x_max): ")
        if(interpo_range==""):
            return None
        else:
            interpo_range=interpo_range.split(",")
            interpo_range[0]=float(interpo_range[0])
            interpo_range[1]=float(interpo_range[1])
            return interpo_range
    except:
        print("\nImproper range of approximation: Exiting ...\n")
        return 'Error'







def approximate():
    try:
        newpath=os.getcwd()+"\\fitted_data"+"\\"
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        Type=input("Available fit: sqrt, sqrt3, poly, invX, ludwik: ")
        index=approximateRange()
        flag=0     
        if(Type.lower()=="poly"):
            order=approximateOrder(input("Polynomial order: "))
        if(index!='Error' and (Type.lower()=="poly" or Type.lower()=="sqrt" or Type.lower()=="sqrt3" or Type.lower()=="invx" or Type.lower()=='ludwik')):
            files=glob.glob("*.txt")
            for i,fp in enumerate(files):
                print("currently running on: ",files[i])
                with open(fp) as file:
                    x = []
                    y = []
                    for line in file:
                        values = line.split()
                        x.append(float(values[0]))
                        y.append(float(values[1]))        
                x_filter = []
                y_filter = []
                if(index==None):
                    for k in range(len(x)):
                        x_filter.append(x[k])
                        y_filter.append(y[k])    
                else:
                    for j in range(len(x)):
                        if((x[j]>float(index[0]))&(x[j]<float(index[1]))):
                            x_filter.append(x[j])
                            y_filter.append(y[j])
                
                if(Type.lower()=='sqrt'):
                    p1=curve_fit(sqrt,x_filter,y_filter)[0]
                    x_lin=np.linspace(x_filter[0],x_filter[-1],1000)
                    f_list=fileExtensionRemover(glob.glob("*.txt"))
                    with open (newpath+f_list[i]+"_fitted_data.txt",'w') as file:
                        for i in range(len(x_lin)):
                            file.write(str(x_lin[i])+" "+str(sqrt(x_lin[i],p1[0],p1[1]))+"\n")
                    flag=1
                    
                elif(Type.lower()=='sqrt3'):
                    p1=curve_fit(sqrt3,x_filter,y_filter)[0]
                    x_lin=np.linspace(x_filter[0],x_filter[-1],1000)
                    f_list=fileExtensionRemover(glob.glob("*.txt"))
                    with open (newpath+f_list[i]+"_fitted_data.txt",'w') as file:
                        for i in range(len(x_lin)):
                            file.write(str(x_lin[i])+" "+str(sqrt3(x_lin[i],p1[0],p1[1]))+"\n")
                    flag=1
           
                elif(Type.lower()=='invx'):
                    p1=curve_fit(invX,x_filter,y_filter)[0]
                    x_lin=np.linspace(x_filter[0],x_filter[-1],1000)
                    f_list=fileExtensionRemover(glob.glob("*.txt"))
                    with open (newpath+f_list[i]+"_fitted_data.txt",'w') as file:
                        for i in range(len(x_lin)):
                            file.write(str(x_lin[i])+" "+str(invX(x_lin[i],p1[0],p1[1]))+"\n")
                    flag=1
                
                     
                elif(Type.lower()=='poly'):
                    if(order != None):  
                        Coef_1=np.polyfit(x_filter,y_filter,int(order))
                        F1=np.poly1d(Coef_1)
                        x_lin=np.linspace(x_filter[0],x_filter[-1],1000)
                        # x_lin=np.linspace(0,48,49)
                        f_list=fileExtensionRemover(glob.glob("*.txt"))
                        with open (newpath+f_list[i]+"_fitted_data.txt",'w') as file:
                            for i in range(len(x_lin)):
                                file.write(str(x_lin[i])+" "+str(F1(x_lin[i]))+"\n")
                        flag=1
                        
                        
                elif(Type.lower()=='ludwik'):
                    p1=curve_fit(ludwik,x_filter,y_filter,maxfev=10000)[0]
                    x_lin=np.linspace(x_filter[0],x_filter[-1],1000)
                    f_list=fileExtensionRemover(glob.glob("*.txt"))
                    print("\n-Yield strain=",p1[0],"\n-Strength coefficient= ",p1[1],'\n-Hardening coefficient= ',p1[2])
                    with open (newpath+f_list[i]+"_fitted_data.txt",'w') as file:
                        for i in range(len(x_lin)):
                            file.write(str(x_lin[i])+" "+str(ludwik(x_lin[i],p1[0],p1[1],p1[2]))+"\n")
                    flag=1             

              
                else:
                    print("\nError in main loop. Exiting ...\n")    
        else:
            print("\nCommand not recognised. Exiting ...\n") 
            
        if(flag==1):
            print('\n---------------------------------------------------------------\n')        
            pyperclip3.copy("path "+newpath)
            print("\nOperation successful! Created path and path command copied to clipboard. Paste to move DesCar to the created directory\n")
    except:
        print("\nSomething went wrong in approximation routine. Exiting ...\n")
        


class Level:

    def __init__(self):
        self.left=None
        self.right=None
        
    
    def set_left(self,left):
        self.left=left
    
    def set_right(self,right):
        self.right=right
        
    def clear(self):
        self.left=None
        self.right=None
        
levelSet=Level()
        

def setLeft(left):
    if(left==''):
        a=input("\nOn what range to the left of the curve would you like to fit you baseline (coma separated): ")
        a=a.split(",")
        a[0]=float(a[0])
        a[1]=float(a[1])
        levelSet.set_left(a)
        print("Left range set to: ",a,"\n")
    else:
        left=left.split(",")
        left[0]=float(left[0])
        left[1]=float(left[1])
        levelSet.set_left(left)
        print("Left range set to: ",left,"\n")
    
def setRight(right):
    if(right==''):
        a=input("\nOn what range to the right of the curve would you like to fit you baseline (coma separated): ")
        a=a.split(",")
        a[0]=float(a[0])
        a[1]=float(a[1])
        levelSet.set_right(a)
        print("Right range set to: ",a,"\n")
    else:
        right=right.split(",")
        right[0]=float(right[0])
        right[1]=float(right[1])
        levelSet.set_right(right)
        print("Right range set to: ",right,"\n")
    
def levelClear():
    levelSet.clear()
    print("\nGeneral level baseline settings cleared succesfully\n")




def level():
    order=approximateOrder(input("Polynomial order: "))
    newpath=os.getcwd()+"\leveled_data"+"\\"
    report_path=os.getcwd()+"\\report_level"+"\\"
    if not os.path.exists(report_path):
        os.makedirs(report_path)
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    
    
        
    if(levelSet.left==None):
        print("\nLeft fitting range: ")
        left=approximateRange()
        if(left==None):
            print("Full range not supported by this function. X low and high range required for leveling routine. Exiting...")
        else:
            print(left)
    else:
        left=levelSet.left
     
    if(levelSet.right==None):
        print("\nRight fitting range: ")
        right=approximateRange()
        if(right==None):
            print("Full range not supported by this function. X low and high range required for leveling routine. Exiting...")
        else:
            print(right)
    else:
        right=levelSet.right
     
    # right=approximateRange()
    # if(right==None):
        # print("Full range not supported by this function. X low and high range required for leveling routine. Exiting...")
    # else:
        # print(right)
            
    f_list=fileExtensionRemover(glob.glob("*.txt"))
    if(left!='Error' and left!=None and right!='Error' and right!=None):        
        files=glob.glob("*.txt")
        for i,fp in enumerate(files):
            print("currently running on: ",files[i])
            with open(fp) as file:
                x = []
                y = []
                for line in file:
                    values = line.split()
                    x.append(float(values[0]))
                    y.append(float(values[1])) 
            x_filter = []
            y_filter = []
            for j in range(len(x)):
                if((x[j]>float(left[0]))&(x[j]<float(left[1]))):
                    x_filter.append(x[j])
                    y_filter.append(y[j])
                elif((x[j]>float(right[0]))&(x[j]<float(right[1]))):
                    x_filter.append(x[j])
                    y_filter.append(y[j])
            # fig=plt.figure()
            # ax=fig.add_subplot()
            Coef_1=np.polyfit(x_filter,y_filter,int(order))
            F1=np.poly1d(Coef_1)
            # x_lin=np.linspace(left[0],right[1],1000) #-1 = takes the last element THE CODE DOES NOT WORK WITH THE X LIN VERSION
            # ax.plot(x,y,ls="",marker=".")   
            # ax.plot(x_lin,F1(x_lin),ls="",marker=".")
            # ax.plot(x,y-F1(x),ls="",marker=".")
            with open (report_path+f_list[i]+"_leveling_curve.txt",'w') as file:
                    for j in range(len(x)):
                        file.write(str(x[j])+" "+str(F1(x[j]))+"\n") 
            with open (newpath+f_list[i]+"_leveled.txt",'w') as file:
                    for j in range(len(x)):
                        file.write(str(x[j])+" "+str(y[j]-F1(x[j]))+"\n") 
                      
    print('\n---------------------------------------------------------------\n')        
    pyperclip3.copy("path "+newpath)
    print("\nOperation successful! Created path and path command copied to clipboard. Paste to move DesCar to the created directory\n")

                                
                    # ax.plot(x_filter,y_filter,ls="",marker=".")
                    # ax.set_xlabel("Position (x)")
                    # ax.set_ylabel("Deflection")
                    # titles=fileExtensionRemover(glob.glob("*.txt"))
                    # ax.set_title("Deflection of "+titles[i])
                    # temp=os.getcwd()
                    # os.chdir(save_dir)
                    # showRamanMaterial(global_material.get_material(),ax)
                    # plt.savefig(titles[i]+".png",format = 'png')
                    # plt.savefig(titles[i]+".eps",format = 'eps')
                    # plt.clf()
                    # plt.close()
                    # os.chdir(temp) 


def sqrt(x,a,b):
    return a*np.sqrt(x)+b
    

def sqrt3(x,a,b):
    return a*np.cbrt(x)+b
    
def invX(x,a,b):
    return a+b/x
    
   
def ludwik(x,a,b,c):
    return a+b*x**c
    
    


def normalise():
    newpath=os.getcwd()+"\\normalised"+"\\"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    a=approximateRange()
    files=glob.glob("*.txt")
    f_list=fileExtensionRemover(glob.glob("*.txt"))
    for i in range(len(files)):
        data_raw=np.loadtxt(files[i], delimiter=" ")
        index=(data_raw[:,0]>float(a[0])) & (data_raw[:,0]<float(a[1]))
        x=data_raw[index,0]
        y=data_raw[index,1]/np.max(data_raw[index,1])
    
        with open (newpath+f_list[i]+"_normalised.txt",'w') as file:
            for j in range(len(x)):
                file.write(str(x[j])+" "+str(y[j])+"\n") 
        
    print('\n---------------------------------------------------------------\n')        
    pyperclip3.copy("path "+newpath)
    print("\nOperation successful! Created path and path command copied to clipboard. Paste to move DesCar to the created directory\n")

        
    