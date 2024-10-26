"""
Siliconflow大模型服务调用算子
访问https://siliconflow.cn/zh-cn/models获取可用的模型的名称
"""
from .base import LLM


API_BASE = "https://api.siliconflow.cn/v1"


class Siliconflow(LLM):
    """Siliconflow平台大模型封装算子"""
    def __init__(self,
                 api_key: str = None,
                 field: str = None,
                 proxy: str = None,
                 model: str = None,
                 ignore_errors: bool = True,
                 prompt: str = None,
                 temp: float = None,
                 topk: int = None,
                 topp: float = None,
                ):
        """Siliconflow平台大模型封装算子

        :param api_key API的Key 必须
        :param field 输入的字段名，如果为None，表示整个输入作为大模型请求参数，否则，提取该字段的值
        :param proxy 调用代理，形式：http(s)://username:password@host:port
        :param model 模型名称 必须
        :param ignore_errors 是否忽略错误 如果为False且调用发生错误则抛出异常，默认True
        :param prompt 提示模板，与field搭配使用 用{data}来绑定输入数据
        :param temp 温度参数
        :param topk TopK参数
        :param topp TopP参数
        """
        super().__init__(API_BASE, field=field, api_key=api_key, model=model, proxy=proxy, prompt=prompt, ignore_errors=ignore_errors,temp=temp,topk=topk,topp=topp)
