from random import random


class DataProvider:
    def iter(self):
        pass

    def __call__(self, *args, **kwargs):
        return self.iter()

    def close(self):
        pass


class RandomGenerator(DataProvider):
    def __init__(self, num_of_times: int = 0):
        self.num_of_times = num_of_times

    def iter(self):
        if self.num_of_times > 0:
            for i in range(self.num_of_times):
                yield random()
        else:
            while True:
                yield random()
