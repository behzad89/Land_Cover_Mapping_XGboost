[![badge text](https://img.shields.io/badge/LinkedIn-blue?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/bvsh/)
# Land Cover Mapping using XGboost
Train a model to produce the Land use and land cover map for Estonia using XGboost
![image](https://user-images.githubusercontent.com/47195556/137954536-c3f10773-2b1c-41ba-9419-da59615355ad.png)

The sentinel-2 satellite data was used to train the XGboost model. The performance is as follow:

```Training performance of XGB:

Training performance of XGB:

0.9113002645447547
              precision    recall  f1-score   support

           1       0.91      0.97      0.94   2923868
           2       0.91      0.94      0.93   1716062
           3       0.83      0.37      0.51    319692
           4       0.93      0.81      0.87    249149
           5       0.95      0.96      0.95    195419
           6       0.90      0.58      0.71     75792
           7       0.86      0.81      0.84     23135
           8       0.57      0.38      0.45     18444

    accuracy                           0.91   5521561
   macro avg       0.86      0.73      0.77   5521561
weighted avg       0.91      0.91      0.90   5521561


________________________________________________________________________________
Test performance of XGB:

0.9068290293876948
              precision    recall  f1-score   support

           1       0.93      0.97      0.95    865578
           2       0.83      0.93      0.88    221242
           3       0.82      0.32      0.46     67557
           4       0.91      0.66      0.76     54820
           5       0.96      0.97      0.96     32110
           6       0.90      0.54      0.67     13528
           7       0.68      0.71      0.70      1492
           8       0.55      0.34      0.42      3486

    accuracy                           0.91   1259813
   macro avg       0.82      0.68      0.73   1259813
weighted avg       0.90      0.91      0.90   1259813
```
