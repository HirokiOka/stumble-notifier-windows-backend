import json
import csv
import warnings
from datetime import datetime
import time
import pickle
from gen_dummy_data import gen_dummy_features,\
                           append_dummy_row_to_csv, read_latest_dummy_feature
from db import connect_db, get_collection,\
               get_latest_codeparams, insert_many_processed
from heart_rate import get_latest_heart_rate_data

warnings.filterwarnings("ignore", category=Warning)

SS_LEN = 60
APPEND_LEN = 5
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
    if (len(state_queue) < SS_LEN):
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

    with open(config_path) as f:
        f_read = f.read()
        metadata = json.loads(f_read)

    calc_results = [[] for i in range(len(metadata))]

    while True:
        for i, m in enumerate(metadata):
            short_dt = datetime.now().time().replace(microsecond=0)

            # Get Features
            classified_path = m['classified_path']
            current_heart_rate_data = get_latest_heart_rate_data(m['whs_path'])
            current_code_data = get_latest_codeparams(client,
                                                      code_coll,
                                                      m['name'])
            current_elapsed_seconds = calc_elapsed_seconds(
                    current_heart_rate_data,
                    current_code_data,
                    m['name'])
            current_feature = make_feature_data(
                    current_heart_rate_data,
                    current_code_data,
                    current_elapsed_seconds)

            # Classify from features
            multi_result = classify_stumble(current_feature, 'multi')
            code_result = classify_stumble(current_feature, 'code')

            # Post-processing
            classified_data = read_classified_csv(classified_path)
            classified_len = len(classified_data)
            processed_data = []
            if (classified_len >= SS_LEN):
                current_classified = classified_data[classified_len-SS_LEN:classified_len]
                current_multi = [int(x[1]) for x in current_classified]
                current_code = [int(x[2]) for x in current_classified]
                # Post-process from 60 classified data
                pp_multi = post_process_stumbles(current_multi)
                pp_code = post_process_stumbles(current_code)
                processed_data = [pp_multi, pp_code]

            calc_results[i].append((
                short_dt,
                multi_result,
                code_result,
                processed_data
                ))
            print(f'{m["name"]}: {short_dt} {processed_data}')

            # Write classified data to a csv file
            if (len(calc_results[i]) >= APPEND_LEN):
                append_classified_to_csv(calc_results[i],
                                         classified_path)
                processed = [x[3] for x in calc_results[i]]
                if (not ([] in processed)):
                    pass
                    # insert_one_processed(client, p_coll, m["name"], post_data)
                    insert_many_processed(client, p_coll, m["name"], processed)
                calc_results[i].clear()

        time.sleep(1.0)


if __name__ == '__main__':
    main()
