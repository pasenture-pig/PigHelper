# chart_generators/__init__.py
from .base import ChartGenerator
from .bar_chart import BarChartGenerator
from .pie_chart import PieChartGenerator
from .line_chart import LineChartGenerator
from .scatter_chart import ScatterChartGenerator


class ChartFactory:
    """图表工厂类"""
    
    _generators = {
        'bar': BarChartGenerator,
        'pie': PieChartGenerator,
        'line': LineChartGenerator,
        'scatter': ScatterChartGenerator,
    }
    
    @classmethod
    def create(cls, chart_type, config):
        """
        创建图表生成器实例
        
        参数:
            chart_type: 图表类型 (bar, pie, line, scatter)
            config: 图表配置字典
        
        返回:
            图表生成器实例
        
        异常:
            ValueError: 不支持的图表类型
        """
        generator_class = cls._generators.get(chart_type)
        if not generator_class:
            raise ValueError(f'不支持的图表类型: {chart_type}')
        return generator_class(config)
    
    @classmethod
    def get_types(cls):
        """获取所有支持的图表类型"""
        return list(cls._generators.keys())

# 保持向后兼容的函数（可选）
def generate_chart(config):
    """
    生成图表（兼容旧版本调用方式）
    """
    chart_type = config.get('type', 'bar')
    generator = ChartFactory.create(chart_type, config)
    return generator.generate()


__all__ = [
    'ChartGenerator',
    'BarChartGenerator',
    'PieChartGenerator',
    'LineChartGenerator',
    'ScatterChartGenerator',
    'ChartFactory',
    'generate_chart',
]