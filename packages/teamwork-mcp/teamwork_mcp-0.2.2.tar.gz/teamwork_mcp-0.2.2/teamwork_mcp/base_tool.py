import asyncio
import datetime
import pickle
import os
import time
import hashlib
import traceback
from functools import wraps
from typing import List, Dict, Any, Union, Optional, Type, Literal
from pydantic import BaseModel, Field
from loguru import logger
from threading import Lock
file_io_lock = Lock()

class BaseTool(BaseModel):
    """
    所有工具的基类
    """
    tool_name: str = Field("GoogleInternetSearch", description="通过关键词搜索网页")

    @staticmethod
    def __call__(tool_name_and_param: "BaseTool")->str:
        raise NotImplementedError

def make_tool_collection(*cls_list):
    return {cls: cls.__call__ for cls in cls_list}

# 装饰器函数
def cache_to_file(class_method=False, cache_file="cache/retrieve_cache.pkl", ttl=0):  # 默认无TTL
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成唯一的缓存键（基于函数名和参数）
            if class_method:
                assert len(args) > 0, "Class method must have at least one argument."
                _args = args[1:]
            else:
                _args = args
            cache_key = hashlib.md5((func.__name__ + str(_args) + str(kwargs)).encode()).hexdigest()

            # 如果缓存文件存在，读取缓存数据
            if os.path.exists(cache_file):
                with file_io_lock:
                    with open(cache_file, "rb") as f:
                        try:
                            cache_data = pickle.load(f)
                        except Exception as e:
                            cache_data = {}
            else:
                cache_data = {}

            # 检查缓存是否存在且未过期
            if cache_key in cache_data:
                cached_entry = cache_data[cache_key]
                if (time.time() - cached_entry["timestamp"] < ttl) or (ttl == 0):
                    return cached_entry["result"]

            # 调用原始函数并缓存结果
            stack = ''.join([item for item in traceback.format_stack() if 'ReinforcedFastFewshotTuner' in item and 'llamakit' not in item][-3:])
            logger.success(f"[LLM CALL] {cache_key}  "+ str(func) + str(_args)[:30] + str(kwargs)[:30])
            tic = time.time()
            result = func(*args, **kwargs)
            toc = time.time()
            dt = toc - tic

            with file_io_lock:
                import json
                try:
                    with open('debug_time_call', 'r', encoding='utf8') as f:
                        all_debug_stack = json.load(f)
                except:
                    all_debug_stack = {}
                all_debug_stack.update({
                    stack: dt + all_debug_stack.get(stack, 0)
                })
                with open('debug_time_call', 'w+', encoding='utf8') as f:
                    json.dump(all_debug_stack, f)

                buf_lines = ""
                for k, v in all_debug_stack.items():
                    buf_lines += f"------------------------\n{k}\n{v}\n\n\n\n\n"
                with open('debug_time_call.md', 'w+', encoding='utf8') as f:
                    f.writelines(buf_lines)

            logger.success(f"[LLM CALL] {cache_key}  "+ str(func) + 'done')
            cache_data_ = {}
            cache_data_[cache_key] = {
                "timestamp": time.time(),
                "result": result
            }
            with file_io_lock:
                if not os.path.exists(cache_file):
                    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
                if os.path.exists(cache_file):
                    with open(cache_file, "rb") as f:
                        try:
                            cache_data = pickle.load(f)
                        except Exception as e:
                            cache_data = {}
                cache_data.update(cache_data_)
                # 将缓存写回文件
                with open(cache_file, "wb") as f:
                    pickle.dump(cache_data, f)
            return result
        return wrapper
    return decorator


