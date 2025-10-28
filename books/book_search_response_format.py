from pydantic import BaseModel
from typing import List

class BookInfo(BaseModel):
    title: str
    author: str
    description: str
    
    
class BookSearchResponseFormat(BaseModel):
    books: List[BookInfo]