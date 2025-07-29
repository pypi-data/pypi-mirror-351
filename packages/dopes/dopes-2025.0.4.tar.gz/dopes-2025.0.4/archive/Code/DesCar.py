import cmd #cmd in small letters is the name of the module. do cmd.Cmd.any_function() to run a function from the class from the module
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import glob
from plotRaman import  *
import os
from filePath import *
from siliconPeakRemover import *
from StressEstimation import *
#from stringSeparation import *
from Intro import*
from material import *
from plotPolytek import *
from interpolate import *
from plotGeneral import *
from comsol import *
from basicDataModifier import *
from Dektak import*
from extractionIV import *



class Plot(cmd.Cmd):

    prompt='DesCar>'
    
    
    
    def __init__(self):
        super().__init__()
        self.material_path=os.getcwd()+"\material_data.txt"
        self.descar_path=os.getcwd()
        
        plot_config=np.genfromtxt(os.getcwd()+"\\plot_config.txt",delimiter=',',dtype='str')
        print(plot_config)
        
        try:
            while(1):
                print("\nWelcome to DesCar ! \n----------------------------------------------\nSaved configuration: ")
                with open(self.descar_path+"\\boot.txt","r") as file:
                        fpi,spi=file.readlines()[0].split(',')
                print("-File path: "+fpi)
                print("-Save path: "+spi)
                print("-Plot style: "+plot_config[0])
                print("-Plot title: "+plot_config[1])
                print("-Plot x: "+plot_config[2])
                print("-Plot y: "+plot_config[3])
                start_path=input("\n(Enter) to keep the configuration or (1) to edit: ")
                if(start_path==""):
                    with open(self.descar_path+"\\boot.txt","r") as file:
                        fpi,spi=file.readlines()[0].split(',')
                        self.file_dir=fpi
                        self.save_dir=spi
                        plot_style(plot_config[0],self.descar_path)
                        plot_title(plot_config[1],self.descar_path)
                        plot_x(plot_config[2],self.descar_path)
                        plot_y(plot_config[3],self.descar_path)
                        break
                if(start_path=="1"):
                    self.file_dir=input('File path: ')
                    self.save_dir=input('Save path: ')
                    print("\nClearing plot settings. Please set in session.")
                    plot_clear(self.descar_path)
                    break
                else:
                    print("Command not recognised. Resuming ...")

        
            if not os.path.exists(self.file_dir):
                raise Exception("file dir does not exists")
            if not os.path.exists(self.save_dir):
                raise Exception("save dir does not exists")
        
        except:
            print("\nBoot file corrupted or path does not exist. Please enter path now: \n")
            self.file_dir=input('\nFile path: ')
            self.save_dir=input('\nSave path: ')

        
        complete_file_path(self.file_dir,self.descar_path)
        complete_save_path(self.save_dir,self.save_dir,self.descar_path)
        
        intro()
    
    
    

    def do_getDir(self,nul):
        'Returns the current source directory. Should not be used. Please use filePath instead'
        self.nul=nul
        print("The current working directory is: " , os.getcwd())
    # def do_raman(self,plotT):
        # 'Allows you to plot raman files.\n-Type raman to launch the wizard\n-Type raman rifle to automatically plot every file in the folder individually (one file per plot)\n-Type raman select to plot a selection of file\n-Type raman all to plot all files on a single plot '
        # self.plotT=plotT
        # plot_raman(plotT,self.save_dir)
        
        
    def do_filePath(self,fp):
        'filePath without argument: gives you the current file path and the ability to upgrade it. filePath + argument changes the file path to the argument after automatically correcting it. No need to worry for the \. Syntax: filePath or filePath something. returns the filePath'
        complete_file_path(fp,self.descar_path)
        
        
    def do_savePath(self,sp):
        'savePath without argument: gives you the current save path and the ability to upgrade it. savePath + argument changes the save path to the argument after automatically correcting it. No need to worry for the \. Syntax: savePath or savePath something. returns the savePath'
        self.save_dir=complete_save_path(sp,self.save_dir,self.descar_path)
    
    def do_path(self,path):
        'Changes both the save and file path. Type path to enter the utility or path + the desired file path to change them directly'
        self.save_dir=complete_save_path(path,self.save_dir,self.descar_path)
        complete_file_path(path,self.descar_path)
        
        
    def do_siliconRemove(self,nul):
        'This routine finds the source .txt files of your raman experiment in the source folder you gave, opens them, removes the silicon peak and saves the modified txts in a new folder\n-The routine create the new folder for you\n-The routine renames the new .txt for you\n-The routine does not modify the original .txt files\n-The removal of the silicon peak is done by substracting a Lorentz fit of the peak (hence no loss of information).'
        self.nul=nul
        peak_remover()
    def do_thermalStress(self,nul):
        'This routine allows you to compute the theoretical thermal stress between two materials in a stack originating from the CTE mismatch\n-The routine gives a first order estimation of the thermal stress based on the given mechanical properties\n-This routine is a simple implementation of the Stoney\'s equation\n-The result of this routine does not replace experimental data\n-The routine saves the result in a txt'
        self.nul=nul
        thermalStessWiz(self.save_dir)
    def do_stressCompensation(self,nul):
        'This routine allows you to compute an estimation of stack parameter to build in order to have a stress free/compensated membrane.\n-This routine only gives a first order estimation and does not replace a proper simulation\n-This routine is a simple implementation of the Stoney\'s equation'
        self.nul=nul
        stressCompensation(self.save_dir)
        
    def do_stoney(self,nul):
        "Computes the thermal stress in a thin film based on Dektak files and the derivative version of the stoney's equation. Material mode supported by this routine => uss material mode to set the substrate properties"
        self.nul=nul
        derivative_stoney(self.save_dir)
    

    def do_material(self,material):
        '\n Help on material:\nMaterial helping routine. Running this command followed by the name of a supported material puts DesCar in the material analysis mode. \n\n-Type material followed by run to enter the wizare\n-Type material followed by the name of the material to enter this material analysis mode\n-Type material exit to exit the analysis mode.\n-Currently supported material: VO2 (type VO2 or vo2), Si \n-The routine allows to overlay the expected material peaks on the raman plots (can be auto saved or not)\n-Upcoming feature: auto detection of the given material in raman plots\n-Type material exit to exit material mode \n'
        materialWiz(material,self.material_path)
    def do_parsePolytec(self,nul):
        '\nAutomatic detection and parsing of the line and map type file from the polytec. Polytec .txt files are cleaned and rewritten to new directory under the generic format of x,y,z column with a dot as coma and a blank as separator\n'
        self.nul=nul
        polyParsAndCorrect()
        #plot_polytek(plotT,self.save_dir)
    def do_approximate(self,nul):
        '\nApproximation of any order or sqrt of a given set of point.'
        self.nul=nul
        approximate()
    def do_plot(self,plotT):
        '\nAllows you to plot .txt files provided in a clean xyz coumn fashion.\n-Type plot to launch the wizard\n-Type plot rifle to automatically plot every file in the folder individually (one file per plot)\n-Type plot select to plot a selection of file\n-Type plot all to plot all files on a single plot\n-Different style possible: individual point, connected data points, fancy connected data point,... \n'
        self.plotT=plotT
        plot(plotT,self.save_dir)
        
    def do_level(self,nul):
        "\nAllows you to level a measurement provided under the form of a clean x,y file . You'll need to provide a range at the beginning and the end of the data.\n"
        self.nul=nul
        level()
        
    def do_levelL(self,left):
        "Allows to set the left leveling range for all subsequent leveling routine run. The routine will not ask for the left range if this is set"
        self.left=left
        setLeft(left)
    
    def do_levelR(self,right):
        "Allows to set the right leveling range for all subsequent leveling routine run. The routine will not ask for the right range if this is set"
        self.right=right
        setRight(right)
     
    def do_levelClear(self,nul):
        "Resets both leveling ranges."
        self.nul=nul
        levelClear()
        
    
    def do_deflection(self,nul):
        "\nFor membrane deflection in polytec. Data must be leveled for best result. Takes a clean x,y file as input. The routine generates a clean x,y txt file with x=the pressure and y=deflection. File name must contain the pressure information). The routine will sort the files automatically (increassing pressure)\n"
        self.nul=nul
        deflection()
        
        
        
    def do_resistanceP(self,nul):
        "\nGets the resistance value from file constaining the x data in their name => typically one IV curve per pressure point\n"
        self.nul=nul
        rPressure()
        
    def do_ramanPressure(self,nul):
        "\nFor membrane deflection under the Raman. The routine takes a clean x,y txt file and provide a txt file of the pressure (x) and the max peak position.!!! For silicon only !!! Pressure data must be contained in the file name\n"
        self.nul=nul
        ramanSiliconPressure()
        
    def do_ramanMap(self,nul):
        "\nTakes RAW raman map measurement and outputs a clean x,y txt file. Takes the n points of the maping and averages them\n"
        self.nul=nul
        ramanMapCleanAndAvg()
        
    def do_comsolClean(self,nul):
        '\nTakes RAW comsol column files and outputs a clean x,y txt file\n'
        self.nul=nul
        comsolClean()
        
    def do_avg(self,nul):
        '\nCompute the average of all the provided files. Takes clean x y txt files\n'
        self.nul=nul
        avg()
    
    def do_colMult(self,coef):
        "\nAllows to multiply a column from a clean x y .txt file by any float constant. Creates a modified copy of the inittial file\n"
        self.coef=coef
        colMult(coef)
        
    def do_colAdd(self,shift):
        "\nAllows to add a cst to every item in a column from a clean x y .txt file. Cst can be any float cst. Creates a modified copy of the initial file\n"
        self.shift=shift
        colAdd(shift)
        
    def do_gfc(self,nul):
        "Generic File Cleaning routine to clean input txt file (support coma and space separation) and outputs clean space separated xyz txt"
        self.nul=nul
        generic_data_cleaner()
    
    def do_gfcColName(self,colName):
        "Sets the column name for all gfc run"
        self.colName=colName
        col_name(colName)
    
    def do_gfcExport(self,colExport):
        "Sets the combination of column to export for all gfc run"
        self.colExport=colExport
        col_export(colExport)
    
    def do_gfcSkip(self,skip):
        "Sets the number of lines to skip in file for all gfc run"
        self.skip=skip
        skip_row(skip)
        
    def do_gfcClear(self,nul):
        "Clears global gfc settings"
        self.nul=nul
        gfClear()
        
        
    def do_setExtOld(self,old):
        "Set an extension to be replaced"
        self.old=old
        old_ext(old)
        
    def do_setExtNew(self,new):
        "Set the replacement extension"
        self.new=new
        new_ext(new)
        
    def do_clearExt(self,nul):
        "Clears extension settings"
        self.nul=nul
        extClear()


    
    def do_dataCycle(self,nul):
        "\nAlligns successive up and down cycles. Will take the last value of the first  up and shift the first  down to allign with it. Then takes the first value of  down1 and alligns the first value of up2 with it. Works on clean xy txt file. Leveling the polytec profiles using the level tool is recommended. Files should be named up1,down1,up2,down2... Will output shifted version of the original files.\n"
        self.nul=nul
        dCycle()
        
    def do_plotTitle(self,title):
        "\nSets global title for plotting routine. Plot routine will not ask for a title if globaly set using this command. Set by typing plotTitle or plotTitle + your title. Reset by using clearPlot\n"
        self.title=title
        plot_title(title,self.descar_path)
        
    def do_plotX(self,x):
        "\nSets global x axis text for plotting routine. Plot routine will not ask for a x axis text if globaly set using this command. Set by typing plotX or plotX + your x text. Reset by using clearPlot\n"
        self.x=x
        plot_x(x,self.descar_path)
        
    def do_plotY(self,y):
        "\nSets global y axis text for plotting routine. Plot routine will not ask for a y axis text if globaly set using this command. Set by typing plotY or plotY + your plotY text. Reset by using clearPlot\n"
        self.y=y
        plot_y(y,self.descar_path)
        
    def do_plotStyle(self,style):
        "\nSets global plot style for plotting routine. Plot routine will not ask for a plot style if globaly set using this command. Set by typing plotStyle or plotStyle + your style. Reset by using clearPlot\n"
        self.style=style
        plot_style(style,self.descar_path)
        
    

    
        
    def do_clearPlot(self,nul):
        "\nResets global plot parameters\n"
        self.nul=nul
        plot_clear(self.descar_path)
        
        
    def do_dektakClean(self,nul):
        "\nTake raw dektak measurement and outputs clean x,y txt. Supports .txt only. Use the extension command to convert the dektak csv to txt prior to using the command\n"
        self.nul=nul
        dektakClean()
        
    def do_extension(self,nul):
        "\nAllow the user to change the extension of all files in a directory. For instance replacing all .csv by a .txt\n"
        self.nul=nul
        extension()
        
        
    def do_trimFN(self,trim):
        "\nRemoves a given sequence of characters from the fine name\n"
        self.trim=trim
        trimFN(trim)
        
        
    def do_normalise(self,nul):
        "\nNormalises all file in folder by the curve max\n"
        self.nul=nul
        normalise()
        
        
        
        
        
        
        
            
    # DesCar automation routines
    
    
    def do_setExtension(self,nul):
        "Sets the extension replacement old and new"
        self.nul=nul
        extClear()
        old_ext("")
        new_ext("")
        print("Extension replacement settings set succesfully !")
        
    
    def do_setLevel(self,nul):
        "Sets both left and right leveling range"
        self.nul=nul
        levelClear()
        setLeft("")
        setRight("")
        print("General level baseline settings set succesfully !")
    
    
    
    def do_setGFC(self,nul):
        "Sets all the global gfc parameters"
        self.nul=nul
        gfClear()
        skip_row("")
        col_name("")
        col_export("")
        print("General file clean parameters set succesfully !")
        
    
    def do_setPlot(self,nul):
        "\n-Allows the user to set global plot parameter. Running this command will ask the user for a general title, x axis, y axis and plot style to be set. \n-Parameters can be set independantly by running plotStyle, plotX, plotY or plotTitle. \n-Set parameters will be used by all plot rifle. The plot routine will not ask for x,y,title or style if globaly set.\n-Reset all plot style by using plotClear\n"
        self.nul=nul
        plot_clear(self.descar_path)
        plot_style("",self.descar_path)
        plot_title("",self.descar_path)
        plot_x("",self.descar_path)
        plot_y("",self.descar_path)
        
        
    
    
        
        
    def do_ramanStrain(self,nul):
        "\nTakes raw raman map files and runs a complete procedure to output raman as function of pressure files\n"
        self.nul=nul
        ramanMapCleanAndAvg()
        self.save_dir=complete_save_path(os.getcwd()+"\\corrected_raman_map",self.save_dir,self.descar_path)
        complete_file_path(os.getcwd()+"\\corrected_raman_map",self.descar_path)
        ramanSiliconPressure()
        self.save_dir=complete_save_path(os.getcwd()+"\\raman_peak_shift",self.save_dir,self.descar_path)
        complete_file_path(os.getcwd()+"\\raman_peak_shift",self.descar_path)
        print("\nRoutine completed successfully ! Path changed to result folder\n")
        
  
    def do_polytecDeflection(self,nul):
        "\nRuns a full polytec analysis routine to obtaine a deflection plot. \n-Takes raw polytec line or map data with the applied pressure given in the name of each txt file\n-Parse and cleans the files\n-Runs a leveling routine\n-Produces a deflection plot \n"
        self.nul=nul
        polyParsAndCorrect()
        self.save_dir=complete_save_path(os.getcwd()+"\\clean_polytec\line",self.save_dir,self.descar_path)
        complete_file_path(os.getcwd()+"\\clean_polytec\line",self.descar_path)
        print("\nPlotting raw line files\n")
        plot_rifle(self.save_dir)
        level()
        self.save_dir=complete_save_path(os.getcwd()+"\\leveled_data",self.save_dir,self.descar_path)
        complete_file_path(os.getcwd()+"\\leveled_data",self.descar_path)
        print("\nPlotting leveled line file\n")
        plot_rifle(self.save_dir)
        deflection()
        self.save_dir=complete_save_path(os.getcwd()+"\\deflection_data",self.save_dir,self.descar_path)
        complete_file_path(os.getcwd()+"\\deflection_data",self.descar_path)
        print("\nRoutine completed successfully ! Path changed to result folder\n")



Plot().cmdloop()


