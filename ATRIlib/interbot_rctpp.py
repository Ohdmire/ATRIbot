import random
from ATRIlib.API.PPYapiv2 import get_user_recentscore_info_stable
from ATRIlib.interbot_untils import convert_mapjson,factBpm
from ATRIlib.PP.Rosu import calculate_map_attrs
from ATRIlib.TOOLS.CommonTools import calculate_rank_for_stable,mods_to_str
from ATRIlib.PP.Rosu import fetch_beatmap_file_async_one,calculate_pp_if_all_stable
from datetime import datetime, timezone, timedelta

bg_thumb = '[CQ:image,file=https://b.ppy.sh/thumb/{sid}l.jpg]'


def missReply(miss, acc, ar, cb, maxcb, stars):
    miss = int(miss)
    r = 'emmm不知道说什么了'
    ar = float(ar)
    stars = float(stars)
    cb = int(cb)
    maxcb = int(maxcb)
    ranReply = '额...'
    if miss == 0:
        if maxcb != cb:
            r = '感受滑条的魅力吧'
        else:
            if acc == 100:
                r = '跟我一起喊爷爷!'
            elif acc >= 99:
                r = 'emmm恐怖,建议踢了'
            else:
                l = ['您还是人马，0miss??',
                     'miss?不存在的!']
                r = random.choice(l)
    else:
        if miss == 1:
            if stars < 5:
                l = ['1miss,治治你的手抖吧',
                     '1miss,再肛一肛，pp就到手了',
                     '专业破梗1miss大法上下颠倒hr']
                r = random.choice(l)
            else:
                l = ['1miss，pp飞了，心痛吗',
                     '出售专治1Miss绝症药，5块/瓶',
                     '差点你就爆了一群爷爷了,1miss距离',
                     '1miss惨案,默哀5分钟']
                r = random.choice(l)
        elif miss < 10:
            if stars < 5:
                l = ['%smiss，你还没fc吗' % miss,
                     '%smiss，再糊糊可能就fc了' % miss]
                r = random.choice(l)
            elif stars < 7:
                r = '%smiss，有点恐怖啊你' % miss
            else:
                r = '%smiss，你是什么怪物' % miss

        else:
            if stars < 4:
                r = '打个低星图，还能%smiss，删游戏吧' % miss
            else:
                if ar > 9.7:
                    r = '%smiss，dalou建议你开ez玩' % miss
                elif miss > 50:
                    r = '%smiss，太菜了，不想评价' % miss
                else:
                    r = '%smiss，%s' % (miss, ranReply)

    randn = random.randint(0, 100)
    if randn < 30:
        return '%smiss，%s' % (miss, ranReply)
    elif randn < 70:
        ranReply = "我没有数据库，怎么锐评"
        return '%smiss，%s' % (miss, ranReply)

    return r

async def formatRctpp2New(data,ppresult):
    """格式化rctpp输出"""
    outp = '{artist} - {title} [{version}] \n'
    outp += 'Beatmap by {creator} \n'
    outp += '[ar{ar} cs{cs} od{od} hp{hp}  bpm{bpm}]\n'
    outp += bg_thumb + '\n'
    # outp += 'stars: {stars}*({oldstar}*) | {mods_str} \n'
    outp += 'stars: {stars}* | {mods_str} \n'
    outp += '{combo}x/{max_combo}x | {acc}% | {rank} \n\n'
    # outp += '{acc}%: {pp}pp({oldpp}pp)\n'
    # outp += '{fcacc}%: {ppfc}pp({oldfcpp}pp)\n'
    # outp += '100.0%: {ppss}pp({oldsspp}pp)\n'
    outp += '{acc}%: {pp}pp\n'
    outp += 'FC: {ppfc}pp\n'
    outp += '100.0%: {ppss}pp\n'
    outp += '{missStr}\n'
    # outp += 'https://osu.ppy.sh/b/{bid}'
    outp += '{date}  (bid:{bid})'

    modd_map_attrs = await calculate_map_attrs(data["beatmap"]["id"],data["mods"])

    stars = round(float(modd_map_attrs['stars']), 2)

    missStr = missReply(data["statistics"]["miss"], data["accuracy"], modd_map_attrs['ar'],
                        data['max_combo'], modd_map_attrs['max_combo_map'], stars=stars)

    bpm = factBpm(float(data['beatmap']['bpm']), mods_to_str(data['mods']))
    ar = round(modd_map_attrs['ar'], 1)

    stb_rank = calculate_rank_for_stable(data["statistics"]["great"], data["statistics"]["ok"], data["statistics"]["meh"], data["statistics"]["miss"])

    has_hd_or_fl = any(m["acronym"] in {"HD", "FL"} for m in data['mods'])

    if has_hd_or_fl:
        if stb_rank == "S":
            stb_rank = "SH"
        elif stb_rank == "SS":
            stb_rank = "XH"

    data["rank"] = stb_rank

    # Handle time conversion (UTC -> UTC+8)
    ended_at_utc = data.get('ended_at', '')
    if ended_at_utc:
        try:
            utc_time = datetime.strptime(ended_at_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            utc8_time = utc_time.astimezone(timezone(timedelta(hours=8)))
            ended_at_utc8 = utc8_time.strftime("%Y-%m-%d %H:%M:%S")
        except:
            ended_at_utc8 = ended_at_utc.replace('T', ' ').replace('Z', '')
    else:
        ended_at_utc8 = ''



    out = outp.format(
        artist=data['beatmapset']['artist_unicode'],
        title=data['beatmapset']['title_unicode'],
        version=data['beatmap']['version'],
        creator=data['beatmapset']['creator'],
        ar=ar,
        cs = round(modd_map_attrs['cs'], 1),
        od=round(modd_map_attrs['od'], 1),
        hp=round(modd_map_attrs['hp'], 1),
        stars=stars,
        # oldstar = round(ojson['stars'], 2),
        combo=data['max_combo'],
        max_combo=modd_map_attrs['max_combo_map'],
        acc=round(data["accuracy"]*100, 2),
        mods_str=mods_to_str(data['mods']),
        pp=round(data["pp"]) if data["pp"] is not None else round(ppresult["pp"]),
        rank=stb_rank,
        ppfc=round(ppresult['fcpp']),
        ppss=round(ppresult['100fcpp']),
        bid=data['beatmap']['id'],
        miss=data["statistics"]["miss"],
        missStr=missStr,
        bpm=bpm,
        sid=data['beatmapset']['id'],
        date=ended_at_utc8
        # oldpp = round(ojson['pp']),
        # oldfcpp = round(oldfcpp),
        # oldsspp = round(oldsspp),
    )
    return out

async def calculate_rctpp_text(data):

    if "great" not in data["statistics"]:
        data["statistics"]["great"] = 0
    if "ok" not in data["statistics"]:
        data["statistics"]["ok"] = 0
    if "meh" not in data["statistics"]:
        data["statistics"]["meh"] = 0
    if "miss" not in data["statistics"]:
        data["statistics"]["miss"] = 0

    if data["beatmap"]["status"] == "ranked" or data["beatmap"]["status"] == "loved":
        # 永久保存谱面
        await fetch_beatmap_file_async_one(data["beatmap"]["id"], Temp=False)

        ppresult = await calculate_pp_if_all_stable(
            data["beatmap"]["id"], data["mods"], data["accuracy"] * 100, data["max_combo"],data["statistics"], Temp=False)
    else:
        # 临时保存谱面
        await fetch_beatmap_file_async_one(data["beatmap"]["id"], Temp=True)

        ppresult = await calculate_pp_if_all_stable(
            data["beatmap"]["id"], data["mods"], data["accuracy"] * 100, data["max_combo"],data["statistics"], Temp=True)

    data['mods'] = [m for m in data['mods'] if m["acronym"] != "CL"]

    result = await formatRctpp2New(data,ppresult)

    return result

