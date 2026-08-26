# chart_generators/font_config.py
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import os
import logging

# 配置日志
logger = logging.getLogger(__name__)

def setup_chinese_font():
    """
    配置 matplotlib 中文字体支持
    自动检测系统环境并选择合适的字体
    """
    
    # 根据操作系统选择字体
    system = platform.system()
    
    # 中文字体候选列表（按优先级排序）
    font_candidates = []
    
    if system == 'Windows':
        font_candidates = [
            'SimHei',           # 黑体
            'Microsoft YaHei',  # 微软雅黑
            'SimSun',           # 宋体
            'KaiTi',            # 楷体
            'FangSong',         # 仿宋
        ]
    elif system == 'Darwin':  # macOS
        font_candidates = [
            'PingFang SC',      # 苹方
            'Heiti SC',         # 黑体
            'STSong',           # 宋体
            'Apple LiGothic',   # 苹果丽黑
            'Arial Unicode MS', # Arial Unicode
        ]
    else:  # Linux
        font_candidates = [
            'WenQuanYi Micro Hei',  # 文泉驿微米黑
            'Noto Sans CJK SC',     # 思源黑体
            'SimHei',
            'DejaVu Sans',
        ]
    
    # 检查系统中可用的字体
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 查找第一个可用的中文字体
    selected_font = None
    for font in font_candidates:
        if font in available_fonts:
            selected_font = font
            logger.info(f'✅ 使用中文字体: {font}')
            break
    
    # 如果找不到，尝试查找任何包含中文的字体
    if not selected_font:
        for f in fm.fontManager.ttflist:
            try:
                # 检查字体是否包含中文字符
                if any('\u4e00' <= char <= '\u9fff' for char in f.name):
                    selected_font = f.name
                    logger.info(f'✅ 使用中文字体: {f.name}')
                    break
            except:
                continue
    
    # 如果还是找不到，使用系统默认字体并给出警告
    if not selected_font:
        selected_font = 'sans-serif'
        logger.warning('⚠️ 未找到中文字体，将使用默认字体（中文可能显示为方块）')
        logger.warning('💡 请安装中文字体:')
        logger.warning('  - Windows: 系统自带中文字体')
        logger.warning('  - macOS: 系统自带中文字体')
        logger.warning('  - Linux: apt-get install fonts-wqy-microhei')
    
    # 设置 matplotlib 字体
    plt.rcParams['font.sans-serif'] = [selected_font] + plt.rcParams['font.sans-serif']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    
    return selected_font

# 在导入时自动配置字体
try:
    setup_chinese_font()
except Exception as e:
    logger.warning(f'⚠️ 字体配置失败: {e}')