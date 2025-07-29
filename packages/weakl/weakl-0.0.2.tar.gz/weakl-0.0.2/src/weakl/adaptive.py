from datetime import timedelta
import pandas as pd
import torch

from weakl.utils import device
from weakl.additive_model import normalize, transform, sob_effects, create_grid



def calculate_total_length(m_list):
    return 1 + sum(2 * m if m != "Linear" else 1 for m in m_list)

def mat_frequency_online(m_list):
    total_length = calculate_total_length(m_list)
    frequencies = torch.zeros(total_length, device=device)

    idx = 1
    for m in m_list:
        if m == "Linear":
            idx += 1
        else:
            freq_range = torch.arange(1, m + 1, device=device)
            frequencies[idx:idx + m] = -freq_range.flip(0)
            frequencies[idx + m:idx + 2 * m] = freq_range
            idx += 2 * m

    return frequencies.unsqueeze(0).unsqueeze(0).unsqueeze(0)

def mat_linear_online(x_data, m_list):
    batch_size, steps, n, d = x_data.shape
    total_columns = calculate_total_length(m_list)
    mat = torch.zeros(batch_size, steps, n, total_columns, device=device)

    col_idx = 1
    for i, m in enumerate(m_list):
        if m == 'Linear':
            mat[:, :, :, col_idx] = x_data[:, :, :, -1] - 1
            col_idx += 1
        else:
            col_idx += 2 * m
    return mat

def mat_data_online(x_data, m_list):
    batch_size, steps, n, d = x_data.shape
    total_columns = calculate_total_length(m_list)
    mat = torch.zeros(batch_size, steps, n, total_columns, device=device)

    mat[:, :, :, 0] = 1

    col_idx = 1
    for i, m in enumerate(m_list):
        if m == 'Linear':
            mat[:, :, :, col_idx] = x_data[:, :, :, i]
            col_idx += 1
        else:
            repeated_data = x_data[:, :, :, i].unsqueeze(-1).expand(batch_size, steps, n, 2 * m)
            mat[:, :, :, col_idx:col_idx + 2 * m] = repeated_data
            col_idx += 2 * m
    return mat


def mat_time_online(x_data, m_list):
    batch_size, steps, n, d = x_data.shape
    total_columns = calculate_total_length(m_list)
    mat = torch.zeros(batch_size, steps, n, total_columns, device=device)

    col_idx = 1
    for i, m in enumerate(m_list):
        if m == 'Linear':
            mat[:, :, :, col_idx] = x_data[:, :, :, -1]
            col_idx += 1
        else:
            repeated_data = x_data[:, :, :, -1].unsqueeze(-1).expand(batch_size, steps, n, 2 * m)
            mat[:, :, :, col_idx:col_idx + 2 * m] = repeated_data
            col_idx += 2 * m
    return mat

def phi_matrix_online(x_data, m_list):
    return  mat_data_online(x_data, m_list) *(torch.exp(-1j * mat_time_online(x_data, m_list)* mat_frequency_online(m_list) / 2) + mat_linear_online(x_data, m_list))

def cov_hourly_online(m_list, data_hourly):
    x_data, x_test, y_data, ground_truth = data_hourly
    phi_mat = phi_matrix_online(x_data, m_list)
    covariance_matrix_X = torch.matmul(phi_mat.transpose(2, 3).conj(), phi_mat)
    covariance_XY = torch.matmul(phi_mat.transpose(2, 3).conj(), y_data)
    phi_mat_z = phi_matrix_online(x_test, m_list)

    return covariance_matrix_X, covariance_XY, phi_mat_z, ground_truth

def half_hour_formatting_online(data, date, features_weakl, hyperparameters):
    begin_train, end_train, end_test = date["begin_train"], date["end_train"], date["end_test"]
    features = features_weakl["features"]
    fourier_vectors = hyperparameters["fourier_vectors"]
    m_list = hyperparameters["m_list"]
    window = hyperparameters["window"]
    data_hourly = []

    for h in range(48):
        x_online_list, x_test_list, y_online_list=[],[],[]

        data_h = data[data['tod']==h]

        data_h.loc[:,features]=normalize(data_h.loc[:,features]).loc[:,features]

        g_h=transform(data_h, m_list, fourier_vectors[h], features)
        g_h.loc[:,features]=normalize(g_h.loc[:,features]).loc[:,features]


        current_end_train = pd.to_datetime(end_train)
        current_end_test = current_end_train+timedelta(days=window)
        g_h['Time']=pd.to_datetime(g_h['Time'])
        
        
        learning_window = len(g_h[(g_h['Time']>=begin_train)&(g_h['Time']<current_end_train)])
        
        while current_end_train < pd.to_datetime(end_test):
            g_train = g_h[(g_h['Time']>=begin_train)&(g_h['Time']<current_end_train)]
            g_test = g_h[(g_h['Time']>=current_end_train)&(g_h['Time']<current_end_test)]
            
            x_online = torch.tensor(g_train[features].values, device=device)
            x_test_online = torch.tensor(g_test[features].values, device=device)


            if x_test_online.shape[0] != 0:
                y_online = torch.tensor(g_train['error'].values, device=device).view(-1,1)*(1+0*1j)

                x_online_list.append(x_online[-learning_window:,:])
                x_test_list.append(x_test_online)
                y_online_list.append(y_online[-learning_window:,:])
                
                

            current_end_train = current_end_train+timedelta(days=window)
            current_end_test = min(current_end_test+timedelta(days=window), pd.to_datetime(end_test))

        g_test = g_h[(g_h['Time']>=end_train)&(g_h['Time']<end_test)]
        ground_truth_online = torch.tensor(g_test['error'].values, device=device)

        data_hourly.append([torch.stack(x_online_list), torch.stack(x_test_list), torch.stack(y_online_list), ground_truth_online])
        

    x_data = torch.stack([data_hourly[i][0] for i in range(48)])
    x_test = torch.stack([data_hourly[i][1] for i in range(48)])
    y_data = torch.stack([data_hourly[i][2] for i in range(48)])
    ground_truth = torch.stack([data_hourly[i][3] for i in range(48)])
    
    return x_data, x_test, y_data, ground_truth

def formatting_online(data, date, features_weakl, hyperparameters, h):
    begin_train, end_train, end_test = date["begin_train"], date["end_train"], date["end_test"]
    features = features_weakl["features"]
    fourier_vectors = hyperparameters["fourier_vectors"]
    m_list = hyperparameters["m_list"]
    window = hyperparameters["window"]
    data_hourly = []

    x_online_list, x_test_list, y_online_list=[],[],[]

    data_h = data[data['tod']==h]

    data_h.loc[:,features]=normalize(data_h.loc[:,features]).loc[:,features]

    g_h=transform(data_h, m_list, fourier_vectors[h], features)
    g_h.loc[:,features]=normalize(g_h.loc[:,features]).loc[:,features]


    current_end_train = pd.to_datetime(end_train)
    current_end_test = current_end_train+timedelta(days=window)
    g_h['Time']=pd.to_datetime(g_h['Time'])
    
    learning_window = len(g_h[(g_h['Time']>=begin_train)&(g_h['Time']<current_end_train)])
    
    while current_end_train < pd.to_datetime(end_test):
        g_train = g_h[(g_h['Time']>=begin_train)&(g_h['Time']<current_end_train)]
        g_test = g_h[(g_h['Time']>=current_end_train)&(g_h['Time']<current_end_test)]
        
        x_online = torch.tensor(g_train[features].values, device=device)
        x_test_online = torch.tensor(g_test[features].values, device=device)


        if x_test_online.shape[0] != 0:
            y_online = torch.tensor(g_train['error'].values, device=device).view(-1,1)*(1+0*1j)

            x_online_list.append(x_online[-learning_window:,:])
            x_test_list.append(x_test_online)
            y_online_list.append(y_online[-learning_window:,:])
            

        current_end_train = current_end_train+timedelta(days=window)
        current_end_test = min(current_end_test+timedelta(days=window), pd.to_datetime(end_test))

    g_test = g_h[(g_h['Time']>=end_train)&(g_h['Time']<end_test)]
    ground_truth_online = torch.tensor(g_test['error'].values, device=device)

    data_hourly.append([torch.stack(x_online_list), torch.stack(x_test_list), torch.stack(y_online_list), ground_truth_online])
        

    x_data = torch.stack([data_hourly[i][0] for i in range(1)])
    x_test = torch.stack([data_hourly[i][1] for i in range(1)])
    y_data = torch.stack([data_hourly[i][2] for i in range(1)])
    ground_truth = torch.stack([data_hourly[i][3] for i in range(1)])

    return x_data, x_test, y_data, ground_truth

def grid_search_online(data, date, features_weakl, n, grid_parameters, hyperparameters):
    grid_m, alpha_const, grid_a, s_list, regression_mask, non_reg_mask = create_grid(features_weakl, n, grid_parameters)
    len_grid_m, len_grid_a, counter = len(grid_m), len(grid_a), 0

    grid_a = grid_a.split(grid_parameters["batch_size"], dim=0)
    batch_number = len(grid_a)
    
    perf_min = torch.inf
    perf_h=[]
    m_list_opt, fourier_opt = [], []
    alpha_list_opt = torch.tensor([], device=device)

   
    data_hourly = half_hour_formatting_online(data, date, features_weakl, hyperparameters)
    for m_list in grid_m:
      cov_hourly = cov_hourly_online(m_list, data_hourly)


      sobolev_effects = sob_effects(features_weakl, m_list, s_list, len(data_hourly[0][0][0]))
      mul1 = alpha_const*(sobolev_effects[non_reg_mask,:].unsqueeze(0))

      print(str(counter*len_grid_a)+"/"+str(len_grid_m*len_grid_a))
      counter_batch = 0
      for grid_a_batch in grid_a:
        print("Batch: "+str(counter_batch)+"/"+str(batch_number))
        counter_batch+=1

        mul2 = grid_a_batch*(sobolev_effects[regression_mask,:].unsqueeze(0))
        sobolev_matrices = torch.sum(mul1, dim=1, keepdim=True) + torch.sum(mul2, dim=1, keepdim=True)
        sobolev_matrices = sobolev_matrices.unsqueeze(2)
       
        fourier_vectors= torch.linalg.solve(cov_hourly[0].unsqueeze(0)+sobolev_matrices, cov_hourly[1].unsqueeze(0))
        
        estimators = torch.matmul(cov_hourly[2].unsqueeze(0), fourier_vectors).squeeze(-1)
        errors = torch.real(cov_hourly[3].unsqueeze(0)-estimators.squeeze(-1))

        perf_hourly =  torch.sqrt(torch.mean(torch.square(errors), dim=2))
        perf_mean = torch.sqrt(torch.mean(torch.square(perf_hourly), dim=1))
            
        min_perf_index = torch.argmin(perf_mean)

        if perf_mean[min_perf_index] < perf_min:
              m_list_opt, alpha_list_opt, perf_opt, fourier_opt, perf_h = m_list, grid_a_batch[min_perf_index], perf_mean[min_perf_index], fourier_vectors[min_perf_index], perf_hourly[min_perf_index]
              perf_min = perf_mean[min_perf_index]
      counter+=1
      
    alpha_opt = torch.zeros(len(regression_mask)+len(non_reg_mask), device=device)
    alpha_opt[regression_mask] = alpha_list_opt.view(-1)
    alpha_opt[non_reg_mask] = alpha_const.view(-1)
  
    return m_list_opt, alpha_opt, s_list, perf_opt, fourier_opt, perf_h