from tnfsh_wiki_teachers_core.abc.crawler_abc import BaseCrawlerABC
from typing import Any, Dict, List, Tuple, TypeVar
import aiohttp
import asyncio
from aiohttp import ClientSession
from tnfsh_wiki_teachers_core.abc.crawler_abc import BaseCrawlerABC
from pydantic import BaseModel

T = TypeVar("T")

# 定義教師映射類型：{教師名稱: URL}
TeacherMap = Dict[str, str]

# 每個科別的詳細資訊
class SubjectInfo(BaseModel):
    """科別的詳細資訊結構。
    
    Attributes:
        url (str): 科別的維基頁面URL
        teachers (TeacherMap): 該科別下的教師映射，格式為 {教師名稱: 教師頁面URL}
    """
    url: str
    teachers: TeacherMap

from tnfsh_wiki_teachers_core.utils.dict_root_model import DictRootModel
# 整體資料結構：{科別名稱: 科別資訊}
class SubjectTeacherMap(DictRootModel[str, SubjectInfo]):
    """科目與教師映射的資料結構。
    
    這是一個巢狀字典結構，用於儲存科目和其詳細資訊：
    - 第一層鍵為科目名稱
    - 值為 SubjectInfo 物件，包含：
        - url: 科別的維基頁面URL
        - teachers: 該科別下的所有教師及其頁面URL
        
    Example:
        {
            "健康與護理科": {
                "url": "/健康與護理科",
                "teachers": {
                    "梁香": "/梁香",
                    "洪美珠": "/洪美珠"
                }
            }
        }
    """
    pass

class IndexCrawler(BaseCrawlerABC[SubjectTeacherMap]):
    """台南一中教師維基索引爬蟲。
    
    此類別負責從台南一中維基系統獲取教師資訊，包括：
    - 抓取所有科目類別
    - 獲取每個科目下的教師列表
    - 建立科目與教師的對應關係
    
    Attributes:
        API (str): 台南一中維基的 API 端點
        semaphore (asyncio.Semaphore): 用於控制併發請求數量的信號量
    """
    
    API = "https://tnfshwiki.tfcis.org/api.php"

    def __init__(self, max_concurrency: int = 5):
        """初始化爬蟲實例。
        
        Args:
            max_concurrency (int): 最大同時請求數，預設為 5
        """
        self.semaphore = asyncio.Semaphore(max_concurrency)    
    def _get_headers(self) -> Dict[str, str]:
        """產生 HTTP 請求標頭。
        
        Returns:
            Dict[str, str]: 包含 User-Agent 和 Accept 的請求標頭字典
        """
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }

    async def _get_subcategories(self, session: ClientSession, cat: str) -> List[str]:
        """獲取指定類別下的所有子類別。
        
        Args:
            session (ClientSession): aiohttp 的會話實例
            cat (str): 要查詢的類別名稱
            
        Returns:
            List[str]: 子類別名稱列表
        """
        async with self.semaphore:
            async with session.get(self.API, headers=self._get_headers(), params={
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Category:{cat}",
                "cmtype": "subcat",
                "cmlimit": "max",
                "format": "json"
            }) as resp:
                data = await resp.json()
                return [i["title"].split(":", 1)[-1] for i in data.get("query", {}).get("categorymembers", [])]    
    async def _get_pages(self, session: ClientSession, cat: str) -> List[str]:
        """獲取指定類別下的所有頁面。
        
        Args:
            session (ClientSession): aiohttp 的會話實例
            cat (str): 要查詢的類別名稱
            
        Returns:
            List[str]: 頁面標題列表
        """
        async with self.semaphore:
            async with session.get(self.API, headers=self._get_headers(), params={
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Category:{cat}",
                "cmtype": "page",
                "cmlimit": "max",
                "format": "json"
            }) as resp:
                data = await resp.json()
                return [i["title"] for i in data.get("query", {}).get("categorymembers", [])]

    async def _process_subject(self, session: ClientSession, subject: str) -> Tuple[str, List[str]]:
        """處理單一科目，獲取該科目下的所有教師。
        
        Args:
            session (ClientSession): aiohttp 的會話實例
            subject (str): 科目名稱
            
        Returns:
            Tuple[str, List[str]]: (科目名稱, 該科目下的教師列表)
        """
        
        subcats = await self._get_subcategories(session, subject)
        if not subcats:
            pages = await self._get_pages(session, subject + "老師")
            return (subject, pages)
        else:
            tasks = [self._get_pages(session, subcat) for subcat in subcats]
            pages_lists = await asyncio.gather(*tasks)
            pages = [page for sublist in pages_lists for page in sublist]
            return (subject, pages)    
    
    async def fetch_raw(self, *args:Any, **kwargs:Any) -> List[Tuple[str, List[str]]]:
        """從維基系統獲取原始資料。
        
        Returns:
            List[Tuple[str, List[str]]]: 科目與其對應教師列表的元組列表
        """
        async with aiohttp.ClientSession() as session:
            subjects = await self._get_subcategories(session, "科目")
            all_tasks = [self._process_subject(session, subject) for subject in subjects]
            results = await asyncio.gather(*all_tasks)
            return results    
    
    def parse(self, raw: Any, *args:Any, **kwargs:Any) -> SubjectTeacherMap:
        """解析原始資料為結構化的科目教師映射。
        
        將爬取的原始資料轉換為正確的資料結構，包含：
        1. 科目URL
        2. 科目下的教師列表及其URL
        
        Args:
            raw: 從 fetch_raw 獲得的原始資料
            
        Returns:
            SubjectTeacherMap: 結構化的科目教師映射
        """
        result: SubjectTeacherMap = SubjectTeacherMap(root={})
        for subject, teacher_list in raw:
            # 初始化科目資訊
            subject_url = f"/{subject.replace(' ', '_')}"
            teachers_map = {
                teacher: f"/{teacher.replace(' ', '_')}"
                for teacher in teacher_list
            }
            if teacher_list:    
                # 建立科目資訊物件
                result[subject] = SubjectInfo(
                    url=subject_url,
                    teachers=teachers_map
                )
        return result

    @classmethod
    async def fetch(cls, max_concurrency:int = 5, *args:Any,  **kwargs:Any) -> SubjectTeacherMap:
        """類別方法：抓取並解析教師資料。
        
        Args:
            max_concurrency (int): 最大同時請求數
            
        Returns:
            SubjectTeacherMap: 結構化的科目教師映射
        """
        return await super().fetch(max_concurrency=max_concurrency)


if __name__ == "__main__":
    async def test():
        result = await IndexCrawler.fetch()
        return result
    import asyncio
    result = asyncio.run(test())
    import json
    print(json.dumps(result.model_dump(), indent=4, ensure_ascii=False))