from filePath import * 
import cmd #cmd in small letters is the name of the module. do cmd.Cmd.any_function() to run a function from the class from the module
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import glob
from plotRaman import  *
import os
import numpy as np
import sys



class Material:
    
    def __init__(self):
        self.material = None 
        self.material_path=None
        self.raman=None
        self.poisson=None
        self.young=None
        self.thermal_exp=None
        self.comment=None
        
    def set_fullMaterial(self,Material,Raman,Young,Poisson,Thermal,Comment):
        self.material=Material
        self.raman=Raman
        self.young=Young
        self.poisson=Poisson
        self.thermal=Thermal
        self.comment=Comment
    
    def get_young(self):
        return self.young

    def get_poisson(self):
        return self.poisson

    
    def get_comment(self):
        return self.comment
     
    def set_material(self,material):
        self.material=material
    
    def get_material(self):
        return self.material
     
    def set_materialPath(self,material_path):
        self.material_path=material_path
    
    def get_materialPath(self):
        return self.material_path


    def get_Raman(self):
        return self.raman
        
    def get_thermal(self):
        return self.thermal
    
    
global_material=Material()




def materialWiz(material,material_path):
    if(material.lower()=="exit"):
        global_material.set_fullMaterial(None,None,None,None,None,None)
        print("\nMaterial analysis mode exited successfully\n")
    else:
        material_vect=loadMaterial(material_path)
        materialName=None
        Young=None
        Poisson=None
        Raman=None
        Thermal=None
        Comment=None
        flag=0
        for i in range(len(material_vect)):
            if(material_vect[i][0].lower()==material.lower()):
                print("\nGlobal material mode set to: ",material_vect[i][0])
                materialName=material_vect[i][0]
                flag=1
                for j in range(len(material_vect[i])):
                    match material_vect[i][j]:
                        case "(Young)": 
                            Young=material_vect[i][j+1]
                        case "(Poisson)":
                            Poisson=material_vect[i][j+1]
                        case "(Comment)":
                            Comment=material_vect[i][j+1]
                        case "(Raman)":
                            Raman=material_vect[i][j+1]
                        case "(Thermal)":
                            Thermal=material_vect[i][j+1]
                global_material.set_fullMaterial(materialName,Raman,Young,Poisson,Thermal,Comment)
        if(flag==0):
            print("\nMaterial not found. Please check the spelling or the material txt file. Note that the uppercases do not matter\n")
        elif(flag==1):
            print(global_material.get_comment(),"\n")     
            
    

def loadMaterial(material_path):
    file=open(material_path)
    material_vect=[]
    for line in file:
        values=line.split(",")
        material_vect.append(values)
    return material_vect

def showRamanMaterial(material,ax):
    try:
        if(global_material.get_material()!=None):
            Raman=global_material.get_Raman().split()
            xdata=ax.get_lines()[0].get_xdata()
            ydata=ax.get_lines()[0].get_ydata()
            ax.set_ylim(ax.get_ylim())
            for i in range(len(Raman)):
                ytext=ydata[xdata>=float(Raman[i])][0]
                ax.plot(float(Raman[i])*np.ones(2),[ax.get_ylim()[0],ytext],color='k',linestyle=':',alpha=0.5)
                # ax.text(float(Raman[i]),ytext*1.1,'     %d '%(float(Raman[i])),rotation=90,ha="left",va="bottom",alpha=0.5)
            print("Adding spectrum data")
                
        else:
            print("No material data to diplay")
    except:
        print("Adding spectrum data not possible in this context. Skipping ...")
        

