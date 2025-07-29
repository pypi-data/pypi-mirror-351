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





def avg():
    print("\nImportant remark: Might bug with polytec file\n")
    
    
    
    newpath=os.getcwd()+"\\avg_data"+"\\"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    files=glob.glob("*.txt")
    a=len(files)
    current_file=""
    try:

        x=np.zeros(file_length(files[1]))
        y=np.zeros(file_length(files[1]))
        print("Opening and averaging ",len(files)," files")
        for i,fp in enumerate(files): #retourne l'index dans i et retourne le premiere element (T1.txt par exemple) dans fp
            current_file=files[i]
            if(((i+1)%a)==0):
                # print("this is i ",i)
                print(files[i])
                with open(fp) as file:
                    x_temp = []
                    y_temp = []
                    for line in file:
                        values = line.split()
                        x_temp.append(float(values[0]))
                        y_temp.append(float(values[1]))
                    sort=np.argsort(x_temp)
                    x_temp1=[]
                    y_temp1=[]
                    for k in range(len(sort)):
                        x_temp1.append(x_temp[sort[k]])
                        y_temp1.append(y_temp[sort[k]])                        
                    x=np.array(x_temp1)
                    # print("this is Y before sum loop if",y)
                    y=y+np.array(y_temp1)
                    # print("this is y after sum: loop if",y)
                # print("this is what will be plotted x",x)
                y=y/a
                # print("this is what will be plotted y/a",y)
                # ax.plot(x,y/a)
                
                    
              
            else:
                with open(fp) as file:
                    print(files[i],"is used with")
                    x1 = []
                    y1 = []
                    for line in file:
                        values = line.split()
                        x1.append(float(values[0]))
                        y1.append(float(values[1]))
                        
                    sort1=np.argsort(x1)
                    x2=[]
                    y2=[]
                    for k in range(len(sort1)):
                        x2.append(x1[sort1[k]])
                        y2.append(y1[sort1[k]])     
                     
                     
                    # print("this is y before sum loop else",y)
                    y=y+np.array(y2)
                    # print("this is y after loop else:",y)               
        fileName=input("\nPlease provide a file name without the extension:")
        with open (newpath+fileName+".txt",'w') as new_file:
            for k in range(len(x)):
                new_file.write(str(x[k])+" "+str(y[k])+"\n")
        
        print('\n---------------------------------------------------------------\n')        
        pyperclip3.copy("path "+newpath)
        print("\nOperation successful! Created path and path command copied to clipboard. Paste to move DesCar to the created directory\n")

    except:
        print('\n---------------------------------------------------------------')
        print('\nError: Operation was halted. Files probably have different length. Please check your files before proceeding. Operation stopped while working on: ',current_file,'\n')




def colMult(coef):
    try:
        if(coef!=None and coef!=" " and coef!=""):
            cstx,csty=coef.split(",")
            cstx=float(cstx)
            csty=float(csty)
            flag=0
        else:
            cstx,csty=input("Please provide a coef (x,y): ").split(",")
            cstx=float(cstx)
            csty=float(csty)
            flag=0
    except:
        flag=1
    if(flag==0):
        newpath=os.getcwd()+"\\multiplied_data"+"\\"
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        files=glob.glob("*.txt")
        f_list=fileExtensionRemover(glob.glob("*.txt"))
        for i,fp in enumerate(files):
            print("Working on: ",files[i])
            with open(fp) as file:
                x = []
                y = []
                for line in file:
                    values = line.split()
                    x.append(float(values[0]))
                    y.append(float(values[1]))
                for j in range(len(x)):
                    x[j]=x[j]*cstx
                    y[j]=y[j]*csty
            with open (newpath+f_list[i]+".txt",'w') as new_file:
                for k in range(len(x)):
                    new_file.write(str(x[k])+" "+str(y[k])+"\n")
        print('\n---------------------------------------------------------------\n')        
        pyperclip3.copy("path "+newpath)
        print("\nOperation successful! Created path and path command copied to clipboard. Paste to move DesCar to the created directory\n")
    else:
        print("Improper input. Exiting ...")

    


def colAdd(shift):
    try:
        if(shift!=None and shift!=" " and shift!=""):
            cstx,csty=shift.split(",")
            cstx=float(cstx)
            csty=float(csty)
            flag=0

        else:
            cstx,csty=input("Please provide an offset (x,y): ").split(",")
            cstx=float(cstx)
            csty=float(csty)
            flag=0
    
    except:
        flag=1
    if(flag==0):
        newpath=os.getcwd()+"\\shifted_data"+"\\"
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        files=glob.glob("*.txt")
        f_list=fileExtensionRemover(glob.glob("*.txt"))
        for i,fp in enumerate(files):
            print("Working on: ",files[i])
            with open(fp) as file:
                x = []
                y = []
                for line in file:
                    values = line.split()
                    x.append(float(values[0]))
                    y.append(float(values[1]))
                for j in range(len(x)):
                    x[j]=x[j]+cstx
                    y[j]=y[j]+csty
            with open (newpath+f_list[i]+".txt",'w') as new_file:
                for k in range(len(x)):
                    new_file.write(str(x[k])+" "+str(y[k])+"\n")
        print('\n---------------------------------------------------------------\n')        
        pyperclip3.copy("path "+newpath)
        print("\nOperation successful! Created path and path command copied to clipboard. Paste to move DesCar to the created directory\n")
    else:
        print("Improper input. Exiting...")



                
                

def generic_data_cleaner():
    print("\nThis routine allows to output clean dual column xy txt from generic input file. \nPlease describe your file:")
    newpath=os.getcwd()+"\\"
    files=glob.glob("*.txt")
    f_list=fileExtensionRemover(glob.glob("*.txt"))
    flag=0
    try:
        if(cleanset.skipRows==None):
            row=int(input("\nHow many rows to skip: "))
        else:
            row=int(cleanset.skipRows)
        column=[]
        if(cleanset.colName==None):
            column.append(input("\nPlease provide the name of the columns (coma separated): ").split(','))
        else:
            column.append(cleanset.colName.split(','))
        temp=[]
        if(cleanset.colExport==None):
            temp.append(input("\nWhat column combination would you like to export (formating 0+1,0+2, ...): ").split(","))
        else:
            temp.append(cleanset.colExport.split(','))
        export=[]
        for i in range(len(temp[0])):
            export.append(temp[0][i].split('+'))
    except:
        flag=1
        print("\nError in input interpretation. Check input or your general gfClean settings. Exiting ...")
    csv=0
    if(flag==0):
        try:
            print("\nStarting procedure ...\n---------------------------------------------------\n")
            for i,fp in enumerate(files):
                print("Working on ",files[i])
                try:
                    data_str=np.loadtxt(files[i],skiprows=row,comments="END_DB",dtype=str)
                    # data_str=np.loadtxt(files[i],skiprows=row,comments="END_DB",dtype=str,delimiter=',')
                except:
                    print("\n!! Error with !!",files[i],"\n")
                    continue   
                for k in range(len(temp[0])):
                    path=newpath+"("+column[0][int(export[k][0])]+"_"+column[0][int(export[k][1])]+")"
                    if not os.path.exists(path):
                            os.makedirs(path)
                    # with open (newpath+f_list[i]+"_("+column[0][int(export[k][0])]+"_"+column[0][int(export[k][1])]+").txt",'w') as file:
                    with open (path+"\\"+f_list[i]+"_("+column[0][int(export[k][0])]+"_"+column[0][int(export[k][1])]+")"+".txt",'w') as file:
                        for j in range(len(data_str[:,0])):
                            file.write(data_str[j,int(export[k][0])].replace(',','.')+" "+data_str[j,int(export[k][1])].replace(',','.')+"\n")
        except:
            print("\n---------------------------------------\n")
            print("\nError in main txt decoding loop. Trying csv decoding.\n")
            csv=1
        if(csv==1):
            try:
                print("\nStarting csv backup procedure ...\n---------------------------------------------------\n")
                for i,fp in enumerate(files):
                    print("Working on ",files[i])
                    try:
                        # data_str=np.loadtxt(files[i],skiprows=row,comments="END_DB",dtype=str)
                        data_str=np.loadtxt(files[i],skiprows=row,comments="END_DB",dtype=str,delimiter=',')
                    except:
                        print("\n!! Error with !!",files[i],"\n")
                        continue   
                    for k in range(len(temp[0])):
                        path=newpath+"("+column[0][int(export[k][0])]+"_"+column[0][int(export[k][1])]+")"
                        if not os.path.exists(path):
                                os.makedirs(path)
                        # with open (newpath+f_list[i]+"_("+column[0][int(export[k][0])]+"_"+column[0][int(export[k][1])]+").txt",'w') as file:
                        with open (path+"\\"+f_list[i]+"_("+column[0][int(export[k][0])]+"_"+column[0][int(export[k][1])]+")"+".txt",'w') as file:
                            for j in range(len(data_str[:,0])):
                                file.write(data_str[j,int(export[k][0])].replace(',','.')+" "+data_str[j,int(export[k][1])].replace(',','.')+"\n")
            except:
                print("\n---------------------------------------\n")
                print("\nDecoding failed. Exiting ...\n")
                flag=1
    if(flag==0): 
        print('\n---------------------------------------------------------------\n')        
        print("\nOperation successful!\n")
                
            

class Clean:

        def __init__(self):
            self.skipRows=None
            self.colExport=None
            self.colName=None
        
        def set_colName(self,colName):
            self.colName=colName
        
        def get_colName(self):
            return self.colName
            
        def set_colExport(self,colExport):
            self.colExport=colExport
        
        def get_colExport(self):
            return self.colExport
            
        def set_skipRows(self,skipRows):
            self.skipRows=skipRows
            
        def get_skipRows(self):
            return self.skipRows
            
        def clear(self):
            self.skipRows=None
            self.colExport=None
            self.colName=None
            
cleanset=Clean()

def col_export(col_export):
    if(col_export==''):
        a=input("\nWhat column combination would you like to export (formating 0+1,0+2, ...): ")
        cleanset.set_colExport(a)
        print("Exported column set to: ",a,"\n")
    else:
        cleanset.set_colExport(col_export)
        print("Exported column set to: ",col_export,"\n")
      
def col_name(col_name):
    if(col_name==''):
        a=input("\nPlease provide the name of the columns (coma separated): ")
        cleanset.set_colName(a)
        print("Col name set to: ",a,"\n")
    else:
        cleanset.set_colName(col_name)
        print("Col names set to: ",col_name,"\n")
        
        
def skip_row(skip):
    if(skip==''):
        a=input("\nNumber of rows to skip: ")
        cleanset.set_skipRows(a)
        print("Skip set to: ",a,"\n")
    else:
        cleanset.set_skipRows(skip)
        print("Skip set to: ",skip,"\n")
        
def gfClear():
    cleanset.clear()
    print("\nGeneral file clean settings cleared succesfully !\n")
        
    