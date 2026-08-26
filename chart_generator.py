import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import base64
from io import BytesIO
import matplotlib.font_manager as fm

# 设置中文字体支持
try:
    # 尝试设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
except:
    pass

def generate_chart(config):
    """
    生成柱状图
    
    参数:
        config: 字典，包含以下键值：
            - title: 图表标题
            - data: 数据列表
            - x_label: X轴标签 (可选)
            - y_label: Y轴标签 (可选)
            - x_ticks: X轴刻度标签列表 (可选)
            - bar_color: 柱状图主色
            - edge_color: 边框颜色
            - background_color: 背景颜色
            - bar_width: 柱状图宽度 (0.1-1.0)
            - font_size: 字体大小
            - title_font_size: 标题字体大小
            - fig_width: 图片宽度 (英寸)
            - fig_height: 图片高度 (英寸)
            - show_grid: 是否显示网格线
            - show_values: 是否显示数值标签
            - custom_colors: 自定义颜色列表 (可选)
    
    返回:
        base64编码的图片字符串
    """
    
    # 提取配置参数，提供默认值
    title = config.get('title', '柱状图')
    data = config.get('data', [10, 20, 15, 30, 25])
    x_label = config.get('x_label')
    y_label = config.get('y_label')
    x_ticks = config.get('x_ticks')
    bar_color = config.get('bar_color', '#667eea')
    edge_color = config.get('edge_color', '#5a6fd6')
    background_color = config.get('background_color', '#ffffff')
    bar_width = config.get('bar_width', 0.6)
    font_size = config.get('font_size', 12)
    title_font_size = config.get('title_font_size', 16)
    fig_width = config.get('fig_width', 10)
    fig_height = config.get('fig_height', 6)
    show_grid = config.get('show_grid', True)
    show_values = config.get('show_values', True)
    custom_colors = config.get('custom_colors')
    
    # 如果没有自定义颜色，使用主色
    if custom_colors:
        colors = custom_colors
    else:
        colors = [bar_color] * len(data)
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    # 设置背景颜色
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)
    
    # 生成X轴位置
    x_positions = np.arange(len(data))
    
    # 绘制柱状图
    bars = ax.bar(x_positions, data, 
                  width=bar_width,
                  color=colors,
                  edgecolor=edge_color,
                  linewidth=1.5,
                  alpha=0.85)
    
    # 设置标题
    ax.set_title(title, fontsize=title_font_size, fontweight='bold', pad=20)
    
    # 设置坐标轴标签
    if x_label:
        ax.set_xlabel(x_label, fontsize=font_size)
    if y_label:
        ax.set_ylabel(y_label, fontsize=font_size)
    
    # 设置X轴刻度
    if x_ticks and len(x_ticks) == len(data):
        ax.set_xticks(x_positions)
        ax.set_xticklabels(x_ticks, fontsize=font_size)
    else:
        # 自动生成X轴标签
        ax.set_xticks(x_positions)
        ax.set_xticklabels([f'Item {i+1}' for i in range(len(data))], fontsize=font_size)
    
    # 设置Y轴刻度字体大小
    ax.tick_params(axis='y', labelsize=font_size)
    
    # 显示网格线
    if show_grid:
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
        ax.set_axisbelow(True)  # 网格线在柱状图下方
    
    # 显示数值标签
    if show_values:
        for i, (bar, value) in enumerate(zip(bars, data)):
            height = bar.get_height()
            # 在柱子上方显示数值
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value}',
                    ha='center', va='bottom',
                    fontsize=font_size,
                    fontweight='bold',
                    color='#333333')
    
    # 自动调整Y轴范围，留出一些空间显示数值标签
    if show_values and data:
        max_value = max(data)
        ax.set_ylim(0, max_value * 1.15 if max_value > 0 else 1)
    
    # 美化边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')
    
    # 自动调整布局
    plt.tight_layout()
    
    # 转换为base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', 
                facecolor=fig.get_facecolor(), edgecolor='none')
    buffer.seek(0)
    
    # 编码为base64
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    # 返回带前缀的base64字符串（方便前端直接显示）
    return f'data:image/png;base64,{image_base64}'


# 为了兼容旧版本的简单调用方式
def generate_simple_chart(chart_type, chart_data):
    """
    简单版本的图表生成（保持向后兼容）
    """
    config = {
        'title': f'{chart_type} Chart',
        'data': chart_data,
        'bar_color': '#667eea',
        'edge_color': '#5a6fd6',
        'bar_width': 0.6,
        'show_grid': True,
        'show_values': True
    }
    return generate_chart(config)