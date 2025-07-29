from pathlib import Path
from lxml import etree
import datetime
import subprocess
from copy import deepcopy

from ATRIlib.TOOLS.CommonTools import calc_diff_color,get_relative_path
from ATRIlib.TOOLS import Download
from ATRIlib.Config import path_config
import os
from io import BytesIO


beatmap_rank_template_file_path = path_config.beatmap_rank_template_file_path

garde_path_forsvg = get_relative_path(path_config.garde_path,3)
mods_path_forsvg = get_relative_path(path_config.mods_path,3)
rank_path_forsvg = get_relative_path(path_config.rank_path,3)
logo_path_forsvg = get_relative_path(path_config.logo_path,3)
avatar_path_forsvg = get_relative_path(path_config.avatar_path,3)
cover_path_forsvg = get_relative_path(path_config.cover_path,3)


avatar_path = path_config.avatar_path
cover_path = path_config.cover_path
beatmap_rank_result_path = path_config.beatmap_rank_result_path

with open(beatmap_rank_template_file_path, 'rb') as f:
    svg_data = f.read()
    parser = etree.XMLParser()
    beatmap_rank_svg_tree = etree.fromstring(svg_data, parser)


async def draw_beatmap_rank_screen(player, other_players, beatmap_info, mods_list,is_old):

    start_time = datetime.datetime.now()

    svg_tree = deepcopy(beatmap_rank_svg_tree)

    logo_ele = svg_tree.xpath(
        '//*[@id="$logo"]')[0]
    logo_ele.tag = 'image'
    logo_ele.set('xlink', f'{logo_path_forsvg}/quaver.png')

    rankstatus = svg_tree.xpath(
        f'//*[@id="RankingStatus/{beatmap_info["ranked"]}"]')[0]
    rankstatus.set('opacity', '1')

    cover_img = cover_path / f'{beatmap_info["beatmapset"]["id"]}.jpg'
    if cover_img.exists() is True:
        pass
    else:
        await Download.download_cover(f'https://assets.ppy.sh/beatmaps/{beatmap_info["beatmapset"]["id"]}/covers/raw.jpg', beatmap_info["beatmapset"]["id"])

    beatmap_cover = svg_tree.xpath(
        '//*[@id="$beatmap_cover"]')[0]
    beatmap_cover.tag = 'image'

    beatmap_cover.set(
        'xlink', f'{cover_path_forsvg}/{beatmap_info["beatmapset"]["id"]}.jpg')
    beatmap_cover.set('preserveAspectRatio', 'xMidYMin slice')
    beatmap_cover.set('height', '560')
    beatmap_cover.set('y', '-300')

    songname_ele = svg_tree.xpath(
        '//*[@id="$songname"]')[0]
    songname_ele_child = songname_ele.getchildren()[0]
    songname_ele_child.text = beatmap_info['beatmapset']['title_unicode']

    color = calc_diff_color(beatmap_info["difficulty_rating"])

    diffname_ele = svg_tree.xpath(
        '//*[@id="$diffname"]')[0]
    diffname_ele.set('fill', f'#{color}')

    diffname_ele_child = diffname_ele.getchildren()[0]
    diffname_ele_child.text = f'{beatmap_info["version"]}({beatmap_info["difficulty_rating"]:.2f}*)'

    mappername_ele = svg_tree.xpath(
        '//*[@id="$mappername"]')[0]
    mappername_ele_child = mappername_ele.getchildren()[0]
    mappername_ele_child.text = beatmap_info['beatmapset']['creator']

    bpm_ele = svg_tree.xpath(
        '//*[@id="$bpm"]')[0]
    bpm_ele_child = bpm_ele.getchildren()[0]
    bpm_ele_child.text = f'{beatmap_info["bpm"]}'

    length_m, length_s = divmod(beatmap_info['total_length'], 60)
    length_ele = svg_tree.xpath(
        '//*[@id="$length"]')[0]
    length_ele_child = length_ele.getchildren()[0]
    length_ele_child.text = f'{length_m:.0f}:{length_s:0>2d}'

    ar_ele = svg_tree.xpath(
        '//*[@id="$ar"]')[0]
    ar_ele_child = ar_ele.getchildren()[0]
    ar_ele_child.text = f'{beatmap_info["ar"]}'

    od_ele = svg_tree.xpath(
        '//*[@id="$od"]')[0]
    od_ele_child = od_ele.getchildren()[0]
    od_ele_child.text = f'{beatmap_info["accuracy"]}'

    cs_ele = svg_tree.xpath(
        '//*[@id="$cs"]')[0]
    cs_ele_child = cs_ele.getchildren()[0]
    cs_ele_child.text = f'{beatmap_info["cs"]}'

    hp_ele = svg_tree.xpath(
        '//*[@id="$hp"]')[0]
    hp_ele_child = hp_ele.getchildren()[0]
    hp_ele_child.text = f'{beatmap_info["drain"]}'

    bid_ele = svg_tree.xpath(
        '//*[@id="$bid"]')[0]
    bid_ele_child = bid_ele.getchildren()[0]
    bid_ele_child.text = f'{beatmap_info["id"]}'

    rankedtime = svg_tree.xpath(
        '//*[@id="$rankedtime"]')[0]
    rankedtime_child = rankedtime.getchildren()[0]

    # 转换一下None为[]
    if mods_list is None:
        mods_list = []
    reverse_modslist = mods_list
    reverse_modslist.reverse()
    mod_ele = svg_tree.xpath(
        '//*[@id="$mods"]')[0]
    mod_ele_x = int(mod_ele.get('x'))
    isFirstMod = True
    if reverse_modslist == []:
        mod_ele.getparent().remove(mod_ele)
    count = 1
    for i in reverse_modslist:
        if isFirstMod is True:
            mod_ele.tag = 'image'
            mod_ele.set('xlink', f'{mods_path_forsvg}/{i}.svg')
            isFirstMod = False
        else:
            new_mod_ele = deepcopy(mod_ele)
            new_mod_ele.tag = 'image'
            new_mod_ele.set('xlink', f'{mods_path_forsvg}/{i}.svg')
            new_mod_ele.set('x', f'{mod_ele_x-60*count}')
            count += 1
            mod_ele.getparent().append(new_mod_ele)

    try:
        formated_time = datetime.datetime.strptime(
            beatmap_info["beatmapset"]['ranked_date'], "%Y-%m-%dT%H:%M:%SZ")
        formated_time = formated_time + datetime.timedelta(hours=8)  # 东八区
    except:
        formated_time = datetime.datetime.strptime(
            beatmap_info["beatmapset"]['last_updated'], "%Y-%m-%dT%H:%M:%SZ")
        formated_time = formated_time + datetime.timedelta(hours=8)  # 东八区

    rankedtime_child.text = formated_time.strftime('%Y/%m/%d %H:%M:%S %p')

    # 渲染玩家自己的成绩

    try:

        my_grade = svg_tree.xpath(
            '//*[@id="my_grade"]')[0]

        my_grade_child = my_grade.getchildren()

        for j in my_grade_child:

            if j.attrib['id'] == '$avatar_my':  # 渲染avatar

                avatar_img = avatar_path / \
                    f'{player["top_score"]["user_id"]}.jpeg'
                if avatar_img.exists() is True:
                    pass
                else:
                    await Download.download_avatar_async([player['user_info']["avatar_url"]], [player["top_score"]["user_id"]])

                j.tag = 'image'
                j.set(
                    'xlink', f'{avatar_path_forsvg}/{player["top_score"]["user_id"]}.jpeg')

            if j.attrib['id'] == '$index_my':  # 渲染index

                # 获取自己在第几位
                for i in other_players:
                    if i["user_info"]['username'] == player["user_info"]['username']:
                        index = other_players.index(i) + 1

                j.getchildren()[0].text = f'{index}.'

                index_in = svg_tree.xpath(
                    '//*[@id="$i_in"]')[0]
                index_in_child = index_in.getchildren()[0]
                index_in_child.text = f'# {index} / {len(other_players)}'

            if j.attrib['id'] == '$backgroud_color_my':
                if player["top_score"]["legacy_total_score"] == 0:
                    for node in j.getchildren():
                        if "fill" in node.attrib and "linear" in node.attrib["fill"]:
                            url_value = node.attrib["fill"]
                            id_value = url_value[5:-1]  # 提取 paint18_linear_0_1
                            print(id_value)
                            target_element = svg_tree.xpath(f'//*[@id="{id_value}"]')[0]
                            if target_element is not None:
                                new_color = "#02D0FF"  # 新的颜色值
                                for stop_element in target_element.getchildren():
                                    stop_element.attrib["stop-color"] = new_color

            if j.attrib['id'] == '$judgementdetails_my':  # 渲染对应的文本咯
                j.getchildren()[
                    0].text = f'{player["top_score"]["statistics"]["great"]}/{player["top_score"]["statistics"]["ok"]}/{player["top_score"]["statistics"]["meh"]}/{player["top_score"]["statistics"]["miss"]}'

            if j.attrib['id'] == '$daysago_my':  # 渲染daysago

                formated_time = datetime.datetime.strptime(
                    player["top_score"]['ended_at'], "%Y-%m-%dT%H:%M:%SZ")  # 格式化
                formated_time = formated_time + \
                    datetime.timedelta(hours=8)  # 时区转换
                now = datetime.datetime.now()

                delta = now - formated_time

                delta_years = delta.days // 365

                delta_months = (delta.days % 365) // 30

                delta_days = delta.days

                delta_hours = delta.seconds // 3600

                delta_minutes = (delta.seconds % 3600) // 60

                delta_seconds = delta.seconds

                if delta_years >= 1:
                    j.getchildren()[
                        0].text = f'{delta_years} years ago'
                elif delta_months >= 1:
                    j.getchildren()[
                        0].text = f'{delta_months} months ago'
                elif delta_days >= 1:
                    j.getchildren()[
                        0].text = f'{delta_days} days ago'
                elif delta_hours >= 1:
                    j.getchildren()[
                        0].text = f'{delta_hours} hours ago'
                elif delta_minutes >= 1:
                    j.getchildren()[
                        0].text = f'{delta_minutes} minutes ago'
                else:
                    j.getchildren()[
                        0].text = f'{delta_seconds} seconds ago'

            if j.attrib['id'] == '$playername_my':  # 渲染playername
                j.getchildren()[
                    0].text = f'{player["user_info"]["username"]}'

            if j.attrib['id'] == '$combo_my':  # 渲染combo
                j.getchildren()[
                    0].text = f'{player["top_score"]["max_combo"]}x'

            if j.attrib['id'] == '$acc_my':  # 渲染acc
                j.getchildren()[
                    0].text = f'{player["top_score"]["accuracy"]*100:.2f}%'

            if j.attrib['id'] == '$score_my' and is_old==False:  # 渲染score
                j.getchildren()[
                    0].text = f'Score:{player["top_score"]["total_score"]:,}'

            if j.attrib['id'] == '$score_my' and is_old==True:  # 渲染score
                j.getchildren()[
                    0].text = f'Score:{player["top_score"]["legacy_total_score"]:,}'

            if j.attrib['id'] == '$mods_my':  # 渲染mods
                j.set('text-anchor', 'end')
                j.set('transform', 'translate(50)')
                modstext = ""
                for mod in player["top_score"]["mods"]:
                    if is_old:
                        if mod['acronym'] == "CL":
                            continue
                    modstext = modstext + mod['acronym'] + ","
                modstext = modstext[:-1]
                j.getchildren()[
                    0].text = f'{modstext}'

            if j.attrib['id'] == '$grade_pic_my':  # 渲染grade
                j.tag = 'image'
                j.set('xlink', f'{garde_path_forsvg}/{player["top_score"]["rank"]}.png')

    except Exception as e:
        print(f'self ranking error:{e}')
        my_grade.set('opacity', '0')
        no_score = svg_tree.xpath(
            '//*[@id="$no_score"]')[0]
        no_score.set('opacity', '1')

        index_in = svg_tree.xpath(
            '//*[@id="$i_in"]')[0]
        index_in.set('opacity', '0')
    # 提前下载其他玩家的头像
    avatar_id_list = []
    avatar_url_list = []

    for i in other_players:

        img = avatar_path / f'{i["top_score"]["user_id"]}.jpeg'

        if img.exists() is True:
            pass
        else:
            avatar_id_list.append(i["top_score"]['user_id'])
            avatar_url_list.append(i['user_info']['avatar_url'])

    await Download.download_avatar_async(avatar_url_list, avatar_id_list)

    # 渲染其他玩家(<16)
    total_display = len(other_players) + 1
    if total_display > 17:
        total_display = 17
    for i in range(1, total_display):
        player_grade = svg_tree.xpath(
            f'//*[@id="player_grade_{i}"]')[0]

        player_grade_child = player_grade.getchildren()

        for j in player_grade_child:  # 每一个就是一个grade了 渲染好每一个grade

            if j.attrib['id'] == f'$avatar_{i}':  # 渲染avatar

                avatar_img = avatar_path / \
                    f'{other_players[i - 1]["top_score"]["user_id"]}.jpeg'
                if avatar_img.exists() is True:
                    pass
                else:
                    await Download.download_avatar_async([other_players[i - 1]['user_info']["avatar_url"]], [other_players[i - 1]["top_score"]["user_id"]])

                j.tag = 'image'
                j.set(
                    'xlink', f'{avatar_path_forsvg}/{other_players[i - 1]["top_score"]["user_id"]}.jpeg')

            if j.attrib['id'] == f'$index_{i}':  # 渲染index
                j.getchildren()[0].text = f'{i}.'
            if j.attrib['id'] == f'$judgementdetails_{i}':  # 渲染对应的文本咯
                j.getchildren()[
                    0].text = f'{other_players[i - 1]["top_score"]["statistics"]["great"]}/{other_players[i - 1]["top_score"]["statistics"]["ok"]}/{other_players[i - 1]["top_score"]["statistics"]["meh"]}/{other_players[i - 1]["top_score"]["statistics"]["miss"]}'

            if j.attrib['id'] == f'$backgroud_color_{i}':
                if other_players[i - 1]["top_score"]["legacy_total_score"] == 0:
                    for node in j.getchildren():
                        if "fill" in node.attrib and "linear" in node.attrib["fill"]:
                            url_value = node.attrib["fill"]
                            id_value = url_value[5:-1]  # 提取 paint18_linear_0_1
                            target_element = svg_tree.xpath(f'//*[@id="{id_value}"]')[0]
                            if target_element is not None:
                                new_color = "#02D0FF"  # 新的颜色值
                                for stop_element in target_element.getchildren():
                                    stop_element.attrib["stop-color"] = new_color

            if j.attrib['id'] == f'$daysago_{i}':  # 渲染daysago
                formated_time = datetime.datetime.strptime(
                    other_players[i - 1]["top_score"]['ended_at'], "%Y-%m-%dT%H:%M:%SZ")  # 格式化

                formated_time = formated_time + \
                    datetime.timedelta(hours=8)  # 时区转换
                now = datetime.datetime.now()  # 当前时间
                delta = now - formated_time

                delta_years = delta.days // 365

                delta_months = (delta.days % 365) // 30

                delta_days = delta.days

                delta_hours = delta.seconds // 3600

                delta_minutes = (delta.seconds % 3600) // 60

                delta_seconds = delta.seconds

                if delta_years >= 1:
                    j.getchildren()[0].text = f'{delta_years} years ago'

                elif delta_months >= 1:
                    j.getchildren()[0].text = f'{delta_months} months ago'

                elif delta_days >= 1:
                    j.getchildren()[0].text = f'{delta_days} days ago'

                elif delta_hours >= 1:
                    j.getchildren()[0].text = f'{delta_hours} hours ago'

                elif delta_minutes >= 1:
                    j.getchildren()[
                        0].text = f'{delta_minutes} minutes ago'

                else:
                    j.getchildren()[
                        0].text = f'{delta_seconds} seconds ago'

            if j.attrib['id'] == f'$playername_{i}':  # 渲染playername
                j.getchildren()[
                    0].text = f'{other_players[i - 1]["user_info"]["username"]}'

            if j.attrib['id'] == f'$combo_{i}':  # 渲染combo
                j.getchildren()[
                    0].text = f'{other_players[i - 1]["top_score"]["max_combo"]}x'

            if j.attrib['id'] == f'$acc_{i}':  # 渲染acc
                j.getchildren()[
                    0].text = f'{other_players[i - 1]["top_score"]["accuracy"]*100: .2f}%'

            if j.attrib['id'] == f'$score_{i}' and is_old==False:  # 渲染score
                j.getchildren()[
                    0].text = f'Score:{other_players[i - 1]["top_score"]["total_score"]:,}'

            if j.attrib['id'] == f'$score_{i}' and is_old==True:  # 渲染score
                j.getchildren()[
                    0].text = f'Score:{other_players[i - 1]["top_score"]["legacy_total_score"]:,}'

            if j.attrib['id'] == f'$mods_{i}':  # 渲染mods
                j.set('text-anchor', 'end')
                j.set('transform', 'translate(50)')
                modstext = ""
                for mod in other_players[i - 1]["top_score"]["mods"]:
                    if is_old:
                        if mod['acronym'] == "CL":
                            continue
                    modstext = modstext + mod['acronym'] + ","
                modstext = modstext[:-1]
                j.getchildren()[0].text = f'{modstext}'

            if j.attrib['id'] == f'$grade_pic_{i}':  # 渲染grade
                j.tag = 'image'
                j.set(
                    'xlink', f'{garde_path_forsvg}/{other_players[i - 1]["top_score"]["rank"]}.png')
    # 去除掉其他未渲染的
    for i in range(len(other_players) + 1, 17):
        player_grade = svg_tree.xpath(
            f'//*[@id="player_grade_{i}"]')[0]

        player_grade.set('opacity', '0')

    # 保存修改后的SVG文件
    with open(f'{beatmap_rank_result_path}/{player["top_score"]["user_id"]}-brk.svg', 'wb') as f:
        content = etree.tostring(svg_tree, pretty_print=True).replace(
            b'xlink="', b'xlink:href="')
        content = content.replace(b'xmlns:xlink:href', b'xmlns:xlink')
        f.write(content)

    # cairosvg.svg2png(url='frame.svg', write_to='frame.png',
    #                  unsafe=True)

    subprocess.run(['inkscape', f'{beatmap_rank_result_path}/{player["top_score"]["user_id"]}-brk.svg',
                    '-o', f'{beatmap_rank_result_path}/{player["top_score"]["user_id"]}-brk.png'])

    endtime = datetime.datetime.now()

    totaltime = endtime - start_time

    print(totaltime)

    with open(f'{beatmap_rank_result_path}/{player["top_score"]["user_id"]}-brk.png', 'rb') as f:
        img_bytes = BytesIO(f.read())
        # 删除文件
        os.remove(f'{beatmap_rank_result_path}/{player["top_score"]["user_id"]}-brk.png')
        os.remove(f'{beatmap_rank_result_path}/{player["top_score"]["user_id"]}-brk.svg')

        img_bytes.seek(0)
        return img_bytes
