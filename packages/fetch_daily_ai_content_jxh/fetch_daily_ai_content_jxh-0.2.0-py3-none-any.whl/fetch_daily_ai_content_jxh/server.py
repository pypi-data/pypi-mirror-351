# -*- coding: utf-8 -*-
"""
-------------------------------------------------
# @Project  :MCP
# @File     :server.py
# @Date     :2025/5/28 上午11:21
# @Author   :JXH
# @Email    :1762556953@qq.com
# @Software :PyCharm
-------------------------------------------------
"""
import requests
from pydantic import BaseModel, Field
import os
import logging
from mcp.server.fastmcp import FastMCP
import dashscope

logger = logging.getLogger('mcp')

settings = {
    'log_level': 'DEBUG'
}

# 初始化MCP服务
mcp = FastMCP('fetch_daily_ai_content_jxh', log_level='ERROR', settings=settings)

# 定义工具
@mcp.tool(name='新闻获取', description='从新闻API获取最新内容')  # 增加超时时间为60秒
async def fetch_daily_ai_content_jxh() -> str:
    """从新闻API获取最新内容并生成摘要"""

    # 基本参数配置
    # 基本参数配置
    apiUrl = 'http://v.juhe.cn/toutiao/index'  # 接口请求URL
    apiKey = 'a9fba89638f3c36b677eb6c6de3efb78'  # 在个人中心->我的数据,接口名称上方查看

    # 接口请求入参配置
    requestParams = {
        'key': apiKey,
        'type': 'keji',
        'page': '1',
        'page_size': '10',
        'is_filter': '',
    }

    # 发起接口网络请求
    response = requests.get(apiUrl, params=requestParams)

    # 解析响应结果
    if response.status_code == 200:
        responseResult = response.json()
        if responseResult['error_code'] == 0:
            news_list = responseResult['result']['data']
            all_news_text = ""

            for news in news_list:
                title = news['title']
                date = news['date']
                category = news['category']
                author_name = news['author_name']
                url = news['url']
                all_news_text += f"标题：{title}\n日期：{date}\n分类：{category}\n作者：{author_name}\n链接：{url}\n\n"

            return all_news_text
        else:
            return f"请求失败: {responseResult['reason']}"
    else:
        return '请求异常'

def run():
    mcp.run(transport='stdio')

if __name__ == '__main__':
    run()
