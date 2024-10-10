import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from io import BytesIO
from matplotlib import font_manager
from ATRIlib.DB.pipeline_daily import pipeline_daily_bp_data
from matplotlib import rcParams

# Set font (keeping this in case you want to use it for other languages in the future)
font_path = 'NotoSerifCJK-Regular.ttc'
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = 'sans-serif'

# 在设置字体之后，添加以下全局字体大小设置
rcParams['font.size'] = 14
rcParams['axes.titlesize'] = 16
rcParams['axes.labelsize'] = 14
rcParams['xtick.labelsize'] = 12
rcParams['ytick.labelsize'] = 12
rcParams['legend.fontsize'] = 12

def plot_distribution(ax, values, title, xlabel, ylabel, allow_negative=False):
    if not values:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
        ax.set_title(title, fontsize=18)
        return

    sns.kdeplot(values, fill=True, ax=ax)
    mean_val = np.mean(values)
    median_val = np.median(values)
    ax.axvline(mean_val, color='r', linestyle='--', label='Mean')
    ax.axvline(median_val, color='g', linestyle='-.', label='Median')
    ax.set_title(title, fontsize=18)
    ax.set_xlabel(xlabel, fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    ax.legend(loc='upper right', fontsize=14)
    if allow_negative:
        ax.set_xlim(min(values) * 1.1, max(values) * 1.1)
    else:
        ax.set_xlim(0, max(values) * 1.1)

def plot_pie_chart(ax, data, title, total_label):
    if not data:
        ax.text(0.5, 0.5, f'No {title} data available', ha='center', va='center', transform=ax.transAxes)
        ax.set_title(f'{title} Distribution', fontsize=18)
        return

    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    top_10 = sorted_data[:10]
    total = sum(data.values())
    top_10_total = sum(player[1] for player in top_10)
    top_10_percentage = (top_10_total / total) * 100
    
    labels = [f"{player[0]}" for player in top_10] + ['Others']
    sizes = [player[1] for player in top_10] + [total - top_10_total]
    colors = plt.cm.Set3(np.linspace(0, 1, 11))
    wedges, _ = ax.pie(sizes, labels=None, colors=colors, startangle=90, wedgeprops=dict(width=0.5))
    ax.axis('equal')

    if title == 'PC':
        legend_labels = [f"{label}: {int(size)} {total_label} ({size/total*100:.1f}%)" for label, size in zip(labels, sizes)]
        centre_text = f"Total {title}: {int(total)}"
    else:
        legend_labels = [f"{label}: {size:.2f} {total_label} ({size/total*100:.1f}%)" for label, size in zip(labels, sizes)]
        centre_text = f"Total {title}: {total:.2f}"

    ax.legend(wedges, legend_labels, title=f"Top 10 {title} Players", 
              loc="center left", bbox_to_anchor=(1, 0.5), 
              fontsize=14, title_fontsize=16)
    
    ax.text(0, 0, centre_text, ha='center', va='center', fontsize=16)

    ax.set_title(f"Top 10 Players: {top_10_percentage:.2f}% of Total {title}", fontsize=18)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

def draw_daily(data, data_other):
    # 处理数据
    pp_data = {player['username']: max(player['pp_array']) for player in data if player['pp_array']}
    pc_data = {player['username']: int(player['play_count_change']) for player in data_other if player['play_count_change'] is not None}
    pt_data = {player['username']: player['play_time_change_hours'] for player in data_other if player['play_time_change_hours'] is not None}
    th_data = {player['username']: player['total_hits_change_w'] for player in data_other if player['total_hits_change_w'] is not None}
    gr_data = {player['username']: player['global_rank_change'] for player in data_other if player['global_rank_change'] is not None}
    pp_change_data = {player['username']: player['pp_change'] for player in data_other if player['pp_change'] is not None}

    pp_values = list(pp_data.values())
    pc_values = list(pc_data.values())
    pt_values = list(pt_data.values())
    th_values = list(th_data.values())
    gr_values = list(gr_data.values())
    pp_change_values = list(pp_change_data.values())

    fig, axes = plt.subplots(6, 2, figsize=(20, 60))

    # 左半边：密度图
    plot_distribution(axes[0, 0], pp_values, 'PP Value Distribution', 'PP Value', 'Density')
    plot_distribution(axes[1, 0], pc_values, 'Play Count Change Distribution', 'Play Count Change', 'Density')
    plot_distribution(axes[2, 0], pt_values, 'Play Time Change Distribution', 'Play Time Change (hours)', 'Density')
    plot_distribution(axes[3, 0], th_values, 'Total Hits Change Distribution', 'Total Hits Change (x10,000)', 'Density')
    plot_distribution(axes[4, 0], gr_values, 'Global Rank Change Distribution', 'Global Rank Change', 'Density', allow_negative=True)
    plot_distribution(axes[5, 0], pp_change_values, 'PP Change Distribution', 'PP Change', 'Density', allow_negative=True)

    # 右半边：环形图
    plot_pie_chart(axes[0, 1], pp_data, 'PP', 'PP')
    plot_pie_chart(axes[1, 1], pc_data, 'PC', 'PC')
    plot_pie_chart(axes[2, 1], pt_data, 'PT', 'hours')
    plot_pie_chart(axes[3, 1], th_data, 'TH', 'w')

    # 全球排名变化条形图
    if gr_data:
        sorted_players_gr = sorted(gr_data.items(), key=lambda x: -x[1])[:10]
        usernames, rank_changes = zip(*sorted_players_gr)
        
        axes[4, 1].bar(usernames, rank_changes)
        axes[4, 1].set_title('Top 10 Global Rank Improvements', fontsize=18)
        axes[4, 1].set_xlabel('Players', fontsize=16)
        axes[4, 1].set_ylabel('Rank Improvement', fontsize=16)
        axes[4, 1].tick_params(axis='x', rotation=45, labelsize=12)
        axes[4, 1].tick_params(axis='y', labelsize=12)
        
        for i, v in enumerate(rank_changes):
            axes[4, 1].text(i, v, str(v), ha='center', va='bottom', fontsize=12)
    else:
        axes[4, 1].text(0.5, 0.5, 'No global rank change data available', ha='center', va='center', transform=axes[4, 1].transAxes)

    # PP变化条形图
    if pp_change_data:
        sorted_players_pp_change = sorted(pp_change_data.items(), key=lambda x: x[1], reverse=True)[:10]
        usernames_pp_change, pp_changes = zip(*sorted_players_pp_change)

        axes[5, 1].bar(usernames_pp_change, pp_changes)
        axes[5, 1].set_title('Top 10 PP Changes', fontsize=18)
        axes[5, 1].set_xlabel('Players', fontsize=16)
        axes[5, 1].set_ylabel('PP Change', fontsize=16)
        axes[5, 1].tick_params(axis='x', rotation=45, labelsize=12)
        axes[5, 1].tick_params(axis='y', labelsize=12)
        
        for i, v in enumerate(pp_changes):
            axes[5, 1].text(i, v, f"{v:.2f}", ha='center', va='bottom', fontsize=12)

        max_change = max(pp_changes)
        axes[5, 1].set_ylim(0, max_change * 1.1)
    else:
        axes[5, 1].text(0.5, 0.5, 'No PP change data available', ha='center', va='center', transform=axes[5, 1].transAxes)

    plt.tight_layout()

    img_bytes = BytesIO()
    plt.savefig(img_bytes, bbox_inches='tight', dpi=300)
    plt.close()

    img_bytes.seek(0)
    return img_bytes

# 更新示例数据
data = [{'pp_array': [138.423, 140.0], 'id': 14545055, 'username': 'Dragon-Fox'}]
data_other = [{'play_count_change': 100, 'global_rank_change': -1000, 'play_time_change_hours': 1.67, 'total_hits_change_w': 10, 'pp_change': 1.577, 'id': 14545055, 'username': 'Dragon-Fox'}]