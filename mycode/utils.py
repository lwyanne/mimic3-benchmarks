''' This module contains code to handle data '''

import os
import numpy as np
import scipy
import sys
from matplotlib import pyplot as plt
import pathlib
import pandas as pd
from json import JSONEncoder
import json
from tqdm import tqdm

n_cont=3097
n_cat=4092



def createItemPositionDict(file):
    """create dict[itemID]->variableIndex,
    the continuous items are arranges in front of the categorical items.
    """
    dic={}
    l=[]
    with open(file) as f:
        content=f.readlines()
        for line in content:
            id=int(line.lstrip().rstrip())
            l.append(id)
        f.close()
        l=list(set(l))
    dic=dict(zip(l,list(range(len(l)))))
    return dic

def createTypeDict(file):
    """Build a dictionary: typeDic[itemID]->boolean(isCategory)
    """
    typeDict={}
    df=pd.read_csv(file)
    itemIDs=df['itemID'].tolist() 
    types=df['isCategory'].tolist() #0 for continuous, 1 for categorical
    typeDict=dict(zip(itemIDs,types))
    return typeDict

class PatientHandler(object):
    """args
    ::task: 'imp' for Inhospital Mortality prediction, 'sa' for survival analysis
    """
    def __init__(self,variableList,task='imp'):
        self.task=task
        dataPath=os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir),'data','root'))
        self.dataPath=dataPath
        self.variableList=variableList
       #self.typeDict=createTypeDict(os.path.join(dataPath,'itemType.csv'))
        self.deleteNeeded=set()

    def gen_list(self, validStrategy='holdout',validrate=0.1):
        """Generate the list of patientIDs in training set, validation set, and test set
        """
        self.trainvalPath=os.path.join(self.dataPath,'train')
        self.testPath=os.path.join(self.dataPath,'test')
        trainval=[f for f in os.listdir(self.trainvalPath)] 
        self.len_trainval=len(trainval)
        self.trainFiles=trainval[:-int(self.len_trainval*validrate)]
        self.valFiles=trainval[int(self.len_trainval*validrate):]
        self.testFiles=[f for f in os.listdir(self.testPath)]

    def gen_data(self):
        """
        Generate 'variables' for each patient in its own directory.
        The 'variables' contains items that belong to Table `labevents` and Table `chartevents`
        The whole process was performed directly on the results 'event.csv' generated by the MIMIC-benchmark codes.
        #TODO: exclude those patients with multiple episodes, or seperate each episode
        """
        self.gen_list()
        with tqdm(total=100) as pbar:
            flag=0
            totallen=self.len_trainval+len(self.testFiles)
            for (filetype,filedir) in zip([self.trainFiles,self.valFiles,self.testFiles],[self.trainvalPath,self.trainvalPath,self.testPath]):
                for patient in filetype:
                    patientPath=os.path.join(filedir,patient)
                    if os.path.exists(os.path.join(patientPath,'variables.npy')):
                    #     os.remove(os.path.join(patientPath,'variables.npy'))
                    #     continue
                    # else:
                    #     continue
                        flag+=1
                        if flag%int((totallen/1000))==0:pbar.update(0.1)
                        continue
                    df=pd.read_csv(os.path.join(patientPath,'events.csv'))
                    #print('read patient %s done'%patient)
                    nrow=df.shape[0]
                    
                    orderedTime=np.sort(df['CHARTTIME'].unique())
                    duation=len(orderedTime)
                    timeDic=dict(zip(list(orderedTime),list(range(duation))))
                    with open(os.path.join(patientPath,'timeList.txt'), 'w') as fp:
                        for i in orderedTime:
                            fp.write('%s,'%i)
                    matrix=np.full((duation,len(self.variableList)),np.nan,dtype=float)
                    #Df=pd.DataFrame(index=orderedTime,columns=self.variableList,dtype=float)
                    for i in range(nrow):
                        try:matrix[timeDic[df.iloc[i,3]],itemDic[df.iloc[i,4]]]=df.iloc[i,5] #TODO: Check the valueom
                        except KeyError: continue
                        except ValueError:
                            self.deleteNeeded.add(df.iloc[i,4])
                            continue
                    #print('matrix generated\n')
                    np.save(os.path.join(patientPath,'variables.npy'),matrix)

                    flag+=1
                    if flag%int((totallen/1000))==0:pbar.update(0.1)
                    # del matrix,orderedTime,timeDic,nrow,duation,df

    def get_one(self,patientID):
        if type(patientID)==int: patientID=str(patientID)
        train=os.path.join(self.trainvalPath,patientID)
        test=os.path.join(self.testPath,patientID)
        if os.path.exists(train): return os.path.abspath(train)
        elif os.path.exists(test): return os.path.abspath(test)
        else: print ("patient does not exist!!!")

    def read_individual(self,patient):
        """
        arg:patient: str or int of patientID
        """
        if os.path.isdir(patient)==False: patient=self.get_one(patient)
        matrix=np.load(os.path.join(patient,'variables.npy'),allow_pickle=True)
        if self.task == 'imp':
            # select those timepoints before the 48th hour in ICU
            temp=pd.read_csv(os.path.join(patient,'stays.csv'))
            intime=temp['INTIME'][0] # Currently only consider the first ICU STAY #TODO:
            flagtime=temp['INTIME'][0]                                          

    def write_delete(self):
        if not os.path.exists('delete.csv'):
             with open('delete.csv','w') as f:
                for i in self.deleteNeeded:
                    f.write('%d\n'%i)






itemDic=createItemPositionDict(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir),'myvariablesList.csv'))
#                    os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir),'data','root','categoricalItems.csv'))])   
# itemlen=len(item_dic)
# #item_dic[861]

# ProcessDict()
variableList=pd.read_csv(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir),'myvariablesList.csv'),header=None).values.tolist()
patientHandler=PatientHandler(variableList)
patientHandler.gen_data()
patientHandler.write_delete()
   