import numpy as np
import pandas as pd
import torch

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def is_running_on_gpu():
  if torch.cuda.is_available():
    print("The algorithm is running on GPU.")
  else:
    print("The algorithm is not running on GPU.")

torch.set_default_dtype(torch.float64)
np_dtype = np.float64


def dataset_load():
    url = "https://zenodo.org/records/10041368/files/dataset_national.csv"
    df = pd.read_csv(url)

    columns = ["date", "tod", 
            "Load", "Load_d1", "Load_d7",
            "temperature_smooth_950", "temperature", "temperature_max_smooth_990", 'temperature_min_smooth_950',
                'toy', 'day_type_week', "day_type_jf"]
    
    data = df[columns].copy()
    data['day_type_week']=np.float64(data.loc[:,'day_type_week'])
    data.rename(columns={'date':'Time'}, inplace=True)
    n = len(data['Time'])
    data['time'] = [i/n*np.pi for i in range(n)]
    return data
