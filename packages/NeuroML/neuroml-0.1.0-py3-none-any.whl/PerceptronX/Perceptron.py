import warnings
import numpy as np
import pandas as pd
import math
from sklearn.preprocessing import StandardScaler
warnings.simplefilter('always', RuntimeWarning)

class Perceptron:    
    def fit(self, data, learning_rate=0.1, tolerance=1e-9):

        sc = data.iloc[:, :-1]
        for col in sc.columns:
            col_data = sc[col]
            if not (is_standard_scaled(col_data) or is_minmax_scaled(col_data)):
                raise RuntimeError(
                    f"Dataset column '{col}' must be either standard scaled or min-max scaled."
                )


        sample=data.iloc[:,-1].shape[0]
        if sample<21:
            raise RuntimeError('The Samples of Dataset for "training" is too small, Consider Larger or atleast More than 20 samples')

        target=data.iloc[:,-1]
        count=target.nunique()
        if count>2.0 and count<20.0:
           self. activation='multi'
        elif count==2:
            self.activation='binary'
        else:
            self.activation='linear'


        
        unique=data.iloc[:,-1].nunique()
        if unique<20 and unique>2:
            self.weight=np.random.randn((data.iloc[1, :-1].shape[0]),unique)
            self.bias=np.zeros(unique)
            self.n = data.shape[0]
            self.learning_rate = learning_rate
            warnings.warn(
            "Warning: Single perceptron is not suitable for multi-class classification. "
            "This function is for learning/demo purposes only and may give poor accuracy.",
                RuntimeWarning
            )
        else:
            self.weight = np.zeros(data.iloc[1, :-1].shape[0])
            self.bias = 0
            self.n = data.shape[0]
            self.learning_rate = learning_rate

        initialize = float('inf')
        tolerance = 1e-9
        max_iter = 10000

        if self.activation == 'linear':
            for i in range(max_iter):
                self.weight, self.bias = gradient_descent_optimisation_linear(data, self.weight, self.bias, self.n, self.learning_rate)
                out = mse_fn(data, self.weight, self.bias, self.activation)
                if initialize - out < tolerance:
                    break
                initialize = out
        elif self.activation=='binary':
            for i in range(max_iter):
                self.weight, self.bias = gradient_descent_optimisation_binary(data, self.weight, self.bias, self.n, self.learning_rate)
                out = bce_fn(data, self.weight, self.bias, self.activation)
                if initialize - out < tolerance:
                    break
                initialize = out
        else:
            for i in range(max_iter):
                self.weight, self.bias, self.X, self.y= gradient_descent_optimisation_multi(data, self.weight, self.bias, self.n, self.learning_rate)
                out = logloss_fn(self.X,self.y, self.weight, self.bias)
                if initialize - out < tolerance:
                    break
                initialize = out

        

        print("Weights:", self.weight)
        print("Bias:", self.bias)
        
        return self.weight, self.bias

    def predict(self, data):
        if not hasattr(self, 'weight') or not hasattr(self, 'bias'):
            raise ValueError("Model must be trained using fit() before calling predict()")
        if self.activation=='multi':
            X = data.values
            self.predicted =predict_fn(self.weight, self.bias, X, self.activation)
        else:
            X = data.values
            self.predicted = np.array([predict_fn(self.weight, self.bias, i, self.activation) for i in X])
            
        return self.predicted


def is_standard_scaled(X, tol_mean=0.5, tol_std=1.8):
    arr = np.array(X)
    means = arr.mean(axis=0)
    stds = arr.std(axis=0)
    check = means < tol_mean and stds < tol_std
    return check

def is_minmax_scaled(X, tol_min=-1.51, tol_max=1.51):
    arr = np.array(X)
    mins = arr.min(axis=0)
    maxs = arr.max(axis=0)
    check = np.all(mins > tol_min) and np.all(maxs < tol_max)
    return check

def predict_fn(weight,bias,row,activation):
    X_array=row
    if activation=='multi':
        if X_array.ndim == 1:
            X_array = X_array.reshape(1, -1)
            
        z = X_array.dot(weight) + bias
        probs = stable_softmax(z)
        predictions = np.argmax(probs, axis=1)
        return predictions

    if type(row)==list:
        row=np.array(row)
    weight=np.array(weight)
    a=weight*row
    b=a.sum()
    value=b+bias
    if activation=='linear':
        result=value
    else:
        result=sigmoid_fn(value)
        if result>=0.5:
            result=1
        else:
            result=0
    return result

def s_scaler_fn(data):
    output=[]
    for i in data.index:
        scaled=(i-np.mean((data)))/np.std((data))
        output.append(scaled)
    return output

def m_scaler_fn(data):
    output=[]
    for i in data:
        scaled=(i-np.min(data))/(np.max(data)-np.min(data))
        output.append(scaled)
    return output


### For Linear Data
def gradient_descent_optimisation_linear(data,weight,bias,n,learning_rate):
    X=data.iloc[:,:-1].values
    y=data.iloc[:,-1].values
    y_pred=np.array([linear_predict(weight,bias,row) for row in X])
    
    gradient_weight=(2/n)*np.dot(y-y_pred,X)
    gradient_bias=(2/n)*np.sum(y-y_pred)

    weight_new=weight+(learning_rate*gradient_weight)
    bias_new=bias+(learning_rate*gradient_bias)
    return weight_new,bias_new

def mse_fn(data,weight,bias,activation):
    y=data.iloc[:,-1].values
    X=data.iloc[:,:-1].values
    y_pred=np.array([linear_predict(weight,bias,row) for row in X])
    mse=np.mean(np.power((y-y_pred),2))
    return mse

def linear_predict(weight,bias,row):
    a=weight*row
    b=a.sum()
    value=b+bias
    return value

### For Binary Data

def gradient_descent_optimisation_binary(data, weight, bias, n, learning_rate):
    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values
    y_pred = np.array([binary_predict(weight, bias, row) for row in X])

    gradient_weight = (1/n) * np.dot(y - y_pred, X)
    gradient_bias = (1/n) * np.sum(y - y_pred)

    weight_new = weight + (learning_rate * gradient_weight)
    bias_new = bias + (learning_rate * gradient_bias)
    return weight_new, bias_new

def binary_predict(weight,bias,row):
    a=weight*row
    b=a.sum()
    value=b+bias
    result = 1 / (1 + np.exp(-value))
    return result

def bce_fn(data,weight,bias,activation):
    y=data.iloc[:,-1].values
    X=data.iloc[:,:-1].values
    y_pred=np.array([binary_predict(weight,bias,row) for row in X])
    bce=-np.mean(y * np.log(y_pred) + (1 - y) * np.log(1 - y_pred))
    return bce

def sigmoid_fn(z):
    z = np.clip(z, -500, 500)
    return 1 / (1 + np.exp(-z))

### For Multi Class Data

def gradient_descent_optimisation_multi(data, weights, bias, N, learning_rate):
    X=data.iloc[:,:-1].values
    y=data.iloc[:,-1]
    y = y.to_numpy().astype(int)
    z = X.dot(weights) + bias
    probs = stable_softmax(z)
    
    y_one_hot = np.zeros_like(probs)
    y_one_hot[np.arange(N), y] = 1
    
    error = probs - y_one_hot
    grad_weights = X.T.dot(error) / N
    grad_bias = np.sum(error, axis=0) / N
    
    updated_weights = weights - learning_rate * grad_weights
    updated_bias = bias - learning_rate * grad_bias
    
    return updated_weights, updated_bias,X,y


def stable_softmax(z):
    z = z - np.max(z, axis=1, keepdims=True)
    exp_z = np.exp(z)
    return exp_z / np.sum(exp_z, axis=1, keepdims=True)


def logloss_fn(X,y_true, weights, bias, eps=1e-15):
    
    N = X.shape[0]

    z = X.dot(weights) + bias 
    probs = stable_softmax(z) 
    

    probs = np.clip(probs, eps, 1 - eps)
    

    K = probs.shape[1]
    y_one_hot = np.zeros_like(probs)
    y_one_hot[np.arange(N), y_true] = 1
    
    log_probs = np.log(probs)
    loss = -np.sum(y_one_hot * log_probs) / N
    
    return loss