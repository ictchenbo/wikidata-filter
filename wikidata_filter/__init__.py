from typing import Any
from types import GeneratorType
from wikidata_filter.loader import DataProvider
from wikidata_filter.loader.base import ArrayProvider, TextProvider
from wikidata_filter.loader.wikidata import WikidataJsonDump
from wikidata_filter.iterator.base import Message, JsonIterator
from wikidata_filter.flow_engine import ProcessFlow


def run(data_provider: DataProvider, iterator: JsonIterator, finish_signal=False):
    print(f"Run flow: \nloader: {data_provider}\nprocessor: {iterator}")
    print("------------------------")
    iterator.on_start()

    # 注意，由于iterator.on_data可能包含yield，因此仅调用iterator.on_data(data)可能不会真正执行
    def execute(data: Any, *args):
        res = iterator.__process__(data)
        if isinstance(res, GeneratorType):
            for _ in res:
                pass

    for item in data_provider.iter():
        execute(item)

    data_provider.close()

    execute(Message.end())

    iterator.on_complete()
    print("------------------------")


def run_flow(flow_file: str, *args, finish_signal: bool = False, input_data=None):
    flow = ProcessFlow(flow_file, *args)
    print('loading YAML flow:', flow.name)
    # 根据命令行参数构造loader
    if input_data:
        if isinstance(input_data, str):
            _loader = TextProvider(input_data)
        elif isinstance(input_data, list):
            _loader = ArrayProvider(input_data)
        else:
            _loader = ArrayProvider([input_data])
        flow.loader = _loader
    assert flow.loader is not None, "loader为空！可通过yaml文件或命令行参数进行配置"
    run(flow.loader, flow.processor, finish_signal=finish_signal or flow.end_signal)


def process_wikidata(infile: str, iterator: JsonIterator, parallels: int = 1, parallel_runner: str = "multi_thread"):
    """ 主函数
    :param infile: 输入文件
    :param iterator 迭代器
    :param parallels 并发数
    :param parallel_runner 并发方法  multi_thread/multi_process
    """

    dump_loader = WikidataJsonDump(infile)

    def process_item(item):
        iterator.on_data(item, None)

    iterator.on_start()
    if parallels > 1:
        if parallel_runner == "multi_thread":
            from concurrent.futures import ThreadPoolExecutor
            pool = ThreadPoolExecutor(max_workers=parallels)
            for item in dump_loader.iter():
                pool.submit(process_item, (item,))
            pool.shutdown()
        else:
            import multiprocessing
            for item, line in dump_loader.iter():
                sub_process = multiprocessing.Process(target=process_item, args=(item,))
                sub_process.start()
    else:
        for item, line in dump_loader.iter():
            process_item(item)

    iterator.on_complete()
