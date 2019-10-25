#!/usr/bin/env python
# coding: utf-8
#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

from pymysql import cursors, connect
from mysql import connector

class SyncToMySQL():
    def processDataToSync(self, final_dict):
        columns_list = ['image_name', 'time', 'price', 'target', 'stop_loss', 'recommadation', 'stock_name',
                        'analyst_name', 'analyst_company','tv_chn_name']
        mySQL_df = pd.DataFrame(columns=columns_list)

        for single_row in final_dict['extracted_data']:
            # print (single_row)
            price = '';
            target = '';
            stop_loss = '';
            recommadation = '';
            stock_name = '';
            analyst_name = '';
            analyst_company = '';
	    tv_chn_name ='';
	    rec_cnt=0; 
            for detail in single_row['Details']:
		tv_chn_name ='CNBC';
			
                if (detail['field_Name'] == 'price'):
                    price = detail['extracted_text'];
		    rec_cnt=rec_cnt+1;

                if (detail['field_Name'] == 'target'):
                    target = detail['extracted_text']
		    rec_cnt=rec_cnt+1;

                if (detail['field_Name'] == 'stop loss'):
                    stop_loss = detail['extracted_text']
		    rec_cnt=rec_cnt+1;

                if (detail['field_Name'] == 'buy' or detail['field_Name'] == 'sell'):
                    recommadation = detail['extracted_text']
		    rec_cnt=rec_cnt+1;

                if (detail['field_Name'] == 'stock_Name'):
                    stock_name = detail['extracted_text']
		    rec_cnt=rec_cnt+1;
	
                if (detail['field_Name'] == 'broker_Name'):
                    analyst_name = detail['extracted_text']
		    rec_cnt=rec_cnt+1;

                if (detail['field_Name'] == 'broker_firm'):
                    analyst_company = detail['extracted_text']
		    rec_cnt=rec_cnt+1;

            # print ('price ',price,' target ',target,' stop_loss',stop_loss,' recommadation',recommadation,' stock_name',stock_name,' analyst_name',analyst_name,' analyst_company',analyst_company)
	    if rec_cnt=>6:
            	extract_dict = {
                	'image_name': single_row['image_name'],
	                'time': single_row['time'],
                	'price': price,
                	'target': target,
                	'stop_loss': stop_loss,
                	'recommadation': recommadation,
                	'stock_name': stock_name,
                	'analyst_name': analyst_name,
                	'analyst_company': analyst_company,
			'tv_chn_name':tv_chn_name
            	}
            	temp_extract_df = pd.DataFrame([extract_dict])
            	mySQL_df = mySQL_df.append(temp_extract_df)
		
        return mySQL_df;


    def sinkDataToMqSQL1(self,mySQL_df):
        database_username = 'streetalpha'
        database_password = 'KentuckyMeeting8|'
        database_ip       = '13.235.233.13'
        database_name     = 'streetalpha'
        database_connection = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}?charset=utf8'.format(database_username, database_password,database_ip, database_name))
        mySQL_df.to_sql(con=database_connection, name='tv_data_extract', if_exists='append')

    def sinkDataToMySQL(self,mySQL_df):
        db_url = {
            'database': "streetalpha",
            'drivername': 'mysql',
            'username': 'streetalpha',
            'password': 'KentuckyMeeting8|',
            'host': '13.235.233.13',
            'query': {'charset': 'utf8'},  # the key-point setting
        }
        
        engine = create_engine(URL(**db_url), encoding="utf8")
	try:
          mySQL_df.to_sql(con=engine, name='tv_data_extract', if_exists='append',index=False)
	except:
	  print ('Error while processing')


'''
import json
import os

mysqlObj = SyncToMySQL();

os.chdir('/home/ubuntu/TextProcessing/outfile');
final_dict = open("extracted.json", "r");
##final_dict=final_dict.encode('UTF-8');
final_dict = eval(final_dict.read());
mySQL_df = mysqlObj.processDataToSync(final_dict)
mysqlObj.sinkDataToMySQL(mySQL_df)
print('Completed!!!')
'''



import json
import os
import pandas as pd
from datetime import datetime
import shutil, os, glob

mysqlObj = SyncToMySQL();

srcDir='/home/ubuntu/TextProcessing/outfile'
dstDir='/home/ubuntu/TextProcessing/data/CNBC/processed/process_json'
while os.listdir(srcDir):
    all_files = glob.glob(srcDir + "/*.json")
    for file in all_files:
        print ('processing :',file)
        final_dict = open(file, "r");
        final_dict = eval(final_dict.read());
        mySQL_df=mysqlObj.processDataToSync(final_dict)
	if mySQL_df.empty == False:
	    print ('Inserting into MqSQL ')
            mysqlObj.sinkDataToMySQL(mySQL_df);
        print ('Move files to destination dir')
        shutil.move(file, dstDir);
print ('Completed!!!')