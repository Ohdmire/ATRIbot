import matplotlib.pyplot as plt
from io import BytesIO

def draw_tdba(bps, times, x_list, y_list, osuname):

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

    img_bytes = BytesIO()

    plt.savefig(img_bytes)
    plt.close()

    img_bytes.seek(0)
    return img_bytes