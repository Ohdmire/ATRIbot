
from pathlib import Path
from lxml import etree
import matplotlib.pyplot as plt
import datetime
import subprocess
from copy import deepcopy
from .CommonTool import calc_diff_color
from .Download import Downloader


class TDBA:
    def draw(self, bps, times, x_list, y_list, osuname):

        plt.rcParams['font.size'] = 20

        plt.figure(figsize=(20, 15))

        plt.subplot(2, 1, 1)
        plt.bar(times, bps, label=osuname)
        plt.xlabel('Hours')
        plt.ylabel('Weighted PP')
        plt.title('Time based Distribution of BPA (UTC+8)')
        plt.legend(prop={'size': 30}, loc='upper left')
        plt.xticks(times)

        plt.subplot(2, 1, 2)
        plt.scatter(x_list, y_list, label=osuname, s=500,
                    alpha=0.7, marker='.')
        plt.xlabel('Hours')
        plt.ylabel('PP')

        plt.xticks(times)
        plt.savefig(f'./data/tmp/tdba/{osuname}-TDBA.png')
        plt.close()
        return f'{osuname}-TDBA.png'

    def drawvs(self, user1bps, user2bps, times, user1x_list, user1y_list, user2x_list, user2y_list, osuname, vsname):

        plt.rcParams['font.size'] = 20

        plt.figure(figsize=(20, 15))

        plt.subplot(2, 1, 1)
        plt.bar(times, user1bps, label=osuname, alpha=1)
        plt.bar(times, user2bps, label=vsname, alpha=0.75)
        plt.xlabel('Hours')
        plt.ylabel('Weighted PP')
        plt.title('Time based Distribution of BPA (UTC+8)')
        plt.legend(prop={'size': 30}, loc='upper left')
        plt.xticks(times)

        plt.subplot(2, 1, 2)
        plt.scatter(user1x_list, user1y_list, label=osuname, s=500,
                    alpha=0.7, marker='.')
        plt.scatter(user2x_list, user2y_list, label=vsname, s=500,
                    alpha=0.7, marker='.')
        plt.xlabel('Hours')
        plt.ylabel('PP')

        plt.xticks(times)
        plt.savefig(f'./data/tmp/tdbavs/{osuname}-{vsname}-vs.png')
        plt.close()
        return f'{osuname}-{vsname}-vs.png'


class ResultScreen:
    def __init__(self):
        self.file_path = Path('./assets/customPanels/result.svg')
        self.garde_path = Path('../../../assets/grade')
        self.mods_path = Path('../../../assets/mods')
        self.rank_path = Path('../../../assets/RankingStatus')
        self.logo_path = Path('../../../assets/logo')
        self.avatar_true_path = Path('../../../data/avatar')
        self.cover_true_path = Path('../../../data/cover')
        self.result_path = Path('./data/tmp/pr')
        with open(self.file_path, 'rb') as f:
            svg_data = f.read()
            parser = etree.XMLParser()
            self.svg_tree = etree.fromstring(svg_data, parser)

        self.download = Downloader()
        self.avatar_path = Path('./data/avatar')
        self.cover_path = Path('./data/cover')

    async def draw(self, data, ppresult):

        start_time = datetime.datetime.now()

        svg_tree = deepcopy(self.svg_tree)

        logo_ele = svg_tree.xpath(
            '//*[@id="$logo"]')[0]
        logo_ele.tag = 'image'
        logo_ele.set('xlink', f'{self.logo_path}/quaver.png')

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
        score_ele_child.text = f'{data["score"]:,}'

        great_ele = svg_tree.xpath(
            '//*[@id="$greatnum"]')[0]
        great_ele_child = great_ele.getchildren()[0]
        great_ele.set('text-anchor', 'end')

        great_ele_child.set('x', '932')
        great_ele_child.text = f'{data["statistics"]["count_300"]}'

        ok_ele = svg_tree.xpath(
            '//*[@id="$oknum"]')[0]
        ok_ele_child = ok_ele.getchildren()[0]
        ok_ele.set('text-anchor', 'end')

        ok_ele_child.set('x', '932')
        ok_ele_child.text = f'{data["statistics"]["count_100"]}'

        meh_ele = svg_tree.xpath(
            '//*[@id="$mehnum"]')[0]
        meh_ele_child = meh_ele.getchildren()[0]
        meh_ele.set('text-anchor', 'end')

        meh_ele_child.set('x', '932')
        meh_ele_child.text = f'{data["statistics"]["count_50"]}'

        miss_ele = svg_tree.xpath(
            '//*[@id="$missnum"]')[0]
        miss_ele_child = miss_ele.getchildren()[0]
        miss_ele.set('text-anchor', 'end')

        miss_ele_child.set('x', '932')
        miss_ele_child.text = f'{data["statistics"]["count_miss"]}'

        greatpercent_ele = svg_tree.xpath(
            '//*[@id="$greatpercent"]')[0]
        greatpercent_ele_child = greatpercent_ele.getchildren()[0]
        greatpercent = data["statistics"]["count_300"] / (data["statistics"]["count_300"] + data["statistics"]
                                                          ["count_100"] + data["statistics"]["count_50"] + data["statistics"]["count_miss"])
        greatpercent_ele_child.text = f'({greatpercent*100:.2f}%)'

        okpercent_ele = svg_tree.xpath(
            '//*[@id="$okpercent"]')[0]
        okpercent_ele_child = okpercent_ele.getchildren()[0]
        okpercent = data["statistics"]["count_100"] / (data["statistics"]["count_300"] + data["statistics"]
                                                       ["count_100"] + data["statistics"]["count_50"] + data["statistics"]["count_miss"])
        okpercent_ele_child.text = f'({okpercent*100:.2f}%)'

        mehpercent_ele = svg_tree.xpath(
            '//*[@id="$mehpercent"]')[0]
        mehpercent_ele_child = mehpercent_ele.getchildren()[0]
        mehpercent = data["statistics"]["count_50"] / (data["statistics"]["count_300"] + data["statistics"]
                                                       ["count_100"] + data["statistics"]["count_50"] + data["statistics"]["count_miss"])
        mehpercent_ele_child.text = f'({mehpercent*100:.2f}%)'

        misspercent_ele = svg_tree.xpath(
            '//*[@id="$misspercent"]')[0]
        misspercent_ele_child = misspercent_ele.getchildren()[0]
        misspercent = data["statistics"]["count_miss"] / (data["statistics"]["count_300"] + data["statistics"]
                                                          ["count_100"] + data["statistics"]["count_50"] + data["statistics"]["count_miss"])
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

        avatar_img = self.avatar_path / f'{data["user"]["id"]}.jpeg'
        if avatar_img.exists() is True:
            pass
        else:
            await self.download.download_avatar_async([data["user"]["avatar_url"]], [data["user"]["id"]])

        avatar = svg_tree.xpath(
            '//*[@id="$avatar"]')[0]
        avatar.tag = 'image'
        # avatar.set('xlink', data['user']['avatar_url'])
        avatar.set(
            'xlink', f'{self.avatar_true_path}/{data["user"]["id"]}.jpeg')

        grade = svg_tree.xpath(
            '//*[@id="$grade"]')[0]
        grade.tag = 'image'
        grade.set('xlink', f'{self.garde_path}/{data["rank"]}.png')

        reverse_modslist = data["mods"]
        reverse_modslist.reverse()
        mod_ele = svg_tree.xpath(
            '//*[@id="$mods"]')[0]
        mod_ele_x = int(mod_ele.get('x'))
        isFirstMod = True
        if reverse_modslist == []:
            mod_ele.getparent().remove(mod_ele)
        for i in reverse_modslist:
            if isFirstMod is True:
                mod_ele.tag = 'image'
                mod_ele.set('xlink', f'{self.mods_path}/{i}.svg')
                isFirstMod = False
            else:
                new_mod_ele = deepcopy(mod_ele)
                new_mod_ele.tag = 'image'
                new_mod_ele.set('xlink', f'{self.mods_path}/{i}.svg')
                new_mod_ele.set('x', f'{mod_ele_x-50}')
                mod_ele.getparent().append(new_mod_ele)
        # rankstatus = svg_tree.xpath(
        #     '//*[@id="$rankstatus"]')[0]
        # rankstatus.tag = 'image'
        # rankstatus.set(
        #     'xlink', f'{self.rank_path}/{data["beatmap"]["ranked"]}.svg')

        rankstatus = svg_tree.xpath(
            f'//*[@id="RankingStatus/{data["beatmap"]["ranked"]}"]')[0]
        rankstatus.set('opacity', '1')

        cover_img = self.cover_path / f'{data["beatmapset"]["id"]}.jpg'
        if cover_img.exists() is True:
            pass
        else:
            await self.download.download_cover(f'https://assets.ppy.sh/beatmaps/{data["beatmapset"]["id"]}/covers/raw.jpg', data["beatmapset"]["id"])

        beatmap_cover = svg_tree.xpath(
            '//*[@id="$beatmap_cover"]')[0]
        beatmap_cover.tag = 'image'
        # coverurl = data['user']['avatar_url']
        beatmap_cover.set(
            'xlink', f'{self.cover_true_path}/{data["beatmapset"]["id"]}.jpg')
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
            data['created_at'], '%Y-%m-%dT%H:%M:%SZ'
        )
        datedplaytime = datedplaytime + datetime.timedelta(hours=8)  # 时区转换

        playtime = datedplaytime.strftime('%Y/%m/%d %H:%M:%S %p')

        playtime_ele = svg_tree.xpath(
            '//*[@id="$playtime"]')[0]
        playtime_ele_child = playtime_ele.getchildren()[0]
        playtime_ele_child.text = playtime

        # 保存修改后的SVG文件
        with open(f'{self.result_path}/{data["user"]["username"]}-pr.svg', 'wb') as f:
            content = etree.tostring(svg_tree, pretty_print=True).replace(
                b'xlink="', b'xlink:href="')
            content = content.replace(b'xmlns:xlink:href', b'xmlns:xlink')
            f.write(content)

        # cairosvg.svg2png(url='frame.svg', write_to='frame.png',
        #                  unsafe=True)

        subprocess.run(['inkscape', f'{self.result_path}/{data["user"]["username"]}-pr.svg',
                       '-o', f'{self.result_path}/{data["user"]["username"]}-pr.png'])

        # with Image(filename='frame1.svg', background=Color("transparent")) as img:
        #     img.format = 'png'
        #     # img.compression_quality = 10
        #     img.save(filename='frame.png')

        endtime = datetime.datetime.now()

        totaltime = endtime - start_time

        print(totaltime)

        return f'{data["user"]["username"]}-pr.png'


class BeatmapRankingscreeen:

    def __init__(self):
        self.file_path = Path('./assets/customPanels/ranking.svg')
        self.garde_path = Path('../../../assets/grade')
        self.mods_path = Path('../../../assets/mods')
        self.rank_path = Path('../../../assets/RankingStatus')
        self.logo_path = Path('../../../assets/logo')
        self.avatar_true_path = Path('../../../data/avatar')
        self.cover_true_path = Path('../../../data/cover')
        self.result_path = Path('./data/tmp/brk')
        with open(self.file_path, 'rb') as f:
            svg_data = f.read()
            parser = etree.XMLParser()
            self.svg_tree = etree.fromstring(svg_data, parser)

        self.download = Downloader()
        self.avatar_path = Path('./data/avatar')
        self.cover_path = Path('./data/cover')

    async def draw(self, player, other_players, beatmap_info):

        start_time = datetime.datetime.now()

        svg_tree = deepcopy(self.svg_tree)

        logo_ele = svg_tree.xpath(
            '//*[@id="$logo"]')[0]
        logo_ele.tag = 'image'
        logo_ele.set('xlink', f'{self.logo_path}/quaver.png')

        rankstatus = svg_tree.xpath(
            f'//*[@id="RankingStatus/{beatmap_info["ranked"]}"]')[0]
        rankstatus.set('opacity', '1')

        cover_img = self.cover_path / f'{beatmap_info["beatmapset"]["id"]}.jpg'
        if cover_img.exists() is True:
            pass
        else:
            await self.download.download_cover(f'https://assets.ppy.sh/beatmaps/{beatmap_info["beatmapset"]["id"]}/covers/raw.jpg', beatmap_info["beatmapset"]["id"])

        beatmap_cover = svg_tree.xpath(
            '//*[@id="$beatmap_cover"]')[0]
        beatmap_cover.tag = 'image'
        # coverurl = data['user']['avatar_url']
        beatmap_cover.set(
            'xlink', f'{self.cover_true_path}/{beatmap_info["beatmapset"]["id"]}.jpg')
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

        try:
            formated_time = datetime.datetime.strptime(
                beatmap_info["beatmapset"]['ranked_date'], "%Y-%m-%dT%H:%M:%SZ")
            formated_time = formated_time + datetime.timedelta(hours=8)  # 东八区
        except:
            formated_time = datetime.datetime.strptime(
                beatmap_info["beatmapset"]['last_update'], "%Y-%m-%dT%H:%M:%SZ")
            formated_time = formated_time + datetime.timedelta(hours=8)  # 东八区

        rankedtime_child.text = formated_time.strftime('%Y/%m/%d %H:%M:%S %p')

        # 渲染玩家自己的成绩

        try:

            my_grade = svg_tree.xpath(
                '//*[@id="my_grade"]')[0]

            my_grade_child = my_grade.getchildren()

            for j in my_grade_child:

                if j.attrib['id'] == '$avatar_my':  # 渲染avatar

                    avatar_img = self.avatar_path / \
                        f'{player["user_id"]}.jpeg'
                    if avatar_img.exists() is True:
                        pass
                    else:
                        await self.download.download_avatar_async([player["avatar_url"]], [player["user_id"]])

                    j.tag = 'image'
                    j.set(
                        'xlink', f'{self.avatar_true_path}/{player["user_id"]}.jpeg')

                if j.attrib['id'] == '$index_my':  # 渲染index

                    # 获取自己在第几位
                    for i in other_players:
                        if i['username'] == player['username']:
                            index = other_players.index(i) + 1

                    j.getchildren()[0].text = f'{index}.'

                    index_in = svg_tree.xpath(
                        '//*[@id="$i_in"]')[0]
                    index_in_child = index_in.getchildren()[0]
                    index_in_child.text = f'# {index} / {len(other_players)}'

                if j.attrib['id'] == '$judgementdetails_my':  # 渲染对应的文本咯
                    j.getchildren()[
                        0].text = f'{player["statistics"]["count_300"]}/{player["statistics"]["count_100"]}/{player["statistics"]["count_50"]}/{player["statistics"]["count_miss"]}'

                if j.attrib['id'] == '$daysago_my':  # 渲染daysago

                    formated_time = datetime.datetime.strptime(
                        player['created_at'], "%Y-%m-%dT%H:%M:%SZ")  # 格式化
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
                        0].text = f'{player["username"]}'

                if j.attrib['id'] == '$combo_my':  # 渲染combo
                    j.getchildren()[
                        0].text = f'{player["max_combo"]}x'

                if j.attrib['id'] == '$acc_my':  # 渲染acc
                    j.getchildren()[
                        0].text = f'{player["accuracy"]*100:.2f}%'

                if j.attrib['id'] == '$score_my':  # 渲染score
                    j.getchildren()[
                        0].text = f'Score:{player["score"]:,}'

                if j.attrib['id'] == '$mods_my':  # 渲染mods
                    j.set('text-anchor', 'end')
                    j.set('transform', 'translate(50)')
                    j.getchildren()[
                        0].text = f'{player["mods"]}'

                if j.attrib['id'] == '$grade_pic_my':  # 渲染grade
                    j.tag = 'image'
                    j.set('xlink', f'{self.garde_path}/{player["rank"]}.png')

        except:
            my_grade.set('opacity', '0')
            no_score = svg_tree.xpath(
                '//*[@id="$no_score"]')[0]
            no_score.set('opacity', '1')
        # 提前下载其他玩家的头像

        for i in other_players:
            avatar_id_list = []
            avatar_url_list = []

            img = self.avatar_path / f'{i["user_id"]}.jpeg'

            if img.exists() is True:
                pass
            else:
                avatar_id_list.append(i['user_id'])
                avatar_url_list.append(i['avatar_url'])

        await self.download.download_avatar_async(avatar_url_list, avatar_id_list)

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

                    avatar_img = self.avatar_path / \
                        f'{other_players[i - 1]["user_id"]}.jpeg'
                    if avatar_img.exists() is True:
                        pass
                    else:
                        # await self.download.get_avatar_file(other_players[i - 1]["avatar_url"], other_players[i - 1]["user_id"])
                        await self.download.download_avatar_async([other_players[i - 1]["avatar_url"]], [other_players[i - 1]["user_id"]])

                    j.tag = 'image'
                    j.set(
                        'xlink', f'{self.avatar_true_path}/{other_players[i - 1]["user_id"]}.jpeg')

                if j.attrib['id'] == f'$index_{i}':  # 渲染index
                    j.getchildren()[0].text = f'{i}.'

                if j.attrib['id'] == f'$judgementdetails_{i}':  # 渲染对应的文本咯
                    j.getchildren()[
                        0].text = f'{other_players[i - 1]["statistics"]["count_300"]}/{other_players[i - 1]["statistics"]["count_100"]}/{other_players[i - 1]["statistics"]["count_50"]}/{other_players[i - 1]["statistics"]["count_miss"]}'

                if j.attrib['id'] == f'$daysago_{i}':  # 渲染daysago
                    formated_time = datetime.datetime.strptime(
                        other_players[i - 1]['created_at'], "%Y-%m-%dT%H:%M:%SZ")  # 格式化

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
                        0].text = f'{other_players[i - 1]["username"]}'

                if j.attrib['id'] == f'$combo_{i}':  # 渲染combo
                    j.getchildren()[
                        0].text = f'{other_players[i - 1]["max_combo"]}x'

                if j.attrib['id'] == f'$acc_{i}':  # 渲染acc
                    j.getchildren()[
                        0].text = f'{other_players[i - 1]["accuracy"]*100: .2f}%'

                if j.attrib['id'] == f'$score_{i}':  # 渲染score
                    j.getchildren()[
                        0].text = f'Score:{other_players[i - 1]["score"]:,}'

                if j.attrib['id'] == f'$mods_{i}':  # 渲染mods
                    j.set('text-anchor', 'end')
                    j.set('transform', 'translate(50)')
                    j.getchildren()[0].text = f'{other_players[i - 1]["mods"]}'

                if j.attrib['id'] == f'$grade_pic_{i}':  # 渲染grade
                    j.tag = 'image'
                    j.set(
                        'xlink', f'{self.garde_path}/{other_players[i - 1]["rank"]}.png')
        # 去除掉其他未渲染的
        print(len(other_players))
        for i in range(len(other_players) + 1, 17):
            player_grade = svg_tree.xpath(
                f'//*[@id="player_grade_{i}"]')[0]

            player_grade.set('opacity', '0')

        # 保存修改后的SVG文件
        with open(f'{self.result_path}/{player["user_id"]}-brk.svg', 'wb') as f:
            content = etree.tostring(svg_tree, pretty_print=True).replace(
                b'xlink="', b'xlink:href="')
            content = content.replace(b'xmlns:xlink:href', b'xmlns:xlink')
            f.write(content)

        # cairosvg.svg2png(url='frame.svg', write_to='frame.png',
        #                  unsafe=True)

        subprocess.run(['inkscape', f'{self.result_path}/{player["user_id"]}-brk.svg',
                       '-o', f'{self.result_path}/{player["user_id"]}-brk.png'])

        endtime = datetime.datetime.now()

        totaltime = endtime - start_time

        print(totaltime)

        return f'{player["user_id"]}-brk.png'
