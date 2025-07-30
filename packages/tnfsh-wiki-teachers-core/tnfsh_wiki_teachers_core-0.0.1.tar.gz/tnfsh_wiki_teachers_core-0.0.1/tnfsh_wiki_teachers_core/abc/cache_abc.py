from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic


TResult = TypeVar("TResult")

class BaseCacheABC(ABC, Generic[TResult]):
    """
    Cache 層的抽象基底類，規範三層快取（memory/file/source）的標準介面。

    推薦 fetch fallback/save 流程：
    1. 先嘗試 fetch_from_memory，若有資料直接回傳。
    2. 若 memory 沒有，則 fetch_from_file，若有資料則 save_to_memory 並回傳。
    3. 若 file 也沒有，則 fetch_from_source，然後 save_to_file、save_to_memory，最後回傳。
    4. 具體流程建議由子類在 fetch 方法中實作。
    """    

    @classmethod
    async def fetch(cls, *args: Any, refresh: bool = False, **kwargs: Any) -> TResult:
        """統一對外取得資料（自動處理 memory/file/source）"""
        self=cls(*args, **kwargs)
        if not refresh:
            # 1. 先嘗試從 memory 拿
            if memory_data := await self.fetch_from_memory(*args, **kwargs):
                return memory_data
            
            # 2. 若 memory 沒有，從 file 拿
            if file_data := await self.fetch_from_file(*args, **kwargs):
                # 有的話存到 memory 再回傳
                await self.save_to_memory(file_data, *args, **kwargs)
                return file_data
        
        # 3. 若 file 也沒有或是要求更新，從 source 拿
        if source_data := await self.fetch_from_source(*args, **kwargs):
            # 存到 file 和 memory
            await self.save_to_file(source_data, *args, **kwargs)
            await self.save_to_memory(source_data, *args, **kwargs)
            return source_data
        
        raise ValueError("無法從任何來源取得資料")    
    @abstractmethod
    async def fetch_from_memory(self, *args:Any, **kwargs:Any) -> TResult | None:
        """從記憶體快取取得資料"""
        pass

    @abstractmethod
    async def save_to_memory(self, data: Any, *args:Any , **kwargs:Any) -> None:
        """儲存資料到記憶體快取"""
        pass    
    
    @abstractmethod
    async def fetch_from_file(self, *args: Any, **kwargs: Any) -> TResult | None:
        """從本地檔案快取取得資料"""          
        pass
    
    @abstractmethod
    async def save_to_file(self, data: Any, *args: Any, **kwargs: Any) -> None:
        """儲存資料到本地檔案快取"""            
        pass


    @abstractmethod
    async def fetch_from_source(self, *args:Any, **kwargs:Any) -> TResult | None:
        """從最終來源取得資料（如網路、其他服務等）"""
        pass