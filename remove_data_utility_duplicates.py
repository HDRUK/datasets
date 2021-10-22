# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 11:10:12 2021

@author: DamonChow
"""



import pandas as pd
import requests



#Function takes in the origianl csv, gets the active datasets from the API and cleans up all duplicates while keeping any manually inputted utility scores
#csv_df is the data_utility.csv in github that needs to be read in first before any updates are made
def Update_Utility_scores(csv_df,api_url):
    
    #This section gets the Active datasets from HDR API
    r = requests.get(
            url = api_url+'/api/v2/datasets',
            params = {'fields': 'name,pid,datasetid,datasetfields.publisher','activeflag':'active'}
        )
    
    data = r.json()['datasets']
    
    
    #Preparing the dataframes, dictionaries and columns we will need later
    #csv_df = pd.read_csv(filepath) #originally used a filepath to the csv but assuming this can be replace when adding to Susheels Script
    all_columns = csv_df.columns.tolist()
    non_utility_fields = ['title','id','pid','publisher']
    utility_columns = [i for i in all_columns if i not in non_utility_fields]
    active_pid = [i.get('pid','No pid') for i in data]
    utility_dict_og = csv_df.to_dict('records') 
    utility_dict = {v.get('pid','No pid'):v for v in utility_dict_og}
    
    #Updates the API data with Keys for the Utility scores 
    #Restructuring the API data dictionary
    for item in data:
        item.pop('submittedDataAccessRequests')
        item.pop('_id')
        
        id_value =  item.pop('datasetid')
        publisher_value = item.pop('datasetfields')
        
        item.update(publisher_value)
        item.update({'id':id_value})
        
        for value in utility_columns:
            item.update({value:''})
    
    #Get the PIDs to be the Key's in the dictionary to call on
    update_dict = {v.get('pid','No pid'):v for v in data}
    
    #Updates the the datasets from the active pid with those that had manually updated utility scores from previous data utility csv
    for k,v in utility_dict.items(): 
        if k in active_pid:
            for key,value in v.items():
                if key not in non_utility_fields and pd.isna(value) == False:
                    update_dict[k].update({key:value.strip()})
                else:
                    pass
    
    final_list = [ v for k,v in update_dict.items()]
    
    final_df = pd.DataFrame(final_list).rename(columns = {'name':'title'}).reindex(columns = all_columns)  
    
    return final_df
     






def main():
    # ASSUMING THIS BOTTOM SECTION CAN BE REMOVED
    api_url = 'https://api.www.healthdatagateway.org/'
    #Add a word cleanup as well (trialling spaces etc.)
    filepath = 'C:/Users/DamonChow/Box/Damon Chow/Working/github Data utility/data_utility_original.csv'
    final_df = Update_Utility_scores(filepath,api_url)
    final_df.to_csv('C:/Users/DamonChow/Box/Damon Chow/Working/github Data utility/data_utility.csv', index = False)    




if __name__ == '__main__':
    main()


















