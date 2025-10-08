"""
MCP - Pydantic Models
定义所有情境数据的输入输出模型
"""
from typing import Optional, List
from pydantic import BaseModel

class WeatherData(BaseModel):
    """标准化的天气数据"""
    temperature: float # e.g., 23.5
    condition: str # e.g., "晴", "小雨"
    city: str

class NewsData(BaseModel):
    headlines: List[str]

class ContextualData(BaseModel):
    """标准化的情境数据输出模型"""
    time_of_day: str # e.g., "清晨", "午后", "深夜"
    weather: Optional[WeatherData]
    news: Optional[NewsData]
    # 未来可扩展，如 user_activity: Optional[MusicData]
