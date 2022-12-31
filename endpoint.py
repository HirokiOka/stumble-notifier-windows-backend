import json
import datetime as dt
import pickle
from connect_mongo import connect_db, get_collection, get_latest_codeparams
from read_heart_data import get_latest_heart_rate_data


STUMBLE_SEQ_LENGTH = 60
date_fmt = '%Y/%m/%d %H:%M:%S'
multi_model_bin_path = './models/multi_model.pickle'
code_model_bin_path = './models/code_model.pickle'

with open(multi_model_bin_path, 'rb') as f:
    multi_model = pickle.load(f)
with open(code_model_bin_path, 'rb') as f:
    code_model = pickle.load(f)

client = connect_db()
collection = get_collection(client, 'codeparams')


def calc_elapsed_seconds(heart_rate_data, code_data, user_id):
    str_heart_rate_data_date = f'{dt.date.today()} {heart_rate_data[0]}'.replace('-', '/')
    heart_rate_data_date = dt.datetime.strptime(str_heart_rate_data_date, date_fmt)
    last_executed_time = dt.datetime.strptime(code_data[0], date_fmt)
    elapse_seconds = (heart_rate_data_date - last_executed_time).seconds
    return elapse_seconds


def make_feature_data(heart_rate_data, code_data, elapse_seconds):
    pnn50 = heart_rate_data[1]
    lf_hf = heart_rate_data[2]
    sloc = code_data[1]
    ted = code_data[2]
    features = [[sloc, ted, elapse_seconds, lf_hf, pnn50]]
    return features


# SLOC, ted, elapsed-sec, lf/hf, pnn50
def classify_stumble(feature_data, mode='multi'):
    classified_result = []
    if (mode == 'code'):
        classified_result = code_model.predict([feature_data[0][:3]])
    elif (mode == 'multi'):
        classified_result = multi_model.predict(feature_data)
    return classified_result[0]


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


config_path = './test_data.json'


def main():
    """
        Real-time processing
    """
    # Setting
    with open(config_path) as f:
        f_read = f.read()
        metadata = json.loads(f_read)
    whs_path = metadata[0]['whs_path']
    user_id = 'nishida'

    # Read current Data
    current_heart_rate_data = get_latest_heart_rate_data(whs_path)
    current_code_data = get_latest_codeparams(client, collection, user_id)

    # Make Feature Data
    current_elapsed_seconds = calc_elapsed_seconds(
            current_heart_rate_data,
            current_code_data,
            user_id)
    current_features = make_feature_data(
            current_heart_rate_data,
            current_code_data,
            current_elapsed_seconds)

    # Detect Stumble
    multi_result = classify_stumble(current_features, 'multi')
    code_result = classify_stumble(current_features, 'code')
    # Post-processing
    # Send Data to DB


if __name__ == '__main__':
    main()
