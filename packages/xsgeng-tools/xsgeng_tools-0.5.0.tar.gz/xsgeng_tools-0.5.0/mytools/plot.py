import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


def add_titles(axes, colors=None):
    return [
        ax.text(
            0.02, 0.98, 
            f'({chr(ord("a")+i)})', 
            ha='left', 
            va='top',
            transform=ax.transAxes,
            color = 'k' if colors is None else colors[i],
        ) for  i, ax in enumerate(axes)
    ]



def add_inset_colorbar(mappable, ax=None, location='upper right', width="5%", height="50%", pad=0.5, orientation='vertical'):
    """
    在 ax 内部添加一个颜色条。如果 ax 为 None，则从 mappable 中提取 ax。

    Parameters:
    - mappable: 与颜色条关联的 mappable 对象（例如，imshow 返回的对象）。
    - ax: 主图的 Axes 对象，默认为 None。
    - location: 颜色条的位置，可以是 'upper right', 'upper left', 'lower left', 'lower right' 等。
    - width: 颜色条的宽度，可以是百分比字符串（例如 "5%"）或具体数值。
    - height: 颜色条的高度，可以是百分比字符串（例如 "50%"）或具体数值。
    - pad: 颜色条与主图之间的间距。
    - orientation: 颜色条的方向，可以是 'vertical' 或 'horizontal'。

    Returns:
    - cax: 颜色条的 Axes 对象。
    """
    # 如果 ax 为 None，则从 mappable 中提取 ax
    if ax is None:
        ax = mappable.axes

    # 如果方向是水平，则交换宽度和高度
    if orientation == 'horizontal':
        width, height = height, width
    
    # 创建一个 inset axes 用于颜色条
    cax = inset_axes(ax, width=width, height=height, loc=location, bbox_to_anchor=(0, 0, 1, 1), bbox_transform=ax.transAxes, borderpad=pad)
    
    # 在 inset axes 上添加颜色条
    plt.colorbar(mappable, cax=cax, orientation=orientation)
    
    return cax


def plot_gradient_line(ax: Axes, x, y, c, cmap='viridis', linewidth=2, **kwargs):
    """
    绘制颜色渐变的线条。

    Parameters:
    - x (array-like): x 轴数据
    - y (array-like): y 轴数据
    - c (array-like): 颜色映射的值
    - cmap (str): 颜色映射名称，默认为 'viridis'
    - linewidth (float): 线条宽度，默认为 2
    - **kwargs: 其他传递给 LineCollection 的参数

    Returns:
    lc: 返回 LineCollection 对象
    """
    # 创建颜色映射
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # 创建颜色映射
    cmap = plt.get_cmap(cmap)
    norm = plt.Normalize(c.min(), c.max())

    # 创建 LineCollection
    lc = LineCollection(segments, cmap=cmap, norm=norm, **kwargs)
    lc.set_array(c)
    lc.set_linewidth(linewidth)

    # 添加到 Axes
    ax.add_collection(lc)
    ax.autoscale_view()

    return lc