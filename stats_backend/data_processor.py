# stats_backend/data_processor.py
import pandas as pd
import numpy as np
import io
import re
from collections import Counter


class DataProcessor:
    """数据处理器"""
    
    def __init__(self):
        self.df = None
        self.headers = []
        self.data_preview = []
    
    def load_csv(self, file_content, encoding='utf-8'):
        """加载CSV文件"""
        try:
            self.df = pd.read_csv(io.BytesIO(file_content), encoding=encoding)
            self._clean_data()
            self._update_preview()
            return {'success': True, 'rows': len(self.df), 'cols': len(self.df.columns)}
        except UnicodeDecodeError:
            encodings = ['gbk', 'gb2312', 'gb18030', 'utf-8-sig', 'latin-1']
            for enc in encodings:
                try:
                    self.df = pd.read_csv(io.BytesIO(file_content), encoding=enc)
                    self._clean_data()
                    self._update_preview()
                    return {'success': True, 'rows': len(self.df), 'cols': len(self.df.columns)}
                except:
                    continue
            return {'success': False, 'error': '无法识别文件编码，请尝试保存为UTF-8格式'}
        except Exception as e:
            return {'success': False, 'error': f'CSV加载失败: {str(e)}'}
    
    def load_excel(self, file_content, sheet_name=0):
        """加载Excel文件"""
        try:
            self.df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name, engine='openpyxl')
            self._clean_data()
            self._update_preview()
            return {'success': True, 'rows': len(self.df), 'cols': len(self.df.columns)}
        except Exception as e:
            try:
                self.df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name, engine='xlrd')
                self._clean_data()
                self._update_preview()
                return {'success': True, 'rows': len(self.df), 'cols': len(self.df.columns)}
            except:
                return {'success': False, 'error': f'Excel加载失败: {str(e)}'}
    
    def load_text_table(self, text_content):
        """从文本粘贴加载表格数据"""
        try:
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            if not lines:
                return {'success': False, 'error': '没有有效数据'}
            
            delimiter = None
            for line in lines:
                if '\t' in line:
                    delimiter = '\t'
                    break
                elif ',' in line:
                    delimiter = ','
                    break
            
            if delimiter:
                data = [line.split(delimiter) for line in lines]
            else:
                data = [re.split(r'\s+', line) for line in lines]
            
            self.df = pd.DataFrame(data)
            
            if len(self.df) > 0:
                first_row = self.df.iloc[0].astype(str)
                has_header = False
                for val in first_row:
                    if isinstance(val, str) and any(c.isalpha() or '\u4e00' <= c <= '\u9fff' for c in val):
                        has_header = True
                        break
                
                if has_header:
                    self.df.columns = first_row
                    self.df = self.df.iloc[1:].reset_index(drop=True)
            
            self._clean_data()
            self._update_preview()
            return {'success': True, 'rows': len(self.df), 'cols': len(self.df.columns)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _clean_data(self):
        """清洗数据，尝试将字符串转换为数值"""
        if self.df is None or self.df.empty:
            return
        
        for col in self.df.columns:
            try:
                self.df[col] = pd.to_numeric(self.df[col], errors='ignore')
            except:
                pass
            
            if self.df[col].dtype == 'object':
                def try_parse_num(val):
                    if pd.isna(val) or val == '':
                        return np.nan
                    if isinstance(val, (int, float)):
                        return val
                    if isinstance(val, str):
                        cleaned = re.sub(r'[^\d.\-eE+]', '', val.strip())
                        if cleaned:
                            try:
                                return float(cleaned)
                            except:
                                pass
                    return val
                
                self.df[col] = self.df[col].apply(try_parse_num)
    
    def _update_preview(self):
        """更新预览数据"""
        if self.df is None or self.df.empty:
            self.headers = []
            self.data_preview = []
            return
        
        self.headers = self.df.columns.tolist()
        preview_rows = min(100, len(self.df))
        self.data_preview = self.df.head(preview_rows).values.tolist()
    
    def get_preview(self, start_row=0, max_rows=50):
        """获取数据预览"""
        if self.df is None or self.df.empty:
            return {'headers': [], 'data': [], 'total_rows': 0}
        
        end_row = min(start_row + max_rows, len(self.df))
        data = self.df.iloc[start_row:end_row].values.tolist()
        
        return {
            'headers': self.headers,
            'data': data,
            'total_rows': len(self.df),
            'start_row': start_row,
            'end_row': end_row
        }
    
    def _safe_float(self, val):
        """安全转换为浮点数 - 严格模式"""
        if pd.isna(val) or val is None or val == '':
            return None
        if isinstance(val, (int, float)):
            if np.isnan(val) or np.isinf(val):
                return None
            return float(val)
        if isinstance(val, str):
            cleaned = re.sub(r'[^\d.\-eE+]', '', val.strip())
            if cleaned:
                try:
                    num = float(cleaned)
                    if not np.isnan(num) and not np.isinf(num):
                        return num
                except:
                    pass
        return None

    def extract_data(self, mode='row', index=0, start_row=0, start_col=0, allow_non_numeric=False):
        """
        提取数据
        
        参数:
            mode: 'row', 'col', 'all'
            index: 行或列的索引（0=表头/行索引）
            allow_non_numeric: 是否允许非数值数据
            start_row: 起始行
            start_col: 起始列
        """
        if self.df is None or self.df.empty:
            return {'success': False, 'error': '没有数据'}
        
        # ===== 按行提取 =====
        if mode == 'row':
            if index == 0:
                header_values = self.df.columns.tolist()[start_col:]
                return {
                    'success': True,
                    'values': [],
                    'raw_data': [header_values],
                    'header_data': header_values,
                    'label': '表头',
                    'source_label': f'表头 (列名) [从列 {start_col} 开始]',
                    'mode': 'row',
                    'index': 0,
                    'count': len(header_values),
                    'has_non_numeric': True,
                    'is_header': True
                }
            
            data_index = index - 1
            if data_index >= len(self.df):
                return {'success': False, 'error': f'行 {index} 不存在，当前有 {len(self.df)} 行数据'}
            
            row_series = self.df.iloc[data_index]
            if start_col > 0:
                row_series = row_series.iloc[start_col:]
            
            raw_values = []
            numeric_values = []
            non_numeric_found = False
            non_numeric_examples = []
            
            for val in row_series:
                raw_values.append(str(val))
                num = self._safe_float(val)
                if num is not None:
                    numeric_values.append(num)
                else:
                    non_numeric_found = True
                    if len(non_numeric_examples) < 3:
                        non_numeric_examples.append(str(val))
            
            # 不允许非数值数据
            if not allow_non_numeric:
                if non_numeric_found and not numeric_values:
                    examples = ', '.join(non_numeric_examples)
                    return {'success': False, 'error': f'行 {index} 从第 {start_col} 列开始全部为非数值，请开启"允许非数值数据"\n非数值示例: {examples}'}
                
                if non_numeric_found and numeric_values:
                    return {
                        'success': True,
                        'values': numeric_values,
                        'raw_data': [raw_values],
                        'header_data': self.df.columns.tolist()[start_col:],
                        'label': f'行{index}',
                        'source_label': f'行 {index} (从列 {start_col} 开始) [已忽略非数值]',
                        'mode': 'row',
                        'index': index,
                        'count': len(numeric_values),
                        'has_non_numeric': False,
                        'is_header': False,
                        'non_numeric_ignored': True
                    }
                
                if not numeric_values:
                    return {'success': False, 'error': f'行 {index} 从第 {start_col} 列开始没有数值数据'}
            
            # 允许非数值数据
            if allow_non_numeric:
                return {
                    'success': True,
                    'values': numeric_values,
                    'raw_data': [raw_values],
                    'header_data': self.df.columns.tolist()[start_col:],
                    'label': f'行{index}',
                    'source_label': f'行 {index} (从列 {start_col} 开始) [含非数值]',
                    'mode': 'row',
                    'index': index,
                    'count': len(raw_values),
                    'has_non_numeric': True,
                    'is_header': False
                }
            
            return {
                'success': True,
                'values': numeric_values,
                'raw_data': [raw_values],
                'header_data': self.df.columns.tolist()[start_col:],
                'label': f'行{index}',
                'source_label': f'行 {index} (从列 {start_col} 开始)',
                'mode': 'row',
                'index': index,
                'count': len(numeric_values),
                'has_non_numeric': False,
                'is_header': False
            }
        
        # ===== 按列提取 =====
        if mode == 'col':
            if index == 0:
                row_labels = self.df.index.tolist()[start_row:]
                return {
                    'success': True,
                    'values': [],
                    'raw_data': [row_labels],
                    'header_data': row_labels,
                    'label': '行索引',
                    'source_label': f'行索引 (从行 {start_row} 开始)',
                    'mode': 'col',
                    'index': 0,
                    'count': len(row_labels),
                    'has_non_numeric': True,
                    'is_header': True
                }
            
            col_index = index - 1
            if col_index >= len(self.df.columns):
                return {'success': False, 'error': f'列 {index} 不存在，当前有 {len(self.df.columns)} 列'}
            
            col_name = self.df.columns[col_index]
            col_data = self.df[col_name].iloc[start_row:]
            
            raw_values = []
            numeric_values = []
            non_numeric_found = False
            non_numeric_examples = []
            
            for val in col_data:
                raw_values.append(str(val))
                num = self._safe_float(val)
                if num is not None:
                    numeric_values.append(num)
                else:
                    non_numeric_found = True
                    if len(non_numeric_examples) < 3:
                        non_numeric_examples.append(str(val))
            
            if not allow_non_numeric:
                if non_numeric_found and not numeric_values:
                    examples = ', '.join(non_numeric_examples)
                    return {'success': False, 'error': f'列 "{col_name}" 从第 {start_row} 行开始全部为非数值，请开启"允许非数值数据"\n非数值示例: {examples}'}
                
                if non_numeric_found and numeric_values:
                    return {
                        'success': True,
                        'values': numeric_values,
                        'raw_data': [raw_values],
                        'header_data': [col_name],
                        'label': col_name,
                        'source_label': f'列 "{col_name}" (从行 {start_row} 开始) [已忽略非数值]',
                        'mode': 'col',
                        'index': index,
                        'count': len(numeric_values),
                        'has_non_numeric': False,
                        'is_header': False,
                        'non_numeric_ignored': True
                    }
                
                if not numeric_values:
                    return {'success': False, 'error': f'列 "{col_name}" 从第 {start_row} 行开始没有数值数据'}
            
            if allow_non_numeric:
                return {
                    'success': True,
                    'values': numeric_values,
                    'raw_data': [raw_values],
                    'header_data': [col_name],
                    'label': col_name,
                    'source_label': f'列 "{col_name}" (从行 {start_row} 开始) [含非数值]',
                    'mode': 'col',
                    'index': index,
                    'count': len(raw_values),
                    'has_non_numeric': True,
                    'is_header': False
                }
            
            return {
                'success': True,
                'values': numeric_values,
                'raw_data': [raw_values],
                'header_data': [col_name],
                'label': col_name,
                'source_label': f'列 "{col_name}" (从行 {start_row} 开始)',
                'mode': 'col',
                'index': index,
                'count': len(numeric_values),
                'has_non_numeric': False,
                'is_header': False
            }
        
        # ===== 全部数据模式 =====
        if mode == 'all':
            data_slice = self.df.iloc[start_row:, start_col:]
            
            if data_slice.empty:
                return {'success': False, 'error': '指定位置没有数据'}
            
            # ✅ 如果允许非数值数据
            if allow_non_numeric:
                header_row = data_slice.columns.tolist()
                raw_data = []
                numeric_values = []
                for idx, row in data_slice.iterrows():
                    row_values = []
                    for val in row:
                        row_values.append(str(val))
                        num = self._safe_float(val)
                        if num is not None:
                            numeric_values.append(num)
                    raw_data.append(row_values)
                
                return {
                    'success': True,
                    'values': numeric_values,
                    'raw_data': raw_data,
                    'header_data': header_row,
                    'label': '全部数据',
                    'source_label': f'全部数据 (行{start_row + 1}→, 列{start_col + 1}→) [含非数值]',
                    'mode': 'all',
                    'index': 0,
                    'count': len(numeric_values),
                    'has_non_numeric': True,
                    'is_header': False
                }
            
            # ✅ 不允许非数值数据：只提取数值列中的数值
            # 先找出哪些列是数值列
            numeric_cols = []
            for col in data_slice.columns:
                # 检查这一列是否全部是数值
                col_data = data_slice[col]
                all_numeric = True
                for val in col_data:
                    if self._safe_float(val) is None:
                        all_numeric = False
                        break
                if all_numeric:
                    numeric_cols.append(col)
            
            # 如果没有数值列
            if not numeric_cols:
                return {
                    'success': False, 
                    'error': f'从第 {start_row + 1} 行第 {start_col + 1} 列开始没有数值列，请开启"允许非数值数据"'
                }
            
            # 只提取数值列的数据
            values = []
            raw_data = []
            for idx, row in data_slice[numeric_cols].iterrows():
                row_values = []
                for val in row:
                    row_values.append(val)
                    num = self._safe_float(val)
                    if num is not None:
                        values.append(num)
                raw_data.append(row_values)
            
            if not values:
                return {'success': False, 'error': f'从第 {start_row + 1} 行第 {start_col + 1} 列开始没有数值数据'}
            
            return {
                'success': True,
                'values': values,
                'raw_data': raw_data,
                'header_data': data_slice.columns.tolist(),
                'label': '全部数据',
                'source_label': f'全部数据 (行{start_row + 1}→, 列{start_col + 1}→) [仅数值列]',
                'mode': 'all',
                'index': 0,
                'count': len(values),
                'has_non_numeric': False,
                'is_header': False,
                'non_numeric_ignored': True
            }
        
        return {'success': False, 'error': f'不支持的提取模式: {mode}'}
    def transpose_data(self):
        """行列互换（转置）"""
        if self.df is None or self.df.empty:
            return {'success': False, 'error': '没有数据'}
        
        old_columns = self.df.columns.tolist()
        old_index = self.df.index.tolist()
        
        self.df = self.df.T
        self.df.columns = old_index
        self.df.index = old_columns
        
        self._update_preview()
        return {
            'success': True,
            'rows': len(self.df),
            'cols': len(self.df.columns),
            'message': f'转置成功：{len(self.df)} 行 × {len(self.df.columns)} 列'
        }
    
    def calculate_stats(self, values):
        """计算统计指标"""
        if not values:
            return None
        
        n = len(values)
        sorted_vals = sorted(values)
        
        sum_val = sum(values)
        mean = sum_val / n
        variance = sum((v - mean) ** 2 for v in values) / (n - 1) if n > 1 else 0
        std = variance ** 0.5 if variance > 0 else 0
        
        max_val = max(values)
        min_val = min(values)
        range_val = max_val - min_val
        
        if n % 2 == 0:
            median = (sorted_vals[n//2 - 1] + sorted_vals[n//2]) / 2
        else:
            median = sorted_vals[n//2]
        
        counter = Counter(values)
        max_freq = max(counter.values())
        modes = [str(k) for k, v in counter.items() if v == max_freq]
        
        return {
            'count': n,
            'sum': sum_val,
            'mean': mean,
            'variance': variance,
            'std': std,
            'max': max_val,
            'min': min_val,
            'range': range_val,
            'median': median,
            'mode': ', '.join(modes) if modes else '无',
            'sorted': sorted_vals
        }
    
    def get_headers(self):
        return self.headers if self.df is not None else []
    
    def get_row_count(self):
        return len(self.df) if self.df is not None else 0