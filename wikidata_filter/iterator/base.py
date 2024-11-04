class JsonIterator:
    """流程处理算子（不包括数据加载）的基础接口"""
    return_multiple: bool = False

    def _set(self, **kwargs):
        """设置组件参数，提供对象属性链式设置"""
        for k, w in kwargs.items():
            setattr(self, k, w)
        return self

    def _get(self, key: str):
        """获取组件参数"""
        return getattr(self, key)

    def on_start(self):
        """处理数据前"""
        pass

    def on_data(self, data: dict or None, *args):
        """处理每一条数据"""
        pass

    def on_complete(self):
        """"结束处理"""
        pass

    @property
    def name(self):
        return self.__class__.__name__

    def __str__(self):
        return f'{self.name}[multiple={self.return_multiple}]'


class Group(JsonIterator):
    """
    迭代器组 将多个迭代器组合在一起
    """
    def __init__(self, *args, skip_none=True):
        super().__init__()
        self.skip_none = skip_none
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
    def __init__(self, *args, ignore_errors=True, skip_none=True):
        super().__init__(*args, skip_none=skip_none)
        self.ignore_errors = ignore_errors
        self.return_multiple = True

    def on_data(self, data: dict or None, *args):
        if self.skip_none and data is None:
            return None
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
            # chain break
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

        return queue
        # if len(queue) == 1:
        #     return queue[0]
        #
        # return data


class Repeat(JsonIterator):
    """重复发送某个数据多次"""
    def __init__(self, num_of_repeats: int):
        super().__init__()
        self.num_of_repeats = num_of_repeats
        self.return_multiple = True

    def on_data(self, data, *args):
        for i in range(self.num_of_repeats):
            yield data
