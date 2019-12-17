import time
from vector import Vec3
from ray import Ray
import datetime


def testing_ray_timing():
    num_runs = 0
    while 1:
        try:
            num_runs = int(input("Please enter the number of runs to perform: "))
            break
        except ValueError:
            print("Use integer only.")
    print(f"Running {num_runs} runs...")

    start_time = time.time()
    with open(f"Testing Ray Timing - {num_runs} Runs - " +
              f"{datetime.datetime.now().strftime('%d-%m-%y__%H-%M-%S')}" +
              ".txt", "w") as f:
        for i in range(1, num_runs):
            start_of_ops_time = time.time()
            ops = 1000 * i
            for j in range(ops):
                pt = Vec3(i, i * 2, i + 1)
                dir1 = Vec3(i - 1, (i - 3) * 2, (i * 10) % 7)
                cross1 = pt.cross(dir1)
                ray = Ray(pt, dir1)
                ray.reflect(cross1, pt)
            f.write(f"{ops}\t{time.time() - start_of_ops_time}\n")
            print(f"Time for {ops} ops: {time.time() - start_of_ops_time}")
    print(f"Total Time: {time.time() - start_time}")