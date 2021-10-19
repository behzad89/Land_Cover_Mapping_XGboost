import sys  
sys.path.insert(0, '../src')

import utils as ut
import rasterio as rs
from rasterio import merge
import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split,cross_val_score,GridSearchCV,StratifiedKFold,RandomizedSearchCV,StratifiedShuffleSplit
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report,roc_auc_score,roc_curve,precision_recall_curve, plot_confusion_matrix

import xgboost as xgb

import joblib
import multiprocessing
from functools import partial,reduce

import os, sys, warnings



model_xgb = joblib.load("../results/xgb_new_lulc_model.pkl")

	
list_imgs = ['patch_s2_0_ee','patch_s2_1_ee','patch_s2_2_ee','patch_s2_3_ee']
print(len(list_imgs))


def img_prediction(img_name):
    img = rs.open(f'../features/patches/{img_name}.tif')
    width=img.width
    height=img.height
    transform=img.transform
    minx,miny,maxx,maxy = img.bounds
    col_names = ["blue", "green","red","red_e1","red_e2","red_e3","nir1","swir1","swir2","nir2"]
    img_ = pd.DataFrame(img.read().reshape(10,-1).T,columns=col_names)
    img_['NDVI'] = img_[['nir1','red']].apply(ut.ndvi,axis=1)
    img_['NDWI'] = img_[['nir1','swir2']].apply(ut.ndwi,axis=1)
    predicted_img = model_xgb.predict(img_)
    
    predicted_img_ = predicted_img.reshape(height,width)
    out_path = f'../results/ee_pred_LULC_{img_name}.tif'
    with rs.open(out_path, "w",
               driver='GTiff',
               count=1,
               transform = transform,
               width=width,
               height=height,
               dtype='uint16',
               crs="epsg:3301",) as output_file:
        output_file.write(np.expand_dims(predicted_img_.astype('uint16'),axis=0))

with multiprocessing.Pool(processes=40) as pool:
    pool.map(img_prediction,list_imgs)
