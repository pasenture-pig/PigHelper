# chart_generators/base.py
import matplotlib
matplotlib.use('Agg')  # 非交互式后端

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import base64
from io import BytesIO
from abc import ABC, abstractmethod
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChartGenerator(ABC):
    """图表生成器基类"""
    
    # 类级别字体配置（所有子类共享）
    _font_configured = False
    
    def __init__(self, config):
        """
        初始化图表生成器
        
        参数:
            config: 图表配置字典
        """
        self.config = config
        self._setup_font()
        self._extract_common_params()
    
    @classmethod
    def _setup_font(cls):
        """配置中文字体（只执行一次）"""
        if cls._font_configured:
            return
        
        system = platform.system()
        
        font_candidates = []
        if system == 'Windows':
            font_candidates = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 'FangSong']
        elif system == 'Darwin':
            font_candidates = ['PingFang SC', 'Heiti SC', 'STSong', 'Apple LiGothic', 'Arial Unicode MS']
        else:
            font_candidates = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'SimHei', 'DejaVu Sans']
        
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        selected_font = None
        for font in font_candidates:
            if font in available_fonts:
                selected_font = font
                logger.info(f'✅ 使用中文字体: {font}')
                break
        
        if not selected_font:
            selected_font = 'sans-serif'
            logger.warning('⚠️ 未找到中文字体，中文可能显示为方块')
        
        plt.rcParams['font.sans-serif'] = [selected_font] + plt.rcParams['font.sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
        
        # ✅ 启用数学文本支持
        plt.rcParams['mathtext.default'] = 'regular'
        
        cls._font_configured = True
    
    def _extract_common_params(self):
        """提取通用参数"""
        self.title = self.config.get('title', '图表')
        self.font_size = self.config.get('font_size', 12)
        self.title_font_size = self.config.get('title_font_size', 16)
        self.fig_width = self.config.get('fig_width', 10)
        self.fig_height = self.config.get('fig_height', 6)
        self.background_color = self.config.get('background_color', '#ffffff')
        self.show_grid = self.config.get('show_grid', True)
        self.show_values = self.config.get('show_values', True)
        
        # 轴范围
        self.x_min = self.config.get('x_min')
        self.x_max = self.config.get('x_max')
        self.y_min = self.config.get('y_min')
        self.y_max = self.config.get('y_max')
    
    def _create_figure(self):
        """创建图形和坐标轴"""
        fig, ax = plt.subplots(figsize=(self.fig_width, self.fig_height))
        fig.patch.set_facecolor(self.background_color)
        ax.set_facecolor(self.background_color)
        return fig, ax
    
    def _apply_axis_limits(self, ax):
        """应用轴范围限制"""
        if self.x_min is not None:
            ax.set_xlim(left=float(self.x_min))
        if self.x_max is not None:
            ax.set_xlim(right=float(self.x_max))
        if self.y_min is not None:
            ax.set_ylim(bottom=float(self.y_min))
        if self.y_max is not None:
            ax.set_ylim(top=float(self.y_max))
    
    def _apply_grid(self, ax):
        """应用网格线"""
        if self.show_grid:
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
            ax.set_axisbelow(True)
    
    def _beautify_axes(self, ax):
        """美化坐标轴边框"""
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_color('#cccccc')
    
    def _set_title_and_labels(self, ax, x_label=None, y_label=None):
        """设置标题和轴标签"""
        ax.set_title(self.title, fontsize=self.title_font_size, fontweight='bold', pad=20)
        if x_label:
            ax.set_xlabel(x_label, fontsize=self.font_size)
        if y_label:
            ax.set_ylabel(y_label, fontsize=self.font_size)
        ax.tick_params(axis='both', labelsize=self.font_size)
    
    def _to_base64(self, fig):
        """将图形转换为base64字符串"""
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight',
                    facecolor=fig.get_facecolor(), edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        return f'data:image/png;base64,{image_base64}'
    
    @abstractmethod
    def generate(self):
        """
        生成图表（子类必须实现）
        
        返回:
            base64编码的图片字符串
        """
        pass
    
    @staticmethod
    def parse_data(data_str):
        """解析逗号分隔的数据"""
        if not data_str or not data_str.strip():
            return []
        return [float(x.strip()) for x in data_str.split(',') if x.strip()]
    
    @staticmethod
    def parse_string_list(data_str):
        """解析逗号分隔的字符串列表"""
        if not data_str or not data_str.strip():
            return []
        return [x.strip() for x in data_str.split(',') if x.strip()]
    
    @staticmethod
    def validate_data_length(data, data_name, expected_len, list_name=''):
        """验证数据长度是否匹配"""
        if data and len(data) != expected_len:
            raise ValueError(
                f'{data_name}数量({len(data)})与{list_name}数量({expected_len})不一致'
            )
        return True