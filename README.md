# Esti-LULC-Map-XGboost
Train a model to produce the Land use and land cover map for Estonia using XGboost

The sentinel-2 satellite data was used to train the XGboost model. The performance is as follow:

```Training performance of XGB:

0.8568426979849576
              precision    recall  f1-score   support

           1       0.88      0.97      0.92    853269
           2       0.78      0.86      0.82    217181
           3       0.62      0.07      0.13     66579
           4       0.73      0.39      0.50     53820
           5       0.87      0.83      0.85     28996
           6       0.68      0.13      0.22     13316
           7       0.67      0.31      0.42      6577
           8       0.57      0.33      0.42      3412

    accuracy                           0.86   1243150
   macro avg       0.73      0.48      0.54   1243150
weighted avg       0.84      0.86      0.83   1243150


________________________________________________________________________________
Test performance of XGB:

0.7570965226098681
              precision    recall  f1-score   support

           1       0.78      0.90      0.84   2474473
           2       0.77      0.82      0.79   1837496
           3       0.27      0.07      0.11    294209
           4       0.49      0.16      0.24    212592
           5       0.73      0.60      0.66    150093
           6       0.17      0.12      0.14     90790
           7       0.60      0.16      0.25     50437
           8       0.21      0.23      0.22     19993

    accuracy                           0.76   5130083
   macro avg       0.50      0.38      0.41   5130083
weighted avg       0.72      0.76      0.73   5130083
```
