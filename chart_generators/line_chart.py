# chart_generators/line_chart.py
import matplotlib.pyplot as plt
import numpy as np
from .base import ChartGenerator


class LineChartGenerator(ChartGenerator):
    """折线图生成器"""
    
    def __init__(self, config):
        super().__init__(config)
        
        # 折线图特有参数
        self.data = self.config.get('data', [10, 20, 15, 30, 25])
        self.x_data = self.config.get('x_data')
        self.x_label = self.config.get('x_label')
        self.y_label = self.config.get('y_label')
        self.x_ticks = self.config.get('x_ticks')
        self.colors = self.config.get('colors', ['#667eea'])
        self.line_width = self.config.get('line_width', 2.5)
        self.marker = self.config.get('marker', 'o')
        self.marker_size = self.config.get('marker_size', 8)
        self.fill_area = self.config.get('fill_area', False)
        
        # 验证数据
        if not self.data:
            raise ValueError('数据不能为空')
        
        # 验证X轴数据
        if self.x_data and len(self.x_data) != len(self.data):
            raise ValueError(
                f'X轴数据数量({len(self.x_data)})与数据数量({len(self.data)})不一致'
            )
        
        # 验证X轴刻度
        if self.x_ticks and len(self.x_ticks) != len(self.data):
            raise ValueError(
                f'X轴标签数量({len(self.x_ticks)})与数据数量({len(self.data)})不一致'
            )
    
    def generate(self):
        """生成折线图"""
        fig, ax = self._create_figure()
        
        # 准备X轴数据
        x_positions = self.x_data if self.x_data else np.arange(len(self.data))
        
        # 绘制折线
        color = self.colors[0] if self.colors else '#667eea'
        
        line = ax.plot(x_positions, self.data,
                       marker=self.marker,
                       markersize=self.marker_size,
                       linewidth=self.line_width,
                       color=color,
                       alpha=0.85)[0]
        
        # 填充面积
        if self.fill_area:
            ax.fill_between(x_positions, 0, self.data,
                           alpha=0.2, color=color)
        
        # 显示数值标签
        if self.show_values:
            max_val = max(self.data) if self.data else 1
            offset = max_val * 0.02
            for x, v in zip(x_positions, self.data):
                ax.text(x, v + offset, str(v),
                       ha='center', va='bottom',
                       fontsize=self.font_size - 1,
                       fontweight='bold',
                       color='#333333')
        
        # 设置标题和轴标签
        self._set_title_and_labels(ax, self.x_label, self.y_label)
        
        # 设置X轴刻度
        if self.x_ticks and len(self.x_ticks) == len(self.data):
            ax.set_xticks(x_positions)
            ax.set_xticklabels(self.x_ticks, fontsize=self.font_size)
        else:
            ax.set_xticks(x_positions)
            ax.set_xticklabels([f'点{i+1}' for i in range(len(self.data))], fontsize=self.font_size)
        
        # 应用轴范围
        self._apply_axis_limits(ax)
        
        # 应用网格和美化
        self._apply_grid(ax)
        self._beautify_axes(ax)
        
        plt.tight_layout()
        return self._to_base64(fig)