import csv
import time

csv_path = "../whs-data/test_1.csv"


def read_latest_data(file_path):
    with open(csv_path, encoding="cp932", mode="r") as f:
        csv_reader = list(csv.reader(f))[5:]
        data = csv_reader[-1]
        result = {"time": data[0], "rri": data[1], "lf/hf": data[7]}
        return result


def calc_pnn50(rri_chunk, window_size=100, lower_rri_threshold=200, upper_rri_threshold=1100):
    last_rri = 0
    all_rri_diff = []
    for v in rri_chunk:
        current_rri = last_rri if ((int(v) < lower_rri_threshold) or (upper_rri_threshold < int(v))) else int(v)
        rri_diff = abs(current_rri - last_rri)
        all_rri_diff.append(rri_diff)
        last_rri = current_rri
    all_rri_diff.pop(0)
    all_nn50 = [v for v in all_rri_diff if v > 50]
    print(len(all_rri_diff))
    pnn50 = len(all_nn50) / window_size
    return pnn50


def scheduler(arg1, arg2):
    print(time.time())


"""
mybeat_data = open(csv_path, encoding="cp932", mode="r")
csv_list = list(csv.reader(mybeat_data))[6:]
mybeat_data.close()
rri_list = [row[1] for row in csv_list]
"""
