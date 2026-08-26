# chart_generators/heatmap_chart.py
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from .base import ChartGenerator


class HeatmapChartGenerator(ChartGenerator):
    """热力图生成器"""
    
    def __init__(self, config):
        super().__init__(config)
        
        # 热力图特有参数
        self.data = self.config.get('data', [
            [10, 20, 30, 25],
            [15, 35, 20, 30],
            [25, 10, 40, 15],
            [30, 25, 15, 35]
        ])
        self.x_labels = self.config.get('x_labels', ['类别A', '类别B', '类别C', '类别D'])
        self.y_labels = self.config.get('y_labels', ['系列1', '系列2', '系列3', '系列4'])
        self.x_label = self.config.get('x_label', 'X轴')
        self.y_label = self.config.get('y_label', 'Y轴')
        self.cmap = self.config.get('cmap', 'RdYlBu_r')  # 颜色方案
        self.show_values = self.config.get('show_values', True)
        self.value_format = self.config.get('value_format', '.1f')  # 数值格式化
        self.cbar_label = self.config.get('cbar_label', '数值')
        self.cbar_orientation = self.config.get('cbar_orientation', 'vertical')  # vertical, horizontal
        
        # 验证数据
        if not self.data:
            raise ValueError('数据不能为空')
        
        # 确保数据是二维的
        if isinstance(self.data[0], (int, float)):
            self.data = [self.data]
        
        self.n_rows = len(self.data)
        self.n_cols = len(self.data[0])
        
        # 验证标签
        if self.x_labels and len(self.x_labels) != self.n_cols:
            raise ValueError(f'X轴标签数量({len(self.x_labels)})与列数({self.n_cols})不一致')
        if self.y_labels and len(self.y_labels) != self.n_rows:
            raise ValueError(f'Y轴标签数量({len(self.y_labels)})与行数({self.n_rows})不一致')
    
    def generate(self):
        """生成热力图"""
        fig, ax = self._create_figure()
        
        # 转换为numpy数组
        data_array = np.array(self.data)
        
        # 绘制热力图
        im = ax.imshow(data_array, cmap=self.cmap, aspect='auto', interpolation='nearest')
        
        # 设置轴标签
        if self.x_labels:
            ax.set_xticks(np.arange(len(self.x_labels)))
            ax.set_xticklabels(self.x_labels, fontsize=self.font_size)
        else:
            ax.set_xticks(np.arange(self.n_cols))
            ax.set_xticklabels([f'列{i+1}' for i in range(self.n_cols)], fontsize=self.font_size)
        
        if self.y_labels:
            ax.set_yticks(np.arange(len(self.y_labels)))
            ax.set_yticklabels(self.y_labels, fontsize=self.font_size)
        else:
            ax.set_yticks(np.arange(self.n_rows))
            ax.set_yticklabels([f'行{i+1}' for i in range(self.n_rows)], fontsize=self.font_size)
        
        # 设置标题和轴标签
        ax.set_title(self.title, fontsize=self.title_font_size, fontweight='bold', pad=20)
        if self.x_label:
            ax.set_xlabel(self.x_label, fontsize=self.font_size)
        if self.y_label:
            ax.set_ylabel(self.y_label, fontsize=self.font_size)
        
        # 显示数值
        if self.show_values:
            for i in range(self.n_rows):
                for j in range(self.n_cols):
                    value = data_array[i, j]
                    # 根据背景颜色选择文字颜色（深色背景用白色，浅色背景用黑色）
                    color = 'white' if value > np.mean(data_array) else 'black'
                    ax.text(j, i, f'{value:{self.value_format}}',
                           ha='center', va='center',
                           fontsize=self.font_size-1,
                           fontweight='bold',
                           color=color)
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax, orientation=self.cbar_orientation, shrink=0.8)
        cbar.set_label(self.cbar_label, fontsize=self.font_size)
        cbar.ax.tick_params(labelsize=self.font_size-1)
        
        # 美化边框
        ax.spines['top'].set_visible(True)
        ax.spines['right'].set_visible(True)
        ax.spines['left'].set_visible(True)
        ax.spines['bottom'].set_visible(True)
        ax.spines['top'].set_color('#cccccc')
        ax.spines['right'].set_color('#cccccc')
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_color('#cccccc')
        
        plt.tight_layout()
        return self._to_base64(fig)