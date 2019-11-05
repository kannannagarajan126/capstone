#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

class SyncToMySQL():
    def processDataToSync(self, final_dict):
        columns_list = ['image_name', 'time', 'price', 'target', 'stop_loss', 'recommadation', 'stock_name',
                        'analyst_name', 'analyst_company', 'tv_chn_name']
        mySQL_df = pd.DataFrame(columns=columns_list)
        side=''
        for single_row in final_dict['extracted_data']:
            # print (single_row)
            price = '';
            target = '';
            stop_loss = '';
            recommadation = '';
            stock_name = '';
            analyst_name = '';
            analyst_company = '';
            tv_chn_name = '';
            prefixStockName = ''; rec_cnt = 0;
            for detail in single_row['Details']:
                tv_chn_name = 'CNBC';

                if (detail['field_Name'] == 'price'):
                    price = detail['extracted_text'];
                    rec_cnt = rec_cnt+1;

                if (detail['field_Name'] == 'target'):
                    target = detail['extracted_text'];
                    rec_cnt = rec_cnt+1;

                if (detail['field_Name'] == 'stop loss'):
                    stop_loss = detail['extracted_text']
                    rec_cnt = rec_cnt+1;

                if (detail['field_Name'] == 'buy' or detail['field_Name'] == 'sell'):
                    recommadation = detail['extracted_text'];
                    rec_cnt = rec_cnt+1;

                if(detail['field_Name'] == 'buyPrefix' or detail['field_Name'] == 'sellPrefix'):
                    prefixStockName = detail['extracted_text']

                if (detail['field_Name'] == 'stock_Name'):
                    stock_name = detail['extracted_text']
                    rec_cnt = rec_cnt+1;

                if (detail['field_Name'] == 'broker_Name'):
                    analyst_name = detail['extracted_text'];
                    rec_cnt = rec_cnt+1;

                if (detail['field_Name'] == 'broker_firm'):
                    analyst_company = detail['extracted_text']
                    rec_cnt = rec_cnt+1;
                
                if rec_cnt>=4:
                    side=single_row['image_side'];

            if (rec_cnt >= 6 and side=='Right') or (rec_cnt >= 4 and side=='Left' ):
                if prefixStockName != '':
                    stock_name = prefixStockName+' '+stock_name

                extract_dict = {
                    'image_name': single_row['image_name'],
                    'time': single_row['time'],
                    'price': price,
                    'target': target,
                    'stop_loss': stop_loss,
                    'recommadation': recommadation,
                    'stock_name': stock_name,
                    'analyst_name': analyst_name,
                    'analyst_company': analyst_company, 'tv_chn_name': tv_chn_name
                }

                temp_extract_df = pd.DataFrame([extract_dict])
                mySQL_df = mySQL_df.append(temp_extract_df)

        return mySQL_df;

    def sinkDataToMySQL(self, mySQL_df):
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
           mySQL_df.to_sql(con=engine, name='tv_data_extract_1',if_exists='append', index=False)
        except:
           print ('Error while processing')


import time
import json
import os
import pandas as pd
from datetime import datetime
import shutil, os, glob
while 1==1:
    f=open("/home/ubuntu/TextProcessing/env/SyncToMySQL_properties.txt","r")
    props = eval (f.read())
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    if current_time>=props['end_time']:
        print(current_time,':','End time reached !!')
        break;
    if (props['exection_mode'] == 'X'):
        print(current_time,':','Exiting..')
        break;
    else:
        mysqlObj = SyncToMySQL();
        srcDir = props['srcDir']
        dstDir = props['dstDir']
        while os.listdir(srcDir):
            all_files = glob.glob(srcDir + "/*.json")
            for file in all_files:
                print(current_time,':','processing :', file)
                final_dict = open(file, "r");
                final_dict = eval(final_dict.read());
                mySQL_df = mysqlObj.processDataToSync(final_dict)
                if mySQL_df.empty == False:
                    print(current_time,':','Inserting into MqSQL ')
                    mysqlObj.sinkDataToMySQL(mySQL_df);
                    print(current_time,':','Move files to destination dir')
                shutil.move(file, dstDir);
        print(current_time,':','No more files to process !!')
        
        time.sleep(int(props['sleep_sec']))
        continue;


