#!/usr/bin/env python3
"""
CSarXiv MCP服务器使用示例 - 社科基金申报代码
"""

import asyncio
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.csarxivcontextserver.server import CSarXivClient

async def example_funding_codes():
    """示例：获取基金代码"""
    print("💰 社科基金申报代码示例")
    print("-" * 40)
    
    async with CSarXivClient() as client:
        codes = await client.get_funding_codes()
        
        if codes:
            print(f"成功获取到 {len(codes)} 个申报代码：\n")
            
            # 按主分类分组显示
            categories = {}
            for code in codes:
                # 提取主分类（如DJ、A、B等）
                import re
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
            
            for category, category_codes in sorted(categories.items()):
                print(f"【{category}类】- 共{len(category_codes)}个代码:")
                for code in category_codes:
                    print(f"  {code['code']}: {code['description']}")
                print()
        else:
            print("未找到基金代码（可能需要网络连接或网站结构调整）")

async def example_specific_category():
    """示例：获取特定分类的代码"""
    print("\n🔍 特定分类代码示例")
    print("-" * 40)
    
    async with CSarXivClient() as client:
        codes = await client.get_funding_codes()
        
        if codes:
            # 查找DJ类代码
            dj_codes = [code for code in codes if code['code'].startswith('DJ')]
            if dj_codes:
                print("DJ - 中共党史党建学相关代码：")
                for code in dj_codes:
                    print(f"  {code['code']}: {code['description']}")
            else:
                print("未找到DJ类代码")
            
            print()
            
            # 查找FX类代码
            fx_codes = [code for code in codes if code['code'].startswith('FX')]
            if fx_codes:
                print("FX - 法学相关代码：")
                for code in fx_codes[:5]:  # 只显示前5个
                    print(f"  {code['code']}: {code['description']}")
                if len(fx_codes) > 5:
                    print(f"  ... 还有{len(fx_codes) - 5}个代码")
            else:
                print("未找到FX类代码")
        else:
            print("未找到基金代码")

async def main():
    """主函数"""
    print("🚀 CSarXiv MCP服务器使用示例")
    print("专注于社科基金申报代码获取")
    print("=" * 60)
    
    # 获取基金代码示例
    await example_funding_codes()
    
    # 获取特定分类代码示例
    await example_specific_category()
    
    print("=" * 60)
    print("✅ 示例完成！")
    print("\n💡 在MCP客户端中，您可以使用以下功能:")
    print("  - get-funding-codes: 获取社科基金申报代码")
    print("  - analyze-funding-codes: 分析申报代码（提示模板）")
    print("\n📝 注意：")
    print("  - 数据来源：CSarXiv.org静态主页")
    print("  - 需要网络连接访问网站")
    print("  - 支持DJ、FX、GL等学科代码格式")
    print("  - 解析逻辑基于实际HTML结构，准确可靠")

if __name__ == "__main__":
    asyncio.run(main()) 