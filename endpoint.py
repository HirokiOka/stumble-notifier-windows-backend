import json
import warnings
import datetime as dt
import pickle
from gen_dummy_data import gen_dummy_features, append_dummy_row_to_csv, read_latest_dummy_feature
from db import connect_db, get_collection, get_latest_codeparams, insert_processed
from heart_rate import get_latest_heart_rate_data


warnings.filterwarnings("ignore", category=Warning)

STUMBLE_SEQ_LENGTH = 60
date_fmt = '%Y/%m/%d %H:%M:%S'
multi_model_bin_path = './models/multi_model.pickle'
code_model_bin_path = './models/code_model.pickle'
config_path = './test_data.json'

with open(multi_model_bin_path, 'rb') as f:
    multi_model = pickle.load(f)
with open(code_model_bin_path, 'rb') as f:
    code_model = pickle.load(f)


def calc_elapsed_seconds(heart_rate_data, code_data, user_id):
    s_heart_date = f'{dt.date.today()} {heart_rate_data[0]}'.replace('-', '/')
    heart_rate_data_date = dt.datetime.strptime(s_heart_date, date_fmt)
    last_executed_time = dt.datetime.strptime(code_data[0], date_fmt)
    elapse_seconds = (heart_rate_data_date - last_executed_time).seconds
    return elapse_seconds


def make_feature_data(heart_rate_data, code_data, elapse_seconds):
    pnn50 = heart_rate_data[1]
    lf_hf = heart_rate_data[2]
    sloc = code_data[1]
    ted = code_data[2]
    # features = [[sloc, ted, elapse_seconds, lf_hf, pnn50]]
    features = [[lf_hf, pnn50, sloc, ted, elapse_seconds]]
    return features


# SLOC, ted, elapsed-sec, lf/hf, pnn50?
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
    state_queue.pop(0)
    return result


def main():
    # Setting
    """
    client = connect_db()
    collection = get_collection(client, 'processed')
    """
    with open(config_path) as f:
        f_read = f.read()
        metadata = json.loads(f_read)
    whs_path = metadata[0]['whs_path']

    """
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
    """

    # Detect Stumbles
    classified_multi = [[], [], [], [], [], [], [], [], []]
    classified_code = [[], [], [], [], [], [], [], [], []]

    while True:
        # Read Features
        for i, md in enumerate(metadata):
            append_dummy_row_to_csv(md['whs_path'])
            d_features = [read_latest_dummy_feature(md['whs_path'])]

            multi_result = classify_stumble(d_features, 'multi')
            code_result = classify_stumble(d_features, 'code')
            classified_multi[i].append(multi_result)
            classified_code[i].append(code_result)

            # Post-processing
            pp_multi = post_process_stumbles(classified_multi[i])
            pp_code = post_process_stumbles(classified_code[i])

            # Send Data to DB
            if ((pp_multi is not None) and (pp_code is not None)):
                post_data = [pp_multi, pp_code]
                # insert_processed(client, collection, post_data)
                print(post_data)


if __name__ == '__main__':
    main()
