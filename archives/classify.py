import pickle
import pandas as pd


sample_data = pd.DataFrame([[0.81, 0.0, 0, 0, 1, 0]],
        columns=['lfhf', 'pnn50', 'sloc', 'ted', 'elapsed-seconds', 'label'])
model = ''
with open('../model/model.pickle', 'rb') as f:
    model = pickle.load(f)
model.predict(sample_data.loc[:, 'lfhf':'elapsed-seconds'])
