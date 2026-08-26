# chart_generators/line_chart.py
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from .base import ChartGenerator


class LineChartGenerator(ChartGenerator):
    """折线图生成器（支持多系列）"""
    
    def __init__(self, config):
        super().__init__(config)
        
        # 折线图特有参数
        self.data = self.config.get('data', {'系列1': [10, 20, 15, 30, 25]})
        self.x_labels = self.config.get('x_labels')
        self.x_label = self.config.get('x_label')
        self.y_label = self.config.get('y_label')
        self.colors = self.config.get('colors', ['#667eea', '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'])
        self.line_width = self.config.get('line_width', 2.5)
        self.marker = self.config.get('marker', 'o')
        self.marker_size = self.config.get('marker_size', 8)
        self.fill_area = self.config.get('fill_area', False)
        self.show_values = self.config.get('show_values', True)
        self.show_legend = self.config.get('show_legend', True)  # ✅ 新增：是否显示图例
        
        # 验证数据
        if not self.data:
            raise ValueError('数据不能为空')
        
        # 处理数据格式：支持字典和列表两种格式
        if isinstance(self.data, dict):
            self.series_names = list(self.data.keys())
            self.series_data = list(self.data.values())
        elif isinstance(self.data, list):
            if isinstance(self.data[0], (list, tuple)):
                self.series_names = [f'系列{i+1}' for i in range(len(self.data))]
                self.series_data = self.data
            else:
                # 单系列
                self.series_names = ['数据']
                self.series_data = [self.data]
        else:
            raise ValueError('数据格式不支持')
        
        self.n_series = len(self.series_data)
        self.n_points = len(self.series_data[0]) if self.series_data else 0
        
        # 验证各系列数据长度一致
        for i, data in enumerate(self.series_data):
            if len(data) != self.n_points:
                raise ValueError(f'系列{i+1}数据长度({len(data)})与第一个系列({self.n_points})不一致')
        
        # 验证标签
        if self.x_labels and len(self.x_labels) != self.n_points:
            raise ValueError(f'X轴标签数量({len(self.x_labels)})与数据点数量({self.n_points})不一致')
        
        # ✅ 确保颜色数量足够
        if len(self.colors) < self.n_series:
            # 如果颜色不够，从默认颜色中补充
            default_colors = ['#667eea', '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', 
                             '#F7DC6F', '#BB8FCE', '#85C1E9', '#F1948A', '#82E0AA']
            self.colors = self.colors + default_colors[len(self.colors):]
    
    def generate(self):
        """生成折线图"""
        fig, ax = self._create_figure()
        
        x_positions = np.arange(self.n_points)
        
        # 绘制每个系列
        for i, (name, data) in enumerate(zip(self.series_names, self.series_data)):
            color = self.colors[i % len(self.colors)]
            
            # 绘制折线
            line = ax.plot(x_positions, data,
                          marker=self.marker,
                          markersize=self.marker_size,
                          linewidth=self.line_width,
                          color=color,
                          label=name,  # ✅ 使用系列名称作为图例标签
                          alpha=0.85)[0]
            
            # 填充面积
            if self.fill_area:
                ax.fill_between(x_positions, 0, data,
                               alpha=0.2, color=color)
            
            # 显示数值标签
            if self.show_values:
                max_val = max(data) if data else 1
                offset = max_val * 0.02 if max_val > 0 else 0.1
                for x, v in zip(x_positions, data):
                    ax.text(x, v + offset, str(v),
                           ha='center', va='bottom',
                           fontsize=self.font_size - 1,
                           fontweight='bold',
                           color='#333333')
        
        # 设置标题和轴标签
        self._set_title_and_labels(ax, self.x_label, self.y_label)
        
        # 设置X轴刻度
        if self.x_labels and len(self.x_labels) == self.n_points:
            ax.set_xticks(x_positions)
            ax.set_xticklabels(self.x_labels, fontsize=self.font_size)
        else:
            ax.set_xticks(x_positions)
            ax.set_xticklabels([f'点{i+1}' for i in range(self.n_points)], fontsize=self.font_size)
        
        # 应用轴范围
        self._apply_axis_limits(ax)
        
        # ✅ 添加图例（多系列时显示，或用户指定显示）
        if self.n_series > 1 or self.show_legend:
            ax.legend(loc='best', fontsize=self.font_size, framealpha=0.9)
        
        # 应用网格和美化
        self._apply_grid(ax)
        self._beautify_axes(ax)
        
        plt.tight_layout()
        return self._to_base64(fig)