# chart_generators/line_generator.py
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
from .font_config import setup_chinese_font

# 确保字体已配置
setup_chinese_font()

def generate_line_chart(config):
    """
    生成折线图
    
    参数:
        config: 字典，包含：
            - title: 图表标题
            - data: 数据列表 (单个系列) 或 数据字典 (多个系列)
            - x_data: X轴数据 (可选)
            - x_label: X轴标签
            - y_label: Y轴标签
            - x_ticks: X轴刻度标签
            - colors: 颜色列表
            - line_width: 线宽
            - marker: 数据点标记样式
            - marker_size: 标记大小
            - fill_area: 是否填充面积
            - show_grid: 是否显示网格线
            - show_values: 是否显示数值标签
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
    title = config.get('title', '折线图')
    data = config.get('data', [10, 20, 15, 30, 25])
    x_data = config.get('x_data')
    x_label = config.get('x_label')
    y_label = config.get('y_label')
    x_ticks = config.get('x_ticks')
    colors = config.get('colors', ['#667eea'])
    line_width = config.get('line_width', 2.5)
    marker = config.get('marker', 'o')
    marker_size = config.get('marker_size', 8)
    fill_area = config.get('fill_area', False)
    show_grid = config.get('show_grid', True)
    show_values = config.get('show_values', True)
    font_size = config.get('font_size', 12)
    title_font_size = config.get('title_font_size', 16)
    fig_width = config.get('fig_width', 10)
    fig_height = config.get('fig_height', 6)
    background_color = config.get('background_color', '#ffffff')
    x_min = config.get('x_min')
    x_max = config.get('x_max')
    y_min = config.get('y_min')
    y_max = config.get('y_max')
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)
    
    # 准备数据
    # 支持多系列数据
    if isinstance(data, dict):
        series_data = data
    else:
        series_data = {'数据': data}
    
    # 准备X轴数据
    if x_data:
        if len(x_data) != len(list(series_data.values())[0]):
            x_positions = np.arange(len(list(series_data.values())[0]))
        else:
            x_positions = x_data
    else:
        x_positions = np.arange(len(list(series_data.values())[0]))
    
    # 绘制折线
    for i, (label, values) in enumerate(series_data.items()):
        color = colors[i % len(colors)] if colors else None
        
        # 绘制折线
        line = ax.plot(x_positions, values, 
                       marker=marker,
                       markersize=marker_size,
                       linewidth=line_width,
                       color=color,
                       label=label,
                       alpha=0.85)
        
        # 填充面积
        if fill_area:
            ax.fill_between(x_positions, 0, values, 
                           alpha=0.2, color=color)
        
        # 显示数值标签
        if show_values:
            for j, (x, v) in enumerate(zip(x_positions, values)):
                ax.text(x, v + (max(values) * 0.02), str(v),
                       ha='center', va='bottom',
                       fontsize=font_size-1,
                       fontweight='bold',
                       color='#333333')
    
    # 设置标题
    ax.set_title(title, fontsize=title_font_size, fontweight='bold', pad=20)
    
    # 设置坐标轴标签
    if x_label:
        ax.set_xlabel(x_label, fontsize=font_size)
    if y_label:
        ax.set_ylabel(y_label, fontsize=font_size)
    
    # 设置X轴刻度
    if x_ticks and len(x_ticks) == len(x_positions):
        ax.set_xticks(x_positions)
        ax.set_xticklabels(x_ticks, fontsize=font_size)
    else:
        ax.set_xticks(x_positions)
        ax.set_xticklabels([f'点{i+1}' for i in range(len(x_positions))], fontsize=font_size)
    
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
    
    # 添加图例
    if len(series_data) > 1:
        ax.legend(loc='best', fontsize=font_size)
    
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