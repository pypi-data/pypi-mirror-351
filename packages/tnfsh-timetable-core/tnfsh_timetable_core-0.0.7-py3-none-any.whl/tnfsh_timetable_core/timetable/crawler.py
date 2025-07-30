from typing import List, Set, Dict, Optional, Literal, Tuple, TypedDict, TypeAlias
import logging
import aiohttp
from aiohttp import client_exceptions
import asyncio
from bs4 import BeautifulSoup
import json

from tnfsh_timetable_core.index.index import Index
from tnfsh_timetable_core.utils.logger import get_logger

class FetchError(Exception):
    """爬取課表時可能發生的錯誤"""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

# 設定日誌
logger = get_logger(logger_level="INFO")

# 別名列表
aliases: List[Set[str]] = [
    {"朱蒙", "吳銘"}
]


TimeInfo: TypeAlias = Tuple[str, str]
PeriodName: TypeAlias = str
Subject: TypeAlias = str
CounterPart: TypeAlias = str
Url: TypeAlias = str
Course: TypeAlias = Dict[Subject, Dict[CounterPart, Url]]

class RawParsedResult(TypedDict):
    last_update: str
    periods: Dict[PeriodName, TimeInfo]
    table: List[List[Course]]


from tnfsh_timetable_core.index.models import ReverseIndexResult

def resolve_target(
    target: str,
    reverse_index: ReverseIndexResult,
    aliases: List[Set[str]]
) -> Optional[str]:
    """
    根據目標名稱解析別名，回傳可用於 reverse_index 的合法 key。
    """
    
    if target in reverse_index:
        logger.debug(f"🎯 找到 {target} 的課表網址")
        return target

    for alias_set in aliases:
        if target in alias_set:
            candidates = alias_set - {target}
            for alias in candidates:
                if alias in reverse_index:
                    logger.info(f"🔄 將 {target} 解析為別名 {alias}")
                    return alias

    return None

async def fetch_raw_html(target: str, refresh: bool = False, max_retries: int = 3, retry_delay: float = 1.0) -> BeautifulSoup:
    """
    非同步抓取原始課表 HTML

    Args:
        target (str): 目標名稱（班級或教師）
        refresh (bool, optional): 是否刷新索引快取. 預設為 False
        max_retries (int, optional): 最大重試次數. 預設為 3
        retry_delay (float, optional): 重試間隔秒數. 預設為 1.0

    Returns:
        BeautifulSoup: 解析後的 HTML 内容

    Raises:
        FetchError: 當發生網路請求錯誤或無法解析目標時拋出
    """
    from tnfsh_timetable_core.index.index import Index
    from tnfsh_timetable_core.index.models import ReverseIndexResult
    index: Index = Index()
    await index.fetch(refresh=refresh)
    if index.reverse_index is None:
        logger.error("❌ 無法獲取索引資料")
        raise FetchError("無法獲取索引資料")
    reverse_index: ReverseIndexResult = index.reverse_index
    base_url: str = index.base_url

    global aliases
    logger.debug(f"🔍 解析目標：{target}")
    real_target = resolve_target(target, reverse_index, aliases)
    if real_target is None:
        logger.error(f"❌ 找不到 {target} 的課表網址")
        raise FetchError(f"找不到 {target} 的課表網址")

    if target == "307":
        relative_url = "C101307.html"
    else:
        relative_url = reverse_index[real_target]["url"]

    full_url = base_url + relative_url
    logger.debug(f"🌐 準備請求網址：{full_url}")

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                logger.debug(f"📡 發送請求：{target} (嘗試 {attempt + 1}/{max_retries})")
                async with session.get(full_url, headers=headers) as response:
                    response.raise_for_status()
                    content = await response.read()
                    logger.debug(f"📥 收到回應：{target}")
                    soup = BeautifulSoup(content, 'html.parser')
                    logger.debug(f"✅ HTML 解析完成：{target}")
                    return soup

        except client_exceptions.ClientResponseError as e:
            error_msg = f"HTTP 狀態碼錯誤 {e.status}: {e.message}"
            logger.warning(f"⚠️ {error_msg}")
            if attempt + 1 < max_retries:
                logger.info(f"🔄 等待 {retry_delay} 秒後重試...")
                await asyncio.sleep(retry_delay)
            else:
                raise FetchError(error_msg)

        except client_exceptions.ClientConnectorError as e:
            error_msg = f"連線錯誤：{str(e)}"
            logger.warning(f"⚠️ {error_msg}")
            if attempt + 1 < max_retries:
                logger.info(f"🔄 等待 {retry_delay} 秒後重試...")
                await asyncio.sleep(retry_delay)
            else:
                raise FetchError(error_msg)

        except (client_exceptions.ServerTimeoutError, asyncio.TimeoutError):
            error_msg = "請求超時"
            logger.warning(f"⚠️ {error_msg}")
            if attempt + 1 < max_retries:
                logger.info(f"🔄 等待 {retry_delay} 秒後重試...")
                await asyncio.sleep(retry_delay)
            else:
                raise FetchError(error_msg)

        except client_exceptions.ClientError as e:
            error_msg = f"網路請求錯誤：{str(e)}"
            logger.warning(f"⚠️ {error_msg}")
            if attempt + 1 < max_retries:
                logger.info(f"🔄 等待 {retry_delay} 秒後重試...")
                await asyncio.sleep(retry_delay)
            else:
                raise FetchError(error_msg)

        except Exception as e:
            error_msg = f"未預期的錯誤：{str(e)}"
            logger.error(f"❌ {error_msg}")
            raise FetchError(error_msg)

def parse_html(soup: BeautifulSoup) -> RawParsedResult:
    """
    解析原始 HTML，擷取 last_update、periods、table
    """
    logger.debug("🔄 開始解析 HTML")
    
    # 擷取更新日期
    update_element = soup.find('p', class_='MsoNormal', align='center')
    if update_element:
        spans = update_element.find_all('span')
        last_update = spans[1].text if len(spans) > 1 else "No update date found."
        logger.debug(f"📅 更新日期：{last_update}")
    else:
        last_update = "No update date found."
        logger.warning("⚠️ 找不到更新日期")

    # 擷取課表 table 並移除 border
    logger.debug("🔍 搜尋主要課表")
    main_table = None
    for table in soup.find_all("table"):
        new_table = BeautifulSoup('<table></table>', 'html.parser').table
        for row in table.find_all("tr"):
            for td in row.find_all('td'):
                if td.get('style') and 'border' in td['style']:
                    td.decompose()
            if len(row.find_all('td')) == 7:
                new_table.append(row)
                
        if len(new_table.find_all('tr')) > 0:
            main_table = new_table
            break

    if main_table is None:
        logger.error("❌ 找不到符合格式的課表")
        raise FetchError("找不到符合格式的課表 table")

    logger.debug("📊 解析課表時間")
    # 擷取 periods
    import re
    re_pattern = r'(\d{2})(\d{2})'
    re_sub = r'\1:\2'
    periods: Dict[str, Tuple[str, str]] = {}
    for row in main_table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        lesson_name = cells[0].text.replace("\n", "").replace("\r", "")
        time_text = cells[1].text.replace("\n", "").replace("\r", "")
        times = [re.sub(re_pattern, re_sub, t.replace(" ", "")) for t in time_text.split("｜")]
        if len(times) == 2:
            periods[lesson_name] = (times[0], times[1])

    # 擷取課程名稱和教師名稱
    # 這裡的 class_td 是一個 td 標籤，包含了課程名稱和教師名稱
    def class_name_split(class_td) -> Dict[str, Dict[str, str]]:
        """分析課程字串為課程名稱和教師名稱，統一回傳字典格式"""
        def clean_text(text: str) -> str:
            """清理文字內容，移除多餘空格與換行"""
            return text.strip("\n").strip("\r").strip(" ").replace(" ", ", ")

        def is_teacher_p(p_tag) -> bool:
            """檢查是否為包含教師資訊的p標籤"""
            return bool(p_tag.find_all('a'))
        
        def parse_teachers(teacher_ps) -> Dict[str, str]:
            """解析所有教師p標籤的資訊"""
            teachers_dict = {}
            for p in teacher_ps:
                for link in p.find_all('a'):
                    name = clean_text(link.text)
                    href = link.get('href', '')
                    teachers_dict[name] = href
            return teachers_dict
        
        def combine_class_name(class_ps) -> str:
            """組合課程名稱"""
            texts = [clean_text(p.text) for p in class_ps]
            combine = ''.join(filter(None, texts)).replace("\n", ", ").replace("\u00a0", "")
            return combine
        
        ps = class_td.find_all('p')
        if not ps:
            return {"": {"": ""}}
        
        teacher_ps = []
        class_ps = []
        for p in ps:
            if is_teacher_p(p):
                teacher_ps.append(p)
            else:
                class_ps.append(p)
        
        teachers_dict = parse_teachers(teacher_ps) if teacher_ps else {"": ""}
        
        if class_ps:
            class_name = combine_class_name(class_ps)
        elif teacher_ps == {'':''}:
            class_name = "找不到課程"
        else:
            class_name = ""
        
        if (class_name and class_name != " ") or teachers_dict != {"": ""}:
            return {class_name: teachers_dict}
        return {"": {"": ""}}

    # 擷取 table raw 格式
    table: List[List[Dict[str, Dict[str, str]]]] = []
    for row in main_table.find_all("tr"):
        cells = row.find_all("td")[2:]  # 跳過前兩列（節次和時間）
        row_data = []
        for cell in cells:
            row_data.append(class_name_split(cell))
        if row_data:
            table.append(row_data)

    logger.info("✅ HTML 解析完成")
    result = RawParsedResult(
        last_update=last_update,
        periods=periods,
        table=table
    )
    return result


if __name__ == "__main__":
    # For test cases, see: tests/test_timetable/test_crawler.py
    pass