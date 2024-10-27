from wikidata_filter import run_flow


if __name__ == '__main__':
    import argparse
    import json
    # 创建解析器对象
    parser = argparse.ArgumentParser(description="wikidata-filter: a simple but strong data processing framework")

    # 添加位置参数
    parser.add_argument("filename", type=str, help="yaml流程定义文件路径")

    # 添加可选参数
    parser.add_argument("-i", "--input", type=str, default=None, help="直接提供流程输入数据")
    parser.add_argument("--json", default=False, action="store_true", help="将--input参数提供的输入数据作为json加载，默认为纯文本")

    # 解析参数
    args, unknown = parser.parse_known_args()
    input_data = args.input
    if input_data and args.json is True:
        input_data = json.loads(input_data)

    flow_file = args.filename

    run_flow(flow_file, *unknown, input_data=input_data)
