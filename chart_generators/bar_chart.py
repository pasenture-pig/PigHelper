# chart_generators/bar_chart.py
import matplotlib.pyplot as plt
import numpy as np
from .base import ChartGenerator


class BarChartGenerator(ChartGenerator):
    """柱状图生成器"""
    
    def __init__(self, config):
        super().__init__(config)
        
        # 柱状图特有参数
        self.data = self.config.get('data', [10, 20, 15, 30, 25])
        self.x_label = self.config.get('x_label')
        self.y_label = self.config.get('y_label')
        self.x_ticks = self.config.get('x_ticks')
        self.bar_color = self.config.get('bar_color', '#667eea')
        self.edge_color = self.config.get('edge_color', '#5a6fd6')
        self.bar_width = self.config.get('bar_width', 0.6)
        self.custom_colors = self.config.get('custom_colors')
        
        # 验证数据
        if not self.data:
            raise ValueError('数据不能为空')
        
        # 验证自定义颜色
        if self.custom_colors and len(self.custom_colors) != len(self.data):
            raise ValueError(
                f'自定义颜色数量({len(self.custom_colors)})与数据数量({len(self.data)})不一致'
            )
        
        # 验证X轴刻度
        if self.x_ticks and len(self.x_ticks) != len(self.data):
            raise ValueError(
                f'X轴标签数量({len(self.x_ticks)})与数据数量({len(self.data)})不一致'
            )
    
    def generate(self):
        """生成柱状图"""
        fig, ax = self._create_figure()
        
        # 准备颜色
        colors = self.custom_colors if self.custom_colors else [self.bar_color] * len(self.data)
        
        # 绘制柱状图
        x_positions = np.arange(len(self.data))
        bars = ax.bar(x_positions, self.data,
                      width=self.bar_width,
                      color=colors,
                      edgecolor=self.edge_color,
                      linewidth=1.5,
                      alpha=0.85)
        
        # 设置标题和轴标签
        self._set_title_and_labels(ax, self.x_label, self.y_label)
        
        # 设置X轴刻度
        if self.x_ticks and len(self.x_ticks) == len(self.data):
            ax.set_xticks(x_positions)
            ax.set_xticklabels(self.x_ticks, fontsize=self.font_size)
        else:
            ax.set_xticks(x_positions)
            ax.set_xticklabels([f'项目 {i+1}' for i in range(len(self.data))], fontsize=self.font_size)
        
        # 应用轴范围
        self._apply_axis_limits(ax)
        
        # 自动调整Y轴范围
        if self.show_values and self.data and self.y_min is None and self.y_max is None:
            max_value = max(self.data)
            if max_value > 0:
                ax.set_ylim(0, max_value * 1.15)
        
        # 显示数值标签
        if self.show_values:
            for bar, value in zip(bars, self.data):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height,
                        str(value),
                        ha='center', va='bottom',
                        fontsize=self.font_size,
                        fontweight='bold',
                        color='#333333')
        
        # 应用网格和美化
        self._apply_grid(ax)
        self._beautify_axes(ax)
        
        plt.tight_layout()
        return self._to_base64(fig)