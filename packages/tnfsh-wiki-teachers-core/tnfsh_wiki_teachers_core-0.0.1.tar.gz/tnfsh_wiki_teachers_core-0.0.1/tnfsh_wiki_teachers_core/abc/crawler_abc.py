from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

TResult = TypeVar("TResult")

class BaseCrawlerABC(ABC, Generic[TResult]):
    """
    Crawler 層的抽象基底類，規範所有爬蟲/資料抓取器的標準介面。
    """
    @abstractmethod
    async def fetch_raw(self, *args:Any, **kwargs:Any) -> Any:
        """
        從其他地方拿到資料
        """
        pass

    @abstractmethod
    def parse(self, raw: Any, *args:Any, **kwargs:Any) -> TResult:
        """
        解析資料成好的資料結構
        """
        pass
    
    @classmethod
    async def fetch(cls, *args:Any, **kwargs:Any) -> TResult:
        """
        拿資料並解析
        """
        self = cls(*args, **kwargs)
        raw = await self.fetch_raw()
        result = self.parse(raw)
        return result