from ATRIlib.DB.pipeline_beatmapranking import get_beatmapranking_up_list_from_db, get_beatmapranking_list_from_db, \
    get_beatmapranking_list_from_db_old,get_beatmapranking_list_from_unrankscore_db,get_beatmapranking_list_from_unrankscore_db_old
from ATRIlib.API.PPYapiv2 import get_beatmap_info
from ATRIlib.TASKS.Jobs import multi_update_users_beatmap_score_async,job_update_unrank_score
from ATRIlib.DRAW.draw_brk import draw_beatmap_rank_screen
from datetime import datetime, timedelta
import logging

brkup_cache = {}
BRKUP_CACHE_DURATION = timedelta(minutes=10)  # Unified cache duration

async def calculate_beatmapranking_update(user_id,beatmap_id, group_id):

    is_ranked = True

    beatmapinfo = await get_beatmap_info(beatmap_id)

    if beatmapinfo == {'error': "Specified beatmap difficulty couldn't be found."}:
        raise ValueError(f"无法找到这个谱面b{beatmap_id}")

    if beatmapinfo["ranked"] not in {1, 2, 4}:
        await job_update_unrank_score(user_id)
        is_ranked = False
        return {"status": "success","is_ranked":is_ranked}

    logging.info(f"Performing cleanup for brkup request: beatmap_id={beatmap_id}, group_id={group_id}")
    # TODO: Implement or call the actual cleanup function here

    cache_key = (beatmap_id, group_id)
    current_time = datetime.now()

    # Check cache
    if cache_key in brkup_cache:
        cached_time, cached_result = brkup_cache[cache_key]
        time_difference = current_time - cached_time
        if time_difference <= BRKUP_CACHE_DURATION:
            remaining_time = BRKUP_CACHE_DURATION - time_difference
            remaining_seconds = int(remaining_time.total_seconds())
            logging.info(
                f"Returning cached result for brkup key: {cache_key}, remaining time: {remaining_seconds} seconds")

            return {"status": "cached", "remaining_seconds": remaining_seconds,
                    "result": cached_result}  # Return cached result
        else:
            # Cache expired, remove it
            del brkup_cache[cache_key]
            logging.info(f"Brkup cache expired for key: {cache_key}")

    # If not in cache or cache expired, fetch new data
    logging.info(f"Fetching new data for brkup key: {cache_key}")
    # Add cleanup logic here
    # Assuming a function exists or needs to be called for cleanup
    # Example: await ATRIlib.beatmapranking.cleanup_brk_temp_data(beatmap_id, group_id)
    logging.info(f"Performing cleanup for brkup request: beatmap_id={beatmap_id}, group_id={group_id}")
    # TODO: Implement or call the actual cleanup function here

    all_users_list = get_beatmapranking_up_list_from_db(group_id)

    users_id_list = []

    for i in all_users_list:
        users_id_list.append(i["user_id"])

    # 这下user_list就是本群玩家了
    result = f'b{beatmap_id}\n'
    result += await multi_update_users_beatmap_score_async(beatmap_id, users_id_list)

    # 更新成功后才
    # Store result in cache
    brkup_cache[cache_key] = (current_time, result)

    return {"status": "success", "result": result,"is_ranked":is_ranked}  # Return status and result

async def calculate_beatmapranking(user_id, beatmap_id, group_id, mods_list,is_old=False,is_ranked=True):
    if "NM" in mods_list:
        mods_list = []
    if "None" in mods_list:
        mods_list = None

    beatmapinfo = await get_beatmap_info(beatmap_id)

    if is_old:
        if is_ranked:
            raw = get_beatmapranking_list_from_db_old(user_id, beatmap_id, group_id, mods_list)
        else:
            raw = get_beatmapranking_list_from_unrankscore_db_old(user_id, beatmap_id, group_id, mods_list)
    else:
        if is_ranked:
            raw = get_beatmapranking_list_from_db(user_id,beatmap_id,group_id,mods_list)
        else:
            raw = get_beatmapranking_list_from_unrankscore_db(user_id,beatmap_id,group_id,mods_list)

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
        user_record = {"top_score": {"user_id" : user_id , "total_score" : -1, "legacy_total_score" : -1}}

    result = await draw_beatmap_rank_screen(user_record, raw, beatmapinfo, mods_list,is_old)

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