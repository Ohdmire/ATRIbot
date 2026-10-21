from io import BytesIO

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.ticker import ScalarFormatter

mpl.rcParams["font.sans-serif"] = ["Noto Sans CJK JP"]
mpl.rcParams["axes.unicode_minus"] = False  # 设置正常显示符号


def draw_grouppp(players, user_id, median_pp):

    # 与文字版保持一致的排序：PP降序，PP相同时按user_id升序
    players = sorted(players, key=lambda player: (-player["pp"], player["user_id"]))
    total = len(players)

    pps = [player["pp"] for player in players]

    user_rank = next(
        index + 1
        for index, player in enumerate(players)
        if player["user_id"] == user_id
    )
    user_pp = players[user_rank - 1]["pp"]
    username = players[user_rank - 1]["username"]

    min_pp, max_pp = min(pps), max(pps)
    pp_span = max(max_pp - min_pp, max(max_pp * 0.02, 1))

    fig, ax = plt.subplots(figsize=(14, 8), dpi=120)
    fig.patch.set_facecolor("white")

    # PP分布密度曲线
    if total >= 2 and max_pp > min_pp:
        sns.kdeplot(
            x=pps,
            ax=ax,
            color="#4C72B0",
            fill=True,
            alpha=0.3,
            linewidth=2.4,
            label=f"PP分布密度 (N={total})",
        )
        ax.set_ylim(0, ax.get_ylim()[1] * 1.18)
    else:
        # 人数太少或PP全部相同时无法拟合密度曲线
        ax.axvline(
            min_pp,
            color="#4C72B0",
            linewidth=2.4,
            label=f"群友PP (N={total})",
        )
        ax.set_ylim(0, 1)
        ax.set_yticks([])

    # 中位数
    ax.axvline(
        median_pp,
        color="#2CA02C",
        linestyle="--",
        linewidth=2.2,
        label=f"中位数 {median_pp:.0f}pp",
    )

    # 25%~75%区间
    if total >= 2:
        q25, q75 = np.percentile(pps, [25, 75])
        ax.axvspan(q25, q75, color="gray", alpha=0.08, label="25%~75%")

    # 查询者位置
    ax.axvline(
        user_pp,
        color="#D62728",
        linewidth=2.2,
        label=f"{username} #{user_rank} {user_pp:.0f}pp",
    )

    ax.set_title(f"{username}在本群的PP排名", fontsize=22, fontweight="bold", pad=16)

    ax.set_xlabel("PP", fontsize=14)
    ax.set_ylabel("分布密度", fontsize=14)
    ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))

    ax.set_xlim(min_pp - pp_span * 0.10, max_pp + pp_span * 0.10)

    ax.grid(alpha=0.15, linestyle="--")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=11)

    ax.legend(loc="upper right", fontsize=11, framealpha=0.9)

    fig.tight_layout()

    img_bytes = BytesIO()
    fig.savefig(
        img_bytes, bbox_inches="tight", dpi=150, facecolor=fig.get_facecolor()
    )
    plt.close(fig)

    img_bytes.seek(0)
    return img_bytes
