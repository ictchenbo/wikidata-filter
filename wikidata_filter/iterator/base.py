from typing import Union, Dict, Any, List
from types import GeneratorType


class Message:
    """对消息进行封装，以便在更高一层处理"""
    def __init__(self, msg_type: str, data=None):
        self.msg_type = msg_type
        self.data = data

    @staticmethod
    def end():
        return Message(msg_type="end")

    @staticmethod
    def normal(data: Any):
        return Message(msg_type="normal", data=data)


class JsonIterator:
    """流程处理算子（不包括数据加载）的基础接口"""
    def _set(self, **kwargs):
        """设置组件参数，提供对象属性链式设置"""
        for k, w in kwargs.items():
            setattr(self, k, w)
        return self

    def _get(self, key: str):
        """获取组件参数"""
        return getattr(self, key)

    def on_start(self):
        """处理数据前，主要用于一些数据处理的准备工作，不应该用于具体数据处理"""
        pass

    def on_data(self, data: Any, *args):
        """处理数据的方法。根据实际需要重写此方法。"""
        pass

    def __process__(self, data: Any, *args):
        """内部调用的处理方法，先判断是否为None 否则调用on_data进行处理，普通节点的on_data方法不会接收到None"""
        # print(f'{self.name}.__process__', data)
        if data is not None:
            if isinstance(data, Message):
                if data.msg_type == 'end':
                    print(f'{self.name} end')
                else:
                    self.on_data(data.data)
            else:
                return self.on_data(data)

    def on_complete(self):
        """结束处理。主要用于数据处理结束后的清理工作，不应该用于具体数据处理"""
        pass

    @property
    def name(self):
        return self.__class__.__name__

    def __str__(self):
        return f"{self.name}"

    def val(self, data, key=None):
        if key is None:
            return data
        if key not in data:
            print(f"Warning: `{key}` not exists")
            return None
        return data[key]


class DictProcessorBase(JsonIterator):
    """针对dict类型数据处理的基类 如果传入的非字典将不做任何处理"""
    def __process__(self, data: Any, *args):
        if data is not None:
            if isinstance(data, dict):
                return self.on_data(data)
            print('Warning: data is not a dict')
            return data


class Multiple(JsonIterator):
    """多个节点组合"""
    nodes: List[JsonIterator] = []

    def __init__(self, *args):
        """
        :param *args 处理算子
        """
        self.nodes.extend(args)

    def add(self, iterator: JsonIterator):
        """添加节点"""
        self.nodes.append(iterator)
        return self

    def on_start(self):
        for it in self.nodes:
            it.on_start()

    def on_complete(self):
        for it in self.nodes[::-1]:
            it.on_complete()

    def __str__(self):
        nodes = [str(it) for it in self.nodes]
        return f'{self.name}(nodes={nodes})'


class Fork(Multiple):
    """
    分叉节点（并行逻辑），各处理节点独立运行。Fork节点本身不产生输出。
    """
    def __init__(self, *args):
        """
        :param *args 处理算子
        """
        super().__init__(*args)

    def __process__(self, data: Any, *args):
        for it in self.nodes:
            it.__process__(data, *args)


class Chain(Multiple):
    """
    链式组合节点（串行逻辑），前一个的输出作为后一个的输入。
    """
    def __init__(self, *args):
        super().__init__(*args)

    def walk(self, data: Any, break_when_empty: bool = True, end_msg: bool = False):
        queue = [data]
        for it in self.nodes:
            # print(it)
            new_queue = []  # cache for next processor, though there's only one item for most time
            # iterate over the current cache
            for current in queue:
                res = it.__process__(current)
                if isinstance(res, GeneratorType):
                    for one in res:
                        if one is not None:
                            new_queue.append(one)
                else:
                    if res is not None:
                        new_queue.append(res)

            # empty, check if break the chain
            if not new_queue and break_when_empty:
                return new_queue

            if end_msg:
                # send a None msg in the end
                new_queue.append(None)

            queue = new_queue
        return queue

    def __process__(self, data: Any, *args):
        # 普通流程中如果收到None 则中断执行链条
        # print('Chain.__process__', data)
        if data is None:
            return None

        # 特殊消息处理
        if isinstance(data, Message):
            if data.msg_type == 'end':
                # print(f'{self.name}: END/Flush signal received.')
                queue = self.walk(data.data, break_when_empty=False, end_msg=True)
                if queue:
                    for one in queue:
                        yield one
                return
            else:
                data = data.data

        # 返回结果 从而支持与其他节点串联
        queue = self.walk(data)
        if queue:
            for one in queue:
                yield one


class Repeat(JsonIterator):
    """重复发送某个数据多次（简单循环）"""
    def __init__(self, num_of_repeats: int):
        super().__init__()
        self.num_of_repeats = num_of_repeats

    def on_data(self, data, *args):
        for i in range(self.num_of_repeats):
            yield data

    def __str__(self):
        return f'{self.name}[num_of_repeats={self.num_of_repeats}]'
