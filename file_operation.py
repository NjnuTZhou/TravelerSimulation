import json
import csv
import os


def open_json_file(path):
    return json.loads(open(path, mode='r', encoding='utf-8').read())


def write_json_file(data, path):
    if os.path.exists(path):
        os.remove(path)
    open(path, mode='a+', encoding='utf-8').write(json.dumps(data, indent=4, ensure_ascii=False))


def print_json(data):
    print(json.dumps(data, indent=4, ensure_ascii=False))


def get_csv_writer(path):
    if os.path.exists(path):
        os.remove(path)
    return csv.writer(open(path, mode='a+', encoding='utf-8', newline=''))


def open_csv_file(path):
    csv_reader = csv.reader(open(path,encoding='utf-8',mode='r'))
    result = []
    for row in csv_reader:
        result.append(row)
    result.pop(0)
    return result
