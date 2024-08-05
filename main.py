import statistics
from typing import List
from prefect import flow, task


@task
def calculate_mean(nums: List[int]):
    return statistics.mean(nums)


@task
def calculate_median(nums: List[int]):
    return statistics.median(nums)


@flow(log_prints=True)
def mean_and_median():
    nums = [5, 2, 2, 3, 5, 4]

    mean = calculate_mean(nums=nums)
    median = calculate_median(nums=nums)

    print(mean, median)


if __name__ == "__main__":
    mean_and_median()
