from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from tnfsh_wiki_teachers_core.index.index import Index
    from tnfsh_wiki_teachers_core.index.crawler import SubjectTeacherMap
    from tnfsh_wiki_teachers_core.index.cache import ReverseIndexMap
class TNFSHWikiTeachersCore:
    async def fetch_index(self, refresh: bool= False, max_concurrency: int=5) -> Index:
        from tnfsh_wiki_teachers_core.index.index import Index
        return await Index.fetch(refresh=refresh, max_concurrency=max_concurrency)
    
    async def fetch_forward_index(self, refresh: bool= False, max_concurrency: int=5) -> SubjectTeacherMap:
        index = await self.fetch_index(refresh=refresh, max_concurrency=max_concurrency)
        if index.index:
            return index.index
        else:
            raise ValueError(f"index is None")
    
    async def fetch_reverse_index(self, refresh: bool= False, max_concurrency: int=5) -> ReverseIndexMap:
        index = await self.fetch_index(refresh=refresh, max_concurrency=max_concurrency)
        if index.reverse_index:
            return index.reverse_index
        else:
            raise ValueError(f"index is None")
        

if __name__ == "__main__":
    async def test():
            
        wiki_core = TNFSHWikiTeachersCore()
        result = await wiki_core.fetch_reverse_index()
        print(type(result))
        print(result)
    import asyncio
    asyncio.run(test())