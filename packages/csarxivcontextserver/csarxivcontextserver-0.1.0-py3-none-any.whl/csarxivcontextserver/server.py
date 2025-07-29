import asyncio
import json
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, quote

import aiohttp
from bs4 import BeautifulSoup
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

# CSarXiv服务器实例
server = Server("CSarXivContextServer")

# 基础URL
BASE_URL = "https://www.csarxiv.org"

class CSarXivClient:
    """CSarXiv.org网站客户端 - 专门用于获取社科基金申报代码"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = BASE_URL
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_funding_codes(self) -> List[Dict[str, Any]]:
        """从主页获取社科基金项目申报代码"""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        try:
            # 从主页获取代码信息
            async with self.session.get(self.base_url) as response:
                if response.status == 200:
                    html = await response.text()
                    codes = self._parse_funding_codes_from_html(html)
                    if codes:
                        return codes
                else:
                    print(f"无法访问网站，状态码: {response.status}")
                    return []
        except Exception as e:
            print(f"获取基金代码时出错: {e}")
            return []
    
    def _parse_funding_codes_from_html(self, html: str) -> List[Dict[str, Any]]:
        """从HTML中解析社科基金项目申报代码"""
        soup = BeautifulSoup(html, 'html.parser')
        codes = []
        
        # 查找所有学科组
        discipline_groups = soup.find_all('div', class_='discipline-group')
        
        for group in discipline_groups:
            # 获取主分类信息
            header = group.find('div', class_='discipline-header')
            if header:
                h4 = header.find('h4')
                if h4:
                    header_text = h4.get_text(strip=True)
                    # 解析主分类，格式如 "DJ - 中共党史党建学"
                    main_match = re.match(r'^([A-Z]{1,3})\s*[-–—]\s*(.+)$', header_text)
                    if main_match:
                        main_code = main_match.group(1)
                        main_name = main_match.group(2)
                        codes.append({
                            'code': main_code,
                            'description': main_name,
                            'type': '社科基金项目申报代码'
                        })
            
            # 获取子分类信息
            content = group.find('div', class_='discipline-content')
            if content:
                subdisciplines = content.find_all('div', class_='subdiscipline')
                for subdiscipline in subdisciplines:
                    code_elem = subdiscipline.find('div', class_='subdiscipline-code')
                    name_elem = subdiscipline.find('div', class_='subdiscipline-name')
                    
                    if code_elem and name_elem:
                        sub_code = code_elem.get_text(strip=True)
                        sub_name = name_elem.get_text(strip=True)
                        
                        if sub_code and sub_name:
                            codes.append({
                                'code': sub_code,
                                'description': sub_name,
                                'type': '社科基金项目申报代码'
                            })
        
        # 按代码排序
        codes.sort(key=lambda x: x['code'])
        
        return codes

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """列出可用的资源"""
    return [
        types.Resource(
            uri=AnyUrl("csarxiv://funding-codes"),
            name="社科基金申报代码",
            description="获取当年社科基金项目申报代码字母",
            mimeType="application/json",
        ),
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """读取特定资源的内容"""
    if uri.scheme != "csarxiv":
        raise ValueError(f"不支持的URI方案: {uri.scheme}")
    
    if uri.path == "/funding-codes":
        async with CSarXivClient() as client:
            codes = await client.get_funding_codes()
            return json.dumps(codes, ensure_ascii=False, indent=2)
    else:
        raise ValueError(f"未知的资源路径: {uri.path}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """列出可用的提示模板"""
    return [
        types.Prompt(
            name="analyze-funding-codes",
            description="分析社科基金申报代码并提供建议",
            arguments=[
                types.PromptArgument(
                    name="research_area",
                    description="研究领域",
                    required=False,
                ),
            ],
        ),
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """生成提示内容"""
    if name == "analyze-funding-codes":
        research_area = (arguments or {}).get("research_area", "")
        
        async with CSarXivClient() as client:
            codes = await client.get_funding_codes()
        
        codes_text = "\n".join([
            f"{code['code']}: {code['description']}"
            for code in codes
        ])
        
        prompt_text = f"以下是社科基金项目申报代码：\n\n{codes_text}\n\n"
        if research_area:
            prompt_text += f"请为研究领域'{research_area}'推荐最适合的申报代码，并说明理由。"
        else:
            prompt_text += "请分析这些申报代码的分类逻辑和特点。"
        
        return types.GetPromptResult(
            description="分析社科基金申报代码",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=prompt_text,
                    ),
                )
            ],
        )
    else:
        raise ValueError(f"未知的提示: {name}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """列出可用的工具"""
    return [
        types.Tool(
            name="get-funding-codes",
            description="获取社科基金项目申报代码",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "特定学科分类（可选，如DJ、FX、GL等）"
                    }
                },
                "required": [],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """处理工具调用请求"""
    if not arguments:
        arguments = {}
    
    if name == "get-funding-codes":
        category = arguments.get("category", "")
        
        async with CSarXivClient() as client:
            codes = await client.get_funding_codes()
        
        if category:
            # 按分类过滤
            filtered_codes = []
            for code in codes:
                if (category.upper() in code['code'] or 
                    category.lower() in code.get('description', '').lower()):
                    filtered_codes.append(code)
            codes = filtered_codes
        
        if codes:
            result_text = f"社科基金项目申报代码（共{len(codes)}个）：\n\n"
            
            # 按主分类分组显示
            categories = {}
            for code in codes:
                # 提取主分类（如DJ、A、B等）
                main_cat = re.match(r'^([A-Z]+)', code['code'])
                if main_cat:
                    cat_key = main_cat.group(1)
                    if cat_key not in categories:
                        categories[cat_key] = []
                    categories[cat_key].append(code)
                else:
                    if 'Other' not in categories:
                        categories['Other'] = []
                    categories['Other'].append(code)
            
            for cat, cat_codes in sorted(categories.items()):
                result_text += f"【{cat}类】\n"
                for code in cat_codes:
                    result_text += f"  {code['code']}: {code['description']}\n"
                result_text += "\n"
        else:
            result_text = "未找到相关代码信息"
        
        return [types.TextContent(type="text", text=result_text)]
    else:
        raise ValueError(f"未知的工具: {name}")

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="CSarXivContextServer",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )