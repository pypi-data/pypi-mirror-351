from filePath import * 
import cmd #cmd in small letters is the name of the module. do cmd.Cmd.any_function() to run a function from the class from the module
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import glob
from plotRaman import  *
import os
import numpy as np
from material import *
import pyperclip3

########################################
#       Nicolas Roisin
#

mpl.rcParams['font.family']='serif'
# cmfont = font_manager.FontProperties(fname=mpl.get_data_path() + '/fonts/ttf/cmr10.ttf')
# mpl.rcParams['font.serif']=cmfont.get_name()
# mpl.rcParams['mathtext.fontset']='cm'
mpl.rcParams['axes.unicode_minus']=False
# mpl.rcParams['lines.marker']="o"
# mpl.rcParams['lines.linestyle']="-"
# mpl.rcParams['lines.markeredgecolor']="k"
# mpl.rcParams['lines.markersize']=3.5
# mpl.rcParams['lines.alpha']=0.5

SMALL_SIZE = 10
MEDIUM_SIZE = 13
BIGGER_SIZE = 15
plt.rcParams["font.family"] = "serif"
plt.rcParams["mathtext.rm"] = "serif"
plt.rcParams["mathtext.it"] = "serif"
plt.rcParams["mathtext.sf"] = "serif"
plt.rcParams["mathtext.fontset"] = "dejavuserif"
plt.rc('font', size=MEDIUM_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
#plt.rc('font', weight="normal")    # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=MEDIUM_SIZE)  # fontsize of the figure title 

#
#       Nicolas Roisin
########################################
 




def plot(plotT,save_dir):
    if(plotT!=""):
        if(plotT=="select"):
            plot_select(save_dir)
        elif(plotT=="all"):
            plot_all(save_dir)
        elif(plotT=="rifle"):
            plot_rifle(save_dir)
    else:
        print("welcome to the generic plot tool of DesCar. This wizard allows you to plot one or more curves on one plot. Avalaible commands include: \n-rifle: plot every file in the folder separatly\n-all: plot all file in the folder on the same plot\n-select: plot a selection of file in the folder on the same plot")
        a=input("Do you want to plot a selection of files or all files in folder. ? (rifle/select/all)")
        if(a=="select"):
            plot_select(save_dir)
        elif(a=="all"):
            plot_all(save_dir)
        elif(a=="rifle"):
            plot_rifle(save_dir)
        else:
            print("Command not recognised. Resuming...")

def plot_rifle(save_dir):
    files=glob.glob("*.txt")
    if(plotstyle.get_style()==None):
        disp=input("\nDisplay type for each curve (separated data points or connected line. Type l, p, f, d, x, lx or lp separated by a coma. Type line, point, fancy, dash, cross, lineCross or linePoint to set a setting for all or Enter to unspecified): ").split(',')
        disp[0]=disp[0].lower()
    else:
        disp=plotstyle.get_style().split()#cheap trick for the code to stay compatible with previous line (legacy)
        disp[0]=disp[0].lower()
    axes = ["",""]
    if(plotstyle.get_x()==None or plotstyle.get_y()==None):
        axes=input("What is the name of the X and Y axes (coma separated x,y): ").split(',')
    else:
        axes=plotstyle.get_x(),plotstyle.get_y()
    for i,fp in enumerate(files):
        print("currently running on: ",files[i])
        fig=plt.figure()
        ax=fig.add_subplot()
        with open(fp) as file:
            x_temp = []
            y_temp = []
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
            try:
                if(disp[0]=="point"):
                    ax.plot(x,y,ls="",marker=".")
                elif(disp[0]=="line"):
                    ax.plot(x,y)
                elif(disp[0]=="fancy"):
                    ax.plot(x,y,ls="-",marker=".",markersize="8",markeredgecolor="k")
                elif(disp[0]=="linepoint"):
                    ax.plot(x,y,ls="-",marker=".") 
                elif(disp[0]=="dash"):
                    ax.plot(x,y,ls='--')
                elif(disp[0]=="cross"):
                    ax.plot(x,y,ls='',marker="x")
                elif(disp[0]=="linecross"):
                    ax.plot(x,y,ls='-',marker="x")
                else:
                    if(disp[i].lower()=="l"):
                        ax.plot(x,y)
                    elif(disp[i].lower()=="p"):
                        ax.plot(x,y,ls="",marker=".")
                    elif(disp[i]=="f"):
                        ax.plot(x,y,ls="-",marker=".",markersize="8",markeredgecolor="k")
                    elif(disp[i]=="lp"):
                        ax.plot(x,y,ls="-",marker=".")
                    elif(disp[i]=="d"):
                        ax.plot(x,y,ls='--')
                    elif(disp[i]=="x"):
                        ax.plot(x,y,ls='',marker="x")
                    elif(disp[0]=="lx"):
                        ax.plot(x,y,ls='-',marker="x")
                    else:
                        print("Display style \"",disp[i],"\" not recognised. Printing \"",files[i],"\" with connected lines")
                        ax.plot(x,y)
            except:
                print("No style detected for \"",files[i],"\" Printing with connected lines")
                ax.plot(x,y)
        try:
            ax.set_xlabel(axes[0])
            ax.set_ylabel(axes[1])
        except:
            print("No X or Y label provided")
            ax.set_xlabel("")
            ax.set_ylabel("")
        titles=fileExtensionRemover(glob.glob("*.txt"))
        ax.set_title(titles[i])
        ax.grid()
        #plt.legend(files[i])
        temp=os.getcwd()
        os.chdir(save_dir)
        showRamanMaterial(global_material.get_material(),ax)
        plt.savefig(titles[i]+".png",format = 'png')
        # plt.savefig(titles[i]+".eps",format = 'eps')
        plt.clf()
        plt.close()
        os.chdir(temp)
        






    
def plot_select(save_dir):
    print("Type the name of a file with or without the .txt or the name of multiple files separated with a coma")
    trf=fileExtension((input("What file do you wanna plot today ?  ")).split(','))
    if(inFolder(trf)!=1):
        print("Missing files: Exiting")
    else:
        if(plotstyle.get_style()==None):
            disp=input("\nDisplay type for each curve (separated data points or connected line. Type l, p, f, d, x, lx or lp separated by a coma. Type line, point, fancy, dash, cross, lineCross or linePoint to set a setting for all Enter to unspecified): ").split(',')
            disp[0]=disp[0].lower()
        else:
            disp=plotstyle.get_style().split()#cheap trick for the code to stay compatible with previous line (legacy)
            disp[0]=disp[0].lower()
    
        if(plotstyle.get_title()==None):
            title=input("What title should we give to the plot  ? ") 
        else:
            title=plotstyle.get_title()   
        axes = ["",""]
        if(plotstyle.get_x()==None or plotstyle.get_y()==None):
            axes=input("What is the name of the X and Y axes (coma separated x,y): ").split(',')
        else:
            axes=plotstyle.get_x(),plotstyle.get_y()
        fig=plt.figure()
        ax=fig.add_subplot()
        for i,fp in enumerate(trf):
            with open(fp) as file:
                x_temp = []
                y_temp = []
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
                try:
                    if(disp[0]=="point"):
                        ax.plot(x,y,ls="",marker=".")
                    elif(disp[0]=="line"):
                        ax.plot(x,y)
                    elif(disp[0]=="fancy"):
                        ax.plot(x,y,ls="-",marker=".",markersize="8",markeredgecolor="k")
                    elif(disp[0]=="linepoint"):
                        ax.plot(x,y,ls="-",marker=".")  
                    elif(disp[0]=="dash"):
                        ax.plot(x,y,ls='--')      
                    elif(disp[0]=="linecross"):
                        ax.plot(x,y,ls='-',marker="x")  
                    elif(disp[0]=="cross"):
                        ax.plot(x,y,ls='',marker="x")                        
                    else:
                        if(disp[i].lower()=="l"):
                            ax.plot(x,y)
                        elif(disp[i].lower()=="p"):
                            ax.plot(x,y,ls="",marker=".")
                        elif(disp[i]=="f"):
                            ax.plot(x,y,ls="-",marker=".",markersize="8",markeredgecolor="k")
                        elif(disp[i]=="lp"):
                            ax.plot(x,y,ls="-",marker=".")
                        elif(disp[i]=="d"):
                            ax.plot(x,y,ls='--')
                        elif(disp[i]=="x"):
                            ax.plot(x,y,ls='',marker="x")
                        elif(disp[i]=="lx"):
                            ax.plot(x,y,ls='-',marker="x")
                        else:
                            print("\nDisplay style \"",disp[i],"\" not recognised. Printing \"",trf[i],"\" with connected lines\n")
                            ax.plot(x,y)
                except:
                    print("\nNo style detected for \"",trf[i],"\" Printing with connected lines\n")
                    ax.plot(x,y)
        try:
            ax.set_xlabel(axes[0])
            ax.set_ylabel(axes[1])
        except:
            print("No X or Y label provided")
            ax.set_xlabel("")
            ax.set_ylabel("")
        ax.set_title(title)
        ax.grid()
        lgd=legend(trf)
        if(lgd!=['']):
            ax.legend(lgd)
        temp=os.getcwd()
        os.chdir(save_dir)
        showRamanMaterial(global_material.get_material(),ax)
        plt.savefig(title+".png",format = 'png')
        # plt.savefig(title+".eps",format = 'eps')
        plt.show()
        plt.clf()
        plt.close()
        os.chdir(temp)
 
 
 
def plot_all(save_dir):
    print("This wizard allows you to plot all the files in the folder.")
    files=glob.glob("*.txt")
    print("\nRoutine will work in the following order:\n")
    for l in range(len(files)):
        print(files[l]) 
    if(plotstyle.get_style()==None):
        disp=input("\nDisplay type for each curve (separated data points or connected line. Type l, p, f, lp, x, lx or d separated by a coma. Type line, point, fancy, linePoint, cross, lineCross or dash to set a setting for all.\nEntry or Enter to unspecified): ").split(',')
        disp[0]=disp[0].lower()
    else:
        disp=plotstyle.get_style().split()#cheap trick for the code to stay compatible with previous line (legacy)
        disp[0]=disp[0].lower()

    if(plotstyle.get_title()==None):
        title=input("What title should we give to the plot  ? ") 
    else:
        title=plotstyle.get_title()   
    axes = ["",""]
    if(plotstyle.get_x()==None or plotstyle.get_y()==None):
        axes=input("What is the name of the X and Y axes (coma separated x,y): ").split(',')
    else:
        axes=plotstyle.get_x(),plotstyle.get_y()
    auto_lgd=''
    fig=plt.figure()
    ax=fig.add_subplot()
    for i,fp in enumerate(files): #retourne l'index dans i et retourne le premiere element (T1.txt par exemple) dans fp
        print("currently running on: ",files[i])
        with open(fp) as file:
            auto_lgd=auto_lgd+","+fp
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
        try:
            if(disp[0]=="point"):
                ax.plot(x,y,ls="",marker=".")
            elif(disp[0]=="line"):
                ax.plot(x,y)
            elif(disp[0]=="fancy"):
                ax.plot(x,y,ls="-",marker=".",markersize="8",markeredgecolor="k")
            elif(disp[0]=="linepoint"):
                ax.plot(x,y,ls="-",marker=".")  
            elif(disp[0]=="dash"):
                ax.plot(x,y,ls='--')
            elif(disp[0]=="cross"):
                ax.plot(x,y,ls='',marker="x")
            elif(disp[0]=="linecross"):
                ax.plot(x,y,ls='-',marker="x")
            else:
                if(disp[i].lower()=="l"):
                    ax.plot(x,y)
                elif(disp[i].lower()=="p"):
                    ax.plot(x,y,ls="",marker=".")
                elif(disp[i]=="f"):
                    ax.plot(x,y,ls="-",marker=".",markersize="8",markeredgecolor="k")
                elif(disp[i]=="lp"):
                    ax.plot(x,y,ls="-",marker=".")
                elif(disp[i]=="d"):
                    ax.plot(x,y,ls='--')
                elif(disp[i]=="x"):
                    ax.plot(x,y,ls='',marker="x")
                elif(disp[i]=="lx"):
                    ax.plot(x,y,ls='-',marker="x")
                else:
                    print("\nDisplay style \"",disp[i],"\" not recognised. Printing \"",files[i],"\" with connected lines\n")
                    ax.plot(x,y)
        except:
            print("\nNo style detected for \"",files[i],"\" Printing with connected lines\n")
            ax.plot(x,y)  
    try:
        ax.set_xlabel(axes[0])
        ax.set_ylabel(axes[1])
    except:
        print("No X or Y label provided")
        ax.set_xlabel("")
        ax.set_ylabel("")
    ax.set_title(title) 
    ax.grid()
    lgd=legend(auto_lgd.split(",")[1:])    
    if(lgd!=['']):
        ax.legend(lgd)
    temp=os.getcwd()
    os.chdir(save_dir)
    showRamanMaterial(global_material.get_material(),ax)
    plt.savefig(title+".png",format = 'png')
    # plt.savefig(title+".eps",format = 'eps')
    plt.show()
    plt.clf()
    plt.close()
    os.chdir(temp)
                    
 
 



class Plot:

    def __init__(self):
            self.x=None
            self.y=None
            self.title=None
            self.legend=None
            self.style=None
            self.lgd=None
    
    def set_title(self,title):
        self.title=title
        
    def set_x(self,x):
        self.x=x

    def set_y(self,y):
        self.y=y
    
    def set_style(self,style):
        self.style=style
        
    def clear(self):
        self.x=None
        self.y=None
        self.title=None
        self.legend=None
        self.style=None
        self.lgd=None
        
    def get_style(self):
        return self.style
           
    def get_x(self):
        return self.x

    def get_y(self):
        return self.y
    
    def get_title(self):
        return self.title
    
    # def set_lgd(self,lgd):
        # self.lgd=lgd


plotstyle=Plot()


def write_plot_config(plot_config,descar_path):
    with open(descar_path+"\\plot_config.txt",w) as file:
        file.write(plot_config)
        




# def plot_lgd(lgd):
    # if(lgd==""):
        # a=input("\nWhat general lgd do you want to use: ")
        # if(a.lower()=="fancy" or a.lower()=="linepoint" or a.lower()=="line" or a.lower()=="point"):
            # plotstyle.set_lgd(a)
            # print("\nGeneral lgd set to: ",a,"\n")
        # else:
            # print("\nlgd not supported by plot general settings. Exiting ...")
    # else:
        # if(lgd.lower()=="fancy" or lgd.lower()=="linepoint" or lgd.lower()=="line" or lgd.lower()=="point"):
            # plotstyle.set_lgd(lgd)
            # print("\nGeneral lgd set to: ",lgd,"\n")
        # else:
            # print("\nlgd not supported by plot general settings. Exiting ...")

def plot_style(style,descar_path):
    if(style==""):
        a=input("\nWhat general style do you want to use: ")
        if(a.lower()=="fancy" or a.lower()=="linepoint" or a.lower()=="line" or a.lower()=="point" or a.lower()=="dash" or a.lower()=="cross" or a.lower()=="linecross"):
            plotstyle.set_style(a)
            plot_config=np.genfromtxt(descar_path+"\\plot_config.txt",delimiter=',',dtype='str')
            style=a.lower()
            title=plot_config[1]
            x=plot_config[2]
            y=plot_config[3]
            with open(descar_path+"\\plot_config.txt",'w') as file:
                file.write(style+','+title+','+x+','+y)
            print("\nGeneral style set to: ",a,"\n")
            
        else:
            print("\nStyle not supported by plot general settings. Exiting ...")
    else:
        if(style.lower()=="fancy" or style.lower()=="linepoint" or style.lower()=="line" or style.lower()=="point" or style.lower()=="dash" or style.lower()=="cross" or style.lower()=="linecross"):
            plotstyle.set_style(style)
            plot_config=np.genfromtxt(descar_path+"\\plot_config.txt",delimiter=',',dtype='str')
            style=style.lower()
            title=plot_config[1]
            x=plot_config[2]
            y=plot_config[3]
            with open(descar_path+"\\plot_config.txt",'w') as file:
                file.write(style+','+title+','+x+','+y)
            print("\nGeneral style set to: ",style,"\n")
        else:
            print("\nStyle not supported by plot general settings. Exiting ...")
        
        
def plot_x(x,descar_path):
    if(x==""):
        a=input("\nWhat general x axis text do you want to use: ")
        plotstyle.set_x(a)
        print("x axis text set to: ",a,"\n")
        plot_config=np.genfromtxt(descar_path+"\\plot_config.txt",delimiter=',',dtype='str')
        style=plot_config[0]
        title=plot_config[1]
        x=a
        y=plot_config[3]
        with open(descar_path+"\\plot_config.txt",'w') as file:
            file.write(style+','+title+','+x+','+y)
    else:
        plotstyle.set_x(x)
        print("x axis text set to: ",x,"\n")
        plot_config=np.genfromtxt(descar_path+"\\plot_config.txt",delimiter=',',dtype='str')
        style=plot_config[0]
        title=plot_config[1]
        x=x
        y=plot_config[3]
        with open(descar_path+"\\plot_config.txt",'w') as file:
            file.write(style+','+title+','+x+','+y)
    

def plot_y(y,descar_path):
    if(y==""):
        a=input("\nWhat general y axis text do you want to use: ")
        plotstyle.set_y(a)
        print("y axis text set to: ",a,"\n")
        plot_config=np.genfromtxt(descar_path+"\\plot_config.txt",delimiter=',',dtype='str')
        style=plot_config[0]
        title=plot_config[1]
        x=plot_config[2]
        y=a
        with open(descar_path+"\\plot_config.txt",'w') as file:
            file.write(style+','+title+','+x+','+y)
    else:
        plotstyle.set_y(y)
        print("y axis text set to: ",y,"\n")
        plot_config=np.genfromtxt(descar_path+"\\plot_config.txt",delimiter=',',dtype='str')
        style=plot_config[0]
        title=plot_config[1]
        x=plot_config[2]
        y=y
        with open(descar_path+"\\plot_config.txt",'w') as file:
            file.write(style+','+title+','+x+','+y)
          
    
def plot_title(title,descar_path):
    if(title==""):
        a=input("\nWhat title do you want to give to all the upcoming plots: ")
        plotstyle.set_title(a)
        print("Title set to: ",a)
        plot_config=np.genfromtxt(descar_path+"\\plot_config.txt",delimiter=',',dtype='str')
        style=plot_config[0]
        title=a
        x=plot_config[2]
        y=plot_config[3]
        with open(descar_path+"\\plot_config.txt",'w') as file:
            file.write(style+','+title+','+x+','+y)
    else:
        plotstyle.set_title(title)
        print("Title set to: ",title,"\n")
        plot_config=np.genfromtxt(descar_path+"\\plot_config.txt",delimiter=',',dtype='str')
        style=plot_config[0]
        title=title
        x=plot_config[2]
        y=plot_config[3]
        with open(descar_path+"\\plot_config.txt",'w') as file:
            file.write(style+','+title+','+x+','+y)
    

def plot_clear(descar_path):
    plotstyle.clear()
    print("\nGeneral plot style cleared succesfully !\n")
    plot_config=np.genfromtxt(descar_path+"\\plot_config.txt",delimiter=',',dtype='str')
    style=''
    title=''
    x=''
    y=''
    with open(descar_path+"\\plot_config.txt",'w') as file:
        file.write(style+','+title+','+x+','+y)
