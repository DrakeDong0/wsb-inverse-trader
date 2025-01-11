import json
import sys
import os
import matplotlib.pyplot as plt


def get_data(file_name):
    folder_path = './monthly_data'
    if not os.path.exists(folder_path):
        print("monthly_data folder does not exist")
        return
    datafiles = [f for f in os.listdir(folder_path) if os.path.isfile(
        os.path.join(folder_path, f))]
    if len(datafiles) == 0:
        print("No weekly data found")
        return

    file_name = (file_name or datafiles[-1]) + ".json"
    if file_name not in datafiles:
        print("file is not in weekly data")
        return

    with open(f'./monthly_data/{file_name}', 'r') as file:
        json_data = json.load(file)

    return json_data


def graph(file_name):
    json_data = get_data(file_name)
    ticker_count = {}

    for item in json_data:
        ticker = item['ticker']
        position = item["position"]
        if position == '':
            continue

        key = (ticker, position)
        if key in ticker_count:
            ticker_count[key] += 1
        else:
            ticker_count[key] = 1

    sorted_data = sorted(ticker_count.items(),
                         key=lambda x: x[1], reverse=True)
    labels = [f"{ticker} ({position})" for (
        ticker, position), count in sorted_data]
    counts = [count for _, count in sorted_data]
    colors = ['red' if position == 'P' else 'blue' for (
        ticker, position), _ in sorted_data]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, counts, color=colors)
    plt.xlabel("Ticker (Position)", fontsize=10)
    plt.ylabel("Count", fontsize=10)
    plt.title("r/wsb Ticker Frequency by Position", fontsize=13)
    plt.xticks(rotation=90, ha="right", fontsize=5)
    plt.tight_layout()
    plt.show()


def graph_frequency(file_name):
    json_data = get_data(file_name)
    ticker_count = {}
    for item in json_data:
        ticker = item['ticker']
        position = item["position"]
        if position == '':
            continue
        if ticker in ticker_count:
            ticker_count[ticker] += 1
        else:
            ticker_count[ticker] = 1

    sorted_data = sorted(ticker_count.items(),
                         key=lambda x: x[1], reverse=True)
    labels = [ticker for ticker, count in sorted_data]
    counts = [count for _, count in sorted_data]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, counts)
    plt.xlabel("Ticker", fontsize=10)
    plt.ylabel("Count", fontsize=10)
    plt.title("Ticker Frequency in r/wsb YOLO Posts", fontsize=13)
    plt.xticks(rotation=90, ha="right", fontsize=5)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Please provide a function and a file name. Format python graph.py function file_name")
    else:
        function_name = sys.argv[1]
        file_name = sys.argv[2]

        if function_name == "graph":
            graph(file_name)
        elif function_name == "graph_freq":
            graph_frequency(file_name)
        else:
            print("No valid function mapped to this script!")
