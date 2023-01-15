import json
import csv
import warnings
from datetime import datetime
import signal
import time
import pickle
from gen_dummy_data import gen_dummy_features,\
                           append_dummy_row_to_csv, read_latest_dummy_feature
from db import connect_db, get_collection,\
               get_latest_codeparams, insert_processed
from heart_rate import get_latest_heart_rate_data


# warnings.filterwarnings("ignore", category=Warning)

STUMBLE_SEQ_LENGTH = 60
APPEND_SEQ_LENGTH = 10
date_fmt = '%Y/%m/%d %H:%M:%S'
multi_model_bin_path = './models/multi_model.pickle'
code_model_bin_path = './models/code_model.pickle'
config_path = './test_data.json'

with open(multi_model_bin_path, 'rb') as f:
    multi_model = pickle.load(f)
with open(code_model_bin_path, 'rb') as f:
    code_model = pickle.load(f)


def calc_elapsed_seconds(heart_rate_data, code_data, user_id):
    # s_heart_date = f'{dt.date.today()} {heart_rate_data[0]}'.replace('-', '/')
    # heart_rate_data_date = datetime.strptime(s_heart_date, date_fmt)
    c_datetime = datetime.now()
    last_executed_time = datetime.strptime(code_data[0], date_fmt)
    elapse_seconds = (c_datetime - last_executed_time).seconds
    return elapse_seconds


def make_feature_data(heart_rate_data, code_data, elapse_seconds):
    pnn50 = heart_rate_data[1]
    lf_hf = heart_rate_data[2]
    sloc = code_data[1]
    ted = code_data[2]
    features = [[lf_hf, pnn50, sloc, ted, elapse_seconds]]
    return features


def classify_stumble(feature_data, mode='multi'):
    classified_result = []
    if (mode == 'code'):
        classified_result = code_model.predict([feature_data[0][2:]])
    elif (mode == 'multi'):
        classified_result = multi_model.predict(feature_data)
    return classified_result[0]


def post_process_stumbles(state_queue, ratio=2/3):
    if (len(state_queue) < STUMBLE_SEQ_LENGTH):
        return None
    result = 0
    threshold = int(len(state_queue) * ratio)
    if (state_queue.count(1) > threshold):
        result = 1
    else:
        result = 0
    state_queue.pop(0)
    return result


def append_classified_to_csv(classified_data, csv_path):
    with open(csv_path, 'a') as f:
        writer = csv.writer(f, lineterminator='\n')
        for _, d in enumerate(classified_data):
            writer.writerow(d)


def read_classified_csv(csv_path):
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        return list(reader)


def main():

    client = connect_db()
    p_coll = get_collection(client, 'processed')
    code_coll = get_collection(client, 'codeparams')
    classified_results = [[], [], [], [], [], [], [], [], []]

    with open(config_path) as f:
        f_read = f.read()
        metadata = json.loads(f_read)

    while True:
        for i, md in enumerate(metadata):
            current_dt = datetime.now()
            # current_dt = datetime.now().time().replace(microsecond=0)

            # Get Features
            whs_path = md['whs_path']
            user_name = md['name']
            classified_path = md['classified_path']
            current_heart_rate_data = get_latest_heart_rate_data(whs_path)
            current_code_data = get_latest_codeparams(client,
                                                      code_coll,
                                                      user_name)
            current_elapsed_seconds = calc_elapsed_seconds(
                    current_heart_rate_data,
                    current_code_data,
                    user_name)
            current_feature = make_feature_data(
                    current_heart_rate_data,
                    current_code_data,
                    current_elapsed_seconds)

            multi_result = classify_stumble(current_feature, 'multi')
            code_result = classify_stumble(current_feature, 'code')
            classified_results[i].append((
                current_dt.time().replace(microsecond=0),
                multi_result,
                code_result))

            # Write classified data to a csv file
            if (len(classified_results[i]) >= APPEND_SEQ_LENGTH):
                """
                    should append all at once?
                """
                append_classified_to_csv(classified_results[i],
                                         classified_path)
                classified_results[i].clear()

            # Post-processing
            classified_data = read_classified_csv(classified_path)
            n = len(classified_data)
            if (n >= STUMBLE_SEQ_LENGTH):
                current_classified = classified_data[n-STUMBLE_SEQ_LENGTH:n]
                current_multi = [int(x[0]) for x in current_classified]
                current_code = [int(x[1]) for x in current_classified]
                pp_multi = post_process_stumbles(current_multi)
                pp_code = post_process_stumbles(current_code)

                # Send Data to DB
                if ((pp_multi is not None) and (pp_code is not None)):
                    """
                        - post all user data at once (regular interval, 10sec?)
                        - stock classified_data of all users?
                            - 10 * 9
                                - to csv file
                                    - append to classified-data?
                    """
                    post_data = [pp_multi, pp_code]
                    print(f'{user_name}: {current_dt.time().replace(microsecond=0)} {post_data}')
                    # insert_processed(client, p_coll, user_name, post_data)
            else:
                print(user_name, current_dt)
        time.sleep(1.0)


if __name__ == '__main__':
    main()
