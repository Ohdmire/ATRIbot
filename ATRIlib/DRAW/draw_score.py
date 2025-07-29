from pathlib import Path
from lxml import etree
import datetime
import subprocess
from copy import deepcopy
from ATRIlib.TOOLS.CommonTools import calc_diff_color
from ATRIlib.TOOLS import Download
import os
from io import BytesIO
from ATRIlib.Config import path_config
from ATRIlib.TOOLS.CommonTools import get_relative_path

pr_template_file_path = path_config.pr_template_file_path

garde_path_forsvg = get_relative_path(path_config.garde_path,3)
mods_path_forsvg = get_relative_path(path_config.mods_path,3)
rank_path_forsvg = get_relative_path(path_config.rank_path,3)
logo_path_forsvg = get_relative_path(path_config.logo_path,3)
avatar_path_forsvg = get_relative_path(path_config.avatar_path,3)
cover_path_forsvg = get_relative_path(path_config.cover_path,3)

avatar_path = path_config.avatar_path
cover_path = path_config.cover_path
score_result_path = path_config.score_result_path

with open(pr_template_file_path, 'rb') as f:
    svg_data = f.read()
    parser = etree.XMLParser()
    score_result_svg_tree = etree.fromstring(svg_data, parser)


async def draw_result_screen(data, ppresult):

    start_time = datetime.datetime.now()

    svg_tree = deepcopy(score_result_svg_tree)

    logo_ele = svg_tree.xpath(
        '//*[@id="$logo"]')[0]
    logo_ele.tag = 'image'
    logo_ele.set('xlink', f'{logo_path_forsvg}/quaver.png')

    combo_ele = svg_tree.xpath(
        '//*[@id="$combo"]')[0]
    combo_ele_child = combo_ele.getchildren()[0]
    combo_ele.set('text-anchor', 'middle')
    combo_ele_child.set('x', '310')
    combo_ele_child.text = f'{data["max_combo"]}x/{ppresult["maxcombo"]}x'

    accuracy_ele = svg_tree.xpath(
        '//*[@id="$accuracy"]')[0]
    accuracy_ele_child = accuracy_ele.getchildren()[0]
    accuracy_ele.set('text-anchor', 'middle')
    accuracy_ele_child.set('x', '747')
    accuracy_ele_child.text = f'{data["accuracy"]*100:.2f}%'

    pp_ele = svg_tree.xpath(
        '//*[@id="$performance"]')[0]
    pp_ele_child = pp_ele.getchildren()[0]
    pp_ele.set('text-anchor', 'middle')
    pp_ele_child.set('x', '1620')

    if data["pp"] is None:
        pp_ele_child.text = f'{ppresult["pp"]:.2f}pp'
        pp_ele.set('fill', '#FFFFFF')
    else:
        pp_ele_child.text = f'{data["pp"]:.2f}pp'
        pp_ele.set('fill', '#FBB03B')

    if data['max_combo'] == ppresult['maxcombo'] and data['pp'] is not None:
        fcpp = data['pp']
    else:
        fcpp = ppresult['fcpp']

    fcpp_ele = svg_tree.xpath(
        '//*[@id="$fcpp"]')[0]
    fcpp_ele_child = fcpp_ele.getchildren()[0]
    fcpp_ele_child.text = f'{fcpp:.0f}pp'

    fcppbar_ele = svg_tree.xpath(
        '//*[@id="$fcppbar"]')[0]
    fcppbar_ele.set('width', f'{ppresult["pp"] / ppresult["fcpp"] * 594}')

    fcppcircle_ele = svg_tree.xpath(
        '//*[@id="$fcppcircle"]')[0]
    fcppcircle_ele.set(
        'transform', f'translate({(ppresult["pp"] / ppresult["fcpp"]) * (1669-1075)})')

    fcpppercent_ele = svg_tree.xpath(
        '//*[@id="$fcpppercent"]')[0]
    fcpppercent_ele_child = fcpppercent_ele.getchildren()[0]
    fcpppercent_ele_child.text = f'{ppresult["pp"]/ppresult["fcpp"]*100:.0f}% / FC'

    fc95_ele = svg_tree.xpath(
        '//*[@id="$95fc"]')[0]
    fc95_ele_child = fc95_ele.getchildren()[0]
    fc95_ele_child.text = f'{ppresult["95fcpp"]:.0f}pp'

    fc96_ele = svg_tree.xpath(
        '//*[@id="$96fc"]')[0]
    fc96_ele_child = fc96_ele.getchildren()[0]
    fc96_ele_child.text = f'{ppresult["96fcpp"]:.0f}pp'

    fc97_ele = svg_tree.xpath(
        '//*[@id="$97fc"]')[0]
    fc97_ele_child = fc97_ele.getchildren()[0]
    fc97_ele_child.text = f'{ppresult["97fcpp"]:.0f}pp'

    fc98_ele = svg_tree.xpath(
        '//*[@id="$98fc"]')[0]
    fc98_ele_child = fc98_ele.getchildren()[0]
    fc98_ele_child.text = f'{ppresult["98fcpp"]:.0f}pp'

    fc99_ele = svg_tree.xpath(
        '//*[@id="$99fc"]')[0]
    fc99_ele_child = fc99_ele.getchildren()[0]
    fc99_ele_child.text = f'{ppresult["99fcpp"]:.0f}pp'

    fc100_ele = svg_tree.xpath(
        '//*[@id="$100fc"]')[0]
    fc100_ele_child = fc100_ele.getchildren()[0]
    fc100_ele_child.text = f'{ppresult["100fcpp"]:.0f}pp'

    aimpp_ele = svg_tree.xpath(
        '//*[@id="$aimpp"]')[0]
    aimpp_ele.set('text-anchor', 'middle')
    aimpp_ele_child = aimpp_ele.getchildren()[0]
    aimpp_ele_child.set('x', '1222')
    aimpp_ele_child.text = f'{ppresult["aimpp"]:.0f}pp/{ppresult["fullaimpp"]:.0f}pp'

    speedpp_ele = svg_tree.xpath(
        '//*[@id="$speedpp"]')[0]
    speedpp_ele.set('text-anchor', 'middle')
    speedpp_ele_child = speedpp_ele.getchildren()[0]
    speedpp_ele_child.set('x', '1404')
    speedpp_ele_child.text = f'{ppresult["speedpp"]:.0f}pp/{ppresult["fullspeedpp"]:.0f}pp'

    accpp_ele = svg_tree.xpath(
        '//*[@id="$accpp"]')[0]
    accpp_ele.set('text-anchor', 'middle')
    accpp_ele_child = accpp_ele.getchildren()[0]
    accpp_ele_child.set('x', '1575')
    accpp_ele_child.text = f'{ppresult["accpp"]:.0f}pp/{ppresult["fullaccpp"]:.0f}pp'

    aimpppercent = svg_tree.xpath(
        '//*[@id="$aimpppercent"]')[0]
    aimpppercent_child = aimpppercent.getchildren()[0]
    try:
        aimpppercent_child.text = f'{ppresult["aimpp"]/ppresult["fullaimpp"]*100:.0f}%'
    except ZeroDivisionError:
        aimpppercent_child.text = 'NaN%'

    speedpppercent = svg_tree.xpath(
        '//*[@id="$speedpppercent"]')[0]
    speedpppercent_child = speedpppercent.getchildren()[0]
    try:
        speedpppercent_child.text = f'{ppresult["speedpp"]/ppresult["fullspeedpp"]*100:.0f}%'
    except ZeroDivisionError:
        speedpppercent_child.text = 'NaN%'

    accpppercent = svg_tree.xpath(
        '//*[@id="$accpppercent"]')[0]
    accpppercent_child = accpppercent.getchildren()[0]
    try:
        accpppercent_child.text = f'{ppresult["accpp"]/ppresult["fullaccpp"]*100:.0f}%'
    except ZeroDivisionError:
        accpppercent_child.text = 'NaN%'

    score_ele = svg_tree.xpath(
        '//*[@id="$score"]')[0]
    score_ele_child = score_ele.getchildren()[0]
    score_ele.set('text-anchor', 'middle')
    score_ele_child.set('x', '1175')
    score_ele_child.text = f'{data["total_score"]:,}'

    great_ele = svg_tree.xpath(
        '//*[@id="$greatnum"]')[0]
    great_ele_child = great_ele.getchildren()[0]
    great_ele.set('text-anchor', 'end')

    great_ele_child.set('x', '932')
    great_ele_child.text = f'{data["statistics"]["great"]}'

    ok_ele = svg_tree.xpath(
        '//*[@id="$oknum"]')[0]
    ok_ele_child = ok_ele.getchildren()[0]
    ok_ele.set('text-anchor', 'end')

    ok_ele_child.set('x', '932')
    ok_ele_child.text = f'{data["statistics"]["ok"]}'

    meh_ele = svg_tree.xpath(
        '//*[@id="$mehnum"]')[0]
    meh_ele_child = meh_ele.getchildren()[0]
    meh_ele.set('text-anchor', 'end')

    meh_ele_child.set('x', '932')
    meh_ele_child.text = f'{data["statistics"]["meh"]}'

    miss_ele = svg_tree.xpath(
        '//*[@id="$missnum"]')[0]
    miss_ele_child = miss_ele.getchildren()[0]
    miss_ele.set('text-anchor', 'end')

    miss_ele_child.set('x', '932')
    miss_ele_child.text = f'{data["statistics"]["miss"]}'

    greatpercent_ele = svg_tree.xpath(
        '//*[@id="$greatpercent"]')[0]
    greatpercent_ele_child = greatpercent_ele.getchildren()[0]
    greatpercent = data["statistics"]["great"] / (data["statistics"]["great"] + data["statistics"]
                                                        ["ok"] + data["statistics"]["meh"] + data["statistics"]["miss"])
    greatpercent_ele_child.text = f'({greatpercent*100:.2f}%)'

    okpercent_ele = svg_tree.xpath(
        '//*[@id="$okpercent"]')[0]
    okpercent_ele_child = okpercent_ele.getchildren()[0]
    okpercent = data["statistics"]["ok"] / (data["statistics"]["great"] + data["statistics"]
                                                    ["ok"] + data["statistics"]["meh"] + data["statistics"]["miss"])
    okpercent_ele_child.text = f'({okpercent*100:.2f}%)'

    mehpercent_ele = svg_tree.xpath(
        '//*[@id="$mehpercent"]')[0]
    mehpercent_ele_child = mehpercent_ele.getchildren()[0]
    mehpercent = data["statistics"]["meh"] / (data["statistics"]["great"] + data["statistics"]
                                                    ["ok"] + data["statistics"]["meh"] + data["statistics"]["miss"])
    mehpercent_ele_child.text = f'({mehpercent*100:.2f}%)'

    misspercent_ele = svg_tree.xpath(
        '//*[@id="$misspercent"]')[0]
    misspercent_ele_child = misspercent_ele.getchildren()[0]
    misspercent = data["statistics"]["miss"] / (data["statistics"]["great"] + data["statistics"]
                                                        ["ok"] + data["statistics"]["meh"] + data["statistics"]["miss"])
    misspercent_ele_child.text = f'({misspercent*100:.2f}%)'

    great_fade_ele = svg_tree.xpath(
        '//*[@id="$great_fade"]')[0]
    great_fade_ele.set(
        'transform', f'translate({(1-greatpercent)*176},0) scale({greatpercent},1)')

    ok_fade_ele = svg_tree.xpath(
        '//*[@id="$ok_fade"]')[0]
    ok_fade_ele.set(
        'transform', f'translate({(1-okpercent)*176},0) scale({okpercent},1)')

    meh_fade_ele = svg_tree.xpath(
        '//*[@id="$meh_fade"]')[0]
    meh_fade_ele.set(
        'transform', f'translate({(1-mehpercent)*176},0) scale({mehpercent},1)')

    miss_fade_ele = svg_tree.xpath(
        '//*[@id="$miss_fade"]')[0]
    miss_fade_ele.set(
        'transform', f'translate({(1-misspercent)*176},0) scale({misspercent},1)')

    bid_ele = svg_tree.xpath(
        '//*[@id="$bid"]')[0]
    bid_ele_child = bid_ele.getchildren()[0]
    bid_ele_child.text = f'{data["beatmap"]["id"]}'

    bpm_ele = svg_tree.xpath(
        '//*[@id="$bpm"]')[0]
    bpm_ele_child = bpm_ele.getchildren()[0]
    bpm_ele_child.text = f'{data["beatmap"]["bpm"]}'

    length_m, length_s = divmod(data["beatmap"]['total_length'], 60)
    length_ele = svg_tree.xpath(
        '//*[@id="$length"]')[0]
    length_ele_child = length_ele.getchildren()[0]
    length_ele_child.text = f'{length_m:.0f}:{length_s:0>2d}'

    ar_ele = svg_tree.xpath(
        '//*[@id="$ar"]')[0]
    ar_ele_child = ar_ele.getchildren()[0]
    ar_ele_child.text = f'{data["beatmap"]["ar"]}'

    od_ele = svg_tree.xpath(
        '//*[@id="$od"]')[0]
    od_ele_child = od_ele.getchildren()[0]
    od_ele_child.text = f'{data["beatmap"]["accuracy"]}'

    cs_ele = svg_tree.xpath(
        '//*[@id="$cs"]')[0]
    cs_ele_child = cs_ele.getchildren()[0]
    cs_ele_child.text = f'{data["beatmap"]["cs"]}'

    hp_ele = svg_tree.xpath(
        '//*[@id="$hp"]')[0]
    hp_ele_child = hp_ele.getchildren()[0]
    hp_ele_child.text = f'{data["beatmap"]["drain"]}'

    avatar_img = avatar_path / f'{data["user"]["id"]}.jpeg'
    if avatar_img.exists() is True:
        pass
    else:
        await Download.download_avatar_async([data["user"]["avatar_url"]], [data["user"]["id"]])

    avatar = svg_tree.xpath(
        '//*[@id="$avatar"]')[0]
    avatar.tag = 'image'
    # avatar.set('xlink', data['user']['avatar_url'])
    avatar.set(
        'xlink', f'{avatar_path_forsvg}/{data["user"]["id"]}.jpeg')

    grade = svg_tree.xpath(
        '//*[@id="$grade"]')[0]
    grade.tag = 'image'
    grade.set('xlink', f'{garde_path_forsvg}/{data["rank"]}.png')

    raw_mods_list = []

    for i in data["mods"]:
        raw_mods_list.append(i["acronym"])

    reverse_modslist = raw_mods_list
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
    # rankstatus = svg_tree.xpath(
    #     '//*[@id="$rankstatus"]')[0]
    # rankstatus.tag = 'image'
    # rankstatus.set(
    #     'xlink', f'{rank_path}/{data["beatmap"]["ranked"]}.svg')

    rankstatus = svg_tree.xpath(
        f'//*[@id="RankingStatus/{data["beatmap"]["ranked"]}"]')[0]
    rankstatus.set('opacity', '1')

    cover_img = cover_path / f'{data["beatmapset"]["id"]}.jpg'
    if cover_img.exists() is True:
        pass
    else:
        await Download.download_cover(f'https://assets.ppy.sh/beatmaps/{data["beatmapset"]["id"]}/covers/raw.jpg', data["beatmapset"]["id"])

    beatmap_cover = svg_tree.xpath(
        '//*[@id="$beatmap_cover"]')[0]
    beatmap_cover.tag = 'image'
    # coverurl = data['user']['avatar_url']
    beatmap_cover.set(
        'xlink', f'{cover_path_forsvg}/{data["beatmapset"]["id"]}.jpg')
    beatmap_cover.set('preserveAspectRatio', 'xMidYMin slice')
    beatmap_cover.set('height', '560')
    beatmap_cover.set('y', '-300')

    songname_ele = svg_tree.xpath(
        '//*[@id="$songname"]')[0]
    songname_ele_child = songname_ele.getchildren()[0]
    songname_ele_child.text = data['beatmapset']['title_unicode']

    color = calc_diff_color(ppresult["difficulty"])

    diffname_ele = svg_tree.xpath(
        '//*[@id="$diffname"]')[0]
    diffname_ele.set('fill', f'#{color}')

    diffname_ele_child = diffname_ele.getchildren()[0]
    diffname_ele_child.text = f'{data["beatmap"]["version"]}({ppresult["difficulty"]:.2f}*)'

    mappername_ele = svg_tree.xpath(
        '//*[@id="$mappername"]')[0]
    mappername_ele_child = mappername_ele.getchildren()[0]
    mappername_ele_child.text = data['beatmapset']['creator']

    playername_ele = svg_tree.xpath(
        '//*[@id="$playername"]')[0]
    playername_ele_child = playername_ele.getchildren()[0]
    playername_ele_child.text = data['user']['username']

    datedplaytime = datetime.datetime.strptime(
        data['ended_at'], '%Y-%m-%dT%H:%M:%SZ'
    )
    datedplaytime = datedplaytime + datetime.timedelta(hours=8)  # 时区转换

    playtime = datedplaytime.strftime('%Y/%m/%d %H:%M:%S %p')

    playtime_ele = svg_tree.xpath(
        '//*[@id="$playtime"]')[0]
    playtime_ele_child = playtime_ele.getchildren()[0]
    playtime_ele_child.text = playtime
    
    endtime = datetime.datetime.now()

    totaltime = endtime - start_time

    print(totaltime)

    # 保存修改后的SVG文件
    with open(f'{score_result_path}/{data["user"]["username"]}-pr.svg', 'wb') as f:
        content = etree.tostring(svg_tree, pretty_print=True).replace(
            b'xlink="', b'xlink:href="')
        content = content.replace(b'xmlns:xlink:href', b'xmlns:xlink')
        f.write(content)

    # cairosvg.svg2png(url='frame.svg', write_to='frame.png',
    #                  unsafe=True)

    subprocess.run(['inkscape', f'{score_result_path}/{data["user"]["username"]}-pr.svg',
                    '-o', f'{score_result_path}/{data["user"]["username"]}-pr.png'])

    with open(f'{score_result_path}/{data["user"]["username"]}-pr.png', 'rb') as f:
        img_bytes = BytesIO(f.read())
        # 删除文件
        os.remove(f'{score_result_path}/{data["user"]["username"]}-pr.png')
        os.remove(f'{score_result_path}/{data["user"]["username"]}-pr.svg')

        img_bytes.seek(0)
        return img_bytes



    # with Image(filename='frame1.svg', background=Color("transparent")) as img:
    #     img.format = 'png'
    #     # img.compression_quality = 10
    #     img.save(filename='frame.png')