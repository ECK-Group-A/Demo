#!/usr/bin/env python3 -u

from datetime import datetime
import random
import sys

old_time = round(datetime.timestamp(datetime.now()), 1)

while True:
    time = datetime.timestamp(datetime.now())
    if time - old_time > 0.1:
        print(round(round((time + (random.random() * 0.01)), 6) * 1000000))
        old_time = round(time, 1)
