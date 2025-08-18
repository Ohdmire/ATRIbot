from ATRIlib.Config.config import deepseek_key,translate_prompt
from openai import OpenAI
from typing import List
import asyncio
import logging
import re

try:
    client = OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com")
except:
    pass

def translate(mycontent):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful translator. Translate the user's markdown text into Chinese. Keep markdown style."},
            {"role": "user", "content": translate_prompt+mycontent},
        ],
        stream=False
    )

    return response.choices[0].message.content


async def async_translate(text: str) -> str:
    """
    异步翻译函数（将同步调用包装为异步）
    """

    def sync_translate():
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system",
                 "content": """你是一个专业的翻译助手，你将翻译一个名为osu!的音乐节奏游戏的更新日志，其中beatmap翻译为谱面，游戏一共有4个模式，
    osu!
    osu!taiko
    osu!catch
    osu!mania
保持原文不翻译。lazer/tachyon为游戏发布流，保持原文。如果遇到markdown格式，保持markdown格式不变。段落之间用'---SEP---'分隔。"""},
                {"role": "user", "content": text},
            ],
            stream=False
        )
        return response.choices[0].message.content

    # 将同步函数放到单独的线程中执行
    return await asyncio.to_thread(sync_translate)




# 最大单次翻译的字符数 (根据API限制调整)
MAX_BATCH_SIZE = 2000
# 每个翻译批次的最大条目数
MAX_BATCH_ITEMS = 4


async def batch_translate(texts: List[str]) -> List[str]:
    """
    批量翻译文本，自动打包和拆分，处理媒体标签（删除img/video标签后翻译剩余内容）
    """
    if not texts:
        return []

    # 预处理：删除媒体标签并记录原始索引和文本
    processed_texts = []
    media_tag_pattern = re.compile(
        r'</?(img|video|source)[^>]*>',  # 匹配开标签、闭标签和自闭合标签
        re.IGNORECASE
    )

    for i, text in enumerate(texts):
        if not text.strip():
            continue
        # 删除所有img和video标签
        cleaned_text = media_tag_pattern.sub('', text).strip()
        if cleaned_text:  # 只有删除标签后仍有内容才处理
            processed_texts.append((i, cleaned_text))

    # 按大小分组打包
    batches = []
    current_batch = []
    current_size = 0

    for i, text in processed_texts:
        text_size = len(text)
        if (current_size + text_size > MAX_BATCH_SIZE or
                len(current_batch) >= MAX_BATCH_ITEMS):
            batches.append(current_batch)
            current_batch = []
            current_size = 0

        current_batch.append((i, text))
        current_size += text_size

    if current_batch:
        batches.append(current_batch)

    # 执行批量翻译
    translated_texts = [""] * len(texts)

    # 处理空文本
    for i, text in enumerate(texts):
        if not text.strip():
            translated_texts[i] = ""

    logging.debug(f"待翻译批次: {batches}")

    for batch in batches:
        batch_indices = [item[0] for item in batch]
        batch_texts = [item[1] for item in batch]
        batch_text = "\n---SEP---\n".join(batch_texts)

        try:
            response = await async_translate(batch_text)

            # 分割逻辑
            sep_pattern = re.compile(r'\n*---SEP---\n*', re.IGNORECASE)
            batch_results = re.split(sep_pattern, response)
            batch_results = [res.strip() for res in batch_results if res.strip()]

            # 确保结果数量匹配
            if len(batch_results) != len(batch_texts):
                logging.warning(
                    f"分割结果数量不匹配: 预期 {len(batch_texts)} 得到 {len(batch_results)}\n{batch_texts} -- {batch_results}"
                )
                if len(batch_results) < len(batch_texts):
                    batch_results += [""] * (len(batch_texts) - len(batch_results))
                else:
                    batch_results = batch_results[:len(batch_texts)]

            logging.debug(f'翻译结果: {batch_results}')

            # 写入最终结果
            for idx, result in zip(batch_indices, batch_results):
                translated_texts[idx] = result.strip()

        except Exception as e:
            logging.error(f"翻译失败: {e}")
            # 失败时回退到原文（不含媒体标签的版本）
            for idx in batch_indices:
                translated_texts[idx] = processed_texts[idx][1]  # 使用已清理的原文

    return translated_texts

