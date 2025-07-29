from pathlib import Path

from lxml import etree
from copy import deepcopy
import datetime
import subprocess
from io import BytesIO
import os
from ATRIlib.TOOLS import Download
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from datetime import timedelta
import seaborn as sns

from ATRIlib.TOOLS.CommonTools import get_relative_path
from ATRIlib.Config import path_config

def warp_text(text,max_chars_per_line):

    words = text.split(' ')
    lines = []
    current_line = ''

    for word in words:
        if len(current_line) + len(word) +1 <= max_chars_per_line:
            current_line += word + ' '
        else:
            lines.append(current_line.strip())
            current_line = word + ' '

    if current_line:
        lines.append(current_line.strip())

    return lines

total_medal_panel_shift = 0
total_medal_pr_panel_shift = 0

class SVGElement:

    def __init__(self, svg_tree, xpath):
        self.element = svg_tree.xpath(xpath)[0]

    def getchildren(self):
        return self.element.getchildren()

    def copy_self(self,count):
        for i in range(count):
            new_ele = deepcopy(self.element)
            new_ele.set('id',f'{self.element.get("id")}_copy_{i}')
            self.element.getparent().append(new_ele)

    def set_text(self, text):
        child = self.element.getchildren()[0]
        child.text = text

    def get_text(self):
        child = self.element.getchildren()[0]
        return child.text

    def set_text_wrap(self,text,max_chars_per_line):
        lines = warp_text(text,max_chars_per_line)
        line_height = 22
        child = self.element.getchildren()[0]
        child.text = ''
        for i,line in enumerate(lines):
            if i == 0:
                tspan = etree.Element('tspan',{"x":child.get('x')})
            else:
                tspan = etree.Element('tspan',{"x":child.get('x'),"dy":f'{str(line_height)}'})
                global total_medal_panel_shift
                total_medal_panel_shift += line_height
            tspan.text = line
            child.append(tspan)

    def get_x(self):
        return self.element.get('x')

    def shift_text_y(self):
        child = self.element.getchildren()[0]
        child.set('y',f'{float(child.get("y")) + total_medal_panel_shift}')

    def shift_y(self):
        self.element.set('y',f'{float(self.element.get("y")) + total_medal_panel_shift}')

    def group_translate_y(self):
        self.element.set('transform',f'translate(0,{total_medal_panel_shift})')

    def expand_y(self):
        self.element.set('height',f'{float(self.element.get("height")) + total_medal_panel_shift}')

    def tag(self, tag):
        self.element.tag = tag

    def set(self, key, value):
        self.element.set(key, value)

    def hide(self):
        self.element.set('display', 'none')

    def show(self):
        self.element.set('display', 'block')

    def set_text_italic(self):
        child = self.element.getchildren()[0]
        child.set('font-style', 'italic')

    def remove(self):
        self.element.getparent().remove(self.element)



medal_template_file_path = path_config.medal_template_file_path
medal_result_path = path_config.medal_result_path

medal_path_forsvg = get_relative_path(path_config.medal_path,3)
avatar_path_forsvg = get_relative_path(path_config.avatar_path,3)

avatar_path = path_config.avatar_path

medal_pr_template_file_path = path_config.medal_pr_template_file_path
medal_pr_result_path = path_config.medal_pr_result_path

with open(medal_template_file_path, 'rb') as f:
    svg_data = f.read()
    parser = etree.XMLParser()
    medal_svg_tree = etree.fromstring(svg_data, parser)

with open(medal_pr_template_file_path, 'rb') as f:
    svg_data = f.read()
    parser = etree.XMLParser()
    medal_pr_svg_tree = etree.fromstring(svg_data, parser)

def convert_quarter_to_season(quarter):
    if quarter == 1:
        return 'Spring'
    if quarter == 2:
        return 'Summer'
    if quarter == 3:
        return 'Fall'
    if quarter == 4:
        return 'Winter'

def draw_medal(medalstruct):
    global total_medal_panel_shift
    svg_tree = deepcopy(medal_svg_tree)

    # 初始化 先隐藏所有的重叠元素
    # stable_only_ele = SVGElement(svg_tree, '//*[@id="$stable_only"]')
    # stable_only_ele.hide()

    fruits_only_ele = SVGElement(svg_tree, '//*[@id="$fruits_only"]')
    fruits_only_ele.hide()

    standard_only_ele = SVGElement(svg_tree, '//*[@id="$standard_only"]')
    standard_only_ele.hide()

    mania_only_ele = SVGElement(svg_tree, '//*[@id="$mania_only"]')
    mania_only_ele.hide()

    taiko_only_ele = SVGElement(svg_tree, '//*[@id="$taiko_only"]')
    taiko_only_ele.hide()



    medal_pic = SVGElement(svg_tree, '//*[@id="$medal_pic"]')
    medal_pic.tag('image')
    medal_pic.set('xlink',f'{medal_path_forsvg}/{medalstruct["medalid"]}.png')

    #Part1

    name_ele = SVGElement(svg_tree, '//*[@id="$name"]')
    name_ele.set_text(medalstruct['name'])

    description_ele = SVGElement(svg_tree, '//*[@id="$description"]')
    description_ele.set_text_wrap(medalstruct['description'],35)

    instructions_ele = SVGElement(svg_tree, '//*[@id="$instructions"]')
    if medalstruct['instructions'] is None:
        instructions_ele.hide()
    else:
        instructions_ele.set_text_italic()
        instructions_ele.shift_text_y()
        instructions_ele.set_text_wrap(medalstruct['instructions'],35)

    mods_ele = SVGElement(svg_tree, '//*[@id="$mods"]')
    print(mods_ele.get_text())
    if mods_ele.get_text() == "":
        mods_ele.hide()
    else:
        mods_ele.shift_text_y()
        mods_ele.set_text(medalstruct['solution_data']['mods'])


    panel_part1_ele = SVGElement(svg_tree, '//*[@id="$panel_part1"]')
    panel_part1_ele.expand_y()

    if medalstruct['restriction'] == 'osu':
        standard_only_ele.show()
    if medalstruct['restriction'] == 'taiko':
        taiko_only_ele.show()
    if medalstruct['restriction'] == 'fruits':
        fruits_only_ele.show()
    if medalstruct['restriction'] == 'mania':
        mania_only_ele.show()

    group_restriction_ele = SVGElement(svg_tree, '//*[@id="$group_restriction"]')
    group_restriction_ele.group_translate_y()

    # Part2

    condition_text_ele = SVGElement(svg_tree, '//*[@id="$condition_text"]')
    condition_text_ele.shift_text_y()

    # 先隐藏
    solution_italic_ele = SVGElement(svg_tree, '//*[@id="$solution_italic"]')
    solution_italic_ele.hide()

    solution_ele = SVGElement(svg_tree, '//*[@id="$solution"]')
    solution_ele.shift_text_y()
    solution_ele.set_text_wrap(medalstruct['solution_data']['solution'],50)
    if 'solution_italic' in medalstruct['solution_data']:
        solution_italic_ele.show()
        solution_italic_ele.set_text_italic()
        solution_italic_ele.shift_text_y()
        solution_italic_ele.set_text_wrap(medalstruct['solution_data']['solution_italic'],50)



    grouping_ele = SVGElement(svg_tree, '//*[@id="$grouping"]')
    grouping_ele.shift_text_y()
    grouping_ele.set_text_wrap(medalstruct['grouping'],35)

    rarity_text_ele = SVGElement(svg_tree, '//*[@id="$rarity_text"]')
    rarity_text_ele.shift_text_y()

    rarity_ele = SVGElement(svg_tree, '//*[@id="$rarity"]')
    rarity_ele.shift_text_y()
    rarity_ele.set_text(f'{medalstruct["rarity_data"]["frequency"]:.2f}%')

    # panel_total_shift
    root = svg_tree
    root.set("height",f'{float(root.get("height")) + total_medal_panel_shift}')
    viewbox_value = root.get("viewBox").split(' ')
    root.set("viewBox",f'{viewbox_value[0]} {float(viewbox_value[1])} {viewbox_value[2]} {float(viewbox_value[3]) + total_medal_panel_shift}')
    clip = svg_tree.xpath('//*[@id="clip0_0_1"]')[0]
    clip.getparent().remove(clip)

    panel_part2_ele = SVGElement(svg_tree, '//*[@id="$panel_part2"]')
    panel_part2_ele.shift_y()

    backgroud_ele = SVGElement(svg_tree, '//*[@id="$backgroud"]')
    backgroud_ele.expand_y()


    # 保存修改后的SVG文件

    total_medal_panel_shift = 0
    with open(f'{medal_result_path}/{medalstruct["medalid"]}.svg', 'wb') as f:
        content = etree.tostring(svg_tree, pretty_print=True).replace(
            b'xlink="', b'xlink:href="')
        content = content.replace(b'xmlns:xlink:href', b'xmlns:xlink')
        f.write(content)

    subprocess.run(['inkscape', f'{medal_result_path}/{medalstruct["medalid"]}.svg',
                    '-o', f'{medal_result_path}/{medalstruct["medalid"]}.png'])


    with open(f'{medal_result_path}/{medalstruct["medalid"]}.png', 'rb') as f:
        img_bytes = BytesIO(f.read())
        # 删除文件
        # os.remove(f'{beatmap_rank_result_path}/{player["top_score"]["user_id"]}-brk.png')
        # os.remove(f'{beatmap_rank_result_path}/{player["top_score"]["user_id"]}-brk.svg')

        img_bytes.seek(0)
        return img_bytes

async def draw_medal_pr(medalprstructlist,userstruct):

    global total_medal_pr_panel_shift

    svg_tree = deepcopy(medal_pr_svg_tree)

    avatar_img = avatar_path / f'{userstruct["id"]}.jpeg'
    if avatar_img.exists() is True:
        pass
    else:
        await Download.download_avatar_async([userstruct["avatar_url"]], [userstruct["id"]])

    avatar_ele = SVGElement(svg_tree, '//*[@id="$avatar"]')

    avatar_ele.tag('image')
    avatar_ele.set('xlink',f'./{avatar_path_forsvg}/{userstruct["id"]}.jpeg')

    username_ele = SVGElement(svg_tree, '//*[@id="$username"]')
    username_ele.set_text(userstruct["username"])

    single_medal_ele = SVGElement(svg_tree, '//*[@id="$single_medal"]')
    single_time_ele = SVGElement(svg_tree, '//*[@id="$time"]')
    single_time_bar_ele = SVGElement(svg_tree, '//*[@id="$time_bar"]')


    # 一次性排版
    total_medal = 0
    total_season = len(medalprstructlist)

    for i in medalprstructlist:
        total_medal += i['count']

    #集体复制
    single_medal_ele.copy_self(total_medal)
    single_time_ele.copy_self(total_season)
    single_time_bar_ele.copy_self(total_season)

    # 定义偏移量和限制110 143
    x_init = 10
    x_offset = 30 + 110
    y_offset = 30 + 143
    max_items_per_row = 5

    y_offset_for_season = 100

    medalid_list = [] # 最后依靠这个list来排版
    time_list = [] # 最后依靠这个list来排版


    count_ele_index = 0
    count_time_ele_index = 0


    for medalstrcut in medalprstructlist:
        # 这是一个season

        # 每个season里面有多少个medal
        season_medal_count = medalstrcut['count']
        achievement_ids = medalstrcut['achievement_ids']
        medalid_list.extend(achievement_ids)

        time_list.append(f'{medalstrcut["year"]}-{convert_quarter_to_season(medalstrcut["quarter"])}')

        count_part_a_line = 0
        count_part_season_index = 0

        single_shift_for_one_season = 0
        for i in range(season_medal_count):

            medal_ele = SVGElement(svg_tree, f'//*[@id="$single_medal_copy_{count_ele_index}"]')

            if count_part_a_line == max_items_per_row: # 一行满了
                count_part_a_line = 0
                total_medal_pr_panel_shift += y_offset
                single_shift_for_one_season += y_offset
            medal_ele.set('transform', f'translate({x_offset*count_part_a_line},{total_medal_pr_panel_shift})')
            count_part_season_index += 1
            count_part_a_line += 1
            count_ele_index += 1 # medalid位移

        # 每个season渲染完成后 位移一下time相关的
        count_time_ele_index += 1  # time位移
        # 每一个season渲染完成后 位移一下time相关的
        total_medal_pr_panel_shift += y_offset_for_season + y_offset
        single_shift_for_one_season += y_offset_for_season + y_offset

        # time_ele的位移渲染完medal才知道第二个time_ele
        time_ele = SVGElement(svg_tree, f'//*[@id="$time_copy_{count_time_ele_index - 1}"]')
        time_ele.set('transform', f'translate({x_init},{total_medal_pr_panel_shift - single_shift_for_one_season})')

        time_bar_ele = SVGElement(svg_tree, f'//*[@id="$time_bar_copy_{count_time_ele_index - 1}"]')
        time_bar_ele.set('transform', f'translate({x_init},{total_medal_pr_panel_shift - single_shift_for_one_season})')


    # 整体渲染完成
    total_medal_pr_panel_shift = total_medal_pr_panel_shift - y_offset_for_season - y_offset

    for i in range(total_medal):
        medal_ele = SVGElement(svg_tree, f'//*[@id="$single_medal_copy_{i}"]')
        medal_ele_pic = medal_ele.element.getchildren()[0]
        medal_ele_pic.tag = 'image'
        medal_ele_pic.set('xlink',f'{medal_path_forsvg}/{medalid_list[i]}.png')

        medal_ele_id = medal_ele.element.getchildren()[1].getchildren()[0]
        medal_ele_id.text = f'{medalid_list[i]}'

    for i in range(total_season):
        time_ele = SVGElement(svg_tree, f'//*[@id="$time_copy_{i}"]')
        time_ele_child = time_ele.getchildren()[0]
        time_ele_child.text = f'{time_list[i]}'

    # 删除一开始被复制的元素
    single_medal_ele.remove()
    single_time_ele.remove()
    single_time_bar_ele.remove()


    background = svg_tree.xpath('//*[@id="$background"]')[0]
    background.set('height',f'{float(background.get("height")) + total_medal_pr_panel_shift}')

    # panel_total_shift
    root = svg_tree
    root.set("height", f'{float(root.get("height")) + total_medal_pr_panel_shift}')
    viewbox_value = root.get("viewBox").split(' ')
    root.set("viewBox",
             f'{viewbox_value[0]} {float(viewbox_value[1])} {viewbox_value[2]} {float(viewbox_value[3]) + total_medal_pr_panel_shift}')
    # clip = svg_tree.xpath('//*[@id="clip0_0_1"]')[0]
    # clip.getparent().remove(clip)


    # 保存修改后的SVG文件

    total_medal_pr_panel_shift = 0
    with open(f'{medal_pr_result_path}/{userstruct["id"]}.svg', 'wb') as f:
        content = etree.tostring(svg_tree, pretty_print=True).replace(
            b'xlink="', b'xlink:href="')
        content = content.replace(b'xmlns:xlink:href', b'xmlns:xlink')
        f.write(content)

    subprocess.run(['inkscape', f'{medal_pr_result_path}/{userstruct["id"]}.svg',
                    '-o', f'{medal_pr_result_path}/{userstruct["id"]}.png'])

    with open(f'{medal_pr_result_path}/{userstruct["id"]}.png', 'rb') as f:
        img_bytes = BytesIO(f.read())
        # 删除文件
        os.remove(f'{medal_pr_result_path}/{userstruct["id"]}.png')
        os.remove(f'{medal_pr_result_path}/{userstruct["id"]}.svg')

        img_bytes.seek(0)
        return img_bytes


def draw_special_medal(specialmedalstruct_pass, specialmedalstruct_fc, username):
    # 创建图形和轴
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # 设置标题
    ax.set_title(f'{username}\'s Special Medal Timeline', fontsize=24)

    # 准备数据
    dates_pass = [datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ") for date in specialmedalstruct_pass.values()]
    dates_fc = [datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ") for date in specialmedalstruct_fc.values()]
    
    y_values_pass = [int(name.split()[0]) for name in specialmedalstruct_pass.keys()]
    y_values_fc = [int(name.split()[0]) for name in specialmedalstruct_fc.keys()]
    
    # 使用折线图替代散点图
    ax.plot(dates_pass, y_values_pass, color='blue', marker='o', linestyle='-', linewidth=2, markersize=8, label='Pass')
    ax.plot(dates_fc, y_values_fc, color='red', marker='o', linestyle='-', linewidth=2, markersize=8, label='FC')
    
    # 设置y轴范围和标签
    ax.set_ylim(0, 11)
    ax.set_yticks(range(1, 11))
    ax.set_ylabel('Star', fontsize=12)
    
    # 设置x轴为日期格式
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    
    # 旋转x轴标签以防止重叠
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    # 为每个点添加标签
    for date, y, name in zip(dates_pass + dates_fc, y_values_pass + y_values_fc, 
                             list(specialmedalstruct_pass.keys()) + list(specialmedalstruct_fc.keys())):
        ax.annotate(name+"*", (date, y), xytext=(5, 5), textcoords='offset points', 
                    fontsize=8, alpha=0.7, rotation=45)
    
    # 添加图例
    ax.legend()
    
    # 添加网格线
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图像到BytesIO对象
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='PNG', dpi=300, bbox_inches='tight')
    img_bytes.seek(0)
    plt.close(fig)
    
    return img_bytes




















