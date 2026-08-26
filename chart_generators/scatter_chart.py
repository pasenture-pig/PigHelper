# chart_generators/scatter_chart.py
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
from .base import ChartGenerator


class ScatterChartGenerator(ChartGenerator):
    """散点图生成器"""
    
    def __init__(self, config):
        super().__init__(config)
        
        # 散点图特有参数
        self.x_data = self.config.get('x_data', [1, 2, 3, 4, 5, 6, 7, 8])
        self.y_data = self.config.get('y_data', [2, 4, 1, 5, 3, 7, 6, 8])
        self.x_label = self.config.get('x_label', 'X轴')
        self.y_label = self.config.get('y_label', 'Y轴')
        self.color = self.config.get('color', '#667eea')
        self.trend_color = self.config.get('trend_color', '#FF6B6B')
        self.point_size = self.config.get('size', 80)
        self.alpha = self.config.get('alpha', 0.7)
        
        # 拟合相关参数
        self.fit_type = self.config.get('fit_type', 'linear')
        self.fit_degree = self.config.get('fit_degree', 1)
        self.show_fit = self.config.get('show_fit', True)
        self.show_confidence_band = self.config.get('show_confidence_band', False)
        
        # 验证数据
        if not self.x_data or not self.y_data:
            raise ValueError('X轴和Y轴数据不能为空')
        
        if len(self.x_data) != len(self.y_data):
            raise ValueError(
                f'X轴数据数量({len(self.x_data)})与Y轴数据数量({len(self.y_data)})不一致'
            )
        
        if self.fit_degree < 1 or self.fit_degree > 8:
            raise ValueError('多项式拟合阶数必须在 1-8 之间')
        
        if self.fit_degree >= len(self.x_data):
            raise ValueError(f'拟合阶数({self.fit_degree})不能大于等于数据点数量({len(self.x_data)})')
        
        self.fit_result = None
    
    def _to_serializable(self, obj):
        """将 numpy 类型转换为 Python 原生类型"""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, dict):
            return {k: self._to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._to_serializable(v) for v in obj]
        else:
            return obj
    
    def _linear_fit(self, x, y):
        """线性拟合"""
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        r2 = r_value ** 2
        
        def func(x_vals):
            return slope * x_vals + intercept
        
        params = {
            'slope': float(slope),
            'intercept': float(intercept),
            'r2': float(r2),
            'std_err': float(std_err),
            'p_value': float(p_value)
        }
        
        display_text = f'y = {slope:.4f}x + {intercept:.4f}\nR² = {r2:.4f}'
        
        return func, r2, params, display_text
    
    def _polynomial_fit(self, x, y, degree):
        """多项式拟合"""
        coeffs = np.polyfit(x, y, degree)
        p = np.poly1d(coeffs)
        
        y_pred = p(x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        def func(x_vals):
            return p(x_vals)
        
        params = {
            'coeffs': coeffs.tolist(),
            'degree': int(degree),
            'r2': float(r2)
        }
        
        # 生成多项式显示文本
        terms = []
        for i, coeff in enumerate(reversed(coeffs)):
            power = degree - i
            if power == 0:
                terms.append(f'{coeff:.4f}')
            elif power == 1:
                terms.append(f'{coeff:.4f}x')
            else:
                terms.append(f'{coeff:.4f}x^{power}')
        
        display_parts = []
        for i, term in enumerate(terms):
            if i == 0:
                display_parts.append(term)
            else:
                if term.startswith('-'):
                    display_parts.append(f' - {term[1:]}')
                else:
                    display_parts.append(f' + {term}')
        
        display_text = 'y = ' + ' '.join(display_parts) + f'\nR² = {r2:.4f}'
        
        return func, r2, params, display_text
    
    def _gaussian_fit(self, x, y):
        """高斯拟合"""
        def gaussian(x_vals, amplitude, mu, sigma, offset):
            return amplitude * np.exp(-((x_vals - mu) ** 2) / (2 * sigma ** 2)) + offset
        
        amplitude_guess = max(y) - min(y)
        mu_guess = x[np.argmax(y)]
        sigma_guess = (max(x) - min(x)) / 6
        offset_guess = min(y)
        
        try:
            popt, pcov = curve_fit(
                gaussian, x, y,
                p0=[amplitude_guess, mu_guess, sigma_guess, offset_guess],
                maxfev=5000
            )
            
            y_pred = gaussian(x, *popt)
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            def func(x_vals):
                return gaussian(x_vals, *popt)
            
            params = {
                'amplitude': float(popt[0]),
                'mu': float(popt[1]),
                'sigma': float(popt[2]),
                'offset': float(popt[3]),
                'r2': float(r2)
            }
            
            display_text = (f'A = {popt[0]:.4f}\n'
                          f'μ = {popt[1]:.4f}\n'
                          f'σ = {popt[2]:.4f}\n'
                          f'offset = {popt[3]:.4f}\n'
                          f'R² = {r2:.4f}')
            
            return func, r2, params, display_text
            
        except Exception as e:
            print(f'高斯拟合失败: {e}，降级为线性拟合')
            return self._linear_fit(x, y)
    
    def _get_fit_label(self, fit_type, r2, degree=None):
        """获取拟合曲线标签（使用普通文本避免字体问题）"""
        # ✅ 使用普通文本 R2 而不是 R²，避免字体支持问题
        if fit_type == 'linear':
            return f'线性拟合 (R2={r2:.4f})'
        elif fit_type == 'polynomial':
            degree_names = ['', '一次', '二次', '三次', '四次', '五次', '六次', '七次', '八次']
            name = degree_names[degree] if degree <= 8 else f'{degree}次'
            return f'{name}多项式拟合 (R2={r2:.4f})'
        elif fit_type == 'gaussian':
            return f'高斯拟合 (R2={r2:.4f})'
        return f'拟合曲线 (R2={r2:.4f})'
    
    def _calculate_confidence_band(self, x, y, func):
        """计算置信带"""
        n = len(x)
        y_pred = func(x)
        residuals = y - y_pred
        mse = np.sum(residuals ** 2) / (n - 2) if n > 2 else 0
        se = np.sqrt(mse) if mse > 0 else 0
        
        if n > 2 and se > 0:
            t_val = stats.t.ppf(0.975, n - 2)
            ci = t_val * se
        else:
            ci = se * 1.96
        
        return y_pred - ci, y_pred + ci
    
    def generate(self):
        """生成散点图"""
        fig, ax = self._create_figure()
        
        # 绘制散点图
        ax.scatter(self.x_data, self.y_data,
                   c=self.color,
                   s=self.point_size,
                   alpha=self.alpha,
                   edgecolors='white',
                   linewidth=1.5,
                   zorder=2,
                   label='数据点')
        
        # 拟合曲线
        if self.show_fit and len(self.x_data) > 1:
            x_sorted = np.array(sorted(self.x_data))
            x_line = np.linspace(min(x_sorted), max(x_sorted), 200)
            
            if self.fit_type == 'linear':
                fit_func, r2, params, display_text = self._linear_fit(self.x_data, self.y_data)
                label = self._get_fit_label('linear', r2)
            elif self.fit_type == 'polynomial':
                fit_func, r2, params, display_text = self._polynomial_fit(
                    self.x_data, self.y_data, self.fit_degree
                )
                label = self._get_fit_label('polynomial', r2, self.fit_degree)
            elif self.fit_type == 'gaussian':
                fit_func, r2, params, display_text = self._gaussian_fit(self.x_data, self.y_data)
                label = self._get_fit_label('gaussian', r2)
            else:
                fit_func, r2, params, display_text = self._linear_fit(self.x_data, self.y_data)
                label = self._get_fit_label('linear', r2)
            
            # ✅ 存储拟合结果
            self.fit_result = {
                'type': self.fit_type,
                'r2': float(r2),
                'display_text': display_text,
                'params': self._to_serializable(params)
            }
            
            # 绘制拟合曲线
            y_line = fit_func(x_line)
            ax.plot(x_line, y_line,
                    color=self.trend_color,
                    linestyle='-',
                    linewidth=2.5,
                    alpha=0.9,
                    label=label,
                    zorder=1)
            
            if self.show_confidence_band and len(self.x_data) > 2:
                y_lower, y_upper = self._calculate_confidence_band(
                    np.array(self.x_data), np.array(self.y_data), fit_func
                )
                ax.fill_between(
                    x_sorted,
                    y_lower,
                    y_upper,
                    color=self.trend_color,
                    alpha=0.15,
                    label='95% 置信区间'
                )
            
            ax.legend(loc='best', fontsize=self.font_size)
        
        self._set_title_and_labels(ax, self.x_label, self.y_label)
        self._apply_axis_limits(ax)
        self._apply_grid(ax)
        self._beautify_axes(ax)
        
        plt.tight_layout()
        
        result = self._to_base64(fig)
        
        # ✅ 始终返回包含 fit_info 的字典（即使没有拟合）
        if self.fit_result:
            return {
                'image': result,
                'fit_info': self.fit_result
            }
        else:
            return {
                'image': result,
                'fit_info': None
            }


def generate_scatter_chart(config):
    """生成散点图（兼容旧版本）"""
    generator = ScatterChartGenerator(config)
    result = generator.generate()
    if isinstance(result, dict):
        return result
    return {'image': result, 'fit_info': None}