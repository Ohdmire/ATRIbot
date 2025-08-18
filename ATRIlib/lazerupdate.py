from ATRIlib.API.github import get_latest_release
import re


async def get_lazer_update():
    data = await get_latest_release()

    # 正则表达式匹配 .exe, .apk 和 .ipa 结尾的文件
    pattern = r'\.(exe|apk|ipa|appimage)$'

    proxy_url = []

    for asset in data['assets']:
        match = re.search(pattern, asset['name'], re.IGNORECASE)
        if match:
            file_type = match.group(1).lower()
            # 根据文件类型设置前缀
            if file_type == "exe":
                prefix = "Windows"
            elif file_type == "apk":
                prefix = "Android"
            elif file_type == "ipa":
                prefix = "iOS"
            elif file_type == "appimage":
                prefix = "Linux"
            else:
                prefix = ""

            # 在下载链接前添加代理前缀和文件类型前缀
            proxy_url.append(f"{prefix}: https://gh-proxy.com/{asset['browser_download_url']}")

    data['proxy_url'] = proxy_url

    return data