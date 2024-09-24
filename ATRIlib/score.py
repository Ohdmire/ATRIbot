from ATRIlib.API.PPYapiv2 import get_user_passrecent_info,get_user_scores_info
from ATRIlib.PP.Rosu import fetch_beatmap_file_async_one,calculate_pp_if_all
from ATRIlib.DRAW.draw_score import draw_result_screen

async def calculate_pr_score(user_id):
    # 计算pr分数
    data = await get_user_passrecent_info(user_id)
    if len(data) == 0:
        raise ValueError("无法找到最近游玩的成绩")
    data = data[0]

    if data["beatmap"]["status"] == "ranked" or data["beatmap"]["status"] == "loved":
        # 永久保存谱面
        await fetch_beatmap_file_async_one(data["beatmap"]["id"], Temp=False)

        ppresult = await calculate_pp_if_all(
            data["beatmap"]["id"], data["mods"], data["accuracy"] * 100, data["max_combo"], Temp=False)
    else:
        # 临时保存谱面
        await fetch_beatmap_file_async_one(data["beatmap"]["id"], Temp=True)

        ppresult = await calculate_pp_if_all(
            data["beatmap"]["id"], data["mods"], data["accuracy"] * 100, data["max_combo"], Temp=True)

    result = await draw_result_screen(data, ppresult)

    return result


async def calculate_score(user_id, beatmap_id):
    data = await get_user_scores_info(user_id, beatmap_id)
    if len(data) == 0:
        raise ValueError("无法找到该谱面游玩的成绩")
    data = data[0]

    if data["beatmap"]["status"] == "ranked" or data["beatmap"]["status"] == "loved":
        # 永久保存谱面
        await fetch_beatmap_file_async_one(data["beatmap"]["id"], Temp=False)

        ppresult = await calculate_pp_if_all(
            data["beatmap"]["id"], data["mods"], data["accuracy"] * 100, data["max_combo"], Temp=False)
    else:
        # 临时保存谱面
        await fetch_beatmap_file_async_one(
            data["beatmap"]["id"], Temp=True)

        ppresult = await calculate_pp_if_all(
            data["beatmap"]["id"], data["mods"], data["accuracy"] * 100, data["max_combo"], Temp=True)

    result = await draw_result_screen(data, ppresult)

    return result