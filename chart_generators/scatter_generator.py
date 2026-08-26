# chart_generators/scatter_generator.py
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
from .font_config import setup_chinese_font

# 确保字体已配置
setup_chinese_font()

def generate_scatter_chart(config):
    """
    生成散点图
    
    参数:
        config: 字典，包含：
            - title: 图表标题
            - x_data: X轴数据
            - y_data: Y轴数据
            - x_label: X轴标签
            - y_label: Y轴标签
            - color: 点的颜色
            - size: 点的大小
            - alpha: 透明度
            - show_trend: 是否显示趋势线
            - show_grid: 是否显示网格线
            - font_size: 字体大小
            - title_font_size: 标题字体大小
            - fig_width: 图片宽度
            - fig_height: 图片高度
            - background_color: 背景颜色
            - x_min: X轴最小值
            - x_max: X轴最大值
            - y_min: Y轴最小值
            - y_max: Y轴最大值
    """
    
    # 提取配置参数
    title = config.get('title', '散点图')
    x_data = config.get('x_data', [1, 2, 3, 4, 5, 6, 7, 8])
    y_data = config.get('y_data', [2, 4, 1, 5, 3, 7, 6, 8])
    x_label = config.get('x_label', 'X轴')
    y_label = config.get('y_label', 'Y轴')
    color = config.get('color', '#667eea')
    size = config.get('size', 80)
    alpha = config.get('alpha', 0.7)
    show_trend = config.get('show_trend', True)
    show_grid = config.get('show_grid', True)
    font_size = config.get('font_size', 12)
    title_font_size = config.get('title_font_size', 16)
    fig_width = config.get('fig_width', 10)
    fig_height = config.get('fig_height', 8)
    background_color = config.get('background_color', '#ffffff')
    x_min = config.get('x_min')
    x_max = config.get('x_max')
    y_min = config.get('y_min')
    y_max = config.get('y_max')
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)
    
    # 绘制散点图
    scatter = ax.scatter(x_data, y_data, 
                        c=color, 
                        s=size, 
                        alpha=alpha,
                        edgecolors='white',
                        linewidth=1.5,
                        zorder=2)
    
    # 绘制趋势线
    if show_trend and len(x_data) > 1:
        z = np.polyfit(x_data, y_data, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(x_data), max(x_data), 100)
        y_line = p(x_line)
        ax.plot(x_line, y_line, 
                color='#FF6B6B', 
                linestyle='--', 
                linewidth=2,
                alpha=0.8,
                label=f'趋势线 (r²={np.corrcoef(x_data, y_data)[0,1]**2:.3f})',
                zorder=1)
        ax.legend(loc='best', fontsize=font_size)
    
    # 设置标题和轴标签
    ax.set_title(title, fontsize=title_font_size, fontweight='bold', pad=20)
    if x_label:
        ax.set_xlabel(x_label, fontsize=font_size)
    if y_label:
        ax.set_ylabel(y_label, fontsize=font_size)
    
    # 设置轴范围
    if x_min is not None:
        ax.set_xlim(left=float(x_min))
    if x_max is not None:
        ax.set_xlim(right=float(x_max))
    if y_min is not None:
        ax.set_ylim(bottom=float(y_min))
    if y_max is not None:
        ax.set_ylim(top=float(y_max))
    
    # 显示网格线
    if show_grid:
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
        ax.set_axisbelow(True)
    
    # 美化边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')
    
    plt.tight_layout()
    
    # 转换为base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none')
    buffer.seek(0)
    
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return f'data:image/png;base64,{image_base64}'