from filePath import * 
import cmd #cmd in small letters is the name of the module. do cmd.Cmd.any_function() to run a function from the class from the module
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import glob
from plotRaman import  *
import os
import numpy as np
import sys



class Machines:
    
    def __init__(self):
        self.machine = None 

        
    def set_machine(self,machine):
        self.machine=machine

    def get_machine(self):
        return self.machine

        
    

global_material=Material()



        

