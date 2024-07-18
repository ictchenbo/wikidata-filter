class JsonIterator:
    return_multiple: bool = False

    def on_start(self):
        pass

    def on_data(self, data: dict or None, *args):
        pass

    def on_complete(self):
        pass


class Group(JsonIterator):
    """
    迭代器组 将多个迭代器组合在一起
    """
    def __init__(self, *args):
        super().__init__()
        self.iterators = [*args]

    def add(self, iterator: JsonIterator):
        self.iterators.append(iterator)
        return self

    def on_start(self):
        for it in self.iterators:
            it.on_start()

    def on_data(self, data: dict or None, *args):
        for it in self.iterators:
            it.on_data(data, *args)

    def on_complete(self):
        for it in self.iterators[::-1]:
            it.on_complete()


class Chain(Group):
    """
    链式 前一个的输出作为后一个的输入
    """
    def __init__(self, *args, ignore_errors=True):
        super().__init__(*args)
        self.ignore_errors = ignore_errors

    def on_data(self, data: dict or None, *args):
        queue = [data]
        for it in self.iterators:
            new_queue = []  # cache for next processor, though there's only one item for most time
            # iterate over the current cache
            for current in queue:
                # if the processor produces multiple items
                if it.return_multiple:
                    for one in it.on_data(current):
                        if one is not None:
                            new_queue.append(one)
                else:
                    one = it.on_data(current)
                    if one is not None:
                        new_queue.append(one)
            if not new_queue:
                break
            queue = new_queue

            # if self.ignore_errors:
            #     try:
            #         data = it.on_data(data, *args)
            #     except Exception as e:
            #         print('processing error!', data)
            #         break
            # else:
            #     data = it.on_data(data, *args)
        if not queue:
            return None

        if len(queue) == 1:
            return queue[0]

        return data


class Repeat(JsonIterator):
    def __init__(self, num_of_repeats: int):
        super().__init__()
        self.num_of_repeats = num_of_repeats
        self.return_multiple = True

    def on_data(self, data, *args):
        for i in range(self.num_of_repeats):
            yield data
