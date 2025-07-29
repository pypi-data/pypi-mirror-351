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







def thermalStress(Ef,Vf,alpha_f,alpha_s,high,low):
    return ((Ef*(10**9))/(1-Vf))*(alpha_f-alpha_s)*(10**-6)*(high-low)
    
def diffStoney(Es,Vs,ts,tf,dp):
    return ((Es*(10**9))/(6*(1-Vs)))*(((ts*(10**-9))**2)/(tf*(10**-9)))*dp
    
    
def thermalStessWiz(save_dir):
    print("\nThis wizard allows you to compute the theoretical thermal stress induced by the thermal expansion coefficient mismatch. \nNote that the actual value is VERY process dependant. This estimation does not replace proper experimental data !. \nIf you use a polymer as thin film please mind the relaxation.")
    print("\n--------------------------------------------------")
    print("Here are some common values for silicon:")
    print("Young modulus of silicon: Isotropic and linearly elastic (165 GPa), <100> (180-200 GPa). \n Consider that it is function of the crystal, doping, ... please chose the value that suits your specific needs. \n In general:Young's modulus = [62,202]GPa (https://www.memsnet.org/material/siliconsibulk/)")
    print("Thermal expansion of silicon: 2.6 ppm (Franssila)")
    print("Poisson ratio of silicon: 0.27 [-] (Franssila). Varies between 0.22 and 0.278. Check for your specific case!")
    print("\n--------------------------------------------------")
    a=input("Do you want to use silicon as your substrate ? (yes/no):")
    if(a=='yes' or a=='y'):
        print("The thermal expansion coef for the substrate will be of 2.6 ppm")
        alpha_f=float(input("What is the thermal expansion coefficient of your thin film [ppm]: "))
        Ef=float(input("What is the young's modulus of your thin film [GPa]: "))
        Vf=float(input("What is the poisson ratio of your material [-]: "))
        high=float(input("What is high temperature [°C]: "))
        low=float(input("What is room temperature [°C]: "))
        name=input("What is the name of your thin film: ")
        sigma=thermalStress(Ef,Vf,alpha_f,2.6,high,low)*(10**-6)
        print("A thin film of ",name," on silicon will generate a thermal stress of ",round(sigma,3)," MPa")
        b=input("Do you want to save this result as .txt ? (yes/no): ")
        if(b=="yes" or b=="y"):
            c=input("Do you want to add a comment ? (enter if not): ")
            temp=os.getcwd()
            os.chdir(save_dir)
            with open (os.getcwd()+"\\"+name+" on silicon.txt",'w') as file:
                file.write("A thin film of "+name+" on a silicon substrate will generate a thermal stress of "+str(round(sigma,3))+" MPa. The parameters used are: \nThermal expansion of silicon: 2.6 [ppm]\nThermal expansion of "+name+": "+str(alpha_f)+" [ppm]\nYoung's Modulus of "+name+": "+str(Ef)+" [GPa]\nPoisson ratio of "+name+": "+str(Vf)+"  [-]\nHigh and low temp of "+name+": "+str(high)+" and "+str(low)+" [°C]"+"\nComment: "+c)
            os.chdir(temp)    
    else:
        if(a=="no" or a=="n"):
            name_s=input("What is the name of your substrate: ")
            alpha_s= float(input("What is the thermal expansion coefficient of "+name_s+" [ppm]: "))
            name=input("What is the name of your thin film: ")
            alpha_f=float(input("What is the thermal expansion coefficient of your thin film [ppm]: "))
            Ef=float(input("What is the young's modulus of your thin film [GPa]: "))
            Vf=float(input("What is the poisson ratio of your material [-]: "))
            high=float(input("What is high temperature [°C]: "))
            low=float(input("What is room temperature [°C]: "))           
            sigma=thermalStress(Ef,Vf,alpha_f,alpha_s,high,low)*(10**-6)
            print("A thin film of ",name," on ",name_s," will generate a thermal stress of ",round(sigma,3)," MPa")
            b=input("Do you want to save this result as .txt ? (yes/no): ")
            if(b=="yes" or b=="y"):
                c=input("Do you want to add a comment ? (enter if not): ")
                temp=os.getcwd()
                os.chdir(save_dir)
                with open (os.getcwd()+"\\"+name+" on silicon.txt",'w') as file:
                    file.write("A thin film of "+name+" on a ",name_s," substrate will generate a thermal stress of "+str(round(sigma,3))+" MPa. The parameters used are: \nThermal expansion of ",name_s," : ",alpha_s," [ppm]\nThermal expansion of "+name+": "+str(alpha_f)+" [ppm]\nYoung's Modulus of "+name+": "+str(Ef)+" [GPa]\nPoisson ratio of "+name+": "+str(Vf)+"  [-]\nHigh and low temp of "+name+": "+str(high)+" and "+str(low)+" [°C]"+"\nComment: "+c)
                    os.chdir(temp)
        else:
            print("Command not recognised. Exiting...")
    return sigma        
           
def stressCompensation(save_dir):
    print("")
    print("This wizard helps you to compensate the thermal stresses in a two layers stack. \nBE CAREFUL with the numbers given by this assistant ! This code relies on a first order estimation of the required thichnesses based on the Stoney Formula.\nThe provided estimation DO NOT replace the need to properly simulate the exact stack geometry.")
    print("\n--------------------------------------------------")
    name_1=input("The first layer in the stack is: ")
    name_2=input("The second layer in the stack is: ")
    param=input("Which quantity do you need to estimate: t_1,t_2,sigma_1,sigma_2 (type 1, 2, 3 or 4):")
    if(param=="1"):
        sigma_1=(input("Residual stresses of "+name_1+" in [MPa]. Press enter without entries if you do not know) [MPa]: "))
        if(sigma_1==""):
            sigma_1=thermalStessWiz()
        sigma_1=float(sigma_1)
        t2=float(input("What is the thickness of "+name_2+" [nm]: "))
        sigma_2=(input("Residual stresses of "+name_2+" in [MPa]. Press enter without entries if you do not know) [MPa]: "))
        if(sigma_2==""):
            sigma_2=thermalStessWiz()
        sigma_2=float(sigma_2)
        t1=t2*(sigma_2/sigma_1)
        print("To compensate ",t2," [nm] of a ",sigma_2," [MPa] layer of  ",name_2," you will need ",t1," [nm] of a",sigma_1," [MPa] layer of",name_1 )
    elif(param=="2"):
        sigma_1=(input("Residual stresses of "+name_1+" in [MPa]. (Press enter without entries if you do not know) [MPa]: "))
        if(sigma_1==""):
            sigma_1=thermalStessWiz()
        sigma_1=float(sigma_1)
        t1=float(input("What is the thickness of "+name_1+" [nm]: "))
        sigma_2=(input("Residual stresses of "+name_2+" in [MPa]. (Press enter without entries if you do not know) [MPa]: "))
        if(sigma_2==""):
            sigma_2=thermalStessWiz()
        sigma_2=float(sigma_2)
        t2=t1*(sigma_1/sigma_2)
        print("To compensate ",t1," [nm] of a ",sigma_1," [MPa] layer of  ",name_1," you will need ",t2," [nm] of a",sigma_2," [MPa] layer of",name_2 )
    elif(param=="3"):
        t1=float(input("What is the thickness of "+name_1+" [nm]: "))
        t2=float(input("What is the thickness of "+name_2+" [nm]: "))
        sigma_2=(input("Residual stresses of "+name_2+" in [MPa]. (Press enter without entries if you do not know) [MPa]: "))
        if(sigma_2==""):
            sigma_2=thermalStessWiz()
        sigma_2=float(sigma_2)
        sigma_1=sigma_2*(t2/t1)
        print("To compensate ",t2," [nm] of a ",sigma_2," [MPa] layer of  ",name_2," you will need ",t1," [nm] of a",sigma_1," [MPa] layer of",name_1 )
    elif(param=="4"):
        t1=float(input("What is the thickness of "+name_1+" [nm]: "))
        t2=float(input("What is the thickness of "+name_2+" [nm]: "))
        sigma_1=(input("Residual stresses of "+name_2+" in [MPa]. (Press enter without entries if you do not know) [MPa]: "))
        if(sigma_1==""):
            sigma_1=thermalStessWiz()
        sigma_1=float(sigma_1)
        sigma_2=sigma_1*(t1/t2)
        print("To compensate ",t1," [nm] of a ",sigma_1," [MPa] layer of  ",name_1," you will need ",t2," [nm] of a",sigma_2," [MPa] layer of",name_2 )
    else:
        print("Command not recognised. Exiting...")
    a=input("Do you want to save this result as a .txt ? (yes/no): ")
    c=input("Do you want to add a comment ? (enter if not): ")
    if(a=="yes" or a=="y"):
        temp=os.getcwd()
        os.chdir(save_dir)
        with open (os.getcwd()+"\\Compensation of "+name_2+" on "+name_1+".txt",'w') as file:
            file.write("To compensate "+str(round(t1))+" [nm] of a "+str(round(sigma_1,3))+" [MPa] layer of  "+name_1+" you will need "+str(round(t2))+" [nm] of a "+str(round(sigma_2,3))+" [MPa] layer of "+name_2+"\nComment: "+c)
        os.chdir(temp)
    
    
    
    
 
 
 
def derivative_stoney(save_dir):
    
    newpath=os.getcwd()+"\\Stoney_report"+"\\"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    
    if(global_material.get_material()!=None):
        print("\nGlobal material mode set to: ",global_material.get_material(),"! Using it as reference substrate")
        material=global_material.get_material()
        young=global_material.get_young()
        poisson=global_material.get_poisson()
        print("Substrate set to: ",material)
        print("Poisson ratio set to: ",poisson," [-]")
        print("Young modulus set to: ",young," [GPa]\n")
    else:
        material=input("\nWhat material do you want to use as substrate: ")
        young=input("Provide the young modulus of the material [GPa]: ")
        poisson=input("Provide the poisson's ration of the material [-]: ")
    

    
    
    flag=0
    thermal_stress=[]
    temp=os.getcwd() 
    try:
        while(flag==0):
            if(input("\nPlease put the dektak measurement in folders with the following name convention:\n-Position in the stack (0 for substrate)_Name of the last layer in the stack _ thickness in nm =>0_silicon_380000,1_sio2_514 for example\n-No float input fot the thicknesses\n\n=>Enter once done")==""):
                flag=1
                folders=glob.glob("*")
                folders.remove("Stoney_report")
                position=[]
                layer_temp=[]
                thick_temp=[]
                for i in range(len(folders)):
                    values=folders[i].split("_")     
                    position.append(values[0])
                    layer_temp.append(values[1])
                    thick_temp.append(values[2])
                
                stack=np.argsort(position)
                layer=[]
                thick=[]
                for i in range(len(stack)):
                    layer.append(layer_temp[stack[i]])
                    thick.append(thick_temp[stack[i]])
                print("\nDetected stack:\n-Layer 0 (substrate): ",layer[0]," with a thickness of ",thick[0]," nm\n-Layer 1 (thin film): ",layer[1]," with a thickness of ",thick[1]," nm\n")
            else:
                print("Invalid command! Resuming ...")


        layer0_path=temp+"\\"+str(stack[0])+"_"+str(layer[0])+"_"+str(thick[0])+"\\"
        layer1_path=temp+"\\"+str(stack[1])+"_"+str(layer[1])+"_"+str(thick[1])+"\\"
        os.chdir(layer0_path)
        files0=glob.glob("*.txt")
        nbre=len(files0)
        os.chdir(layer1_path)
        files1=glob.glob("*.txt")


        
        for i in range(nbre):
            fig=plt.figure()
            ax=fig.add_subplot()
            x1=[]
            y1=[]
            x0=[]
            y0=[]
            x=[]
            y=[]
            os.chdir(layer1_path)
            with open(files1[i]) as file:
                for line in file:
                    values=line.split()
                    x1.append(float(values[0])*(10**-6))
                    y1.append(float(values[1])*(10**-9))
            os.chdir(layer0_path)
            with open(files0[i]) as file:
                for line in file:
                    values=line.split()
                    x0.append(float(values[0])*(10**-6))
                    y0.append(float(values[1])*(10**-9))
            for j in range(len(x0)):
                x.append(x1[j])
                y.append(y1[j]-y0[j])

            # fig=plt.figure()
            # ax=fig.add_subplot()
            # ax.plot(x,y)
            # ax.plot(x,y1)
            # ax.plot(x,y0)
            # plt.show()
            
            Coef_1=np.polyfit(x,y,2)
            F1=np.poly1d(Coef_1)
            F2=np.polyder(F1,2)
            # print(thick[0])
            # print(thick[1])
            # print(F2[0])

            
        
            # thermal_stress=round((-1)*((float(young)*(10**9)*(float(thick[0])*(10**(-9)))**2)/(6*(1-float(poisson))*(float(thick[1])*(10**(-9)))))*float(F2[0]),2) #les floats sont moches mais what you gonna do
            # youngf=float(young)
            # poissonf=float(poisson)
            # thickf=float(thick[1])
            # thicks=float(thick[0])
            # dp=float(F2[0])
            # thermal_stress=diffStoney(youngf,poissonf,thicks,thickf,dp)
            thermal_stress.append(round(diffStoney(float(young),float(poisson),float(thick[0]),float(thick[1]),float(F2[0])),2))
            
            print("The thermal stresses in the top ",layer[1]," layer of ",files0[i]," are estimated to be around: ",str(thermal_stress[i]*10**-6)," MPa")

            ax.plot(x,y)
            ax.plot(x,F1(x))
            titles=fileExtensionRemover(glob.glob("*.txt"))  
            ax.set_title(titles[i])
            tempi=os.getcwd()
            os.chdir(newpath)
            plt.savefig(titles[i]+".png",format = 'png')
            plt.clf()
            plt.close()
            os.chdir(tempi)

        try:
            tempi=os.getcwd()
            os.chdir(newpath)
            with open (os.getcwd()+"\\Stoney_report.txt",'w') as file:
                for i in range(nbre):
                    file.write("-The thermal stresses in the top "+layer[1]+" layer of "+files0[i]+" are estimated to be around: "+str(thermal_stress[i]*10**-6)+" MPa\n")
                file.write("\n\n\n=>Parameters of substrate:\n\n-Material: "+str(material)+"\n-Young: "+str(young)+"[GPa]\n-Poisson: "+str(poisson)+" [-]")
            os.chdir(tempi)
        except:
            print("\n-------------------------------------------------------------\n")
            print("\nError in data export loop. \n\n=>Exiting ...\n\n")
        os.chdir(temp)
        
    except:
        print("\n-------------------------------------------------------------\n")
        print("Error in file path managment or in the main loop execution. Check the following:\n\n-The name convention of the dektak measurement folder as specified above\n-The extension .txt of measurement file. Not .csv. Use the extension command to convert your csv to txt\n-Did you clean the raw dektak file ? Use the dektakClean or gfc command to do so.\n\n=>Exiting ...\n")
        os.chdir(temp)

        
        


