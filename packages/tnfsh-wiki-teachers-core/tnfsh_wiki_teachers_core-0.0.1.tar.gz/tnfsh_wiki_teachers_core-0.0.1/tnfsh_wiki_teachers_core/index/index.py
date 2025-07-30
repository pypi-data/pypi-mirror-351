from __future__ import annotations
from typing import Self, Any
from tnfsh_wiki_teachers_core.abc.domain_abc import BaseDomainABC
from pydantic import BaseModel
from tnfsh_wiki_teachers_core.index.crawler import SubjectTeacherMap
from tnfsh_wiki_teachers_core.index.cache import ReverseIndexMap


class Index(BaseDomainABC, BaseModel):
    
    index: SubjectTeacherMap| None = None
    reverse_index: ReverseIndexMap| None = None

    @classmethod
    async def fetch(cls, refresh:bool = False, max_concurrency:int = 5, *args: Any, **kwargs:Any) -> Self:
        from tnfsh_wiki_teachers_core.index.cache import IndexCache, ReverseIndexCache
        index = await IndexCache.fetch(refresh=refresh, max_concurrency=max_concurrency)
        reverse_index = await ReverseIndexCache.fetch(refresh=refresh, max_concurrency=max_concurrency)
        instance = cls(index=index, reverse_index=reverse_index)
        
        return instance
    

if __name__ == "__main__":
    import asyncio
    async def test():
        wiki_index = await Index.fetch()
        index = wiki_index.index
        reverse_index = wiki_index.reverse_index
        import json
        if index:
            print(json.dumps(index.model_dump(), indent=4, ensure_ascii=False))
        print("========")
        if reverse_index:
            print(json.dumps(reverse_index.model_dump(), indent=4, ensure_ascii=False))
    asyncio.run(test())