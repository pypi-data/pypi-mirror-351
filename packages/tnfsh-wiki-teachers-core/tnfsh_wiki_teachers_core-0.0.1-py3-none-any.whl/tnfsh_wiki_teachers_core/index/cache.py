"""台南一中教師維基索引快取模組。

此模組提供了快取機制，用於儲存和讀取從維基系統爬取的教師資訊。
它實現了三層快取策略：記憶體快取、檔案快取和來源重新抓取。

Classes:
    TeacherInfo: 教師資訊的資料模型
    IndexCache: 正向索引（科目 -> 教師列表）的快取管理
    ReverseIndexCache: 反向索引（教師 -> 科目資訊）的快取管理
"""

from typing import Any
from tnfsh_wiki_teachers_core.abc.cache_abc import BaseCacheABC
from tnfsh_wiki_teachers_core.index.crawler import SubjectTeacherMap, IndexCrawler
from pydantic import BaseModel

class TeacherInfo(BaseModel):
    """教師資訊模型，用於反向索引。
    
    此類別定義了每位教師的基本資訊，包括其所屬科目和維基頁面連結。
    用於建立反向索引，方便由教師名稱查找相關資訊。

    Attributes:
        category (str): 教師所屬科目類別
        url (str): 教師的維基頁面URL
    """
    category: str
    url: str
    
from tnfsh_wiki_teachers_core.utils.dict_root_model import DictRootModel

class ReverseIndexMap(DictRootModel[str, TeacherInfo]): 
    """反向索引映射，將教師名稱對應到其科目和URL資訊。

    這個類別提供了一個映射結構，可以快速地根據教師名稱查找其相關資訊。
    它繼承自 DictRootModel，提供了一個類似字典的介面，但具有更好的型別安全性。

    Type Parameters:
        str: 鍵的類型，這裡是教師名稱
        TeacherInfo: 值的類型，包含教師的科目和URL資訊

    Example:
        reverse_index = ReverseIndexMap(root={
            "王小明": TeacherInfo(category="數學", url="/王小明")
        })
        teacher_info = reverse_index["王小明"]  # 獲取教師資訊
    """
    pass

# 全域快取變數：用於記憶體快取層
index_cache: SubjectTeacherMap| None = None  # 正向索引快取
reverse_index_cache: ReverseIndexMap| None = None  # 反向索引快取

class IndexCache(BaseCacheABC[SubjectTeacherMap]):
    """正向索引快取管理器。

    此類別實現了三層快取機制來管理台南一中教師維基的正向索引資料
    （從科目到教師的映射）。三個快取層級依序為：
    1. 記憶體快取: 使用全域變數 index_cache，提供最快的存取速度
    2. 檔案快取: 將資料持久化到本地檔案系統
    3. 來源抓取: 當其他快取層級失效時，從維基網站重新抓取

    繼承自 BaseCacheABC，使用 SubjectTeacherMap 作為資料模型。

    Attributes:
        max_concurrency (int): 抓取資料時的最大併發請求數
        _cache_dir (Path): 快取檔案的目錄路徑
        _cache_file (Path): 快取檔案的完整路徑

    Example:
        cache = IndexCache()
        data = await cache.fetch()  # 自動從最快的可用快取層級獲取資料
    """    
    def __init__(self, max_concurrency:int = 5):
        """初始化索引快取管理器。

        Args:
            max_concurrency (int): 從來源抓取資料時的最大併發請求數，預設為 5
        """
        from pathlib import Path
        self.max_concurrency: int = max_concurrency
        self._cache_dir = Path(__file__).resolve().parent / "cache"
        self._cache_file = self._cache_dir / "prebuilt_index.json"
        self._cache_dir.mkdir(exist_ok=True)
    
    @classmethod
    async def fetch(cls, refresh: bool = False, max_concurrency: int = 5) -> SubjectTeacherMap:
        """類別方法：取得索引資料。

        這是主要的資料存取入口點。它會按照優先順序嘗試從不同的快取層級獲取資料：
        1. 記憶體快取（如果 refresh=False）
        2. 檔案快取（如果 refresh=False）
        3. 來源重新抓取

        Args:
            refresh (bool): 是否強制從來源重新抓取，忽略快取
            max_concurrency (int): 抓取時的最大併發請求數

        Returns:
            SubjectTeacherMap: 科目到教師的映射資料
        """
        return await super().fetch(refresh=refresh, max_concurrency=max_concurrency)

    async def fetch_from_memory(self, *args: Any, **kwargs: Any) -> SubjectTeacherMap | None:
        """從記憶體快取中取得資料。
        
        這是最快的資料存取方式，但資料會在程式結束時消失。

        Returns:
            SubjectTeacherMap | None: 快取的索引資料，若快取不存在則為 None
        """
        return index_cache
    
    async def save_to_memory(self, data: SubjectTeacherMap, *args: Any, **kwargs: Any) -> None:
        """將資料儲存到記憶體快取。

        Args:
            data (SubjectTeacherMap): 要快取的索引資料
        """
        global index_cache
        index_cache = data
    async def fetch_from_file(self, *args: Any, **kwargs: Any) -> SubjectTeacherMap | None:
        """從本地檔案快取取得資料。
        
        此方法會嘗試從本地檔案系統讀取快取資料。當記憶體快取不可用時，
        這是第二個嘗試的快取層級。

        Returns:
            SubjectTeacherMap | None: 快取的索引資料，若讀取失敗則為 None
        """
        import json
        try:
            if not self._cache_file.exists():
                return None
                
            with open(self._cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return SubjectTeacherMap.model_validate(data)
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    async def save_to_file(self, data: SubjectTeacherMap, *args: Any, **kwargs: Any) -> None:
        """將資料儲存到本地檔案快取。
        
        此方法負責將資料持久化到檔案系統，確保資料可以在程式重啟後仍然可用。
        檔案會以 JSON 格式儲存，並使用 UTF-8 編碼以正確處理中文字元。
        
        Args:
            data (SubjectTeacherMap): 要快取的索引資料，包含科目到教師的映射
        """
        import json
        with open(self._cache_file, "w", encoding="utf-8") as f:
            json.dump(data.model_dump(), f, ensure_ascii=False, indent=4)
    async def fetch_from_source(self, max_concurrency:int = 5, *args: Any, **kwargs: Any) -> SubjectTeacherMap:
        """從維基網站重新抓取資料。
        
        當所有快取層級都失效時，此方法會被調用來從原始來源重新抓取資料。
        這是最慢但能獲得最新資料的方式。

        Args:
            max_concurrency (int): 最大併發請求數，用於控制對伺服器的請求頻率
            
        Returns:
            SubjectTeacherMap: 新抓取的科目教師映射資料
        """
        index_crawler = IndexCrawler()
        result: SubjectTeacherMap = await index_crawler.fetch(*args, max_concurrency=max_concurrency, **kwargs)
        return result

    

class ReverseIndexCache(BaseCacheABC[ReverseIndexMap]):
    """反向索引的快取管理器。

    此類別實現了三層快取機制來管理教師到科目的反向索引映射。
    它可以快速查找特定教師的科目歸屬和維基頁面連結。快取層級依序為：
    1. 記憶體快取: 使用全域變數 reverse_index_cache
    2. 檔案快取: JSON 格式的本地檔案存儲
    3. 來源重建: 從正向索引重新建構

    此類別繼承自 BaseCacheABC，使用 ReverseIndexMap 作為資料模型。

    Attributes:
        max_concurrency (int): 從來源抓取資料時的最大併發請求數
        _cache_dir (Path): 快取檔案的存放目錄
        _cache_file (Path): 反向索引快取檔案的路徑
    """
    
    def __init__(self, max_concurrency:int = 5):
        """初始化反向索引快取管理器。

        Args:
            max_concurrency (int): 從來源抓取資料時的最大併發請求數
        """
        from pathlib import Path
        self.max_concurrency: int = max_concurrency
        self._cache_dir = Path(__file__).resolve().parent / "cache"
        self._cache_file = self._cache_dir / "prebuilt_reverse_index.json"
        self._cache_dir.mkdir(exist_ok=True)
    @classmethod
    async def fetch(cls, refresh: bool = False, max_concurrency: int = 5) -> ReverseIndexMap:
        """類別方法：取得反向索引資料。

        這是獲取反向索引的主要入口點，會依序嘗試：
        1. 記憶體快取（若 refresh=False）
        2. 檔案快取（若 refresh=False）
        3. 從正向索引重新建構

        Args:
            refresh (bool): 是否強制重新建構索引，忽略快取
            max_concurrency (int): 重建索引時的最大併發請求數

        Returns:
            ReverseIndexMap: 教師到科目的反向映射
        """
        return await super().fetch(refresh=refresh, max_concurrency=max_concurrency)

    async def fetch_from_memory(self, *args: Any, **kwargs: Any) -> ReverseIndexMap | None:
        """從記憶體快取中取得反向索引。
        
        這是最快的資料存取方式，但資料會在程式結束時消失。

        Returns:
            ReverseIndexMap | None: 快取的反向索引，若快取不存在則為 None
        """
        return reverse_index_cache
    
    async def save_to_memory(self, data: ReverseIndexMap, *args: Any, **kwargs: Any) -> None:
        """將反向索引儲存到記憶體快取。

        Args:
            data (ReverseIndexMap): 要快取的反向索引資料
        """
        global reverse_index_cache
        reverse_index_cache = data
    async def fetch_from_file(self, *args: Any, **kwargs: Any) -> ReverseIndexMap | None:
        """從本地檔案快取取得反向索引資料。
        
        此方法會嘗試從本地檔案系統讀取快取的反向索引。當記憶體快取不可用時，
        這是第二個嘗試的快取層級。檔案內容會被驗證並轉換為正確的資料模型。

        Returns:
            ReverseIndexMap | None: 快取的反向索引資料，若讀取或驗證失敗則為 None
        """
        import json
        try:
            if not self._cache_file.exists():
                return None
                
            with open(self._cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return ReverseIndexMap.model_validate(data)
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    async def save_to_file(self, data: ReverseIndexMap, *args: Any, **kwargs: Any) -> None:
        """將反向索引儲存到本地檔案快取。
        
        此方法負責將反向索引資料持久化到檔案系統。它會使用 model_dump 
        方法確保資料正確序列化，並以 JSON 格式儲存。

        Args:
            data (ReverseIndexMap): 要快取的反向索引資料
        """
        import json
        with open(self._cache_file, "w", encoding="utf-8") as f:
            json.dump(data.model_dump(), f, ensure_ascii=False, indent=4)
    async def fetch_from_source(self, max_concurrency:int = 5, *args: Any, **kwargs: Any) -> ReverseIndexMap:
        """從正向索引重新建構反向索引。
        
        當所有快取層級都失效時，此方法會被調用。它會：
        1. 從維基網站抓取最新的正向索引
        2. 將科目到教師的映射轉換為教師到科目的映射
        
        這個過程相對耗時，但能確保資料的完整性和即時性。

        Args:
            max_concurrency (int): 抓取正向索引時的最大併發請求數
            
        Returns:
            ReverseIndexMap: 新建構的反向索引映射
        """
        index_crawler = IndexCrawler()
        forward_index: SubjectTeacherMap = await index_crawler.fetch(*args, max_concurrency=max_concurrency, **kwargs)
        reverse_index_map: ReverseIndexMap = ReverseIndexMap(root={})

        # 將正向索引轉換為反向索引
        for category, subject_info in forward_index.items():
            for name, url in subject_info.teachers.items():
                reverse_index_map[name] = TeacherInfo(category=category, url=url)

        return reverse_index_map


if __name__ == "__main__" :
    import asyncio
    import json
    result = asyncio.run(IndexCache.fetch(refresh=True, max_concurrency=5))
    print(json.dumps(result.model_dump(), indent=4, ensure_ascii=False))