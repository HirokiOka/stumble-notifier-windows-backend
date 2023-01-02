import random
import csv
import time


def gen_float_num(min_num, max_num):
    rand = random.random() * (max_num - min_num) + min_num
    return round(rand, 2)


def gen_dummy_features():
    sloc = random.randint(0, 40)
    ted = random.randint(0, 10)
    elapsed_sec = random.randint(0, 3000)
    lf_hf = gen_float_num(0, 10)
    pnn50 = gen_float_num(0, 1)
    return [[sloc, ted, elapsed_sec, lf_hf, pnn50]]


def append_dummy_row_to_csv(csv_path):
    dummy_data = gen_dummy_features()
    with open(csv_path, 'a', encoding="cp932") as f:
        writer = csv.writer(f)
        writer.writerow(dummy_data[0])
        print(f'{dummy_data[0]} appended to {csv_path}')


def test_dummy():
    while True:
        print(gen_dummy_features())
        time.sleep(1)


def test_write():
    while True:
        append_dummy_row_to_csv('test.csv')
        time.sleep(1)
