from ATRIlib.DB.pipeline_beatmapranking import get_beatmapranking_up_list_from_db,get_beatmapranking_list_from_db
from ATRIlib.API.PPYapiv2 import get_beatmap_info
from ATRIlib.TASKS.Jobs import multi_update_users_beatmap_score_async
from ATRIlib.DRAW.draw_brk import draw_beatmap_rank_screen

async def calculate_beatmapranking_update(beatmap_id, group_id):
    beatmapinfo = await get_beatmap_info(beatmap_id)

    if beatmapinfo == {'error': "Specified beatmap difficulty couldn't be found."}:
        return "无法找到该谱面"

    all_users_list = get_beatmapranking_up_list_from_db(group_id)

    users_id_list = []

    for i in all_users_list:
        users_id_list.append(i["user_id"])

    # 这下user_list就是本群玩家了
    result = f'b{beatmap_id}\n'
    result += await multi_update_users_beatmap_score_async(beatmap_id, users_id_list)

    return result

async def calculate_beatmapranking(user_id, beatmap_id, group_id, mods_list):
    if "NM" in mods_list:
        mods_list = []
    if "None" in mods_list:
        mods_list = None

    beatmapinfo = await get_beatmap_info(beatmap_id)

    raw = get_beatmapranking_list_from_db(user_id,beatmap_id,group_id,mods_list)

    user_record = None
    for record in raw:
        if record["top_score"]["user_id"] == user_id:
            user_record = record
            # break
        if "great" not in record["top_score"]["statistics"]:
            record["top_score"]["statistics"]["great"] = 0
        if "ok" not in record["top_score"]["statistics"]:
            record["top_score"]["statistics"]["ok"] = 0
        if "meh" not in record["top_score"]["statistics"]:
            record["top_score"]["statistics"]["meh"] = 0
        if "miss" not in record["top_score"]["statistics"]:
            record["top_score"]["statistics"]["miss"] = 0
    if user_record is None:
        user_record = {"top_score": {"user_id" : user_id , "total_score" : -1}}

    result = await draw_beatmap_rank_screen(user_record, raw, beatmapinfo, mods_list)

    return result



    # try:
    #     # 更新个人成绩
    #
    #     await self.update_scores_info(user_id, beatmap_id)
    #
    #     userscores = self.db_score.find(
    #         {"beatmap_id": beatmap_id, "user_id": user_id})
    #
    #     user_best_score = {}
    #     user_best_score.update({"score": -1})
    #     for userscore in userscores:
    #
    #         if userscore["score"] > user_best_score["score"]:  # 愚人节
    #             if mods_list is not None:
    #                 try:
    #                     if sorted(userscore["mods"]) == sorted(mods_list):
    #                         user_best_score = userscore
    #                 except:
    #                     pass
    #             else:
    #                 user_best_score = userscore
    #
    #         # 加入用户名,avatar_url
    #     username = self.db_user.find_one(
    #         {"id": user_best_score["user_id"]})["username"]
    #
    #     avatar_url = self.db_user.find_one(
    #         {"id": user_best_score["user_id"]})["avatar_url"]
    #
    #     user_best_score.update({"username": username})
    #     user_best_score.update({"avatar_url": avatar_url})
    #
    # except:
    #
    #     user_best_score = {}
    #     # username = self.db_user.find_one(
    #     #     {"id": user_id})["username"]
    #
    #     user_best_score = {"user_id": user_id}
    #
    # beatmapinfo = await get_beatmap_info(beatmap_id)
    #
    # # 查找群友的最好成绩
    #
    # group_users_list = self.db_group.find_one(
    #     {"id": group_id})["user_id_list"]
    #
    # all_users_list = self.db_bind.find({"id": {"$in": group_users_list}})
    #
    # # 这下user_list就是本群玩家了
    #
    # other_users_best_score_list = []
    #
    # for another_user in all_users_list:
    #
    #     another_userscores = self.db_score.find(
    #         {"beatmap_id": beatmap_id, "user_id": another_user["user_id"]})
    #
    #     another_user_best_score = {}
    #     another_user_best_score.update({"score": -1})
    #
    #     for another_userscore in another_userscores:
    #         if another_userscore["score"] > another_user_best_score["score"]:  # 愚人节
    #             if mods_list is not None:
    #                 try:
    #                     if sorted(another_userscore["mods"]) == sorted(mods_list):
    #                         another_user_best_score = another_userscore
    #                 except:
    #                     pass
    #             else:
    #                 another_user_best_score = another_userscore
    #
    #     if another_user_best_score != {"score": -1}:
    #         other_users_best_score_list.append(another_user_best_score)
    #
    # sorted_others = sort_by_givenkey_reverse(
    #     other_users_best_score_list, "score")
    #
    # final_sorted_others = []
    #
    # # 加入用户名,avatar_url
    # for sorted_other in sorted_others:
    #
    #     try:
    #         username = self.db_user.find_one(
    #             {"id": sorted_other["user_id"]})["username"]
    #
    #         avatar_url = self.db_user.find_one(
    #             {"id": sorted_other["user_id"]})["avatar_url"]
    #
    #         sorted_other.update({"username": username})
    #         sorted_other.update({"avatar_url": avatar_url})
    #
    #         final_sorted_others.append(sorted_other)
    #     except:
    #         print(f'error {sorted_other}')
    #
    # result = await Dtools.draw_beatmap_rank_screen(user_best_score, final_sorted_others, beatmapinfo, mods_list)
    #
    # return result