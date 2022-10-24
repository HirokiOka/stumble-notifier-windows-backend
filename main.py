import pickle
import pandas as pd
import time
import datetime
from db_request import get_codeparams_from_std_id, post_all_data_from_id
from read_csv import read_latest_data, calc_pnn50

pnn50_window_size = 100
multi_model_bin_path = './models/multi_model.pickle'
code_model_bin_path = './models/code_model.pickle'
p_info = [
        {
         "id": "2030848h",
         "whs_path": "../whs-data/test_2.csv",
         "current_heart_data": {},
         "rri_chunk": [],
         "last_code_saved": -1
         },
        {
         "id": "2041201h",
         "whs_path": "../whs-data/test_3.csv",
         "current_heart_data": {},
         "rri_chunk": [],
         "last_code_saved": -1
         },
        {
         "id": "2070877H",
         "whs_path": "../whs-data/test_4.csv",
         "current_heart_data": {},
         "rri_chunk": [],
         "last_code_saved": -1
         },
        {
         "id": "2110645H",
         "whs_path": "../whs-data/test_5.csv",
         "current_heart_data": {},
         "rri_chunk": [],
         "last_code_saved": -1
         },
        {
         "id": "2120823h",
         "whs_path": "../whs-data/test_6.csv",
         "current_heart_data": {},
         "rri_chunk": [],
         "last_code_saved": -1
         },
        {
         "id": "2141064h",
         "whs_path": "../whs-data/test_7.csv",
         "current_heart_data": {},
         "rri_chunk": [],
         "last_code_saved": -1
         }
        ]


def str_date_to_datetime(date):
    r_date = 0
    if ('AM' in date or 'PM' in date):
        date = date.split(' ')
        date = date[0].split(',')[0] + ' ' + date[1]
        r_date = datetime.datetime.strptime(date, '%m/%d/%Y %H:%M:%S')
    else:
        r_date = datetime.datetime.strptime(date, '%Y/%m/%d %H:%M:%S')
    return r_date


def calc_elapsed_sec(current_saved_at, last_saved_at):
    c_saved_date = str_date_to_datetime(current_saved_at)
    last_saved_date = str_date_to_datetime(last_saved_at)
    elapsed_seconds = (c_saved_date - last_saved_date).seconds
    return elapsed_seconds


def update_heart_params(user_info):
    latest_heart_data = read_latest_data(user_info["whs_path"])
    user_info["current_heart_data"] = {
            "time": latest_heart_data["time"],
            "lf/hf": latest_heart_data["lf/hf"]}
    user_info["rri_chunk"].append(latest_heart_data["rri"])


def make_feature_data(std_id, codeparams, elapsed_sec, rri_chunk, whs_params):
    sloc = codeparams["sloc"]
    ted = codeparams["ted"]
    lf_hf = whs_params["lf/hf"]
    pnn50 = calc_pnn50(rri_chunk)
    feature_data = pd.DataFrame([[lf_hf, pnn50, sloc, ted, elapsed_sec]],
                                columns=["lfhf", "pnn50",
                                         "sloc", "ted", "elapsed-seconds"])
    return feature_data



def main():
    sleep_sec = 0.1
    start_time = datetime.datetime.now()
    multi_model = ''
    code_model = ''
    test_info = [
            {"id": "2030848h",
             "whs_path": "../whs-data/test_1.csv",
             "current_heart_data": {},
             "rri_chunk": [],
             "stumble_states": [],
             "last_code_saved": -1
             },
            {
             "id": "2070877H",
             "whs_path": "../whs-data/test_3.csv",
             "current_heart_data": {},
             "rri_chunk": [],
             "stumble_states": [],
             "last_code_saved": -1
             }
            ]

    with open(multi_model_bin_path, 'rb') as f:
        multi_model = pickle.load(f)
    with open(code_model_bin_path, 'rb') as f:
        code_model = pickle.load(f)

    while(True):
        for d in test_info:
            update_heart_params(d)

        # Prediction
        for idx, info in enumerate(test_info):
            if (len(info["rri_chunk"]) > pnn50_window_size):
                std_id = info["id"]
                latest_codeparams = get_codeparams_from_std_id(std_id)[-1]
                source_code = latest_codeparams["code"]
                saved_at = latest_codeparams["savedAt"]
                elapsed_sec = 0
                if (info["last_code_saved"] == -1):
                    elapsed_sec = (datetime.datetime.now() - start_time).seconds
                else:
                    elapsed_sec = calc_elapsed_sec(saved_at, info["last_code_saved"])

                current_feature_data = make_feature_data(std_id,
                                                         latest_codeparams,
                                                         elapsed_sec,
                                                         info["rri_chunk"],
                                                         info["current_heart_data"])
                multi_result = int(multi_model.predict(current_feature_data)[0])
                code_result = int(code_model.predict(current_feature_data.loc[:,'sloc':'elapsed-seconds'])[0])
                feature_dict = current_feature_data.to_dict()
                print(std_id, current_feature_data, multi_result, code_result)
                try:
                    print(post_all_data_from_id(std_id, saved_at,
                          source_code,
                          feature_dict, multi_result, code_result))
                except:
                    print("Prediction data post failed")

                info["last_code_saved"] = saved_at
                info["rri_chunk"].pop(0)
            else:
                print(info["id"] + ": " + str(len(info["rri_chunk"])))
        time.sleep(sleep_sec)


if __name__ == '__main__':
    main()
