#! /bin/bash

if [ `date +%H` -ge 17 ] 
then
  echo "End time reached will exit !!"
  exit -1
fi

echo "-------------- Alert !! for process status ---------------------" > /home/ubuntu/TextProcessing/data/status.txt

cd /home/ubuntu/screendumps/CNBC/csv_files
echo "Count of incomming files from ocr output to be processed" >> /home/ubuntu/TextProcessing/data/status.txt
ls -lrt | wc -l >> /home/ubuntu/TextProcessing/data/status.txt
echo "-----------------------------------"  >> /home/ubuntu/TextProcessing/data/status.txt

cd /home/ubuntu/TextProcessing/in
echo "Count of incomming files to Text processing to be processed" >> /home/ubuntu/TextProcessing/data/status.txt
ls -lrt | wc -l >> /home/ubuntu/TextProcessing/data/status.txt
echo "-----------------------------------"  >> /home/ubuntu/TextProcessing/data/status.txt

cd /home/ubuntu/TextProcessing/outfile
echo "Count of incomming files from Text processing to be inserted to DB" >> /home/ubuntu/TextProcessing/data/status.txt
ls -lrt | wc -l >> /home/ubuntu/TextProcessing/data/status.txt
echo "-----------------------------------"  >> /home/ubuntu/TextProcessing/data/status.txt 

echo "dumpScreen python process :" >> /home/ubuntu/TextProcessing/data/status.txt
echo "-----------------------------------"  >> /home/ubuntu/TextProcessing/data/status.txt 
sudo ps -ef | grep "dumpScreen" >> /home/ubuntu/TextProcessing/data/status.txt
echo "-----------------------------------"  >> /home/ubuntu/TextProcessing/data/status.txt 

echo "OCR python process :" >> /home/ubuntu/TextProcessing/data/status.txt
echo "-----------------------------------"  >> /home/ubuntu/TextProcessing/data/status.txt 
sudo ps -ef | grep "OCR" >> /home/ubuntu/TextProcessing/data/status.txt
echo "-----------------------------------"  >> /home/ubuntu/TextProcessing/data/status.txt 

echo "Text processing python process :" >> /home/ubuntu/TextProcessing/data/status.txt
echo "-----------------------------------"  >> /home/ubuntu/TextProcessing/data/status.txt 
sudo ps -ef | grep "Text" >> /home/ubuntu/TextProcessing/data/status.txt
echo "-----------------------------------"  >> /home/ubuntu/TextProcessing/data/status.txt 


echo "------------- Python script called to post on Slack bot ----------------------" 
sudo python3 /home/ubuntu/TextProcessing/bin/slackBot.py



