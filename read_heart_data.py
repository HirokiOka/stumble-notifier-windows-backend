import csv

PNN50_WINDOW_SIZE = 100
LOWER_RRI_THRESHOLD = 200
UPPER_RRI_THRESHOLD = 1100


def calc_pnn50(rri_chunk):
    if (len(rri_chunk) < PNN50_WINDOW_SIZE):
        return 0
    last_rri = 0
    all_rri_diff = []
    for v in rri_chunk:
        current_rri = last_rri if ((int(v) < LOWER_RRI_THRESHOLD) or (UPPER_RRI_THRESHOLD < int(v))) else int(v)
        rri_diff = abs(current_rri - last_rri)
        all_rri_diff.append(rri_diff)
        last_rri = current_rri
    all_rri_diff.pop(0)
    all_nn50 = [v for v in all_rri_diff if v > 50]
    pnn50 = len(all_nn50) / PNN50_WINDOW_SIZE
    return pnn50


# return a list of [time, RRI, lf/hf]
def get_latest_heart_rate_data(file_path):
    result = []
    with open(file_path, encoding="cp932", mode="r") as f:
        data = list(csv.reader(f))[6:]
        number_of_data = 0
        if (len(data) > PNN50_WINDOW_SIZE):
            number_of_data = 100
        else:
            number_of_data = len(data)
        heart_rate_data = data[:number_of_data]
        result = [[d[0], d[1], d[7]] for d in heart_rate_data]
    return result


# Test
# test_path = './whs-data/test_1.csv'
# get_latest_heart_rate_data(test_path)
# print(get_latest_heart_rate_data(test_path))
