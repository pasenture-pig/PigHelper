# chart_generators/__init__.py
from .base import ChartGenerator
from .bar_chart import BarChartGenerator
from .pie_chart import PieChartGenerator
from .line_chart import LineChartGenerator
from .scatter_chart import ScatterChartGenerator

# 3D图表
from .bar_3d_chart import Bar3DChartGenerator
from .pie_3d_chart import Pie3DChartGenerator
from .line_3d_chart import Line3DChartGenerator

# 热力图
from .heatmap_chart import HeatmapChartGenerator

# 曲面热力图
from .surface_chart import SurfaceChartGenerator


class ChartFactory:
    """图表工厂类"""
    
    _generators = {
        'bar': BarChartGenerator,
        'pie': PieChartGenerator,
        'line': LineChartGenerator,
        'scatter': ScatterChartGenerator,
        # 3D图表
        'bar_3d': Bar3DChartGenerator,
        'pie_3d': Pie3DChartGenerator,
        'line_3d': Line3DChartGenerator,
        # 热力图
        'heatmap': HeatmapChartGenerator,
        # 曲面热力图
        'surface': SurfaceChartGenerator,
    }
    
    @classmethod
    def create(cls, chart_type, config):
        generator_class = cls._generators.get(chart_type)
        if not generator_class:
            raise ValueError(f'不支持的图表类型: {chart_type}')
        return generator_class(config)
    
    @classmethod
    def get_types(cls):
        return list(cls._generators.keys())


def generate_chart(config):
    chart_type = config.get('type', 'bar')
    generator = ChartFactory.create(chart_type, config)
    return generator.generate()


__all__ = [
    'ChartGenerator',
    'BarChartGenerator',
    'PieChartGenerator',
    'LineChartGenerator',
    'ScatterChartGenerator',
    'Bar3DChartGenerator',
    'Pie3DChartGenerator',
    'Line3DChartGenerator',
    'HeatmapChartGenerator',
    'SurfaceChartGenerator',
    'ChartFactory',
    'generate_chart',
]