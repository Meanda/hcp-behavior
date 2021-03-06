# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 12:25:12 2021

@author: zhangyajie
"""
import pandas as pd
import numpy as np
from functools import reduce

# bool for laterly filter
def remove_item(n):
    return n != '999'

#load the behaviorial directory
sim_path = "D:/hcpd/hcpd_simplified/behavior_simplified_dictionary.xlsx"
sim = pd.read_excel(sim_path).fillna('999')
sim_df_dict = dict()
#generate basic dataframe 
total = pd.read_csv("D:/hcpd/HCPD_SubjInfo.csv", dtype='string').drop('age in years', axis=1)
total.columns=['src_subject_id','interview_age','sex']
total['interview_age'] = pd.Series(total['interview_age'].drop(total.index[0]).fillna('0'))
total = total.set_index('src_subject_id')


#generate dict for subtable and rename columns
beh_dir = "D:/hcpd/"
for ind,row in sim.iterrows():
    usecols = str(row[2]).split(',')+str(row[3]).split(',')+str(row[4]).split(',')+str(row[5]).split(',')+str(row[6]).split(',')
    if '999' in usecols:
        usecols =  list(filter(remove_item, usecols))
    df = pd.read_table(beh_dir+f'{row[0]}.txt', usecols=usecols)
    sim_df_dict[f'{row[0]} {row[1]}'] = df
    if 'version_form' in usecols:
        sim_df_dict[f'{row[0]} {row[1]}'] = pd.DataFrame(df[df['version_form'].str.contains(row[1])])
    if 'comqother' in usecols:
        sim_df_dict[f'{row[0]} {row[1]}'] = pd.DataFrame()
        if 'Parent' in row[1]:
            sim_df_dict[f'{row[0]} {row[1]}'] = pd.DataFrame(df[df['comqother']==f'caregiver about child subject'])
        else: 
            sim_df_dict[f'{row[0]} {row[1]}'] = pd.DataFrame(df[df['comqother']==f'subject about self'])
    col_rename = list(sim_df_dict[f'{row[0]} {row[1]}'].columns.copy())
    for index,col in enumerate(sim_df_dict[f'{row[0]} {row[1]}'].columns):
        for key,value in {3:'rawscore',4:'tscore',5:'age_corrected',6:'full_corrected'}.items():
            if col in row[key]:
                col_rename[index] = row[0]+' '+row[1]+' '+value
    sim_df_dict[f'{row[0]} {row[1]}'].columns = col_rename

# drop discription row, fill NaN, and rename several special dicts 
for name, df in sim_df_dict.items():
    sim_df_dict[name] = df.drop(df.index[0],axis=0).fillna('0')
    for col in df.columns:
        if col in ['version_form','comqother']:
            sim_df_dict[name] = df.drop(labels=col, axis=1)    
sim_df_dict['tlbx_sensation01 Words-In-Noise'].columns = ['src_subject_id','interview_age','sex','tlbx_sensation01 Litsen left_correct','tlbx_sensation01 Listen right_correct','tlbx_sensation01 Listen left_threshhold','tlbx_sensation01 Listen right_threshhold']
sim_df_dict['tlbx_motor01 Gait Speed'].columns = ['src_subject_id','interview_age','sex','tlbx_motor01 Locomotion middle_raw','tlbx_motor01 Locomotion fast_raw','tlbx_motor01 Locomotion tscore']
sim_df_dict['tlbx_motor01 Dexterity'].columns = ['src_subject_id','interview_age','sex','tlbx_motor01 Dexterity dominant_raw','tlbx_motor01 Dexterity nondom_raw','tlbx_motor01 Dexterity dominant_t','tlbx_motor01 Dexterity nondom_t','tlbx_motor01 Dexterity donimant_aj','tlbx_motor01 Dexterity nondom_aj']        
sim_df_dict['tlbx_motor01 Strength'].columns = ['src_subject_id','interview_age','sex','tlbx_motor01 Strength dominant_raw','tlbx_motor01 Strength nondom_raw','tlbx_motor01 Strength dominant_t','tlbx_motor01 Strength nondom_t','tlbx_motor01 Strength donimant_aj','tlbx_motor01 Strength nondom_aj']        
sim_df_dict['deldisk01 DELAY_3.5'].columns = ['src_subject_id','interview_age','sex','deldisk01 DELAY_3.5 auc_20 tscore','deldisk01 DELAY_3.5 auc_100 tscore']
sim_df_dict['deldisk01 PennCNP'].columns = ['src_subject_id','interview_age','sex','deldisk01 PennCNP auc_200 tscore','deldisk01 PennCNP auc_40000 tscore']
#merge subtables
df_list=[total]
for value in sim_df_dict.values():
    value = value.set_index('src_subject_id').drop(['interview_age','sex'],axis=1)
    df_list.append(value)

final_df = reduce(lambda left, right: left.join(right,  how='left'), df_list)
final_df = final_df.reset_index()

aggre = dict()    
for i in final_df.columns:
    if i != 'src_subject_id':# aggregate dataframe 
        aggre[i] = 'first'
final_df = final_df.groupby('src_subject_id', as_index=False).aggregate(aggre).reindex(columns=final_df.columns)

# generate multi-index
type_index = [0,0,0]
col_index = list(final_df.columns)
file_index = []
for i in list(col_index)[3:]:
    i = i.split(' ')[0]
    file_index.append(i)
for i in file_index:
    df = sim[sim['filename'].isin([i])]
    type_index.append(int(df.iloc[0,7]))
final_df.columns=[type_index, col_index]
# output csv file
sim_dir = 'D:/hcpd/hcpd_simplified/'
#for name, df in sim_df_dict.items():
#    df.to_csv(sim_dir+f'{name}_simplified.csv', index=False)
final_df.to_csv(sim_dir+'final_simplified.csv', index=False)

