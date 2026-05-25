from io import BytesIO

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

mpl.rcParams["font.sans-serif"] = ["Noto Sans CJK JP"]
mpl.rcParams["axes.unicode_minus"] = False


def draw_replay_similarity_distance(data):
    comparisons = data["comparisons"]
    if not comparisons:
        raise ValueError("没有可绘制的 replay 相似度数据")

    shown = comparisons
    negative_examples = sorted(
        [item for item in comparisons if item["similarity"] < 0],
        key=lambda item: item["similarity"],
    )[:30]
    labeled = []
    labeled_ids = set()
    for item in comparisons[:30] + negative_examples:
        label_id = item["player"]["user_id"]
        if label_id not in labeled_ids:
            labeled.append(item)
            labeled_ids.add(label_id)
    similarities = np.array([item["similarity"] for item in shown], dtype=float)
    xs = np.array([item["x"] for item in shown], dtype=float)
    ys = np.array([item["y"] for item in shown], dtype=float)

    fig, ax = plt.subplots(figsize=(12, 12), dpi=160)
    fig.patch.set_facecolor("#f7f8fb")
    ax.set_facecolor("#ffffff")

    ax.axhline(0, color="#d0d7de", linewidth=1.0, zorder=0)
    ax.axvline(0, color="#d0d7de", linewidth=1.0, zorder=0)
    ax.scatter(
        [0],
        [0],
        s=180,
        c="#111827",
        marker="*",
        zorder=4,
        label=data["base"]["username"],
    )
    scatter = ax.scatter(
        xs,
        ys,
        s=88,
        c=similarities,
        cmap="coolwarm",
        vmin=-100,
        vmax=100,
        edgecolors="#1f2933",
        linewidths=0.7,
        alpha=0.92,
        zorder=3,
    )
    colorbar = fig.colorbar(scatter, ax=ax, fraction=0.046, pad=0.04)
    colorbar.set_label("Cosine similarity (%)", fontsize=11)

    labeled_xs = np.array([item["x"] for item in labeled], dtype=float)
    labeled_ys = np.array([item["y"] for item in labeled], dtype=float)
    labeled_similarities = np.array([item["similarity"] for item in labeled], dtype=float)
    for item, x, y, similarity in zip(labeled, labeled_xs, labeled_ys, labeled_similarities):
        ax.text(
            x,
            y,
            f" {item['player']['username']}\n {similarity:.1f}%",
            va="bottom",
            ha="left",
            fontsize=10,
            color="#1f4e8c" if similarity < 0 else "#26313d",
        )
    ax.text(
        0,
        0,
        f" {data['base']['username']}",
        va="top",
        ha="left",
        fontsize=12,
        color="#111827",
    )

    ax.set_xlabel("Embedding PCA X relative to player", fontsize=12)
    ax.set_ylabel("Embedding PCA Y relative to player", fontsize=12)
    ax.set_title(
        f"{data['base']['username']} 为原点的本群 replay 二维距离图",
        fontsize=18,
        pad=16,
        color="#1f2933",
    )
    # ax.text(
    #     0,
    #     1.015,
    #     f"展示最近的 {len(top)}/{len(comparisons)} 人，跳过 {len(data['skipped'])} 人；X/Y 为模型 embedding 相对坐标的二维投影",
    #     transform=ax.transAxes,
    #     fontsize=11,
    #     color="#667085",
    # )

    ax.grid(color="#e5e9f0", linestyle="-", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#d0d7de")
    ax.spines["bottom"].set_color("#d0d7de")
    max_extent = max(
        float(np.max(np.abs(xs))) if len(xs) else 0.0,
        float(np.max(np.abs(ys))) if len(ys) else 0.0,
        0.05,
    )
    ax.set_xlim(-max_extent * 1.2, max_extent * 1.2)
    ax.set_ylim(-max_extent * 1.2, max_extent * 1.2)
    ax.set_aspect("equal", adjustable="box")

    img_bytes = BytesIO()
    plt.savefig(
        img_bytes, bbox_inches="tight", format="jpeg", facecolor=fig.get_facecolor()
    )
    plt.close(fig)
    img_bytes.seek(0)
    return img_bytes
