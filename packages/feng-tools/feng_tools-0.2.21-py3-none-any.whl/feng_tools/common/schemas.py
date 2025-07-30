import math
from typing import Optional, TypeVar, Generic, Any

from pydantic import BaseModel, Field, computed_field

_T = TypeVar("_T")

class ApiResponse(BaseModel, Generic[_T]):
    """api接口响应"""
    success:Optional[bool] = Field(default=True, description="是否成功")
    message: Optional[str] = Field(default='success', description="提示信息")
    # 0或者200都是正常
    error_code: Optional[int] = Field(default=0, description="错误编码")
    data:Optional[_T] = Field(default=None, description="返回数据")


class HandleResult(BaseModel, Generic[_T]):
    """处理结果"""
    success:Optional[bool] = Field(default=True, description="是否成功")
    # 0或者200都是正常
    error_code:Optional[int] = Field(default=0, description="错误编码")
    message:Optional[str] = Field(default='success', description="提示信息")
    data:Optional[_T] = Field(default=None, description="返回数据")


class PageData(BaseModel, Generic[_T]):
    """分页数据"""
    page_num:Optional[int] = None
    page_size:Optional[int] = None
    total:Optional[int] = None
    items:Optional[list[_T]] = None
    def __init__(self, page_num: int, page_size: int, total: int, items: list[_T], /, **data: Any):
        super().__init__(**data)
        self.page_num = page_num
        self.page_size = page_size
        self.total = total
        self.items = items
    @computed_field
    @property
    def has_next(self) -> Optional[bool]:
        return self.page_num<math.ceil(self.total/self.page_size)

    @computed_field
    @property
    def total_page(self) -> Optional[int]:
        return math.ceil(self.total/self.page_size)
