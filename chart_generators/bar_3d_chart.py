# chart_generators/bar_3d_chart.py
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from .base import ChartGenerator


class Bar3DChartGenerator(ChartGenerator):
    """3D柱状图生成器"""
    
    def __init__(self, config):
        super().__init__(config)
        
        # 3D柱状图特有参数
        self.data = self.config.get('data', [[10, 20, 15], [25, 30, 20], [15, 10, 25]])
        self.x_labels = self.config.get('x_labels', ['类别A', '类别B', '类别C'])
        self.y_labels = self.config.get('y_labels', ['系列1', '系列2', '系列3'])
        self.x_label = self.config.get('x_label', 'X轴')
        self.y_label = self.config.get('y_label', 'Y轴')
        self.z_label = self.config.get('z_label', '数值')
        self.bar_color = self.config.get('bar_color', '#667eea')
        self.edge_color = self.config.get('edge_color', '#5a6fd6')
        self.show_values = self.config.get('show_values', True)
        self.elev = self.config.get('elev', 25)  # 视角仰角
        self.azim = self.config.get('azim', 45)   # 视角方位角
        
        # 验证数据
        if not self.data or not isinstance(self.data, list):
            raise ValueError('数据必须是非空二维列表')
        
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
        """生成3D柱状图"""
        fig = plt.figure(figsize=(self.fig_width, self.fig_height))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor(self.background_color)
        fig.patch.set_facecolor(self.background_color)
        
        # 准备数据
        x = np.arange(self.n_cols)
        y = np.arange(self.n_rows)
        x_pos, y_pos = np.meshgrid(x, y)
        x_pos = x_pos.flatten()
        y_pos = y_pos.flatten()
        z_pos = np.zeros_like(x_pos)
        
        # 柱状图尺寸
        dx = 0.6
        dy = 0.6
        dz = np.array(self.data).flatten()
        
        # 颜色
        if isinstance(self.bar_color, str):
            colors = [self.bar_color] * len(dz)
        else:
            colors = self.bar_color
        
        # 绘制3D柱状图
        bars = ax.bar3d(x_pos, y_pos, z_pos, dx, dy, dz,
                        color=colors,
                        edgecolor=self.edge_color,
                        alpha=0.85,
                        zsort='average')
        
        # 设置轴标签
        ax.set_xlabel(self.x_label, fontsize=self.font_size, labelpad=10)
        ax.set_ylabel(self.y_label, fontsize=self.font_size, labelpad=10)
        ax.set_zlabel(self.z_label, fontsize=self.font_size, labelpad=10)
        
        # 设置刻度标签
        if self.x_labels:
            ax.set_xticks(x + dx/2)
            ax.set_xticklabels(self.x_labels, fontsize=self.font_size, rotation=45, ha='right')
        if self.y_labels:
            ax.set_yticks(y + dy/2)
            ax.set_yticklabels(self.y_labels, fontsize=self.font_size)
        
        # 设置视角
        ax.view_init(elev=self.elev, azim=self.azim)
        
        # 设置标题
        ax.set_title(self.title, fontsize=self.title_font_size, fontweight='bold', pad=20)
        
        # 显示数值标签
        if self.show_values:
            for i, (xi, yi, zi) in enumerate(zip(x_pos, y_pos, dz)):
                ax.text(xi, yi, zi + max(dz) * 0.02, f'{zi:.1f}',
                       ha='center', va='bottom', fontsize=self.font_size-1,
                       fontweight='bold', color='#333333')
        
        # 美化
        ax.grid(True, alpha=0.2)
        ax.xaxis.pane.set_facecolor(self.background_color)
        ax.yaxis.pane.set_facecolor(self.background_color)
        ax.zaxis.pane.set_facecolor(self.background_color)
        
        plt.tight_layout()
        return self._to_base64(fig)