from ATRIlib.API.github import get_latest_release
import re

async def get_lazer_update():

    data = await get_latest_release()

    # 正则表达式匹配 .exe 和 .apk 结尾的文件
    pattern = r'\.(exe|apk)$'

    proxy_url = []
    
    for asset in data['assets']:
        match = re.search(pattern, asset['name'], re.IGNORECASE)
        if match:
            file_type = match.group(1).lower()
            prefix = "Windows" if file_type == "exe" else "Android" if file_type == "apk" else ""
            # 在下载链接前添加代理前缀和文件类型前缀
            proxy_url.append(f"{prefix}: https://ghp.ci/{asset['browser_download_url']}")

    data['proxy_url'] = proxy_url

    return data
