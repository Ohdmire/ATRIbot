
from pathlib import Path
from lxml import etree
import cairosvg
import matplotlib.pyplot as plt
import datetime


class TDBA:
    def draw(self, bps, times, x_list, y_list, osuname):

        plt.rcParams['font.size'] = 20

        plt.figure(figsize=(20, 15))

        plt.subplot(2, 1, 1)
        plt.bar(times, bps, label=osuname)
        plt.xlabel('Hours')
        plt.ylabel('Weighted PP')
        plt.title('Time based Distribution of BPA')
        plt.legend(prop={'size': 30})
        plt.xticks(times)

        plt.subplot(2, 1, 2)
        plt.scatter(x_list, y_list, label=osuname, s=500,
                    alpha=0.7, marker='.')
        plt.xlabel('Hours')
        plt.ylabel('PP')

        plt.xticks(times)
        plt.savefig(f'./data/tmp/{osuname}-TDBA.png')
        plt.close()
        return f'{osuname}-TDBA.png'


class ResultScreen:
    def __init__(self):
        self.file_path = Path('./assets/customPanels/result.svg')

        with open(self.file_path, 'rb') as f:
            svg_data = f.read()
            parser = etree.XMLParser(remove_blank_text=True)
            self.svg_tree = etree.fromstring(svg_data, parser)

    def draw(self, data):

        combo_ele = self.svg_tree.xpath(
            '//*[@id="$combo"]')[0]
        combo_ele_child = combo_ele.getchildren()[0]
        combo_ele.set('text-anchor', 'middle')
        combo_ele_child.set('x', '330')
        combo_ele_child.text = f'{data["max_combo"]}x'

        accuracy_ele = self.svg_tree.xpath(
            '//*[@id="$accuracy"]')[0]
        accuracy_ele_child = accuracy_ele.getchildren()[0]
        accuracy_ele.set('text-anchor', 'middle')
        accuracy_ele_child.set('x', '767')
        accuracy_ele_child.text = f'{data["accuracy"]*100:.2f}%'

        pp_ele = self.svg_tree.xpath(
            '//*[@id="$performance"]')[0]
        pp_ele_child = pp_ele.getchildren()[0]
        pp_ele.set('text-anchor', 'middle')
        pp_ele_child.set('x', '1640')
        pp_ele_child.text = f'{data["pp"]:.2f}pp'

        score_ele = self.svg_tree.xpath(
            '//*[@id="$score"]')[0]
        score_ele_child = score_ele.getchildren()[0]
        score_ele.set('text-anchor', 'middle')
        score_ele_child.set('x', '1195')
        score_ele_child.text = f'{data["score"]}'

        great_ele = self.svg_tree.xpath(
            '//*[@id="$greatnum"]')[0]
        great_ele_child = great_ele.getchildren()[0]
        great_ele.set('text-anchor', 'end')

        great_ele_child.set('x', '932')
        great_ele_child.text = f'{data["statistics"]["count_300"]}'

        ok_ele = self.svg_tree.xpath(
            '//*[@id="$oknum"]')[0]
        ok_ele_child = ok_ele.getchildren()[0]
        ok_ele.set('text-anchor', 'end')

        ok_ele_child.set('x', '932')
        ok_ele_child.text = f'{data["statistics"]["count_100"]}'

        meh_ele = self.svg_tree.xpath(
            '//*[@id="$mehnum"]')[0]
        meh_ele_child = meh_ele.getchildren()[0]
        meh_ele.set('text-anchor', 'end')

        meh_ele_child.set('x', '932')
        meh_ele_child.text = f'{data["statistics"]["count_50"]}'

        miss_ele = self.svg_tree.xpath(
            '//*[@id="$missnum"]')[0]
        miss_ele_child = miss_ele.getchildren()[0]
        miss_ele.set('text-anchor', 'end')

        miss_ele_child.set('x', '932')
        miss_ele_child.text = f'{data["statistics"]["count_miss"]}'

        greatpercent_ele = self.svg_tree.xpath(
            '//*[@id="$greatpercent"]')[0]
        greatpercent_ele_child = greatpercent_ele.getchildren()[0]
        greatpercent = data["statistics"]["count_300"] / (data["statistics"]["count_300"] + data["statistics"]
                                                          ["count_100"] + data["statistics"]["count_50"] + data["statistics"]["count_miss"])
        greatpercent_ele_child.text = f'{greatpercent*100:.2f}%'

        okpercent_ele = self.svg_tree.xpath(
            '//*[@id="$okpercent"]')[0]
        okpercent_ele_child = okpercent_ele.getchildren()[0]
        okpercent = data["statistics"]["count_100"] / (data["statistics"]["count_300"] + data["statistics"]
                                                       ["count_100"] + data["statistics"]["count_50"] + data["statistics"]["count_miss"])
        okpercent_ele_child.text = f'{okpercent*100:.2f}%'

        mehpercent_ele = self.svg_tree.xpath(
            '//*[@id="$mehpercent"]')[0]
        mehpercent_ele_child = mehpercent_ele.getchildren()[0]
        mehpercent = data["statistics"]["count_50"] / (data["statistics"]["count_300"] + data["statistics"]
                                                       ["count_100"] + data["statistics"]["count_50"] + data["statistics"]["count_miss"])
        mehpercent_ele_child.text = f'{mehpercent*100:.2f}%'

        misspercent_ele = self.svg_tree.xpath(
            '//*[@id="$misspercent"]')[0]
        misspercent_ele_child = misspercent_ele.getchildren()[0]
        misspercent = data["statistics"]["count_miss"] / (data["statistics"]["count_300"] + data["statistics"]
                                                          ["count_100"] + data["statistics"]["count_50"] + data["statistics"]["count_miss"])
        misspercent_ele_child.text = f'{misspercent*100:.2f}%'

        great_fade_ele = self.svg_tree.xpath(
            '//*[@id="$great_fade"]')[0]
        great_fade_ele.set('transform', f'translate({(1-greatpercent)*176},0) scale({greatpercent},1)')

        ok_fade_ele = self.svg_tree.xpath(
            '//*[@id="$ok_fade"]')[0]
        ok_fade_ele.set('transform', f'translate({(1-okpercent)*176},0) scale({okpercent},1)')

        meh_fade_ele = self.svg_tree.xpath(
            '//*[@id="$meh_fade"]')[0]
        meh_fade_ele.set('transform', f'translate({(1-mehpercent)*176},0) scale({mehpercent},1)')

        miss_fade_ele = self.svg_tree.xpath(
            '//*[@id="$miss_fade"]')[0]
        miss_fade_ele.set('transform', f'translate({(1-misspercent)*176},0) scale({misspercent},1)')

        bpm_ele = self.svg_tree.xpath(
            '//*[@id="$bpm"]')[0]
        bpm_ele_child = bpm_ele.getchildren()[0]
        bpm_ele_child.text = f'{data["beatmap"]["bpm"]}'

        length_m, length_s = divmod(data["beatmap"]['total_length'], 60)
        length_ele = self.svg_tree.xpath(
            '//*[@id="$length"]')[0]
        length_ele_child = length_ele.getchildren()[0]
        length_ele_child.text = f'{length_m:.0f}:{length_s:0>2d}'

        ar_ele = self.svg_tree.xpath(
            '//*[@id="$ar"]')[0]
        ar_ele_child = ar_ele.getchildren()[0]
        ar_ele_child.text = f'{data["beatmap"]["ar"]}'

        od_ele = self.svg_tree.xpath(
            '//*[@id="$od"]')[0]
        od_ele_child = od_ele.getchildren()[0]
        od_ele_child.text = f'{data["beatmap"]["accuracy"]}'

        cs_ele = self.svg_tree.xpath(
            '//*[@id="$cs"]')[0]
        cs_ele_child = cs_ele.getchildren()[0]
        cs_ele_child.text = f'{data["beatmap"]["cs"]}'

        hp_ele = self.svg_tree.xpath(
            '//*[@id="$hp"]')[0]
        hp_ele_child = hp_ele.getchildren()[0]
        hp_ele_child.text = f'{data["beatmap"]["drain"]}'

        avatar = self.svg_tree.xpath(
            '//*[@id="$avatar"]')[0]
        avatar.tag = 'image'
        avatar.set('href', data['user']['avatar_url'])

        beatmap_cover = self.svg_tree.xpath(
            '//*[@id="$beatmap_cover"]')[0]
        beatmap_cover.tag = 'image'
        coverurl = f'https://assets.ppy.sh/beatmaps/{data["beatmapset"]["id"]}/covers/raw.jpg'
        # coverurl = data['user']['avatar_url']
        beatmap_cover.set('href', coverurl)
        beatmap_cover.set('preserveAspectRatio', 'xMidYMin slice')
        beatmap_cover.set('height', '560')
        beatmap_cover.set('y', '-300')

        songname_ele = self.svg_tree.xpath(
            '//*[@id="$songname"]')[0]
        songname_ele_child = songname_ele.getchildren()[0]
        songname_ele_child.text = data['beatmapset']['title_unicode']

        diffname_ele = self.svg_tree.xpath(
            '//*[@id="$diffname"]')[0]
        diffname_ele_child = diffname_ele.getchildren()[0]
        diffname_ele_child.text = f'{data["beatmap"]["version"]}({data["beatmap"]["difficulty_rating"]}*)'

        mappername_ele = self.svg_tree.xpath(
            '//*[@id="$mappername"]')[0]
        mappername_ele_child = mappername_ele.getchildren()[0]
        mappername_ele_child.text = data['beatmapset']['creator']

        playername_ele = self.svg_tree.xpath(
            '//*[@id="$playername"]')[0]
        playername_ele_child = playername_ele.getchildren()[0]
        playername_ele_child.text = data['user']['username']

        datedplaytime = datetime.datetime.strptime(
            data['created_at'], '%Y-%m-%dT%H:%M:%SZ'
        )
        datedplaytime = datedplaytime + datetime.timedelta(hours=8)  # 时区转换

        playtime = datedplaytime.strftime('%Y/%m/%d %H:%M:%S %p')

        playtime_ele = self.svg_tree.xpath(
            '//*[@id="$playtime"]')[0]
        playtime_ele_child = playtime_ele.getchildren()[0]
        playtime_ele_child.text = playtime

        # 保存修改后的SVG文件
        with open('frame.svg', 'wb') as f:
            f.write(etree.tostring(self.svg_tree, pretty_print=True))

        cairosvg.svg2png(url='frame.svg', write_to='frame.png',
                         unsafe=True)
        # with Image(filename='frame1.svg', background=Color("transparent")) as img:
        #     img.format = 'png'
        #     # img.compression_quality = 10
        #     img.save(filename='frame.png')

        return data
