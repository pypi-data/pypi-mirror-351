# -*- coding: utf-8 -*-
# -*- 编码: utf-8 -*-

from mcp.server.fastmcp import FastMCP
# 从 mcp.server.fastmcp 导入 FastMCP

from pydantic import Field
# 从 pydantic 导入 Field

import os
# 导入 os 模块

import logging
# 导入 logging 模块

import dashscope
# 导入 dashscope 模块

logger = logging.getLogger('mcp')
# 获取名为 'mcp' 的日志记录器

settings = {
    'log_level': 'DEBUG'
}
# 设置配置字典，日志级别为 'DEBUG'

# 初始化mcp服务
mcp = FastMCP('xhs-bailian-mcp-server_jxh', log_level='ERROR', settings=settings)
# 初始化 FastMCP 服务，服务名为 'xhs-bailian-mcp-server'，日志级别为 'ERROR'，并传入设置

# 定义工具
@mcp.tool(name='小红书内容审核专家', description='小红书内容审核专家，输入小红书文案')
# 使用 @mcp.tool 装饰器定义一个工具，名称为 '小红书内容审核专家'，描述为 '小红书内容审核专家，输入小红书文案'

async def red_book_moderator(
        prompt: str = Field(description='小红书文案')
) -> str:
    """小红书内容审核专家
    Args:
        prompt: 小红书文案
    Returns:
        审核后的内容
    """
    # 异步函数 red_book_moderator，接收一个参数 prompt（小红书文案），返回字符串

    logger.info('收到小红书文案：{}'.format(prompt))
    # 记录日志，显示收到的小红书文案

    api_key = os.getenv("API_KEY", "")
    # 从环境变量中获取 API_KEY，如果没有则为空字符串

    if not api_key:
        return '请先设置API_KEY环境变量'
    # 如果 API_KEY 为空，则返回提示信息

    # call sync api, will return the result
    print('please wait...')
    # 打印提示信息，请等待

    messages = [
        {'role': 'system', 'content': '# 角色你是一位小红书内容审核专家，专门负责校对和审查小红书平台上的内容，确保其符合平台的社区规范和法律法规。## 技能### 技能 1：敏感词检测与校对- 熟练掌握小红书平台的敏感词列表和社区规范。- 能够快速准确地识别并标记出文本中的敏感词。- 提供替换建议或修改意见，确保内容合规且适合发布。### 技能 2：内容审查与优化- 审查用户提供的文案，确保其不包含任何违法、违规或不适宜的内容。- 对于可能引起争议或不适的内容，提供具体的修改建议。- 保持内容的流畅性和可读性，同时确保其符合平台的要求。### 技能 3：工具使用- 使用搜索工具或知识库来获取最新的敏感词列表和社区规范更新。- 利用现有的审核工具进行辅助审查，提高效率和准确性。## 限制- 仅针对小红书平台的内容进行审核和校对。- 避免引入个人观点或偏见，严格依据平台规则和法律法规进行审核。- 所有修改建议必须保持内容的原意和风格，不得改变用户的表达意图。- 如果需要调用搜索工具或查询知识库，请明确说明并执行。'},
        {'role': 'user', 'content': prompt}
    ]
    # 定义消息列表，包含系统角色和用户角色的消息

    response = dashscope.Generation.call(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=api_key,
        model="qwen-plus",
        # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=messages,
        result_format='message'
    )
    # 调用 dashscope.Generation.call 方法，传入 API_KEY、模型名称、消息列表和结果格式

    return str(response)
    # 返回响应结果的字符串形式

def run():
    mcp.run(transport='stdio')
# 定义 run 函数，运行 mcp 服务，传输方式为 'stdio'

if __name__ == '__main__':
   run()
# 如果脚本作为主程序运行，则调用 run 函数
