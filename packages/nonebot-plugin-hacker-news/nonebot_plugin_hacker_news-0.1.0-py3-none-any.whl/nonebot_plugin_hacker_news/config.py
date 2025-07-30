from pydantic import Extra, BaseModel
from typing import Optional, List, Union


class Config(BaseModel, extra=Extra.ignore):
    hn_api_base_url: str = "https://hacker-news.firebaseio.com/v0"
    hn_api_timeout: int = 10  # 请求超时时间，单位秒
    
    hn_auto_broadcast: bool = False  # 是否开启定时播报功能
    hn_broadcast_interval: int = 3600  # 定时播报间隔，单位秒
    hn_broadcast_mode: str = "interval"  # 播报模式，"interval"为间隔模式，"cron"为定时模式
    hn_broadcast_cron: str = "0 8 * * *"  # cron表达式，默认每天早上8点
    hn_max_comments_depth: int = 3  # 获取评论的最大深度
    hn_max_items_per_request: int = 10  # 单次请求最大获取条数
    hn_broadcast_groups: List[int] = []  # 定时播报的群组列表
    hn_broadcast_articles_count: int = 5  # 每次播报的文章数量
    hn_broadcast_header_format: str = "[BROADCAST] {time} Hacker News Update"  # 播报消息头部格式，{time}会被替换为当前时间
