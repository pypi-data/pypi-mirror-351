# WeaKL

**WeaKL** is a Python package for constructing **kernel methods** with **weak physical information** as introduced in the paper  
[**Forecasting time series with constraints**](https://arxiv.org/abs/2502.10485) (2025) by Nathan Doumèche, Francis Bach, Eloi Bedek, Claire Boyer, Gérard Biau, and Yannig Goude.



##  Features

- Build kernels tailored to weak information
- Compatible with NumPy and PyTorch backends  
- GPU support via PyTorch for accelerated computation  

## Installation

You can install the package via pip:

```bash
pip install weakl
```

## Resources

* **Tutorial:** [https://github.com/claireBoyer/tutorial-piml](https://github.com/claireBoyer/tutorial-piml)
* **Source code:** [https://github.com/NathanDoumeche/weakl](https://github.com/NathanDoumeche/weakl)
* **Bug reports:** [https://github.com/NathanDoumeche/weakl/issues](https://github.com/NathanDoumeche/weakl/issues)



## Citation
To cite this package:

    @article{doumèche2025forecastingtimeseriesconstraints,
      title={Forecasting time series with constraints}, 
      author={Nathan Doumèche and Francis Bach and Éloi Bedek and Gérard Biau and Claire Boyer and Yannig Goude},
      year={2025},
      journal={arXiv:2502.10485},
      url={https://arxiv.org/abs/2502.10485}
    }

# Minimum examples

## Training an additive model

```python
import pandas as pd
from weakl.utils import device, dataset_load
from weakl.additive_model import 

# Download the dataset on the French electricity load
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

hyperparameters = {"m_list": m_list,
                   "s_list": s_list,
                   "alpha_list": alpha_list}

# Training the model
dates_test = {
"begin_train": "2013-01-08 00:00:00+00:00",
"end_train": "2022-09-01 00:00:00+00:00",
"end_test": "2023-02-28 00:00:00+00:00"
}

data_hourly = half_hour_formatting(data, dates_test, features_weakl)
cov_hourly = cov_hourly_m(m_list, data_hourly)
sobolev_matrix = Sob_matrix(alpha_list, s_list, m_list)*len(data_hourly[0][0])
M_stacked = torch.stack([sobolev_matrix for i in range(48)])

# Evaluating the RMSE
perf_test, fourier_vectors_test, perf_h_test = WeakL(data, hyperparameters, cov_hourly, M_stacked, criterion=criterion)
print("The RMSE of the model is "+ str(perf_test.cpu().numpy()))
```

## Learning the hyperparameters of the additive model by grid search

## Training a model with time adaption