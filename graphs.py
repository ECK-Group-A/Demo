import os
from os import times
from pkg_resources import yield_lines
from tqdm import tqdm
import time
import statistics
import math

def readTimestamps():
    with open('camera.log', 'r') as f1:
        with open('lidar.log', 'r') as f2:
            timestamps1 = {round(int(t.strip()) / 100000): int(t.strip()) for t in f1}
            timestamps2 = {round(int(t.strip()) / 100000): int(t.strip()) for t in f2}

            keys = list(set(list(timestamps1.keys()) + list(timestamps2.keys())))

            timestamps = {timestamp: (timestamps1.get(timestamp, None), timestamps2.get(timestamp, None)) for timestamp in keys}

            return timestamps

t = tqdm(total=1)

while True:
    timestamps = readTimestamps()
    unmached = 0
    total = len(timestamps.keys())

    found_start = False

    for key in timestamps.keys():
        if None in timestamps[key]:
            if found_start:
                unmached += 1
        else:
            found_start = True

    differences = []

    for key in timestamps.keys():
        if not None in timestamps[key]:
            differences.append(abs(timestamps[key][0] - timestamps[key][1]) / 1000)

    if len(differences) > 2:
        total_timestamps = str(total).rjust(10)
        unmached_timestamps = str(unmached).rjust(10)
        percentage_matched = format(round(100 - (unmached / total) * 100, 2), '.2f').rjust(10)
        average_difference = format(round(statistics.mean(differences), 2), '.2f').rjust(10)
        median_difference = format(round(statistics.median(differences), 2), '.2f').rjust(10)
        max_difference = format(round(max(differences), 2), '.2f').rjust(10)
        min_difference = format(round(min(differences), 2), '.2f').rjust(10)
        std_deviation = format(round(statistics.stdev(differences), 2), '.2f').rjust(10)
        std_error = format(round(statistics.stdev(differences) / math.sqrt(len(differences)), 2), '.2f').rjust(10)
        median_error = format(round(statistics.median(differences) / math.sqrt(len(differences)), 2), '.2f').rjust(10)
        mean_error = format(round(statistics.mean(differences) / math.sqrt(len(differences)), 2), '.2f').rjust(10)

    os.system('clear')

    print(f"Total timestamps:    {total_timestamps}")
    print(f"Unmached timestamps: {unmached_timestamps}")
    print(f"Percentage matched:  {percentage_matched} %")

    print()

    if len(differences) > 2:
        print(f"Mean difference:     {average_difference} μs")
        print(f"Median difference:   {median_difference} μs")
        print(f"Max difference:      {max_difference} μs")
        print(f"Min difference:      {min_difference} μs")
        print()
        print(f"Standard deviation:  {std_deviation} μs")
        print(f"Standard error:      {std_error} μs")
        print(f"Median error:        {median_error} μs")
        print(f"Mean error:          {median_difference} μs")
    else:
        print("Mean difference:             NA μs")
        print("Median difference:           NA μs")
        print("Max difference:              NA μs")
        print("Min difference:              NA μs")
        print()
        print("Standard deviation:          NA μs")
        print("Standard error:              NA μs")
        print("Median error:                NA μs")
        print("Mean error:                  NA μs")

    time.sleep(0.5)