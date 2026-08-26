# chart_generators/pie_3d_chart.py
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from .base import ChartGenerator


class Pie3DChartGenerator(ChartGenerator):
    """3D饼图生成器"""
    
    def __init__(self, config):
        super().__init__(config)
        
        # 3D饼图特有参数
        self.data = self.config.get('data', [30, 25, 20, 15, 10])
        self.labels = self.config.get('labels', ['类别A', '类别B', '类别C', '类别D', '类别E'])
        self.colors = self.config.get('colors')
        self.show_percentage = self.config.get('show_percentage', True)
        self.show_values = self.config.get('show_values', True)
        self.elev = self.config.get('elev', 30)
        self.azim = self.config.get('azim', 45)
        self.pie_height = self.config.get('pie_height', 0.3)
        
        # 验证
        if not self.data:
            raise ValueError('数据不能为空')
        if self.labels and len(self.labels) != len(self.data):
            raise ValueError(f'标签数量({len(self.labels)})与数据数量({len(self.data)})不一致')
        if self.colors and len(self.colors) != len(self.data):
            raise ValueError(f'颜色数量({len(self.colors)})与数据数量({len(self.data)})不一致')
    
    def _draw_pie_segment(self, ax, start_angle, end_angle, radius, z_bottom, z_top, color, label):
        """绘制单个饼图扇形"""
        theta = np.linspace(np.radians(start_angle), np.radians(end_angle), 30)
        
        # 扇形顶面和底面的点
        x_top = radius * np.cos(theta)
        y_top = radius * np.sin(theta)
        x_bottom = x_top
        y_bottom = y_top
        
        # 绘制顶面（填充多边形）
        # 使用 plot_surface 绘制扇形顶面
        if len(theta) > 2:
            # 创建网格用于顶面
            r_vals = np.linspace(0, radius, 10)
            theta_vals = theta
            R, Theta = np.meshgrid(r_vals, theta_vals)
            X = R * np.cos(Theta)
            Y = R * np.sin(Theta)
            Z = np.full_like(X, z_top)
            ax.plot_surface(X, Y, Z, color=color, alpha=0.85, shade=True)
        
        # 绘制底面
        if len(theta) > 2:
            r_vals = np.linspace(0, radius, 10)
            theta_vals = theta
            R, Theta = np.meshgrid(r_vals, theta_vals)
            X = R * np.cos(Theta)
            Y = R * np.sin(Theta)
            Z = np.full_like(X, z_bottom)
            ax.plot_surface(X, Y, Z, color=color, alpha=0.6, shade=True)
        
        # 绘制侧面（外弧面）
        # 使用 plot_surface 绘制弧形侧面
        if len(theta) > 2:
            z_vals = np.linspace(z_bottom, z_top, 10)
            Theta_side, Z_side = np.meshgrid(theta, z_vals)
            X_side = radius * np.cos(Theta_side)
            Y_side = radius * np.sin(Theta_side)
            ax.plot_surface(X_side, Y_side, Z_side, color=color, alpha=0.8, shade=True)
        
        # 绘制两个半径边（侧面边界）
        for angle in [start_angle, end_angle]:
            rad = np.radians(angle)
            x_edge = [0, radius * np.cos(rad)]
            y_edge = [0, radius * np.sin(rad)]
            ax.plot(x_edge, y_edge, [z_bottom, z_bottom], color='white', linewidth=1)
            ax.plot(x_edge, y_edge, [z_top, z_top], color='white', linewidth=1)
            ax.plot([x_edge[0], x_edge[0]], [y_edge[0], y_edge[0]], [z_bottom, z_top], color='white', linewidth=1)
            ax.plot([x_edge[1], x_edge[1]], [y_edge[1], y_edge[1]], [z_bottom, z_top], color='white', linewidth=1)
        
        # 添加标签
        if label:
            mid_angle = np.radians((start_angle + end_angle) / 2)
            label_radius = radius * 0.6
            x_label = label_radius * np.cos(mid_angle)
            y_label = label_radius * np.sin(mid_angle)
            ax.text(x_label, y_label, z_top + self.pie_height * 0.3, label,
                   ha='center', va='center', fontsize=self.font_size-1,
                   fontweight='bold', color='#333333')
    
    def generate(self):
        """生成3D饼图"""
        fig = plt.figure(figsize=(self.fig_width, self.fig_height))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor(self.background_color)
        fig.patch.set_facecolor(self.background_color)
        
        # 准备数据
        total = sum(self.data)
        if total == 0:
            raise ValueError('数据总和不能为0')
        
        # 默认颜色
        if not self.colors:
            default_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
                              '#F7DC6F', '#BB8FCE', '#85C1E9', '#F1948A', '#82E0AA']
            self.colors = default_colors[:len(self.data)]
        
        # 计算角度
        angles = [0]
        for d in self.data[:-1]:
            angles.append(angles[-1] + d / total * 360)
        angles.append(360)
        
        # 半径和高度
        radius = 1.0
        z_bottom = 0
        z_top = self.pie_height
        
        # 绘制每个扇形
        for i, (value, color) in enumerate(zip(self.data, self.colors)):
            start_angle = angles[i]
            end_angle = angles[i + 1]
            
            # 构建标签
            label_text = None
            if self.labels and i < len(self.labels):
                label_text = self.labels[i]
                if self.show_percentage:
                    pct = value / total * 100
                    label_text += f'\n{pct:.1f}%'
                elif self.show_values:
                    label_text += f'\n{value}'
            
            self._draw_pie_segment(ax, start_angle, end_angle, radius, 
                                  z_bottom, z_top, color, label_text)
        
        # 设置视角和范围
        ax.view_init(elev=self.elev, azim=self.azim)
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_zlim(0, self.pie_height * 1.5)
        
        # 隐藏轴
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_zlabel('')
        
        # 设置标题
        ax.set_title(self.title, fontsize=self.title_font_size, fontweight='bold', pad=20)
        
        # 添加图例
        if self.labels:
            legend_elements = [plt.Rectangle((0, 0), 1, 1, facecolor=c, edgecolor='white', linewidth=1)
                              for c in self.colors[:len(self.labels)]]
            ax.legend(legend_elements, self.labels[:len(self.colors)], 
                     loc='center left', bbox_to_anchor=(1.1, 0.5), 
                     fontsize=self.font_size-1)
        
        plt.tight_layout()
        return self._to_base64(fig)