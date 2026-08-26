# chart_generators/__init__.py
from .bar_generator import generate_bar_chart
from .pie_generator import generate_pie_chart
from .line_generator import generate_line_chart
from .scatter_generator import generate_scatter_chart
from .font_config import setup_chinese_font

# 确保字体已配置
setup_chinese_font()

__all__ = [
    'generate_bar_chart',
    'generate_pie_chart', 
    'generate_line_chart',
    'generate_scatter_chart'
]