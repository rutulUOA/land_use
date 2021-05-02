"""
This module is designed to simulate urban growth
using land cover data, urban growth driving parameters
and Cellular Automata model

Author: PratyushTripathy
Date Modified: 23 November, 2018

Operating System: Windows 8
Python Version: 3.4.4

Following is the order of the land cover data:
    Built-up land --> Class 1
    Vegetation --> Class 2
    Water body --> Class 3
    Others --> Class 4
    
"""

####################################################
####################################################
##                                                ##
##              #######       #######             ##
##            ##              ##   ##             ##
##           ##              ##     ##            ##
##           ##             ###########           ##
##           ##            ##         ##          ##
##            ##          ##           ##         ##
##              #######  ####         ####        ##
##                                                ##
####################################################

#Importing all necessary libraries
import os, math
import numpy as np
from osgeo import gdal
from copy import deepcopy

#Defining function to read raster file and return array and datasource
def readraster(file):
    dataSource = gdal.Open(file)
    band = dataSource.GetRasterBand(1)
    band = band.ReadAsArray()
    return(dataSource, band)
  
def identicalList(inList):
    global logical
    inList = np.array(inList)
    logical = inList==inList[0]
    if sum(logical) == len(inList):
        return(True)
    else:
        return(False)

def builtupAreaDifference(landcover1, landcover2, buclass=1, cellsize=100):
    return(sum(sum(((landcover2==buclass).astype(int)-(landcover1==buclass).astype(int))!=0))*(cellsize**2)/1000000)
    
#Defining class to read land cover file of two time periods
class landcover():
    
    def __init__(self, file1, file2):
        self.ds_lc1, self.arr_lc1 = readraster(file1)
        self.ds_lc2, self.arr_lc2 = readraster(file2)
        self.performChecks()

    def performChecks(self):
        #check the rows and columns of input land cover datasets
        print("Checking the size of input rasters...")
        if (self.ds_lc1.RasterXSize == self.ds_lc2.RasterXSize) and (self.ds_lc1.RasterYSize == self.ds_lc2.RasterYSize):
            print("Land cover data size matched.")
            self.row, self.col = (self.ds_lc1.RasterYSize, self.ds_lc1.RasterXSize)
        else:
            print("Input land cover files have different height and width.")
        #Check the number of classes in input land cover images
        print("\nChecking feature classes in land cover data...")
        if (self.arr_lc1.max() == self.arr_lc2.max()) and (self.arr_lc1.min() == self.arr_lc2.min()):
            print("The classes in input land cover files are matched.")
            self.nFeature = (self.arr_lc1.max() - self.arr_lc1.min())
        else:
            print("Input land cover data have different class values/ size.")

    def transitionMatrix(self):
        self.tMatrix = np.random.randint(1, size=(self.nFeature, self.nFeature))
        for x in range(0,self.row):
            for y in range(0,self.col):
                t1_pixel = self.arr_lc1[x,y]
                t2_pixel = self.arr_lc2[x,y]
                self.tMatrix[t1_pixel-1, t2_pixel-1] += 1
        self.tMatrixNorm = np.random.randint(1, size=(4,5)).astype(float)
        print("\nTransition Matrix computed, normalisation in progress..")
        #Creating normalised transition matrix
        for x in range(0, self.tMatrix.shape[0]):
            for y in range(0, self.tMatrix.shape[1]):
                self.tMatrixNorm[x,y] = self.tMatrix[x,y]/(self.tMatrix[x,:]).sum()
                
class growthFactors():

    def __init__(self, *args):
        self.gf = dict()
        self.gf_ds = dict()
        self.nFactors = len(args)
        n = 1
        for file in args:
            self.gf_ds[n], self.gf[n] = readraster(file)
            n += 1
        self.performChecks()

    def performChecks(self):
        print("\nChecking the size of input growth factors...")
        rows = []
        cols = []
        for n in range(1, self.nFactors+1):
            rows.append(self.gf_ds[n].RasterYSize)
            cols.append(self.gf_ds[n].RasterXSize)
        if (identicalList(rows) == True) and ((identicalList(cols) == True)):
            print("Input factors have same row and column value.")
            self.row = self.gf_ds[n].RasterYSize
            self.col = self.gf_ds[n].RasterXSize
        else:
            print("Input factors have different row and column value.")

class fitmodel():

    def __init__(self, landcoverClass, growthfactorsClass, kernelSize = 3):
        self.landcovers = landcoverClass
        self.factors = growthfactorsClass
        self.performChecks()
        self.kernelSize = kernelSize

    def performChecks(self):
        print("\nMatching the size of land cover and growth factors...")
        if (self.landcovers.row == self.factors.row) and (self.factors.col == self.factors.col):
            print("Size of rasters matched.")
            self.row = self.factors.row
            self.col = self.factors.col
        else:
            print("ERROR! Raster size not matched please check.")

    def setThreshold(self, builtupThreshold, *OtherThresholdsInSequence):
        self.threshold = list(OtherThresholdsInSequence)
        self.builtupThreshold = builtupThreshold
        if len(self.threshold) == (len(self.factors.gf)):
            print("\nThreshold set for factors")
        else:
            print('ERROR! Please check the number of factors.')

    def predict(self, base=1):
        if base==1:
            self.predicted = deepcopy(self.landcovers.arr_lc1)
        elif base==2:
            self.predicted = deepcopy(self.landcovers.arr_lc2)
        else:
            raise ValueError("Set base to 1 or 2")
        sideMargin = math.ceil(self.kernelSize/2)
        for y in range(sideMargin,self.row-(sideMargin-1)):
            for x in range(sideMargin,self.col-(sideMargin-1)):
                kernel = self.landcovers.arr_lc1[y-(sideMargin-1):y+(sideMargin), x-(sideMargin-1):x+(sideMargin)]
                builtupCount = sum(sum(kernel==1))
                #If the number of built-up cells greater than equal to assigned threshold
                if (builtupCount >= self.builtupThreshold):
                #if (builtupCount >= self.builtupThreshold) and (self.factors.gf[5][y,x] != 1):  # Adding exception for the restricted areas
                    for factor in range(1,self.factors.nFactors+1):
                #If the assigned thresholds are less than zero, then the smaller than rule applies, else greater than
                        if self.threshold[factor-1] < 0:
                            if (self.factors.gf[factor][y,x] <= abs(self.threshold[factor-1])):
                                self.predicted[y, x] = 1
                            else:
                                pass
                        elif self.threshold[factor-1] > 0:
                            if (self.factors.gf[factor][y,x] >= self.threshold[factor-1]):
                                self.predicted[y, x] = 1
                            else:
                                pass
                if (y%500==0) and (x%500==0):
                    print("Row: %d, Col: %d, Builtup cells count: %d\n" % (y, x, builtupCount), end="\r", flush=True)

    def checkAccuracy(self):
        #Statistical Accuracy
        self.actualBuildup = builtupAreaDifference(self.landcovers.arr_lc1, self.landcovers.arr_lc2)
        self.predictedBuildup = builtupAreaDifference(self.landcovers.arr_lc1, self.predicted)
        self.spatialAccuracy = 100 - (sum(sum(((self.predicted==1).astype(float)-(self.landcovers.arr_lc2==1).astype(float))!=0))/sum(sum(self.landcovers.arr_lc2==1)))*100
        print("Actual growth: %d, Predicted growth: %d" % (self.actualBuildup, self.predictedBuildup))
        #Spatial Accuracy
        print("Spatial accuracy: %f" % (self.spatialAccuracy))

    def exportPredicted(self, outFileName):
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create(outFileName, self.col, self.row, 1, gdal.GetDataTypeByName('Byte'))
        outdata.SetGeoTransform(self.landcovers.ds_lc1.GetGeoTransform())
        outdata.SetProjection(self.landcovers.ds_lc1.GetProjection())
        outdata.GetRasterBand(1).WriteArray(self.predicted)
        outdata.GetRasterBand(1).SetNoDataValue(0)        
        outdata.FlushCache() 
        outdata = None
