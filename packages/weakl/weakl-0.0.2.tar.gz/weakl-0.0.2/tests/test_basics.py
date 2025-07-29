import src.weakl.adaptive as adapt
from src.weakl.additive_model import AdditiveWeaKL
from src.weakl.utils import device, dataset_load
import pandas as pd
import numpy as np
import torch as torch

def test_dataset():
    data = dataset_load()

    # Defining the additive model
    features_weakl = {
    "features": ["Load_d1", "temperature_smooth_950", "temperature",
                "temperature_max_smooth_990", 'temperature_min_smooth_950',
                'toy',  'day_type_week', 'day_type_jf', 'Load_d7','time'],
    "features_type":['linear','regression','regression','regression','regression', 
                'regression','categorical7','linear','linear','linear']
    }

    features_weakl["masked"] = features_weakl["features_type"].copy()

    # Setting the hyperparameters of the model
    m_list = ['Linear', 10, 10, 10, 10, 10, 4, 'Linear', 'Linear', 'Linear']
    alpha_list = torch.tensor([1.0000e-30, 1.0000e-30, 1.0000e-05, 1.0000e-03, 1.0000e-03, 1.0000e-04, 1.0000e-08, 1.0000e-30, 1.0000e-30, 1.0000e-30, 1.0000e-30],
        device=device)
    s_list = ['*', 2, 2, 2, 2, 2, 0, '*', '*', '*']

    # Training the model
    dates = {
    "begin_train": "2013-01-08 00:00:00+00:00",
    "end_train": "2022-09-01 00:00:00+00:00",
    "end_test": "2023-02-28 00:00:00+00:00"
    }

    model = AdditiveWeaKL(m_list, s_list, alpha_list)
    model.fit(data, dates, features_weakl)

    

    # Evaluating the RMSE
    rmse_hourly = model.rmse_hourly
    rmse = model.rmse
    print("The RMSE of the model is "+ str(rmse))
    assert True