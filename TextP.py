#!/usr/bin/env python
# coding: utf-8


import os
from os import listdir
from os.path import isfile, join
import string
import numpy as np
import pandas as pd
import json
#from nltk.corpus import stopwords
#import nltk
#nltk.download('stopwords')
#from unidecode import unidecode
import soundex
from difflib import SequenceMatcher
import distance
import string


class TextProcessor():
    def intializeLogger(self,logFilePath):
        import logging    
        # set up logging to file - see previous section for more details
        logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=logFilePath,
                    filemode='a')
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)
    
        # Now, we can log to the root logger, or any other logger. First the root...
        logging.info('Intialized logging ...')
        return logging
    
    def remove_metadata(self,lines):
        start=0
        for i in range(len(lines)):
            if(lines[i] == '\n'):
                start = i+1
                break
        new_lines = lines[start:]
        return new_lines
    
    def tokenize_sentence(self,line):
        words = line[0:len(line)-1].strip().split("\n")    
        words = self.preprocess(words) 
        return words
    

    def preprocess(self,words):       
        punctuations = (string.punctuation).replace("'", "") 
        punctuations=(string.punctuation).replace(".", "") 
        trans_table = str.maketrans('', '', punctuations)
        #trans_table=[ str.maketrans('', '', punctuations) for word in words]
        stripped_words = [word.translate(trans_table) for word in words]    
        words = [str for str in stripped_words if str]
        words = [ word.encode('ascii', 'ignore')  for word in words ]
        words = [ word.decode("utf-8") for word in words ]    
        p_words = []
        for word in words:
            if len(word)>0:
                if (word[0] and word[len(word)-1] == "'"):
                    word = word[1:len(word)-1]
                elif(word[0] == "'"):
                    word = word[1:len(word)]
                else:
                    word = word
                    p_words.append(word)
        words = p_words
        words = [word for word in words if not len(word) == 1]
        words = [str for str in words if str]
        words = [word.lower() for word in words]
        words = [str.replace("\r","") for str in words if str]
        words = [str.replace("\\u","") for str in words if str]
        
        words = [str.replace("â€œ","") for str in words if str]
        words = [str.replace("â€","") for str in words if str]
        words = [str.replace("â€˜","") for str in words if str]
        words = [str.replace("iâ€","") for str in words if str]
        words = [str.replace("Â°","") for str in words if str]
        words = [str.replace("Â«ss","") for str in words if str]
        words = [str.replace("^","") for str in words if str]
        words = [str.replace("Â","") for str in words if str]
        words = [str.replace("«o","") for str in words if str]
        words = [str.replace("©","") for str in words if str]
        words = [str.replace("¢","") for str in words if str]
        words = [str.replace("~","") for str in words if str]
        words = [str.replace("˜","") for str in words if str]
        words = [str.replace("‘","") for str in words if str]
        words = [str.replace("»","") for str in words if str]
        
        
        words = [str.replace("|","") for str in words if str]
        words = [str.replace(":","") for str in words if str]
        
        
        #words = [unidecode(unicode(singleWord , encoding = "utf-8")) for singleWord in words ]

        #words = [singleWord.decode('utf-8').strip() for singleWord in words ]
        #words = [singleWord.encode('ascii',errors='ignore') for singleWord in words if 1==1]
        #words = [str.decode("utf-8") for singleWord in words if 1==1]
        #words = [str.decode("utf-8") for singleWord in words if 1==1]

        words = [word for word in words if len(word) > 2]
        return words
        
            
    def word2vec(self,word):
        from collections import Counter
        from math import sqrt

        # count the characters in word
        cw = Counter(word)
        #print (cw)
        # precomputes a set of the different characters
        sw = set(cw)
        #print (sw)
        # precomputes the "length" of the word vector
        lw = sqrt(sum(c*c for c in cw.values()))
        #print (lw)
    
        # return a tuple
        return cw, sw, lw
    
    
    def cosdis(self,v1, v2):
        # which characters are common to the two words?
        common = v1[1].intersection(v2[1])
        # by definition of cosine distance we have
        return sum(v1[0][ch]*v2[0][ch] for ch in common)/v1[2]/v2[2]

    
    def readData(self,logging,pathFile):
        import pandas as pd
        #logging.info('Reading the data from ',pathFile);
        raw_text=pd.read_csv(pathFile);
        return raw_text;
    

    def preProcessData(self,logging,raw_text):       
        config='';
        formated_list=[];
        image_name=''
        columns_list=['Image_name','config','formated_word']
        dataFrame_formated = pd.DataFrame(columns=columns_list)

        for index, row in raw_text.iterrows():
            words=[]
            words1=[]
            side=''
            
            if (str(row['Text']).strip() != "" and str(row['Text'])!='nan'):
                append_word=" | ";
                words=row['Text']+append_word
                words=self.remove_metadata(words)
                words=self.tokenize_sentence(words)
                #logging.info('formated text : ',words)
                
            if (str(row['SN_L-SD_R']).strip() != "" and str(row['SN_L-SD_R'])!='nan'):
                append_word=" | ";
                words1=row['SN_L-SD_R']+append_word
                words1=self.remove_metadata(words1)
                words1=self.tokenize_sentence(words1)
                #logging.info('SN_L-SD_R text',words1)    
        
            if len(words) !=0 :
                words=words1+words
                #logging.info('combined word',words)
                
                if row['Config']=='Right':
                    side='Right'
                elif row['Config']=='Left':
                    side='Left'
            
            temp_dict={
                'Image_name':row['Image_Name'],
                'config':side,
                'formated_word':[words]
            }
            #logging.info('temp_dict : ',temp_dict)
            #logging.info('--------------------------------------------------------------------------------------------')
            temp_df=pd.DataFrame(temp_dict)
            
            dataFrame_formated=dataFrame_formated.append(temp_df)
            #formated_list.append(words)
        return dataFrame_formated    
    
    
    def selective_words_fuc(self,logging,config):
        #print ('printed config',config)
        selective_temp_words=[]
        for fields_details in config['fields_details']:
            if ((fields_details['primary_config']['isPrimary']) == 'Y'):
                selective_temp_words.append(fields_details['primary_config']['raw_field'])
            else:
                selective_temp_words.append([fields_details['field_Name']])
        #logging.info(selective_temp_words)
        selective_words = [x for sublist in selective_temp_words for x in sublist]
        #logging.info(selective_words)
        return selective_words

    def retrive_threshold(self,logging,field_Name,config):
        for fields_details in config['fields_details']:
            if (fields_details['field_Name'] == field_Name):
                return float (fields_details['primary_config']['simliarity_threshold'])

            
    def getMethodDetails(self,logging,field_Name,config):
        for fields_details in config['fields_details']:
            if (fields_details['field_Name'] == field_Name):
                return fields_details['Call_method']
            

    def getFieldsDetails(self,field_name,config):
        for i in range(0,int(len(field_name))-1):
            differnet_fields=config['fields_details']
            if(differnet_fields[i]['field_Name'] == field_name):
                return (differnet_fields[i])

    def getPrimaryORSecondary(self,field_Name,config):
        for fields_details in config['fields_details']:
            if (fields_details['field_Name'] == field_Name):
                return fields_details['primary_config']['isPrimary']
            
    def getSencondaryDetails(self,field_Name,config):
        for fields_details in config['fields_details']:
            if (fields_details['field_Name'] == field_Name):
                return fields_details['secondary_config']
            
    def filterOutRecords(self,logging,dataFrame_formated):
        final_list=[]
        count_threshold=4
        config={}
        columns_list=['Image_name','config','formated_word']
        refined_formated = pd.DataFrame(columns=columns_list)
        
        for index, each_line in dataFrame_formated.iterrows():
            str_config=str(each_line['config'])
            if str_config == 'Left':
                config=left_config
            elif str_config == 'Right':
                config=right_config
            else:
                config=left_config    
            selective_words_v=self.selective_words_fuc(logging,config)
            
            count_key_words=0
            added_var=False
            #logging.info("----------------------------------------------------------------------------------")
            #logging.info('each_line : ',each_line)
            #logging.info('formated_word :',each_line['formated_word'])
            for row in each_line['formated_word']:
                #logging.info("----------------------------------------------------------------------------------")
                for selectedWord in selective_words_v:
                    formatted_each_word=row
                    #logging.info('formatted_each_word :',formatted_each_word)
                    #logging.info('Check if ',selectedWord,' word is present in the ',formatted_each_word)
            
                    va = self.word2vec(str(formatted_each_word))
                    vb = self.word2vec(str(selectedWord))
                    #print (str(formatted_each_word),'----',str(selectedWord),'----',self.cosdis(va,vb))
                
                    if (self.cosdis(va,vb) > float(self.retrive_threshold(logging,selectedWord,config)) ):
                        #logging.info('')
                        count_key_words=count_key_words+1
                        #logging.info('worked : ',formatted_each_word,'-',selectedWord)
                        #logging.info('count_key_words :',count_key_words)
                        #logging.info('count_key_words>=count_threshold :',count_key_words>=count_threshold)
                        #logging.info('added_var :',added_var)
                        #logging.info('')
                    if(count_key_words>=count_threshold and added_var==False):
                        #logging.info('added')
                        added_var=True
                        final_list.append(each_line)
                        temp_dict={
                            'Image_name':each_line['Image_name'],
                            'config':each_line['config'],
                            'formated_word':[each_line['formated_word']]
                        }
                        temp_df=pd.DataFrame(temp_dict)
                        refined_formated=refined_formated.append(temp_df)
                    
                        #logging.info("----------------------------------------------------------------------------------")
                    #else:
                            #logging.info('Not present !!!') 
        return refined_formated;

    
    def evaluateField(self,logging,orgText,findText,threshold):
        #print ('orgText : ',orgText,' findText :',findText,' threshold: ',threshold)
        inVar=False
        soundVar=False
        cosDis=False
        similarVar=False
        distVar=False
    
        inVar=orgText in findText
        s=soundex.getInstance()
        soundVar=s.soundex(orgText) == s.soundex(findText) 
        #logging.info ('inVar ',inVar)
        #logging.info ('soundVar ',soundVar)
        if (inVar==True or soundVar==True):
            return orgText
        else:
            w1=self.word2vec(str(orgText))
            w2=self.word2vec(str(findText))
        
            #logging.info ('cosdis :',self.cosdis(w1,w2))
            if self.cosdis(w1,w2) > float(threshold):
                cosDis=True
        
            #logging.info ('seq match :',SequenceMatcher(a=orgText,b=findText).ratio())
            if SequenceMatcher(a=orgText,b=findText).ratio()>float(threshold):
                similarVar=True
        
            #print ('levenshtein:',distance.levenshtein(orgText,findText))
            if distance.levenshtein(orgText,findText)<=8:
                distVar=True
        
            if (cosDis==True and similarVar==True and distVar==True):
                return orgText
            else:
                return ""
    
    def retriveFieldName(self,logging,single_word,selectedWord,config):
        #logging.info('-------------------------------------------------------------')
        string_ops=single_word.find(selectedWord)>=0
    
        if(string_ops):
            return selectedWord
        else:            
            sim_threshold=self.retrive_threshold(logging,selectedWord,config)
            if (sim_threshold == None):
                   sim_threshold=.99 
            return self.evaluateField(logging,selectedWord,single_word,sim_threshold);        

    def callFactoryMethod(self,logging,field_name,single_word,single_line_cpy,detail_dict,config):
        #logging.info('callFactoryMethod:')
        method_Name=self.getMethodDetails(logging,field_name,config)
        #print ('method Name :',method_Name)
        if (method_Name == 'blankInBetween'):
            #logging.info('++++++++++++++++++++++++++++++++++++++++++++++++')
            #logging.info('Sending -',field_name,single_word)
            result_text=self.blankInBetween(logging,field_name,single_word)
            #logging.info("called blankInBetween-",result_text)
            #logging.info('++++++++++++++++++++++++++++++++++++++++++++++++')
            return result_text
        elif (method_Name=='getFullrecord'):
            derived_word,sec_postion=self.getFullrecord(logging,field_name,single_word,single_line_cpy,detail_dict,config)
            return derived_word,sec_postion;
        elif (method_Name=='checkIfAvailable'):
            result_text,sec_postion=self.checkIfAvailable(logging,field_name,single_word,single_line_cpy,detail_dict,config)
            return result_text,sec_postion;
        elif (method_Name=='getfullRecordInbetween'):
            result_text,sec_postion=self.getfullRecordInbetween(logging,field_name,single_word,single_line_cpy,detail_dict,config)
            return result_text,sec_postion;
        else :
            return "Didnt match";

    def checkIfAvailable(self,logging,field_Name,single_word,single_line_cpy,detail_dict,config):
        #logging.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        #logging.info('field_Name : ',field_Name)
        #logging.info('single_word : ',single_word)
        #logging.info('single_line_cpy : ',single_line_cpy)
        
        if (self.getPrimaryORSecondary(field_Name,config) == 'Y'):
            #logging.info('This is primary !!')        
            #if primary return the word just like that
            return single_word,None;
        else:
            #logging.info('This is secondary !!')
            #if we have before or after need to check if that field is gathered corretly
            secodary_dict=self.getSencondaryDetails(field_Name,config)
            dependency_field_Name=secodary_dict['dependency_field_Name']
            field_postion=""

            for details_ind in detail_dict:
                #logging.info('details_ind : ',details_ind)
                if (details_ind['field_Name']==dependency_field_Name):
                    field_postion=details_ind['postion_extracted']
                    how_many_section=secodary_dict['how_many_section']
                    #logging.info('field_postion : ',field_postion)
                    #logging.info('how_many_section : ',how_many_section)
                
                    #if secondary parse the word need to check if its before or after a word
                    #if they are gathered +1 for before and -1 for after
                    if(field_postion !=None):
                    
                        if secodary_dict['access_type']=='before':
                            #logging.info('before method')
                            if field_postion-int(how_many_section) >= 0:
                                inVar=False;
                                soundVar=False;
                                lineVar=False;
                                inVar=field_Name in single_line_cpy[field_postion-int(how_many_section)]
                                s=soundex.getInstance()
                                soundVar=s.soundex(field_Name) == s.soundex(single_line_cpy[field_postion-int(how_many_section)]) 
                                                                
                                if (inVar==True or soundVar==True):
                                    return field_Name,field_postion-int(how_many_section)
                                else:
                                    for single_rec_Num in range(0,len(single_line_cpy)):
                                        lineVar=field_Name in single_line_cpy[single_rec_Num]
                                        if (lineVar==True):
                                            return field_Name,single_rec_Num
                                        else:
                                            return None,None
                            else:
                                return None,None
                        
                        elif secodary_dict['access_type']=='after':
                            if field_postion-int(how_many_section) >= 0:
                                inVar=False;
                                soundVar=False;                                
                                inVar=field_Name in single_line_cpy[field_postion+int(how_many_section)]
                                s=soundex.getInstance()
                                soundVar=s.soundex(field_Name) == s.soundex(single_line_cpy[field_postion+int(how_many_section)]) 
                                if (inVar==True or soundVar==True):
                                    return field_Name,field_postion+int(how_many_section)
                                else:
                                    for single_rec_Num in range(0,len(single_line_cpy)):
                                        lineVar=field_Name in single_line_cpy[single_rec_Num]
                                        if (lineVar==True):
                                            return field_Name,single_rec_Num
                                        else:
                                            return None,None
                            else:
                                return None,None
                    else:
                        return None,None
        return None,None

    
    def getfullRecordInbetween(self,logging,field_Name,single_word,single_line_cpy,detail_dict,config):
        secodary_dict=self.getSencondaryDetails(field_Name,config)
        field_one=secodary_dict['FieldOne']
        field_two=secodary_dict['Fieldtwo']
        total_sec=secodary_dict['how_many_section']
        field_one_postion=''
        field_two_postion=''
        #logging.info ('field_one :',field_one)
        #logging.info ('field_two :',field_two)
        #logging.info ('total_sec ',total_sec)
        for details_ind in detail_dict:
            #logging.info ('details_ind[field_Name]',details_ind['field_Name'])
            #logging.info ('field_one:',field_one)
            #logging.info (details_ind['field_Name']==field_one)
            if (field_one_postion=='' and details_ind['field_Name']==field_one):
                field_one_postion=details_ind['postion_extracted']
            
            if (field_two_postion=='' and details_ind['field_Name']==field_two):
                field_two_postion=details_ind['postion_extracted']
        
        #logging.info ('field_one_postion : ',field_one_postion)
        #logging.info ('field_two_postion : ',field_two_postion)
        
        if (field_one_postion!='' and field_two_postion!=''):
            # check if we have the record in the 
    
            if((int(field_two_postion)-int(field_one_postion))-1 > 0):
                ## Currently gets only one postion details
                postion=int(field_two_postion)-1;
                data_retrived=single_line_cpy[int(field_two_postion)-1];
                #logging.info ('postion :',postion,' data_retrived:',data_retrived);
                return data_retrived,postion;    
            else:
                return None,None
        else:
            return None,None
            
    
    def getFullrecord(self,logging,field_Name,single_word,single_line_cpy,detail_dict,config):
        if (self.getPrimaryORSecondary(field_Name,config) == 'Y'):
            #logging.info('This is primary !!')        
            #if primary return the word just like that
            return single_word,None;
        else:
            #logging.info('This is secondary !!')
        
            #if we have before or after need to check if that field is gathered corretly
            secodary_dict=self.getSencondaryDetails(field_Name,config)
            dependency_field_Name=secodary_dict['dependency_field_Name']
            field_postion=""
        
            for details_ind in detail_dict:
                if (details_ind['field_Name']==dependency_field_Name):
                    field_postion=details_ind['postion_extracted']
                    how_many_section=secodary_dict['how_many_section']
                    #if secondary parse the word need to check if its before or after a word
                    #if they are gathered +1 for before and -1 for after
                    if(field_postion !=None):
                        if secodary_dict['access_type']=='before':
                            #logging.info('inside getFullrecord 3:',detail_dict)
                            if field_postion-int(how_many_section) >= 0:
                                try:
                                    return single_line_cpy[field_postion-int(how_many_section)],field_postion-int(how_many_section)
                                except:
                                    return None,None
                            else:
                                return None,None
                        elif secodary_dict['access_type']=='after':
                            #logging.info('inside getFullrecord 3:',detail_dict)
                            if field_postion+int(how_many_section) >= 0:
                                try:
                                    return single_line_cpy[field_postion+int(how_many_section)],field_postion+int(how_many_section)
                                except:
                                    return None,None
                            else:
                                return None,None
                    else:
                        return None,None
        return None,None

    def blankInBetween(self,logging,field_Name,single_word):
        #logging.info (field_Name,'-',single_word)
        field_Name_list=field_Name.split()
        #logging.info ('field_Name_list','-',field_Name_list)
        if (len(field_Name_list)<1):
            #logging.info ('len(field_Name_list)<1',len(field_Name_list)<1)
            return ""   
        elif(len(field_Name_list)==1):
            #logging.info ('len(field_Name_list)==1',len(field_Name_list)==1)
            split_words_list=single_word.split()
            if (len(split_words_list) == 1):
                #logging.info ("len(split_words_list)",len(split_words_list))
                return ""
            elif (len(split_words_list) == 2):
                #logging.info (split_words_list[1])
                return split_words_list[1]
            elif (len(split_words_list) >2):
                #logging.info ('(len(split_words_list) >2) ',len(split_words_list) >2 ) 
                field_Name_lenght=len(field_Name)
                single_word_lenght=len(single_word)
                if (single_word_lenght>field_Name_lenght):
                    return str(single_word[field_Name_lenght:single_word_lenght]).strip()
                else:
                    return ""
        elif(len(field_Name_list)>=2):
            #logging.info ('len(field_Name_list)>=2',len(field_Name_list)>=2)
            field_Name_lenght=len(field_Name)
            single_word_lenght=len(single_word)
            if (single_word_lenght>field_Name_lenght):
                return str(single_word[field_Name_lenght:single_word_lenght]).strip()
            else:
                split_words_list=single_word.split();
                if (len(split_words_list) == 2):
                    return split_words_list[1];
                else:
                    return ""
                
   
    def refreshSelective_words(self,selective_words_v):
        field_dict={}
        for selectedWord in selective_words_v:
            field_dict[selectedWord]='N'
        return field_dict

    def createDetailedDif(self,field_Name):
        detailed_dif={ 
            "field_Name":field_Name,
            "extracted_text":"",
            "postion_extracted":""
        }
        return detailed_dif;

    def extracInformation(self,logging,refined_formated):
        final_dict={}
        extracted_data=[]
        field_dict={}
        #for single_line in final_list:
        for index, row in refined_formated.iterrows():
            config={}
            str_config=row['config']
            #logging.info ('str_config',str_config)
            if str_config == 'Left':
                config=left_config
            elif str_config == 'Right':
                config=right_config
            else:
                config=left_config   
            selective_words_v=self.selective_words_fuc(logging,config)
            single_line=row['formated_word']

            solution_dict={}
            solution_dict['Raw_text']=single_line
            solution_dict['image_side']=str_config
            solution_dict['image_name']=row['Image_name']
            solution_dict['time']=row['Image_name'][0:19]
            
            #print ('----------------------------------------------------------------------')
            #print ('Current line that is processed',single_line)
            #print ('----------------------------------------------------------------------')
            
            details_dict=[]
            individual_field={}
            field_dict= self.refreshSelective_words(selective_words_v)
            for single_word in single_line:        
                for selectedWord in selective_words_v:
                    if field_dict[selectedWord] == 'N':
                        #print('========================================')
                        #print('field_dict : ',field_dict)
                        #print('single words processed :',single_word)
                        #print('selectedWord :',selectedWord)
                        #print('========================================')
                        #if primary
                        if self.getPrimaryORSecondary(selectedWord,config) == 'Y':

                            #print('Check if ',selectedWord,' word is present in the ',single_word)
                            field_name=self.retriveFieldName(logging,single_word,selectedWord,config)
                            #print ('feild_name retrived : ',field_name)

                            if (field_name!=""):
                                #print(field_name," its primary")
                                individual_field=self.createDetailedDif(field_name)
                                fetched_value =self.callFactoryMethod(logging,field_name,single_word,single_line,details_dict,config)
                                #details_dict[field_name]=fetched_value
                                #print('fetched_value : ',fetched_value)
                                individual_field['extracted_text']=fetched_value
                                individual_field['postion_extracted']=single_line.index(single_word)
                                field_dict[selectedWord] = 'Y'
                                details_dict.append(individual_field)
                                break;
                            else:
                                continue;
                                
            for selectedWord in selective_words_v:
                if field_dict[selectedWord] == 'N':
                    #logging.info ('========================================')
                    #logging.info ('field_dict : ',field_dict)
                    #logging.info ('single words processed :',single_word)
                    #logging.info ('selectedWord :',selectedWord)
                    #logging.info ('========================================')

                    if self.getPrimaryORSecondary(selectedWord,config) == 'N':
                        #logging.info ('-----------------------------------------------------------------------------------------')
                        #logging.info (selectedWord," its secondary")
                        #logging.info ('')
                        #logging.info ('before executing sec: ',details_dict)
                        details_dict_cpy=details_dict
                        fetched_value,sec_postion =self.callFactoryMethod(logging,selectedWord,single_word,single_line,details_dict_cpy,config)
                        #logging.info (" secondary value fetched : ",fetched_value," postion : ",sec_postion)

                        if fetched_value != None and sec_postion != None :
                            #logging.info ('')
                            individual_field=self.createDetailedDif(selectedWord)
                            individual_field['extracted_text']=fetched_value
                            individual_field['postion_extracted']=sec_postion
                            field_dict[selectedWord] = 'Y'
                            #logging.info ('')

                            details_dict.append(individual_field)      
                            #logging.info ('-----------------------------------------------------------------------------------------')
                            #break;

            solution_dict['Details']=details_dict
            #logging.info (solution_dict)
            #logging.info ('-----------------------------------------------------------------------------------------')
            extracted_data.append(solution_dict)

        final_dict['extracted_data']=extracted_data;
        return final_dict
    
    def __init__(self):
        print ('Class is built')



import time
import json
import os
import pandas as pd
from datetime import datetime
import shutil, os, glob

import sys
import warnings
import json
warnings.simplefilter("ignore")

## Creating object for the object 
textP=TextProcessor()

## Creating the logger files 
logging=textP.intializeLogger('/home/ubuntu/TextProcessing/log/TextProcessing.log');
logging.info('All set now !!!');
logging.info('reading the data ');

while 1==1:
    f=open("/home/ubuntu/TextProcessing/env/TextP_properties.txt","r")
    props = eval (f.read())
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    if current_time>=props['end_time']:
        print('End time reached !!')
        break;
    if (props['exection_mode'] == 'X'):
        print ('Execution mode X is set so exiting ..')
        break;
    else:
        ##### Configration for CNBC channel
        os.chdir(props['config_file']);
        left = open("left_config.txt", "r")
        left_config = eval(left.read())
        
        right = open("right_config.txt", "r")
        right_config=eval(right.read())
        
        srcDir=props['srcDir'];
        dstDir=props['dstDir'];
        while os.listdir(srcDir):
            all_files = glob.glob(srcDir + "/*.csv")
    
            for file in all_files:
                
                os.chdir(props['srcDir']);
                ## Reading the in directory files
                print ('currently processing file :',file )
                try:
                    raw_text=textP.readData(logging,file);
                    dataFrame_formated=textP.preProcessData(logging,raw_text)
                    
                    ## Filter out only valid data
                    filtered_formated=textP.filterOutRecords(logging,dataFrame_formated)

                    ## Extract information only from valid data
                    result_json=textP.extracInformation(logging,filtered_formated)
        
                    now = datetime.now()
                    current_time = now.strftime("%d_%m_%Y_%H_%M_%S")
                    file_name='CNBC_'+current_time+'_'+str(now.microsecond)+'.json'
                    print ('file_name:',file_name)
        
                    ## writing the data to the output dir
                    os.chdir(props['outFile']);
                    with open(file_name, 'w') as outfile:
                        json.dump(result_json,outfile,ensure_ascii=False)      
                except:
                    print ('Error while processing !!')
                shutil.move(file, dstDir);
                print ('file moved :',file)
                print ('------------------------------------------------------')
        print ('No more files to process')
        time.sleep(int(props['sleep_sec']))
        continue;