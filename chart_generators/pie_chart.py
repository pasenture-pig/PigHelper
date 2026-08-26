# chart_generators/pie_chart.py
import matplotlib.pyplot as plt
import numpy as np
from .base import ChartGenerator


class PieChartGenerator(ChartGenerator):
    """饼图生成器"""
    
    def __init__(self, config):
        super().__init__(config)
        
        # 饼图特有参数
        self.data = self.config.get('data', [30, 25, 20, 15, 10])
        self.labels = self.config.get('labels')
        self.colors = self.config.get('colors')
        self.explode = self.config.get('explode')
        self.start_angle = self.config.get('start_angle', 90)
        self.shadow = self.config.get('shadow', True)
        self.show_legend = self.config.get('show_legend', True)
        self.show_percentage = self.config.get('show_percentage', True)
        self.show_values = self.config.get('show_values', True)
        
        # 验证数据
        if not self.data:
            raise ValueError('数据不能为空')
        
        # 验证标签
        if self.labels and len(self.labels) != len(self.data):
            raise ValueError(
                f'标签数量({len(self.labels)})与数据数量({len(self.data)})不一致'
            )
        
        # 验证颜色
        if self.colors and len(self.colors) != len(self.data):
            raise ValueError(
                f'颜色数量({len(self.colors)})与数据数量({len(self.data)})不一致'
            )
        
        # 验证扇形分离
        if self.explode:
            if len(self.explode) != len(self.data):
                raise ValueError(
                    f'扇形分离参数数量({len(self.explode)})与数据数量({len(self.data)})不一致'
                )
            # 限制范围 0-0.5
            self.explode = [max(0, min(0.5, v)) for v in self.explode]
        
        # 默认颜色
        if not self.colors:
            default_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
                              '#F7DC6F', '#BB8FCE', '#85C1E9', '#F1948A', '#82E0AA']
            self.colors = default_colors[:len(self.data)]
    
    def generate(self):
        """生成饼图"""
        fig, ax = self._create_figure()
        
        # 准备标签
        labels = self.labels if self.labels else [f'类别{i+1}' for i in range(len(self.data))]
        
        # 准备扇形分离
        explode_list = self.explode if self.explode else [0] * len(self.data)
        
        # 准备百分比显示
        autopct = None
        if self.show_percentage and self.show_values:
            total = sum(self.data)
            autopct = lambda pct: f'{pct:.1f}%\n({int(pct/100*total)})' if total > 0 else f'{pct:.1f}%'
        elif self.show_percentage:
            autopct = '%1.1f%%'
        elif self.show_values:
            total = sum(self.data)
            autopct = lambda pct: f'{int(pct/100*total)}'
        
        # 绘制饼图
        wedges, texts, autotexts = ax.pie(
            self.data,
            labels=labels if not (self.show_values or self.show_percentage) else None,
            colors=self.colors,
            explode=explode_list,
            autopct=autopct,
            startangle=self.start_angle,
            shadow=self.shadow,
            textprops={'fontsize': self.font_size},
            pctdistance=0.85 if self.show_values and self.show_percentage else 0.6
        )
        
        # 如果只显示数值，显示在扇形外
        if self.show_values and not self.show_percentage:
            for wedge, value in zip(wedges, self.data):
                ang = (wedge.theta2 + wedge.theta1) / 2
                x = 1.1 * np.cos(np.radians(ang))
                y = 1.1 * np.sin(np.radians(ang))
                ax.text(x, y, str(value), ha='center', va='center', fontsize=self.font_size)
        
        # 设置标题
        ax.set_title(self.title, fontsize=self.title_font_size, fontweight='bold', pad=20)
        
        # 确保饼图是圆的
        ax.axis('equal')
        
        # 添加图例
        if self.show_legend and labels:
            ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=self.font_size)
        
        plt.tight_layout()
        return self._to_base64(fig)