# chart_generators/pie_generator.py
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
from .font_config import setup_chinese_font

# 确保字体已配置
setup_chinese_font()

def generate_pie_chart(config):
    """
    生成饼图
    
    参数:
        config: 字典，包含：
            - title: 图表标题
            - data: 数据列表
            - labels: 标签列表 (可选)
            - colors: 颜色列表 (可选)
            - explode: 扇形分离 (可选)
            - show_percentage: 是否显示百分比
            - show_values: 是否显示数值
            - font_size: 字体大小
            - title_font_size: 标题字体大小
            - fig_width: 图片宽度
            - fig_height: 图片高度
            - background_color: 背景颜色
            - start_angle: 起始角度
            - shadow: 是否显示阴影
    """
    
    # 提取配置参数
    title = config.get('title', '饼图')
    data = config.get('data', [30, 25, 20, 15, 10])
    labels = config.get('labels')
    colors = config.get('colors')
    explode = config.get('explode')
    show_percentage = config.get('show_percentage', True)
    show_values = config.get('show_values', True)
    font_size = config.get('font_size', 12)
    title_font_size = config.get('title_font_size', 16)
    fig_width = config.get('fig_width', 10)
    fig_height = config.get('fig_height', 8)
    background_color = config.get('background_color', '#ffffff')
    start_angle = config.get('start_angle', 90)
    shadow = config.get('shadow', True)
    
    # 如果标签数量不匹配，自动生成
    if not labels or len(labels) != len(data):
        labels = [f'类别{i+1}' for i in range(len(data))]
    
    # 如果颜色数量不匹配，使用默认颜色
    default_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
                      '#F7DC6F', '#BB8FCE', '#85C1E9', '#F1948A', '#82E0AA']
    if not colors or len(colors) != len(data):
        colors = default_colors[:len(data)]
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)
    
    # 准备扇形分离
    if explode:
        explode_list = [float(e) for e in explode.split(',')] if isinstance(explode, str) else explode
        if len(explode_list) != len(data):
            explode_list = [0] * len(data)
    else:
        explode_list = [0] * len(data)
    
    # 绘制饼图
    autopct = None
    if show_percentage and show_values:
        autopct = lambda pct: f'{pct:.1f}%\n({int(pct/100*sum(data))})' if sum(data) > 0 else f'{pct:.1f}%'
    elif show_percentage:
        autopct = '%1.1f%%'
    elif show_values:
        autopct = lambda pct: f'{int(pct/100*sum(data))}'
    
    wedges, texts, autotexts = ax.pie(
        data,
        labels=labels if not show_values and not show_percentage else None,
        colors=colors,
        explode=explode_list,
        autopct=autopct,
        startangle=start_angle,
        shadow=shadow,
        textprops={'fontsize': font_size},
        pctdistance=0.85 if show_values and show_percentage else 0.6
    )
    
    # 如果只显示数值标签，显示在扇形外
    if show_values and not show_percentage:
        for i, (wedge, value) in enumerate(zip(wedges, data)):
            ang = (wedge.theta2 + wedge.theta1) / 2
            x = 1.1 * np.cos(np.radians(ang))
            y = 1.1 * np.sin(np.radians(ang))
            ax.text(x, y, str(value), ha='center', va='center', fontsize=font_size)
    
    # 设置标题
    ax.set_title(title, fontsize=title_font_size, fontweight='bold', pad=20)
    
    # 确保饼图是圆的
    ax.axis('equal')
    
    # 添加图例（如果有标签）
    if labels:
        ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=font_size)
    
    plt.tight_layout()
    
    # 转换为base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', 
                facecolor=fig.get_facecolor(), edgecolor='none')
    buffer.seek(0)
    
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return f'data:image/png;base64,{image_base64}'