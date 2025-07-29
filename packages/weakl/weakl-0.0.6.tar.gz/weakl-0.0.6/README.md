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

To cite the dataset:

    @article{doumèche2023humanspatialdynamicselectricity,
      title={Human spatial dynamics for electricity demand forecasting: the case of France during the 2022 energy crisis}, 
      author={Nathan Doumèche and Yann Allioux and Yannig Goude and Stefania Rubrichi},
      year={2023},
      journal={arXiv:2309.16238},
      url={https://arxiv.org/abs/2309.16238}
    }

# Minimum examples

## Loading the dataset
To experiment the package, we provide the dataset of Doumèche et al. (2023) on the French electricity demand. The complete description of the dataset is available in the paper of Doumèche et al. (2023). 


The features of this dataset are the following time series:
* $t$ is the timestamp,  
* the French electricity load $\text{Load}_t$ at time $t$,  
* $\text{Load}_1$ and $\text{Load}_7$ are the electricity demand lagged by one day and seven days,  
* $\text{temperature}$ is the French average temperature, $\text{temperature\_smooth\_950}$, $\text{temperature\_max\_smooth\_990}$, and $\text{temperature\_min\_smooth\_950}$ are smoothed versions of $\text{temperature}$,  
* the time of year $\text{toy} \in \{1, \dots, 365\}$ encodes the position within the year,  
* the day of the week $\text{day\_type\_week} \in \{1, \dots, 7\}$ encodes the position within the week,  
* $\text{day\_type\_jf}$ is a boolean variable set to one during holidays.

Each time series is sampled at a frequency of $30$ minutes from 2013-01-08 to 2023-03-01.

To load the dataset, run the following code.

```python
from weakl.utils import dataset_load

# Download the dataset on the French electricity load
data = dataset_load()
```

## Training an additive model

In the following example, the feature variable is  
$$
X = (\text{Load}_1, \text{Load}_7, \text{temperature}, \text{temperature\_smooth\_950}, \text{temperature\_max\_smooth\_990},
$$
$$
\text{temperature\_min\_smooth\_950}, \text{toy}, \text{day\_type\_week}, \text{day\_type\_jf}, t).
$$  
Here, the target $Y = \text{Load}$ is the electricity demand, so $d_1 = 10$ and $d_2 = 1$.  
The goal is to learn the function $f^\star$ such that $\mathbb{E}(Y \mid X) = f^\star(X)$.



In this example, the additive WeaKL is $$f_\theta(x) = \sum_{\ell=1}^{10} g_\ell(x_\ell),$$ where:

* the effects $g_1$, $g_2$, and $g_{10}$ of $\mathrm{Load}_1$, $\mathrm{Load}_7$, and $t$ are linear,
* the effects $g_3,\dots, g_7$ of the temperature features and $\mathrm{toy}$ are nonlinear with $m=10$,
* the effects $g_8$ and $g_9$ of   $\text{day\_type\_week}$ and $\text{day\_type\_jf}$ are categorical with $|E| = 7$ and $|E| = 2$.


```python
from weakl.additive_model import AdditiveWeaKL
from weakl.utils import device, dataset_load
import torch as torch

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
```

## Learning the hyperparameters of the additive model by grid search

## Training a model with time adaption