#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from datetime import datetime
import shutil, os, glob
 

#srcDir='/home/ubuntu/screendumps/CNBC/csv_files'
#dstDir='/home/ubuntu/TextProcessing/data/CNBC/processed/rawFile'
#inDir='/home/ubuntu/TextProcessing/in/'

srcDir='/home/ubuntu/TextProcessing/tempTest'
dstDir='/home/ubuntu/TextProcessing/testDst'
inDir='/home/ubuntu/TextProcessing/'



while os.listdir(srcDir):

    all_files = glob.glob(srcDir + "/*.csv")

    li = []
    current_files=[]
    # Combining all the files to single csv file
    cnt=1
    fileExist=False
    for filename in all_files:
        fileExist=True
        current_files.append(filename)
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)
        cnt=cnt+1
        if cnt>=100:
            break;
    
    if fileExist==True :
        frame = pd.concat(li, axis=0, ignore_index=True)
    
        #Drop the unwanted column
        final_df=frame.drop('Unnamed: 0', axis=1)
    
        #getting current time to check create the file name 
        now = datetime.now()
        current_time = now.strftime("%d_%m_%Y_%H_%M_%S")
        file_name='CNBC_'+current_time+'_'+str(now.microsecond)
        print ('file_name:',file_name)

        #Write the data to csv file
        final_df.to_csv(inDir+file_name+'.csv', index = None, header=True)

        #Move files from source directory to incomming directory
        for fileName in current_files:
            shutil.move(fileName, dstDir);
        
print ('Completed')





