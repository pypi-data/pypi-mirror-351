import glob
import os
import shutil 


def filePathCorr(filePath):
    if(filePath[-1]=='\\'):
        return filePath
    else:
        return filePath+'\\'
        
def fileExtensionSingle(fileNameList):
    if(len(fileNameList)<4):
        fileNameList=fileNameList+".txt"
    else:
        if(fileNameList!=".txt"):
            fileNameList=fileNameList+".txt"
    return fileNameList 


 
def fileExtension(fileNameList):
    for i in range(len(fileNameList)):
        int_file=fileNameList[i]
        if(len(int_file)<4):
            fileNameList[i]=fileNameList[i]+".txt"
        else:
            if(int_file[-4:]!=".txt"):
                fileNameList[i]=fileNameList[i]+".txt"
    return fileNameList
    
def fileExtensionRemover(fileNameList):
    for i in range(len(fileNameList)):
        int_file=fileNameList[i]
        if(int_file[-4:]==".txt"):
            fileNameList[i]=fileNameList[i].replace(".txt","")
            # fileNameList[i]=fileNameList[i].replace("_"," ")
    return fileNameList

    
def inFolder(file_name): #takes an array
    file_list=glob.glob("*.txt")
    count=0
    for i in range(len(file_name)):
        flag=0
        while(flag==0):
            for fp in enumerate(file_list):
                if(file_name[i]==fp[1]):
                    print(file_name[i]," found in dir")
                    count=count+1
                    flag=1
            if(flag==0):
                print(file_name[i]," not in dir")
                flag=1
    if(count==len(file_name)): 
        print("all files found in dir. Ok to continue...")
        return 1
    else:
        print("missing files in dir.Resuming...")
        return 0
    


def descarFileConfig(fp,sp,descar_path):
    with open(descar_path+"\\boot.txt","r") as file:
        fpi,spi=file.readlines()[0].split(',')
    if(fp!="null" and sp!="null"):
        fpi=fp
        spi=sp
    if(fp!="null" and sp=="null"):
        fpi=fp
    elif(fp=="null" and sp!="null"): 
        spi=sp
    elif(fp=="null" and sp=="null"):
        print("Path configuration unchanged")
    else:
        print("\n!!CRITICAL ERROR!! Unable to access, load or write the DesCar path confifg file: boot.txt\nUsing DesCar past this error might result in data overwritte\n")
    
    with open(descar_path+"\\boot.txt","w") as file:  
        file.write(fpi+","+spi)

    
        


    

def complete_file_path(fp,descar_path):
    if(fp!=""):
        os.chdir(filePathCorr(fp))
        descarFileConfig(fp,"null",descar_path)
        print("\nFile path changed to:",filePathCorr(fp))
        return fp
    else:
        print("\nThe current file path is:\n", os.getcwd())
        while(1):
            a=input(' Do you want to keep it ? (y/n): ')
            if(a=='n'):
                fpi=filePathCorr(input("Please provide a file path to the data source folder: "))
                os.chdir(fpi)
                descarFileConfig(fp,"null",descar_path)
                print("The path has been changed to: ", fpi)
                break
            elif(a=='y'):
                fpi=filePathCorr(os.getcwd())
                print("Current file directory kept")
                break
            else:
                print("Command not recognised. Resuming...")
        return fpi
 


def complete_save_path(sp,csp,descar_path):
    if(sp!=""):
        save_dir=filePathCorr(sp)
        descarFileConfig("null",sp,descar_path)
        print("\nSave path changed to: ",filePathCorr(save_dir))
        return save_dir
    else:
        print("\nThe current save path is:\n", csp)
        while(1):
            a=input(' Do you want to keep it ? (y/n): ')
            if(a=='n'):
                spi=filePathCorr(input("Please provide a save path: "))
                descarFileConfig("null",sp,descar_path)
                print("The path has been changed to: ", spi)
                break
            elif(a=='y'):
                spi=filePathCorr(csp)
                print("Current save directory kept")
                break
            else:
                print("Command not recognised. Resuming...")
        return spi 
    

def file_length(file):
    with open(file) as fp:
        x=[]
        for line in fp:
            values = line.split()
            x.append(float(values[0]))       
    return len(x)



def legend(file_list):
    while(1):
        a=input("Do you want to display the automatic legend ? (y/n): ")
        if(a=="y"):
            print("The legend will be:",fileExtensionRemover(file_list))
            legend=fileExtensionRemover(file_list)
            break
        elif(a=="n"):
            legend=input("What legend do you want to give to the curve sir ? (S1,S2,): ")
            legend=legend.split(',') 
            print("The legend will be:",legend)
            break
        else:
            print("Command not recognised. Resuming")
    return legend
  

def file_duplication():
    files=glob.glob("*.txt")
    print("Found files:",files)
    newpath=os.getcwd()+"\modified_files"+"\\"
    print("The current path:",os.getcwd())
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    for i, fp in enumerate(files):
        shutil.copy2(os.getcwd()+"\\"+files[i],newpath)
    print("All filed copied to: ",newpath)
    os.chdir(newpath)
    files=glob.glob("*.txt")
    for i, fp in enumerate(files):
        os.rename(files[i],"no_Si_peaks_"+files[i])
    return(newpath)
    
    
    

class Extension: 
    def __init__(self):
        self.old=None
        self.new=None

    def set_old(self,old):
        self.old=old
    
    def get_old(self):
        return self.old
        
    def set_new(self,new):
        self.new=new
    
    def get_new(self):
        return self.new
        
    def clear_extension(self):
        self.old=None
        self.new=None
        
extensionset=Extension()
    
    
def old_ext(old_ext):
    if(old_ext==''):
        a=input("\nPlease provide the old extension (.txt, .csv, ...) with the dot: ")
        extensionset.set_old(a)
        print("Old extenstion set to: ",a,"\n")
    else:
        extensionset.set_old(old_ext)
        print("Old extenstion set to: ",old_ext,"\n")
        
        
def new_ext(new_ext):
    if(new_ext==''):
        a=input("\nPlease provide the new extension (.txt, .csv, ...) with the dot: ")
        extensionset.set_new(a)
        print("New extenstion set to: ",a,"\n")
    else:
        extensionset.set_new(new_ext)
        print("New extenstion set to: ",new_ext,"\n")
        
def extClear():
    extensionset.clear_extension()
    print("\nGeneral extension settings cleared succesfully !\n")
 
 
 
 
 
 
 
 
 
 
    
    

def extension():
    try:
        if(extensionset.get_old()==None):
            old=input("\nWhat extension do you want to replace (.csv, .txt, ...): ")
        else:
            old=extensionset.get_old()
        files=glob.glob("*"+old)
        f_list=fileExtensionRemover(glob.glob("*"+old))
        print("\n")
        for i in range(len(files)):
            print("Found: ",files[i])
            
        if(extensionset.get_new()==None):
            new=input("\nWhat extension do you want to use (.csv, .txt, ...): ")
        else:
            new=extensionset.get_new()    
            
            
        
        print("\n")
        for i,fp in enumerate(files):
            with open(fp) as file:
                values=[]
                for line in file:
                    values.append(line)
            with open (f_list[i].replace(old,new),'w') as new_file:
                print("Outputing ",f_list[i].replace(old,new))
                for k in range(len(values)):
                    new_file.write(values[k])
        print('\n---------------------------------------------------------------\n') 
        print("\nOperation successful!\n")
    except:
        print('\n---------------------------------------------------------------\n') 
        print("\nError in the mail loop. Exiting ...\n")
                
                
def trimFN(trim):
    try:
        if(trim==""):
            trim=input("\nSequence to remove from the file name: ")
        files=glob.glob("*.txt")
        f_list=fileExtensionRemover(glob.glob("*.txt"))
        for i,fp in enumerate(files):
            if(trim in fp):
                print("Found: ",fp)
        print("\n")
        print("\nRemoving characters ...\n")
        for i,fp in enumerate(files):
            if(trim in fp):
                with open(fp) as file:
                    values=[]
                    for line in file:
                        values.append(line)
                with open (f_list[i].replace(trim,"")+".txt",'w') as new_file:
                    print("Outputing: ",f_list[i].replace(trim,""))
                    for k in range(len(values)):
                        new_file.write(values[k]) 
        print('\n---------------------------------------------------------------\n') 
        print("\nOperation successful!\n")
    except:
        print('\n---------------------------------------------------------------\n') 
        print("\nError in the mail loop. Exiting ...\n")