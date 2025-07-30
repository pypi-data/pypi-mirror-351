import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
import types
import tiktoken
import uuid
import time
from functools import lru_cache
from pydantic import BaseModel, Field
from loguru import logger
from best_logger import print_dict

class McpMixin():

    def get_mcp_client(self):
        from teamwork_mcp import SyncedMcpClient
        client = SyncedMcpClient(server_url="http://xxxxxxxxxxxxxxxxx:33333/sse")
        return client

    @lru_cache
    def tool_workshop_list_tools(self, client):
        from teamwork_mcp.manifest_tool import all_tool_manifest_prompt
        client = self.get_mcp_client()
        result = client.list_tools()
        tool_description = all_tool_manifest_prompt(result, print_formatted=False)
        return result, tool_description

    def tool_workshop_call_tools(self, tool_call_struct):
        client = self.get_mcp_client()
        try:
            result = client.call_tool(tool_call_struct['name'], tool_call_struct['arguments'])
            return result.content[0].text
        except:
            logger.exception("Tool call failed")
            return "The tool call failed. Please check the tool name and arguments."


    def compress_text_with_focus(self, text, overflow_handler_prompt, desired_length=None):
        from beyond.light_llm import LLMHandle
        mini_llm = LLMHandle().get_llm("qwen-plus")
        overflow_handler_prompt = overflow_handler_prompt.replace("\n", " ")
        text = text.strip()
        # if desired_length is None:
        ydata_extend_compress = [
            {
                "role": "user",
                "content": 
                    f"去除正文<text>中的乱码、超链接和其他无关信息（如广告等），忠实保留所有信息，尽可能地避免修改原文正文。"
                    f"逐字逐句地处理，不翻译原始语言，不满足Markdown格式的地方转化为Markdown格式，禁止总结和压缩。如果正文中有超链接，保留超链接的文字部分，去除超链接的URL部分。"
                    f"“重点关注”:\n{overflow_handler_prompt}\n\n"
                    f"输出格式：\n\n<text>...去除乱码和无关信息增加可读性...</text>\n\n\n\n"
                    f"正文：\n\n"
                    f"\n\n<text>\n{text}\n</text>"
            },
        ]

        logger.warning('compressing tool call result, this may take a while')
        think, result, tool = mini_llm.chat(messages = ydata_extend_compress, display=False)
        true_result = result.replace("<text>", "").replace("</text>", "")
        print_dict({
            text: true_result
        }, mod="web-extract")
        return true_result

    def compress_tool_call(self, tool_call_result: str, overflow_handler_prompt: str = "", desired_length: int = 5000, max_compress_capacity = 20*1000):
        encoder = tiktoken.encoding_for_model('gpt-4')
        tool_call_result = tool_call_result.strip()

        token_length = len(encoder.encode(tool_call_result))
        if token_length < desired_length:
            # 工具调用的Token没有超出上限
            return tool_call_result

        # 处理super long
        from beyond.long_text_breaker import breakdown_text_to_satisfy_token_limit
        tool_call_result_array = breakdown_text_to_satisfy_token_limit(tool_call_result, limit=min(4096, token_length//2))
        for i in range(len(tool_call_result_array)):
            pre = ""
            if i != 0: tool_call_result_array[i] = f"{pre} \n......\n {tool_call_result_array[i]}"
        with ThreadPoolExecutor(max_workers=16) as executor:
            tool_call_result_array_first_compress = list(executor.map(lambda text: self.compress_text_with_focus(text, overflow_handler_prompt=overflow_handler_prompt), tool_call_result_array))

        # # 合并后，压缩
        true_result = '\n'.join(tool_call_result_array_first_compress)

        token_length = len(encoder.encode(true_result))
        text_len = len(true_result)
        if token_length > max_compress_capacity:
            overflow_ratio = max_compress_capacity / token_length
            true_result = true_result[:int(text_len*overflow_ratio)]

        return true_result

    async def tool_call(self, mcp_client, completion_text, compress_tool_call=True):
        import json
        import re

        # 使用正则表达式提取所有的<tool_call>标签内容
        tool_call_pattern = r'<tool_call>([\s\S]*?)</tool_call>'
        matches = re.findall(tool_call_pattern, completion_text)
        if len(matches) == 0:
            return None
        if len(matches) == 1:
            tool_call_struct = json.loads(matches[0].strip())
            return_buffer = await asyncio.to_thread(self.tool_workshop_call_tools, tool_call_struct)
            return_buffer = await self.compress_tool_call(return_buffer) if compress_tool_call else return_buffer
            return return_buffer
        else:
            return_buffer = ""
            for match in matches:
                tool_call_struct = json.loads(match.strip())
                this_tool_result = await asyncio.to_thread(self.tool_workshop_call_tools, tool_call_struct)
                return_buffer += f"Result from {tool_call_struct['name']}:\n{this_tool_result}\n"
            return_buffer = await self.compress_tool_call(return_buffer) if compress_tool_call else return_buffer
            return return_buffer

    def tool_call_with_cache(self, json_struct, compress_tool_call, overflow_handler_prompt):
        return_buffer = self.tool_workshop_call_tools(json_struct)
        return_buffer_c = self.compress_tool_call(return_buffer, overflow_handler_prompt) if compress_tool_call else return_buffer
        return return_buffer_c

    def tool_call_from_json(self, mcp_client, json_struct, compress_tool_call=True, overflow_handler_prompt=""):
        return_buffer = self.tool_call_with_cache(json_struct, compress_tool_call, overflow_handler_prompt)
        print_dict({
            "tool": str(json_struct),
            "result": str(return_buffer)
        }, mod="llm")
        return f"# The selected tools\n\n{str(json_struct)}\n\n# The toolcall result\n\n{return_buffer}"
