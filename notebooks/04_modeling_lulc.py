import rasterio as rs
from rasterio import merge
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split,cross_val_score,GridSearchCV,StratifiedKFold,RandomizedSearchCV,StratifiedShuffleSplit
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report,roc_auc_score,roc_curve,precision_recall_curve, plot_confusion_matrix
import os, sys, warnings
import xgboost as xgb


warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


data = pd.read_parquet('../features/testing_data_ee_LULC.parquet')
print(data.shape)

val_data = pd.read_parquet('../features/training_data_ee_LULC.parquet')
print(val_data.shape)

# Constants
TARGET_COL ='lulc'
FTS_COLS = [x for x in data.columns if x != TARGET_COL]
print(FTS_COLS)


X = data[FTS_COLS]
y = data[TARGET_COL]
X_train = data[FTS_COLS]
y_train = data[TARGET_COL]
X_test = val_data[FTS_COLS]
y_test = val_data[TARGET_COL]



print(y_train.unique())
import time
start_time = time.time()
params = {
	'n_estimators':5000,
    	'eta': 0.1,
    	'max_depth':6,
    	'objective':'multi:softmax',
    	'num_class': 8,
	'subsample': 0.7,
	'colsample_bytree':0.7,
	"tree_method": "gpu_hist",
	'predictor': 'gpu_predictor'
}

model = xgb.XGBClassifier(**params)
model.fit(X_train,y_train, eval_set=[(X_train, y_train), (X_test,y_test)],early_stopping_rounds=10,eval_metric='mlogloss',verbose=10)
print("--- %s seconds ---" % (time.time() - start_time))


start_time = time.time()
y_test_pred = model.predict(X_test)
y_train_pred = model.predict(X_train)
print("Training performance of XGB:")
print()
print(accuracy_score(y_train,y_train_pred))
print(classification_report(y_train,y_train_pred))
print()
print("_" * 80)
print("Test performance of XGB:")
print()
print(accuracy_score(y_test,y_test_pred))
print(classification_report(y_test,y_test_pred))
print("--- %s seconds ---" % (time.time() - start_time))

import joblib
joblib_file = "../results/xgb_new_lulc_model.pkl"  
joblib.dump(model, joblib_file)