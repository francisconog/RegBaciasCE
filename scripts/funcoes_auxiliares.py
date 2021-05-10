import numpy as np
import tensorflow.keras.backend as k

def get_batches(df, seq):

    data_batch = []
    for i in range(df.shape[0]-seq):

        batch = df[i:(seq + i)]
        data_batch.append(batch)


    return data_batch

def NASH(y_true,y_prev):
    return 1 - sum((y_prev-y_true)**2)/(sum((y_true-np.mean(y_true))**2))
  

def NSE_K(y_true,y_prev):
    return 1 - k.sum((y_prev-y_true)**2)/(k.sum((y_true-k.mean(y_true))**2))

def RMSE (y_true,y_prev):
    return np.sqrt(np.mean((y_true - y_prev)**2))

def RMSE_Keras (y_true,y_prev):
    return k.sqrt(k.mean((y_true - y_prev)**2))

def RMSLE__Keras (y_true,y_prev):
    return k.sqrt(k.mean((k.log(y_true + 1) - k.log(y_prev + 1))**2))

def create_x(dataset, seq=1):
	dataX = []
	for i in range(len(dataset)-seq-1):
		a = dataset[i:(i+seq), 0]
		dataX.append(a)

	return np.array(dataX)

def create_y(dataset, seq=1):
	dataY = []
	for i in range(len(dataset)-seq-1):
		a = dataset[(i+seq-1)]
		dataY.append(a)

	return np.array(dataY)
