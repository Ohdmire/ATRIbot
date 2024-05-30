
from pathlib import Path
from lxml import etree
import matplotlib.pyplot as plt
import datetime
import subprocess
from copy import deepcopy
from .CommonTool import calc_diff_color


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
        self.result_path = Path('./data/tmp/pr')

    def draw(self, data, ppresult):

        with open(self.file_path, 'rb') as f:
            svg_data = f.read()
            parser = etree.XMLParser()
            svg_tree = etree.fromstring(svg_data, parser)

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
        aimpppercent_child.text = f'{ppresult["aimpp"]/ppresult["fullaimpp"]*100:.0f}%'

        speedpppercent = svg_tree.xpath(
            '//*[@id="$speedpppercent"]')[0]
        speedpppercent_child = speedpppercent.getchildren()[0]
        speedpppercent_child.text = f'{ppresult["speedpp"]/ppresult["fullspeedpp"]*100:.0f}%'

        accpppercent = svg_tree.xpath(
            '//*[@id="$accpppercent"]')[0]
        accpppercent_child = accpppercent.getchildren()[0]
        accpppercent_child.text = f'{ppresult["accpp"]/ppresult["fullaccpp"]*100:.0f}%'

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

        avatar = svg_tree.xpath(
            '//*[@id="$avatar"]')[0]
        avatar.tag = 'image'
        avatar.set('xlink', data['user']['avatar_url'])

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
        rankstatus = svg_tree.xpath(
            '//*[@id="$rankstatus"]')[0]
        rankstatus.tag = 'image'
        rankstatus.set(
            'xlink', f'{self.rank_path}/{data["beatmap"]["ranked"]}.svg')
        beatmap_cover = svg_tree.xpath(
            '//*[@id="$beatmap_cover"]')[0]
        beatmap_cover.tag = 'image'
        coverurl = f'https://assets.ppy.sh/beatmaps/{data["beatmapset"]["id"]}/covers/raw.jpg'
        # coverurl = data['user']['avatar_url']
        beatmap_cover.set('xlink', coverurl)
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

        return f'{data["user"]["username"]}-pr.png'
