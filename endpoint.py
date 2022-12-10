import pickle
from read_heart_data import get_latest_heart_rate_data, calc_pnn50


STUMBLE_SEQ_LENGTH = 60
multi_model_bin_path = './models/multi_model.pickle'
code_model_bin_path = './models/code_model.pickle'

with open(multi_model_bin_path, 'rb') as f:
    multi_model = pickle.load(f)
with open(code_model_bin_path, 'rb') as f:
    code_model = pickle.load(f)


"""
 - get heart rate data from csv(x)
 - get code data from DB
 - caclulate features
    - pNN50(x)
    - elapsed seconds
 - post-processing(x)
 - real-time processing
"""


# SLOC, AST ED, elapsed-sec, lf/hf, pnn50
def classify_stumble(feature_data, mode='multi'):
    classified_result = []
    if (mode == 'code'):
        classified_result = code_model.predict(feature_data)
    elif (mode == 'multi'):
        classified_result = multi_model.predict(feature_data)
    return classified_result


def post_process_stumbles(state_queue, ratio=2/3):
    if (len(state_queue) < STUMBLE_SEQ_LENGTH):
        return None
    result = 0
    threshold = int(len(state_queue) * ratio)
    if (state_queue.count(0) > threshold):
        result = 1
    else:
        result = 0
    return result





sample_code_features = [[24, 2, 200], [24, 2, 200]]
sample_multi_features = [[7.4, 10.0, 24, 2, 200], [2.0, 12.0, 24, 2, 200]]
print(classify_stumble(sample_code_features, mode='code'))
print(classify_stumble(sample_multi_features, mode='multi'))
