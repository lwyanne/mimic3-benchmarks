from utils import *
itemDic=createItemPositionDict(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir),'myvariablesList.csv'))
l1=pd.read_csv(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir),'myvariablesList.csv'),header=None).values.tolist()
l2=pd.read_csv(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir),'delete.csv'),header=None).values.tolist()
l=list(set(l1)-set(l2))
variableList=l
patientHandler=PatientHandler()
patientHandler.gen_data(variableList)
#patientHandler.write_delete()