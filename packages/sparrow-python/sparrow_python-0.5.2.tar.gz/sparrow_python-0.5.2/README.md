# sparrow-python

[![image](https://img.shields.io/badge/Pypi-0.1.7-green.svg)](https://pypi.org/project/sparrow-python)
[![image](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)
[![image](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## TODO
- [ ] 找一个可以优雅绘制流程图、示意图的工具，如ppt？
- [ ]  实现一个优雅的TextSplitter

- [ ] prompt调试页面
- [ ] 相关配置指定支持：prompt后端地址；模型参数配置；
- [ ] 
- [ ] 添加测试按钮，模型选项，模型配置
- [ ] 原生git下载支持
- [ ]
- [X] streamlit 多模态chat input: https://github.com/streamlit/streamlit/issues/7409
- [ ] from .cv.image.image_processor import messages_preprocess 添加是否对网络url替换为base64的控制；添加对video切帧的支持
- [ ] https://github.com/hiyouga/LLaMA-Factory/blob/main/src/llamafactory/chat/vllm_engine.py#L99

识别下面链接的滚动截图：
https://sjh.baidu.com/site/dzfmws.cn/da721a31-476d-42ed-aad1-81c2dc3a66a3

vllm 异步推理示例：

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.sampling_params import SamplingParams
import torch

# Define request data model
class RequestData(BaseModel):
    prompts: List[str]
    max_tokens: int = 2048
    temperature: float = 0.7

# Initialize FastAPI app
app = FastAPI()

# Determine device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize AsyncLLMEngine
engine_args = AsyncEngineArgs(
    model="your-model-name",  # Replace with your model name
    dtype="bfloat16",
    gpu_memory_utilization=0.8,
    max_model_len=4096,
    trust_remote_code=True
)
llm_engine = AsyncLLMEngine.from_engine_args(engine_args)

# Define the inference endpoint
@app.post("/predict")
async def generate_text(data: RequestData):
    sampling_params = SamplingParams(
        max_tokens=data.max_tokens,
        temperature=data.temperature
    )
    request_id = "unique_request_id"  # Generate a unique request ID
    results_generator = llm_engine.generate(data.prompts, sampling_params, request_id)
  
    final_output = None
    async for request_output in results_generator:
        final_output = request_output
  
    assert final_output is not None
    text_outputs = [output.text for output in final_output.outputs]
    return {"responses": text_outputs}

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

```

## image downloader
```python

import os
import hashlib
from icrawler.builtin import BingImageCrawler, BaiduImageCrawler, GoogleImageCrawler
from PIL import Image
import glob
import shutil
import io


class ImageDownloader:
    """使用icrawler库实现的图片下载器"""
    
    def __init__(self, save_dir="downloaded_images"):
        """
        初始化图片下载器
        
        参数:
            save_dir: 图片保存的目录，默认为"downloaded_images"
        """
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
    
    def download_from_baidu(self, keyword, num_images=20):
        """
        从百度图片搜索并下载图片
        
        参数:
            keyword: 搜索关键词
            num_images: 要下载的图片数量
        
        返回:
            下载的图片数量
        """
        # 为每个关键词创建一个临时目录
        temp_dir = os.path.join(self.save_dir, "_temp_" + keyword.replace(" ", "_"))
        os.makedirs(temp_dir, exist_ok=True)
        
        # 创建最终保存的关键词目录
        keyword_dir = os.path.join(self.save_dir, keyword.replace(" ", "_"))
        os.makedirs(keyword_dir, exist_ok=True)
        
        print(f"从百度搜索并下载 '{keyword}' 的图片...")
        
        # 创建百度爬虫
        crawler = BaiduImageCrawler(
            downloader_threads=4,
            storage={'root_dir': temp_dir}
        )
        
        # 执行爬取
        crawler.crawl(keyword=keyword, max_num=num_images)
        
        # 转换所有图片为jpg格式并使用哈希文件名，保存到对应关键词目录
        converted = self._convert_images_to_jpg_with_hash(temp_dir, keyword, keyword_dir, "baidu")
        
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return converted
    
    def download_from_bing(self, keyword, num_images=20):
        """
        从必应图片搜索并下载图片
        
        参数:
            keyword: 搜索关键词
            num_images: 要下载的图片数量
        
        返回:
            下载的图片数量
        """
        # 为每个关键词创建一个临时目录
        temp_dir = os.path.join(self.save_dir, "_temp_" + keyword.replace(" ", "_"))
        os.makedirs(temp_dir, exist_ok=True)
        
        # 创建最终保存的关键词目录
        keyword_dir = os.path.join(self.save_dir, keyword.replace(" ", "_"))
        os.makedirs(keyword_dir, exist_ok=True)
        
        print(f"从必应搜索并下载 '{keyword}' 的图片...")
        
        # 创建必应爬虫
        crawler = BingImageCrawler(
            downloader_threads=4,
            storage={'root_dir': temp_dir}
        )
        
        # 执行爬取
        crawler.crawl(keyword=keyword, max_num=num_images)
        
        # 转换所有图片为jpg格式并使用哈希文件名，保存到对应关键词目录
        converted = self._convert_images_to_jpg_with_hash(temp_dir, keyword, keyword_dir, "bing")
        
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return converted
    
    def download_from_google(self, keyword, num_images=20):
        """
        从谷歌图片搜索并下载图片
        
        参数:
            keyword: 搜索关键词
            num_images: 要下载的图片数量
        
        返回:
            下载的图片数量
        """
        # 为每个关键词创建一个临时目录
        temp_dir = os.path.join(self.save_dir, "_temp_" + keyword.replace(" ", "_"))
        os.makedirs(temp_dir, exist_ok=True)
        
        # 创建最终保存的关键词目录
        keyword_dir = os.path.join(self.save_dir, keyword.replace(" ", "_"))
        os.makedirs(keyword_dir, exist_ok=True)
        
        print(f"从谷歌搜索并下载 '{keyword}' 的图片...")
        
        # 创建谷歌爬虫
        crawler = GoogleImageCrawler(
            downloader_threads=4,
            storage={'root_dir': temp_dir}
        )
        
        # 执行爬取
        crawler.crawl(keyword=keyword, max_num=num_images)
        
        # 转换所有图片为jpg格式并使用哈希文件名，保存到对应关键词目录
        converted = self._convert_images_to_jpg_with_hash(temp_dir, keyword, keyword_dir, "google")
        
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return converted
    
    def download_images(self, keyword, num_images=20, engine="bing"):
        """
        根据关键词从指定搜索引擎下载图片
        
        参数:
            keyword: 搜索关键词
            num_images: 要下载的图片数量
            engine: 搜索引擎，支持"baidu"、"bing"或"google"
        
        返回:
            下载的图片数量
        """
        if engine == "baidu":
            return self.download_from_baidu(keyword, num_images)
        elif engine == "bing":
            return self.download_from_bing(keyword, num_images)
        elif engine == "google":
            return self.download_from_google(keyword, num_images)
        else:
            raise ValueError(f"不支持的搜索引擎: {engine}，请使用 'baidu', 'bing' 或 'google'")
    
    def _get_image_hash(self, image_data):
        """
        计算图片内容的MD5哈希值
        
        参数:
            image_data: 图片二进制数据
        
        返回:
            图片的哈希值
        """
        return hashlib.md5(image_data).hexdigest()
    
    def _convert_images_to_jpg_with_hash(self, directory, keyword, target_dir, engine):
        """
        将目录中的所有图片转换为jpg格式，并使用哈希值作为文件名
        
        参数:
            directory: 图片所在目录
            keyword: 搜索关键词（用于元数据）
            target_dir: 图片保存的目标目录
            engine: 使用的搜索引擎
        
        返回:
            成功转换的图片数量
        """
        converted_count = 0
        # 获取所有图片文件
        image_files = glob.glob(os.path.join(directory, '*.*'))
        
        # 创建元数据文件路径
        metadata_path = os.path.join(target_dir, "metadata.txt")
        
        for img_path in image_files:
            try:
                # 尝试打开图片
                with open(img_path, 'rb') as f:
                    image_data = f.read()
                
                # 计算图片内容的哈希值
                hash_value = self._get_image_hash(image_data)
                
                try:
                    # 尝试加载图片以确保它是有效的
                    img = Image.open(io.BytesIO(image_data))
                    
                    # 转换为RGB模式（以防是RGBA或其他模式）
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    
                    # 使用哈希值作为文件名
                    jpg_filename = f"{hash_value}.jpg"
                    jpg_path = os.path.join(target_dir, jpg_filename)
                    
                    # 如果文件已存在，跳过（避免重复）
                    if os.path.exists(jpg_path):
                        print(f"图片已存在 (哈希值: {hash_value})")
                        converted_count += 1
                        continue
                    
                    # 保存为jpg
                    img.save(jpg_path, "JPEG")
                    
                    # 记录元数据到文本文件
                    with open(metadata_path, "a", encoding="utf-8") as meta_file:
                        meta_file.write(f"{jpg_filename}\t{keyword}\t{engine}\n")
                    
                    converted_count += 1
                    print(f"保存图片到 {target_dir}: {jpg_filename}")
                    
                except Exception as e:
                    print(f"处理图片失败: {e}")
                
            except Exception as e:
                print(f"无法处理图片 {img_path}: {e}")
        
        print(f"成功处理并哈希化 {converted_count} 张图片，保存到 '{target_dir}'")
        return converted_count


def main():
    """主函数，演示如何使用ImageDownloader类"""
    # 创建下载器实例
    downloader = ImageDownloader(save_dir="女性图片集")
    
    # 示例关键词
    keywords = [
        "户外自拍女性",
        "女性写真",
        "动漫女角色",
        "影视剧女角色",
        "短片",
        "校园 女生",
        "随手拍",
        "女性 自拍",
    ]
    
    # 下载每个关键词的图片
    for keyword in keywords:
        downloader.download_images(keyword, num_images=100, engine="bing")
        downloader.download_images(keyword, num_images=100, engine="google")
        downloader.download_images(keyword, num_images=100, engine="baidu")
        print("-" * 50)


def download_images_simple():
    from bing_image_downloader import downloader

    keywords = [
        "影视剧女演员",
        "户外自拍女性",
        "女性写真",
        "女明星生活照",
        "动漫女角色",
        "影视剧女角色",
        "短片 女性角色",
        "校园 女性",
        "女性 自拍",
        "女生",
        "女生自拍",
    ]
    
    # 下载每个关键词的图片
    for keyword in keywords:
        # 从必应下载图片
        downloader.download(
            keyword,
            limit=10,
            output_dir="女性图片集",
            adult_filter_off=False,
            force_replace=False,
            timeout=60
        )
        print(f"完成下载关键词: {keyword}")
        print("-" * 50)


if __name__ == "__main__":
    # download_images_simple()
    main()

```


## call mllm client

```python
#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MLLM client
"""

import pandas as pd
from typing import List, Callable, Optional, Any, Union

# pip install sparrow-python==0.5.1
from sparrow import OpenAIClient, batch_process_messages, ImageCacheConfig

from mod_base.mllm.base import MllmClientBase


class MllmClient(MllmClientBase):
    """
    MLLM客户端实现类
    """

    def __init__(
        self,
        model: str,
        base_url: str,
        api_key="EMPTY",
        concurrency_limit=10,
        max_qps=50,
        timeout=60,
        retry_times=3,
        retry_delay=0.55,
        cache_image=False,
        **kwargs,
    ):
        """
        初始化MLLM客户端
        
        Args:
            model: 模型名称
            base_url: API基础URL
            api_key: API密钥
            concurrency_limit: 并发限制
            max_qps: 最大QPS
            timeout: 超时时间（秒）
            retry_times: 重试次数
            retry_delay: 重试延迟（秒）
            cache_image: 是否缓存图片
            **kwargs: 其他参数
        """
        self.client = OpenAIClient(
            api_key=api_key,
            base_url=base_url,
            concurrency_limit=concurrency_limit,
            max_qps=max_qps,
            timeout=timeout,
            retry_times=retry_times,
            retry_delay=retry_delay,
            **kwargs,
        )
        self.model = model
        self.cache_config = ImageCacheConfig(
            enabled=cache_image,
            cache_dir="image_cache",
            force_refresh=False,
            retry_failed=False,
        )
    
    async def call_llm(
        self,
        messages_list,
        model=None,
        temperature=0.1,
        max_tokens=2000,
        top_p=0.95,
        safety_level="none",
        **kwargs,
    ):
        """
        调用LLM
        
        Args:
            messages_list: 消息列表
            model: 模型名称，默认使用初始化时指定的模型
            temperature: 温度参数
            max_tokens: 最大生成token数
            top_p: top_p参数
            safety_level: 安全级别
            **kwargs: 其他参数
            
        Returns:
            response_list: 响应列表
        """
        if model is None:
            model = self.model

        messages_list = await batch_process_messages(
            messages_list,
            preprocess_msg=True,
            max_concurrent=8,
            cache_config=self.cache_config,
        )
        response_list, _ = await self.client.chat_completions_batch(
            messages_list=messages_list,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            return_summary=True,
            safety_level=safety_level,
            **kwargs,
        )
        return response_list
    
    async def call_llm_with_selection(
        self,
        messages_list,
        n_predictions: int = 3,
        selector_fn: Optional[Callable[[List[Any]], Any]] = None,
        model=None,
        temperature=0.1,
        max_tokens=2000,
        top_p=0.95,
        safety_level="none",
        **kwargs,
    ):
        """
        增强版LLM调用方法，对每条消息进行n次预测，并使用选择函数选择最佳结果
        
        Args:
            messages_list: 消息列表
            n_predictions: 每条消息预测次数
            selector_fn: 选择函数，接收n个响应列表，返回选中的响应
                         如果为None，默认返回第一个响应
            model: 模型名称，默认使用初始化时指定的模型
            temperature: 温度参数
            max_tokens: 最大生成token数
            top_p: top_p参数
            safety_level: 安全级别
            **kwargs: 其他参数
            
        Returns:
            response_list: 选择后的响应列表
        """
        if model is None:
            model = self.model
            
        # 默认选择函数(如果未提供)，简单返回第一个响应
        if selector_fn is None:
            selector_fn = lambda responses: responses[0]
            
        # 为每条消息创建n个副本
        expanded_messages_list = []
        for messages in messages_list:
            for _ in range(n_predictions):
                expanded_messages_list.append(messages)
                
        # 调用模型获取所有响应
        messages_list = await batch_process_messages(
            expanded_messages_list,
            preprocess_msg=True,
            max_concurrent=8,
            cache_config=self.cache_config,
        )
        all_responses, _ = await self.client.chat_completions_batch(
            messages_list=messages_list,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            return_summary=True,
            safety_level=safety_level,
            **kwargs,
        )
        
        # 重组响应并应用选择函数
        selected_responses = []
        for i in range(0, len(all_responses), n_predictions):
            message_responses = all_responses[i:i+n_predictions]
            print(f"{message_responses=}")
            selected_response = selector_fn(message_responses)
            selected_responses.append(selected_response)
            
        return selected_responses

    async def call_llm_nested(
        self,
        messages_list_list,
        model=None,
        temperature=0.1,
        max_tokens=2000,
        top_p=0.95,
        safety_level="none",
        **kwargs,
    ):
        """
        处理嵌套的messages_list_list结构
        将messages_list_list展平为messages_list，调用call_llm获取结果，再重组为response_list_list
        这样做可以提高整体调用性能

        Args:
            messages_list_list: 嵌套的消息列表列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成token数
            top_p: top_p参数
            safety_level: 安全级别
            **kwargs: 其他参数

        Returns:
            response_list_list: 嵌套的响应列表列表，与输入结构对应
        """
        # 记录每个子列表的长度，用于之后重组结果
        lengths = [len(messages_list) for messages_list in messages_list_list]
        
        # 展平messages_list_list
        flattened_messages_list = []
        for messages_list in messages_list_list:
            flattened_messages_list.extend(messages_list)
        
        # 调用call_llm获取展平后的response_list
        flattened_response_list = await self.call_llm(
            flattened_messages_list,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            safety_level=safety_level,
            **kwargs,
        )
        
        # 根据之前记录的长度，将展平的response_list重组为response_list_list
        response_list_list = []
        start_idx = 0
        for length in lengths:
            response_list_list.append(flattened_response_list[start_idx:start_idx + length])
            start_idx += length
        
        return response_list_list
    
    async def call_llm_nested_with_selection(
        self,
        messages_list_list,
        n_predictions: int = 3,
        selector_fn: Optional[Callable[[List[Any]], Any]] = None,
        model=None,
        temperature=0.1,
        max_tokens=2000,
        top_p=0.95,
        safety_level="none",
        **kwargs,
    ):
        """
        处理嵌套的messages_list_list结构，并对每条消息进行多次预测和选择
        
        Args:
            messages_list_list: 嵌套的消息列表列表
            n_predictions: 每条消息预测次数
            selector_fn: 选择函数，接收n个响应列表，返回选中的响应
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成token数
            top_p: top_p参数
            safety_level: 安全级别
            **kwargs: 其他参数

        Returns:
            response_list_list: 嵌套的响应列表列表，与输入结构对应
        """
        # 记录每个子列表的长度，用于之后重组结果
        lengths = [len(messages_list) for messages_list in messages_list_list]
        
        # 展平messages_list_list
        flattened_messages_list = []
        for messages_list in messages_list_list:
            flattened_messages_list.extend(messages_list)
        
        # 调用enhanced_call_llm获取展平后的response_list
        flattened_response_list = await self.call_llm_with_selection(
            flattened_messages_list,
            n_predictions=n_predictions,
            selector_fn=selector_fn,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            safety_level=safety_level,
            **kwargs,
        )
        
        # 根据之前记录的长度，将展平的response_list重组为response_list_list
        response_list_list = []
        start_idx = 0
        for length in lengths:
            response_list_list.append(flattened_response_list[start_idx:start_idx + length])
            start_idx += length
        
        return response_list_list

    def process_text(self, text: str):
        """
        预处理text
        """
        return f"请判断图片内容是否涉及色情。"

    def process_image(self, image: str):
        """
        预处理image
        """
        return image

    def preprocess_dataframe(
        self,
        df: pd.DataFrame,
        image_col: str,
        text_col: str,
    ):
        """
        预处理df
        """
        df[text_col] = df[text_col].apply(self.process_text)
        df[image_col] = df[image_col].apply(self.process_image)
        return df

    async def call_dataframe(
        self,
        df: pd.DataFrame,
        image_col: str,
        text_col: str,
        **kwargs,
    ):
        """
        调用dataframe
        
        Args:
            df: 数据框
            image_col: 图片列名
            text_col: 文本列名
            **kwargs: 模型请求参数
            
        Returns:
            response_list: 响应列表
        """
        df = self.preprocess_dataframe(df, image_col, text_col)

        messages_list = []
        for index, row in df.iterrows():
            messages_list.append(
                [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"{row[text_col]}"},
                            {"type": "image_url", "image_url": {"url": f"{str(row[image_col])}"}},
                        ],
                    }
                ]
            )
        return await self.call_llm(messages_list, **kwargs)
    
    async def call_dataframe_with_selection(
        self,
        df: pd.DataFrame,
        image_col: str,
        text_col: str,
        n_predictions: int = 3,
        selector_fn: Optional[Callable[[List[Any]], Any]] = None,
        **kwargs,
    ):
        """
        调用dataframe并对每条消息进行多次预测和选择
        
        Args:
            df: 数据框
            image_col: 图片列名
            text_col: 文本列名
            n_predictions: 每条消息预测次数
            selector_fn: 选择函数，接收n个响应列表，返回选中的响应
            **kwargs: 模型请求参数
            
        Returns:
            response_list: 响应列表
        """
        df = self.preprocess_dataframe(df, image_col, text_col)

        messages_list = []
        for index, row in df.iterrows():
            messages_list.append(
                [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"{row[text_col]}"},
                            {"type": "image_url", "image_url": {"url": f"{str(row[image_col])}"}},
                        ],
                    }
                ]
            )
        return await self.call_llm_with_selection(
            messages_list, 
            n_predictions=n_predictions,
            selector_fn=selector_fn,
            **kwargs
        )

    def load_dataframe(
        self,
        table_path: str,
        sheet_name: str = 0,
        max_num: int = None,
    ) -> pd.DataFrame:
        """
        加载并过滤Excel数据

        Args:
            table_path: 表格文件路径
            sheet_name: 要读取的sheet名称
            max_num: 最大处理数量限制

        Returns:
            处理后的DataFrame

        Raises:
            ValueError: 当输入参数无效时
            FileNotFoundError: 当文件不存在时
        """
        # 验证输入参数
        if not table_path:
            raise ValueError("表格文件路径不能为空")

        # 读取数据
        try:
            if table_path.endswith(".xlsx"):
                df = pd.read_excel(table_path, sheet_name=sheet_name)
            elif table_path.endswith(".csv"):
                df = pd.read_csv(table_path)
            else:
                raise ValueError(f"不支持的文件格式: {table_path}")
        except Exception as e:
            raise ValueError(f"读取文件失败: {str(e)}")

        # 去除空行
        # df = df.dropna()
        #
        if df.empty:
            print(f"警告: 过滤后数据为空")
            return df

        # 应用数量限制
        if max_num is not None:
            df = df.head(max_num)

        print(f"加载数据完成: {len(df)} 行")
        df = df.astype(str)
        print(f"{df.head(2)=}")

        return df

    async def call_table(
        self,
        table_path: str,
        image_col: str = "image",
        text_col: str = "text",
        sheet_name: str = 0,
        max_num: int = None,
        **kwargs,
    ):
        """
        调用table
        
        Args:
            table_path: 表格文件路径
            image_col: 图片列名，默认为"image"
            text_col: 文本列名，默认为"text"
            sheet_name: sheet名称，默认为0
            max_num: 最大处理数量限制
            **kwargs: 其他参数
            
        Returns:
            response_list: 响应列表
        """
        df = self.load_dataframe(table_path, sheet_name, max_num)
        return await self.call_dataframe(df, image_col, text_col, **kwargs)
    
    async def call_table_with_selection(
        self,
        table_path: str,
        image_col: str = "image",
        text_col: str = "text",
        sheet_name: str = 0,
        max_num: int = None,
        n_predictions: int = 3,
        selector_fn: Optional[Callable[[List[Any]], Any]] = None,
        **kwargs,
    ):
        """
        调用table并对每条消息进行多次预测和选择
        
        Args:
            table_path: 表格文件路径
            image_col: 图片列名，默认为"image"
            text_col: 文本列名，默认为"text"
            sheet_name: sheet名称，默认为0
            max_num: 最大处理数量限制
            n_predictions: 每条消息预测次数
            selector_fn: 选择函数，接收n个响应列表，返回选中的响应
            **kwargs: 其他参数
            
        Returns:
            response_list: 响应列表
        """
        df = self.load_dataframe(table_path, sheet_name, max_num)
        return await self.call_dataframe_with_selection(
            df, 
            image_col, 
            text_col, 
            n_predictions=n_predictions,
            selector_fn=selector_fn,
            **kwargs
        )


if __name__ == "__main__":
    import asyncio
    from rich import print

    api_key = "bce-v3/ALTAK-DVWdmy3xDCZimNsJ7nMx3/4cb74b2e8e41713a755d48fec97b1ecc787f98da"
    base_url = "https://qianfan.baidubce.com/v2"
    model = "ernie-4.5-turbo-vl-32k"
    client = MllmClient(
        model=model,
        base_url=base_url,
        api_key=api_key,
        concurrency_limit=10,
        max_qps=50,
        cache_image=True,
    )

    print(
        asyncio.run(
            client.call_table_with_selection(
                table_path="dataset/case_视频/小视频封面色情模型随机数据0421.xlsx",
                image_col="竖版封面地址",
                text_col="副标题",
                max_num=5,
                n_predictions=3,
                selector_fn=lambda responses: responses[0],
            )
        )
    )


```


## 待添加脚本

## Install

```bash
pip install sparrow-python
# Or dev version
pip install sparrow-python[dev]
# Or
pip install -e .
# Or
pip install -e .[dev]
```

## Usage

### Multiprocessing SyncManager

Open server first:

```bash
$ spr start-server
```

The defualt port `50001`.

(Process1) productor:

```python
from sparrow.multiprocess.client import Client

client = Client(port=50001)
client.update_dict({'a': 1, 'b': 2})
```

(Process2) consumer:

```python
from sparrow.multiprocess.client import Client

client = Client(port=50001)
print(client.get_dict_data())

>> > {'a': 1, 'b': 2}
```

### Common tools

- **Kill process by port**

```bash
$ spr kill {port}
```

- **pack & unpack**
  support archive format: "zip", "tar", "gztar", "bztar", or "xztar".

```bash
$ spr pack pack_dir
```

```bash
$ spr unpack filename extract_dir
```

- **Scaffold**

```bash
$ spr create awosome-project
```

### Some useful functions

> `sparrow.relp`
> Relative path, which is used to read or save files more easily.

> `sparrow.performance.MeasureTime`
> For measuring time (including gpu time)

> `sparrow.performance.get_process_memory`
> Get the memory size occupied by the process

> `sparrow.performance.get_virtual_memory`
> Get virtual machine memory information

> `sparrow.add_env_path`
> Add python environment variable (use relative file path)
