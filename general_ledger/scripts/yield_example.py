import random


def random_item(*args):
    tmp = args
    idx = random.randint(0, len(tmp) - 1)
    item = tmp.pop(idx)
    yield item


for _ in range(10):
    print(random_item("a", "b", "c", "d", "e"))
