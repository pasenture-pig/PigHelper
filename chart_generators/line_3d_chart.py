# chart_generators/line_3d_chart.py
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from .base import ChartGenerator


class Line3DChartGenerator(ChartGenerator):
    """3D折线图生成器"""
    
    def __init__(self, config):
        super().__init__(config)
        
        # 3D折线图特有参数
        self.data = self.config.get('data', {
            '系列1': [10, 20, 15, 30, 25],
            '系列2': [5, 15, 25, 20, 35],
            '系列3': [15, 10, 20, 25, 30]
        })
        self.x_labels = self.config.get('x_labels', ['点1', '点2', '点3', '点4', '点5'])
        self.x_label = self.config.get('x_label', 'X轴')
        self.y_label = self.config.get('y_label', 'Y轴')
        self.z_label = self.config.get('z_label', '数值')
        self.colors = self.config.get('colors', ['#667eea', '#FF6B6B', '#4ECDC4'])
        self.line_width = self.config.get('line_width', 2.5)
        self.marker = self.config.get('marker', 'o')
        self.marker_size = self.config.get('marker_size', 8)
        self.show_values = self.config.get('show_values', True)
        self.elev = self.config.get('elev', 25)
        self.azim = self.config.get('azim', 45)
        
        # 验证数据
        if not self.data:
            raise ValueError('数据不能为空')
        
        # 提取系列数量
        if isinstance(self.data, dict):
            self.series_names = list(self.data.keys())
            self.series_data = list(self.data.values())
        else:
            self.series_names = [f'系列{i+1}' for i in range(len(self.data))]
            self.series_data = self.data
        
        self.n_series = len(self.series_data)
        self.n_points = len(self.series_data[0]) if self.series_data else 0
        
        # 验证标签
        if self.x_labels and len(self.x_labels) != self.n_points:
            raise ValueError(f'X轴标签数量({len(self.x_labels)})与数据点数量({self.n_points})不一致')
    
    def generate(self):
        """生成3D折线图"""
        fig = plt.figure(figsize=(self.fig_width, self.fig_height))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor(self.background_color)
        fig.patch.set_facecolor(self.background_color)
        
        # 生成X轴位置
        x_positions = np.arange(self.n_points)
        
        # 为每个系列分配Y轴位置
        y_positions = np.arange(self.n_series)
        
        # 绘制每条折线
        for i, (name, data) in enumerate(zip(self.series_names, self.series_data)):
            y_pos = np.full_like(x_positions, y_positions[i])
            color = self.colors[i % len(self.colors)]
            
            ax.plot(x_positions, y_pos, data,
                   marker=self.marker,
                   markersize=self.marker_size,
                   linewidth=self.line_width,
                   color=color,
                   label=name,
                   alpha=0.85)
            
            # 显示数值标签
            if self.show_values:
                for x, y, z in zip(x_positions, y_pos, data):
                    ax.text(x, y, z + max(data) * 0.02, f'{z:.1f}',
                           ha='center', va='bottom',
                           fontsize=self.font_size-1,
                           fontweight='bold')
        
        # 设置轴标签
        ax.set_xlabel(self.x_label, fontsize=self.font_size, labelpad=10)
        ax.set_ylabel(self.y_label, fontsize=self.font_size, labelpad=10)
        ax.set_zlabel(self.z_label, fontsize=self.font_size, labelpad=10)
        
        # 设置刻度标签
        if self.x_labels:
            ax.set_xticks(x_positions)
            ax.set_xticklabels(self.x_labels, fontsize=self.font_size, rotation=45, ha='right')
        else:
            ax.set_xticks(x_positions)
            ax.set_xticklabels([f'点{i+1}' for i in range(self.n_points)], fontsize=self.font_size)
        
        ax.set_yticks(y_positions)
        ax.set_yticklabels(self.series_names, fontsize=self.font_size)
        
        # 设置视角
        ax.view_init(elev=self.elev, azim=self.azim)
        
        # 设置标题
        ax.set_title(self.title, fontsize=self.title_font_size, fontweight='bold', pad=20)
        
        # 添加图例
        ax.legend(loc='best', fontsize=self.font_size)
        
        # 美化
        ax.grid(True, alpha=0.2)
        ax.xaxis.pane.set_facecolor(self.background_color)
        ax.yaxis.pane.set_facecolor(self.background_color)
        ax.zaxis.pane.set_facecolor(self.background_color)
        
        plt.tight_layout()
        return self._to_base64(fig)