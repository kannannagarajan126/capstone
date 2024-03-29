#!/usr/bin/env python
# coding: utf-8


import time
import pandas as pd
from datetime import datetime
import shutil, os, glob
 

def processRawDataFile(props):    
    srcDir=props['srcDir']
    dstDir=props['dstDir']
    inDir=props['inDir']
    badFiles=props['badFiles']
    
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
            if cnt>=1:
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
		print ('*'*10)
                try:
                  print ('source file : ',srcDir,'/',fileName)
                  print ('dstDir file : ',dstDir,'/',fileName)
                  #shutil.move(os.path.join(srcDir, fileName),os.path.join(dstDir, fileName))
                  shutil.move(fileName, dstDir);
                except:
                  print ('Exception occred while moving file so moving to badFile dir')
                  shutil.move(fileName, badFiles);
                print ('*'*10)
            print ('Completed')
        else:
            print ('No files to process !!')
        
    print ('No more files to process !! ')    
        



while 1==1:
    f=open("/home/ubuntu/TextProcessing/env/Create_CNBC_dataFiles_properties.txt","r")
    props = eval (f.read())
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    if current_time>=props['end_time']:
        print('End time reached !!')
        break;
    if (props['exection_mode'] == 'X'):
        print ('Exit mode is on..')
        break;
    else:
        processRawDataFile(props)
        time.sleep(int(props['sleep_sec']))
        continue;
        
  
 