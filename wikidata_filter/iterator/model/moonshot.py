"""
月之暗面（Kimi）大模型服务调用算子
访问https://platform.moonshot.cn/docs/api/chat#%E5%85%AC%E5%BC%80%E7%9A%84%E6%9C%8D%E5%8A%A1%E5%9C%B0%E5%9D%80
"""
from .base import LLM

API_BASE = "https://api.moonshot.cn/v1"
MODEL_NAME = "moonshot-v1-8"


class Moonshot(LLM):
    """月之暗面（Kimi）大模型封装算子"""
    def __init__(self,
                 api_key: str,
                 field: str = None,
                 proxy: str = None,
                 ignore_errors: bool = True,
                 prompt: str = None,
                 temp: float = None,
                 topk: int = None,
                 topp: float = None,
                 ):
        """
                :param api_key API的Key 必须
                :param field 输入的字段名，如果为None，表示整个输入作为大模型请求参数，否则，提取该字段的值
                :param proxy 调用代理，形式：http(s)://username:password@host:port
                :param ignore_errors 是否忽略错误 如果为False且调用发生错误则抛出异常，默认True
                :param prompt 提示模板，与field搭配使用 用{data}来绑定输入数据
                :param temp 温度参数
                :param topk TopK参数
                :param topp TopP参数
        """
        super().__init__(API_BASE, field=field, api_key=api_key, model=MODEL_NAME, proxy=proxy, prompt=prompt, ignore_errors=ignore_errors,temp=temp,topk=topk,topp=topp)
