#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SyncToMySQL():
    
    def get_cosine_sim(self,*strs): 
        vectors = [t for t in self.get_vectors(*strs)]
        return cosine_similarity(vectors)
    
    def get_vectors(self,*strs):
        text = [t for t in strs]
        vectorizer = CountVectorizer(text)
        vectorizer.fit(text)
        return vectorizer.transform(text).toarray()

    # helper function
    def get_indexes_max_value(self,lst):
        max_value = max(lst)
        if lst.count(max_value) > 1:
            return [i for i, x in enumerate(lst) if x == max(lst)]
        else:
            return lst.index(max(lst))
    
    def get_ticker_cosine_sim(self,stock_name):
        df_tickers = pd.read_csv("/home/ubuntu/TextProcessing/config/tickers.csv", header = 0)
        df_tickers['NAME OF COMPANY']=df_tickers['NAME OF COMPANY'].str.lower()
        tic = ""
        # filter records based on words in stock name
        stock_name_strs = stock_name.split()
        #print(stock_name_strs)
        sub_strs = ('|'.join(stock_name_strs))
        #print(sub_strs)
        filtered_df = df_tickers[df_tickers['NAME OF COMPANY'].str.contains(sub_strs)]
        if filtered_df.empty:
            return tic
        names = filtered_df['NAME OF COMPANY']
        #print(names.values)
        company_name = []
        cos_sim = []
        for i in range(len(names.values)):
            #print(names.values[i])
            #print(stock)
            cs = self.get_cosine_sim(stock_name,names.values[i])[0][1]
            #print(cs)
            if cs > 0:
                company_name.append(names.values[i])
                cos_sim.append(cs)
        #print(cos_sim)
        if len(cos_sim) == 0:
            return ""
        max_indices = self.get_indexes_max_value(cos_sim)
        if type(max_indices) is list:
            snames = [company_name[i] for i in max_indices]
            #print(snames)
            sub_str_cnt = []
            for i in range(len(snames)):
                sub_cnt = 0
                for s in stock_name_strs:
                    if snames[i].find(s) != -1:
                        sub_cnt = sub_cnt + 1
                sub_str_cnt.append(sub_cnt)
            #print(sub_str_cnt)
            max_substr_indices = self.get_indexes_max_value(sub_str_cnt) 
            #print(max_substr_indices)
            maxpos = 0
            if type(max_substr_indices) is list:
                #print('list')
                maxpos = max_substr_indices[0]
            else:
                maxpos = max_substr_indices
            #print('maxpos')
            #print(maxpos)
            c_name = snames[maxpos]
            #print(c_name)
            tic = filtered_df[filtered_df['NAME OF COMPANY'] == c_name]['SYMBOL'].values
            #print(tic)
        else:
            c_name = company_name[max_indices]
            tic = filtered_df[filtered_df['NAME OF COMPANY'] == c_name]['SYMBOL'].values
            #print(tic)
    
        if len(tic) != 0:
            return tic[0]
        else:
            return ""
    
    def processDataToSync(self, final_dict):
        columns_list = ['image_name', 'time', 'price', 'target', 'stop_loss', 'recommadation', 'stock_name',
                        'analyst_name', 'analyst_company', 'tv_chn_name','NSE_ticker']
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
            ticket_name='';
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
                    print ('Stock Name :',stock_name)
                    try:
                        if (stock_name != None or stock_name != ''):
                            ticket_name=self.get_ticker_cosine_sim(stock_name);
                            print ('Ticker retrived :',ticket_name)
                    except:
                        print ('Error occured while selecting the ticker value');
                        
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
                    stock_name = prefixStockName+' '+stock_name;

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
                    'tv_chn_name': tv_chn_name,
                    'NSE_ticker':ticket_name
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



