# chart_generators/surface_chart.py
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from .base import ChartGenerator


class SurfaceChartGenerator(ChartGenerator):
    """曲面热力图生成器"""
    
    def __init__(self, config):
        super().__init__(config)
        
        # 曲面图特有参数
        self.data = self.config.get('data', [
            [10, 15, 20, 18, 12],
            [15, 25, 35, 28, 20],
            [20, 35, 45, 38, 25],
            [18, 28, 38, 32, 22],
            [12, 20, 25, 22, 15]
        ])
        self.x_labels = self.config.get('x_labels')
        self.y_labels = self.config.get('y_labels')
        self.x_label = self.config.get('x_label', 'X轴')
        self.y_label = self.config.get('y_label', 'Y轴')
        self.z_label = self.config.get('z_label', '数值')
        self.cmap = self.config.get('cmap', 'RdYlBu_r')
        self.show_values = self.config.get('show_values', True)
        self.value_format = self.config.get('value_format', '.1f')
        self.elev = self.config.get('elev', 30)
        self.azim = self.config.get('azim', 225)
        self.alpha = self.config.get('alpha', 0.85)
        self.wireframe = self.config.get('wireframe', False)
        self.contour = self.config.get('contour', False)
        self.contour_levels = self.config.get('contour_levels', 10)
        
        # 验证数据
        if not self.data:
            raise ValueError('数据不能为空')
        
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
        """生成曲面热力图"""
        fig = plt.figure(figsize=(self.fig_width, self.fig_height))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor(self.background_color)
        fig.patch.set_facecolor(self.background_color)
        
        # 准备数据
        data_array = np.array(self.data)
        x = np.arange(self.n_cols)
        y = np.arange(self.n_rows)
        X, Y = np.meshgrid(x, y)
        Z = data_array
        
        # 绘制曲面
        surf = ax.plot_surface(X, Y, Z,
                               cmap=self.cmap,
                               alpha=self.alpha,
                               linewidth=0,
                               antialiased=True)
        
        # 添加线框
        if self.wireframe:
            ax.plot_wireframe(X, Y, Z,
                             color='black',
                             linewidth=0.5,
                             alpha=0.3)
        
        # 添加底部投影等高线
        if self.contour:
            ax.contour(X, Y, Z,
                      zdir='z',
                      offset=np.min(Z) - (np.max(Z) - np.min(Z)) * 0.15,
                      levels=self.contour_levels,
                      cmap=self.cmap,
                      alpha=0.5)
        
        # 设置轴标签
        ax.set_xlabel(self.x_label, fontsize=self.font_size, labelpad=10)
        ax.set_ylabel(self.y_label, fontsize=self.font_size, labelpad=10)
        ax.set_zlabel(self.z_label, fontsize=self.font_size, labelpad=10)
        
        # 设置刻度标签
        if self.x_labels:
            ax.set_xticks(np.arange(len(self.x_labels)))
            ax.set_xticklabels(self.x_labels, fontsize=self.font_size-1, rotation=45, ha='right')
        else:
            ax.set_xticks(np.arange(self.n_cols))
            ax.set_xticklabels([f'{i+1}' for i in range(self.n_cols)], fontsize=self.font_size-1)
        
        if self.y_labels:
            ax.set_yticks(np.arange(len(self.y_labels)))
            ax.set_yticklabels(self.y_labels, fontsize=self.font_size-1)
        else:
            ax.set_yticks(np.arange(self.n_rows))
            ax.set_yticklabels([f'{i+1}' for i in range(self.n_rows)], fontsize=self.font_size-1)
        
        # 设置视角
        ax.view_init(elev=self.elev, azim=self.azim)
        
        # 设置标题
        ax.set_title(self.title, fontsize=self.title_font_size, fontweight='bold', pad=20)
        
        # 显示数值标签（在曲面上方）
        if self.show_values:
            for i in range(self.n_rows):
                for j in range(self.n_cols):
                    value = data_array[i, j]
                    ax.text(j, i, value + (np.max(Z) - np.min(Z)) * 0.03,
                           f'{value:{self.value_format}}',
                           ha='center', va='bottom',
                           fontsize=self.font_size-1,
                           fontweight='bold',
                           color='#333333')
        
        # 添加颜色条
        cbar = fig.colorbar(surf, ax=ax, shrink=0.6, aspect=20)
        cbar.set_label(self.z_label, fontsize=self.font_size)
        cbar.ax.tick_params(labelsize=self.font_size-1)
        
        # 美化
        ax.grid(True, alpha=0.2)
        ax.xaxis.pane.set_facecolor(self.background_color)
        ax.yaxis.pane.set_facecolor(self.background_color)
        ax.zaxis.pane.set_facecolor(self.background_color)
        
        plt.tight_layout()
        return self._to_base64(fig)