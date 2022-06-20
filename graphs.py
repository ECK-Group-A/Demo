import os
import time
import statistics
import math
import plotext as plt
from rich import print

def readTimestamps():
    with open('camera.log', 'r') as f1:
        with open('lidar.log', 'r') as f2:
            timestamps1 = {round((int(t.strip()) / 100000000) % 36000): round((int(t.strip()) / 1000) % 3600000000) for t in f1}
            timestamps2 = {round(int(t.strip()) / 100000): int(t.strip()) for t in f2}

            keys = list(set(list(timestamps1.keys()) + list(timestamps2.keys())))

            timestamps = {timestamp: (timestamps1.get(timestamp, None), timestamps2.get(timestamp, None)) for timestamp in keys}

            return timestamps

while True:
    timestamps = readTimestamps()
    unmached = 0
    total = len(timestamps.keys())

    found_start = False

    for key in timestamps.keys():
        if None in timestamps[key]:
            total -= 1
            if found_start:
                unmached += 1
        else:
            found_start = True

    differences = []

    for key in timestamps.keys():
        if not None in timestamps[key]:
            differences.append(timestamps[key][0] - timestamps[key][1])
    
    with open("differences.txt", "w") as f:
        for difference in differences:
            f.write(str(difference) + "\n")

    with open("timestamps.txt", "w") as f:
        for data in timestamps.items():
            f.write(str(data) + "\n")

    total_timestamps = str(total).rjust(10)
    unmached_timestamps = str(unmached).rjust(10)
    percentage_matched = format(round(100 - (unmached / total) * 100, 2), '.2f').rjust(10)

    camera_differences = [t[1][0] - (t[0] * 100000) for t in timestamps.items() if not t[1][0] == None]
    lidar_differences = [t[1][1] - (t[0] * 100000) for t in timestamps.items() if not t[1][1] == None]

    terminal_size = os.get_terminal_size()

    if len(differences) > 2:
        average_difference1 = format(round(statistics.mean(differences), 2), '.2f').rjust(10)
        median_difference1 = format(round(statistics.median(differences), 2), '.2f').rjust(10)
        max_difference1 = format(round(max(differences), 2), '.2f').rjust(10)
        min_difference1 = format(round(min(differences), 2), '.2f').rjust(10)
        std_deviation1 = format(round(statistics.stdev(differences), 2), '.2f').rjust(10)
        std_error1 = format(round(statistics.stdev(differences) / math.sqrt(len(differences)), 2), '.2f').rjust(10)
        median_error1 = format(round(statistics.median(differences) / math.sqrt(len(differences)), 2), '.2f').rjust(10)
        mean_error1 = format(round(statistics.mean(differences) / math.sqrt(len(differences)), 2), '.2f').rjust(10)

        average_difference2 = format(round(statistics.mean(camera_differences), 2), '.2f').rjust(10)
        median_difference2 = format(round(statistics.median(camera_differences), 2), '.2f').rjust(10)
        max_difference2 = format(round(max(camera_differences), 2), '.2f').rjust(10)
        min_difference2 = format(round(min(camera_differences), 2), '.2f').rjust(10)
        std_deviation2 = format(round(statistics.stdev(camera_differences), 2), '.2f').rjust(10)
        std_error2 = format(round(statistics.stdev(camera_differences) / math.sqrt(len(camera_differences)), 2), '.2f').rjust(10)
        median_error2 = format(round(statistics.median(camera_differences) / math.sqrt(len(camera_differences)), 2), '.2f').rjust(10)
        mean_error2 = format(round(statistics.mean(camera_differences) / math.sqrt(len(camera_differences)), 2), '.2f').rjust(10)

        average_difference3 = format(round(statistics.mean(lidar_differences), 2), '.2f').rjust(10)
        median_difference3 = format(round(statistics.median(lidar_differences), 2), '.2f').rjust(10)
        max_difference3 = format(round(max(lidar_differences), 2), '.2f').rjust(10)
        min_difference3 = format(round(min(lidar_differences), 2), '.2f').rjust(10)
        std_deviation3 = format(round(statistics.stdev(lidar_differences), 2), '.2f').rjust(10)
        std_error3 = format(round(statistics.stdev(lidar_differences) / math.sqrt(len(lidar_differences)), 2), '.2f').rjust(10)
        median_error3 = format(round(statistics.median(lidar_differences) / math.sqrt(len(lidar_differences)), 2), '.2f').rjust(10)
        mean_error3 = format(round(statistics.mean(lidar_differences) / math.sqrt(len(lidar_differences)), 2), '.2f').rjust(10)
        
        plt.plot_size(200, 15)
        plt.subplots(1, 3)
        plt.cld()
        plt.subplot(1,1).hist(differences, 50)
        plt.subplot(1,1).title("Timestamp difference Camera and LIDAR")
        plt.subplot(1,1).ylabel("Frequency")
        plt.subplot(1,1).xlabel("Time Difference (us)")
        plt.subplot(1,2).hist(camera_differences, 50)
        plt.subplot(1,2).title("Timestamp difference 100ms and Camera")
        plt.subplot(1,2).ylabel("Frequency")
        plt.subplot(1,2).xlabel("Time Difference (us)")
        plt.subplot(1,3).hist(lidar_differences, 50)
        plt.subplot(1,3).title("Timestamp difference 100ms and LIDAR")
        plt.subplot(1,3).ylabel("Frequency")
        plt.subplot(1,3).xlabel("Time Difference (us)")


    os.system('clear')

    print()
    print("[bold underline red]Lidar Camera Synchronization Demo[/bold underline red]")
    print()
    print(f"Total timestamps:    {total_timestamps}   {' ' * round(terminal_size[0] / 3 - 34)}Unmached timestamps: {unmached_timestamps}   {' ' * round(terminal_size[0] / 3 - 34)}Percentage matched:  {percentage_matched} %")
    print()

    if len(differences) > 2:
        plt.show()
        print()
        print(f"Mean difference:     {average_difference1} μs{' ' * round(terminal_size[0] / 3 - 34)}Mean difference:     {average_difference2} μs{' ' * round(terminal_size[0] / 3 - 34)}Mean difference:     {average_difference3} μs")
        print(f"Median difference:   {median_difference1 } μs{' ' * round(terminal_size[0] / 3 - 34)}Median difference:   {median_difference2 } μs{' ' * round(terminal_size[0] / 3 - 34)}Median difference:   {median_difference3 } μs")
        print(f"Max difference:      {max_difference1    } μs{' ' * round(terminal_size[0] / 3 - 34)}Max difference:      {max_difference2    } μs{' ' * round(terminal_size[0] / 3 - 34)}Max difference:      {max_difference3    } μs")
        print(f"Min difference:      {min_difference1    } μs{' ' * round(terminal_size[0] / 3 - 34)}Min difference:      {min_difference2    } μs{' ' * round(terminal_size[0] / 3 - 34)}Min difference:      {min_difference3    } μs")
        print()
        print(f"Standard deviation:  {std_deviation1     } μs{' ' * round(terminal_size[0] / 3 - 34)}Standard deviation:  {std_deviation2     } μs{' ' * round(terminal_size[0] / 3 - 34)}Standard deviation:  {std_deviation3     } μs")
        print(f"Standard error:      {std_error1         } μs{' ' * round(terminal_size[0] / 3 - 34)}Standard error:      {std_error2         } μs{' ' * round(terminal_size[0] / 3 - 34)}Standard error:      {std_error3         } μs")
        print(f"Median error:        {median_error1      } μs{' ' * round(terminal_size[0] / 3 - 34)}Median error:        {median_error2      } μs{' ' * round(terminal_size[0] / 3 - 34)}Median error:        {median_error3      } μs")
        print(f"Mean error:          {mean_error1        } μs{' ' * round(terminal_size[0] / 3 - 34)}Mean error:          {mean_error2        } μs{' ' * round(terminal_size[0] / 3 - 34)}Mean error:          {mean_error3        } μs")
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