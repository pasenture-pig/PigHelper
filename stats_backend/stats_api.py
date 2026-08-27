# stats_backend/stats_api.py
from flask import Blueprint, request, jsonify
from .data_processor import DataProcessor

stats_bp = Blueprint('stats', __name__, url_prefix='/api/stats')

data_processor = DataProcessor()


@stats_bp.route('/upload', methods=['POST'])
@stats_bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有上传文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '文件名为空'})
        
        # 获取文件内容
        file_content = file.read()
        filename = file.filename.lower()
        
        # 根据文件扩展名选择加载方法
        if filename.endswith('.csv'):
            encoding = request.form.get('encoding', 'utf-8')
            result = data_processor.load_csv(file_content, encoding)
        elif filename.endswith('.xlsx'):
            result = data_processor.load_excel(file_content, sheet_name=0)
        elif filename.endswith('.xls'):
            # 旧版 Excel 格式
            try:
                result = data_processor.load_excel(file_content, sheet_name=0)
            except:
                return jsonify({'success': False, 'error': '无法读取 .xls 文件，请转换为 .xlsx 格式'})
        else:
            return jsonify({'success': False, 'error': '不支持的文件格式，请上传 CSV 或 Excel 文件 (.csv, .xlsx, .xls)'})
        
        if result.get('success'):
            preview = data_processor.get_preview(start_row=0, max_rows=50)
            return jsonify({
                'success': True,
                'info': {
                    'rows': result.get('rows', 0),
                    'cols': result.get('cols', 0),
                    'filename': file.filename
                },
                'preview': preview
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', '加载失败')})
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@stats_bp.route('/paste', methods=['POST'])
def paste_data():
    try:
        data = request.get_json()
        text_content = data.get('text', '')
        if not text_content:
            return jsonify({'success': False, 'error': '没有数据'})
        
        result = data_processor.load_text_table(text_content)
        if result.get('success'):
            preview = data_processor.get_preview(start_row=0, max_rows=50)
            return jsonify({
                'success': True,
                'info': {
                    'rows': result.get('rows', 0),
                    'cols': result.get('cols', 0)
                },
                'preview': preview
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', '加载失败')})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@stats_bp.route('/preview', methods=['POST'])
def get_preview():
    try:
        data = request.get_json()
        start_row = data.get('start_row', 0)
        max_rows = data.get('max_rows', 50)
        
        preview = data_processor.get_preview(start_row, max_rows)
        return jsonify({
            'success': True,
            'preview': preview
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@stats_bp.route('/analyze', methods=['POST'])
def analyze_data():
    try:
        data = request.get_json()
        mode = data.get('mode', 'row')
        index = data.get('index', 0)
        allow_non_numeric = data.get('allow_non_numeric', False)
        start_row = data.get('start_row', 0)
        start_col = data.get('start_col', 0)
        
        if data_processor.df is None or data_processor.df.empty:
            return jsonify({'success': False, 'error': '没有数据，请先上传或粘贴数据'})
        
        extracted = data_processor.extract_data(mode, index, start_row, start_col, allow_non_numeric)
        if not extracted.get('success'):
            return jsonify({'success': False, 'error': extracted.get('error', '提取失败')})
        
        is_header = extracted.get('is_header', False)
        has_non_numeric = extracted.get('has_non_numeric', False)
        
        if is_header:
            return jsonify({
                'success': True,
                'extracted': {
                    'values': extracted.get('raw_data', []),
                    'header_data': extracted.get('header_data', []),
                    'label': extracted.get('label', ''),
                    'source_label': extracted.get('source_label', ''),
                    'mode': extracted.get('mode', ''),
                    'index': extracted.get('index', 0),
                    'count': extracted.get('count', 0),
                    'has_non_numeric': True,
                    'is_header': True
                },
                'stats': None,
                'has_non_numeric': True,
                'is_header': True
            })
        
        if has_non_numeric:
            return jsonify({
                'success': True,
                'extracted': {
                    'values': extracted.get('values', []),
                    'raw_data': extracted.get('raw_data', []),
                    'header_data': extracted.get('header_data', []),
                    'label': extracted.get('label', ''),
                    'source_label': extracted.get('source_label', ''),
                    'mode': extracted.get('mode', ''),
                    'index': extracted.get('index', 0),
                    'count': extracted.get('count', 0),
                    'has_non_numeric': True,
                    'is_header': False
                },
                'stats': None,
                'has_non_numeric': True,
                'is_header': False
            })
        
        stats = data_processor.calculate_stats(extracted['values'])
        if not stats:
            return jsonify({'success': False, 'error': '计算统计指标失败'})
        
        return jsonify({
            'success': True,
            'extracted': {
                'values': extracted['values'],
                'raw_data': extracted.get('raw_data', []),
                'header_data': extracted.get('header_data', []),
                'label': extracted.get('label', ''),
                'source_label': extracted.get('source_label', ''),
                'mode': extracted.get('mode', ''),
                'index': extracted.get('index', 0),
                'count': extracted.get('count', 0),
                'has_non_numeric': False,
                'is_header': False
            },
            'stats': stats,
            'has_non_numeric': False,
            'is_header': False
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@stats_bp.route('/reset', methods=['POST'])
def reset_data():
    global data_processor
    data_processor = DataProcessor()
    return jsonify({'success': True})


@stats_bp.route('/info', methods=['GET'])
def get_info():
    if data_processor.df is None:
        return jsonify({'success': True, 'has_data': False})
    
    return jsonify({
        'success': True,
        'has_data': True,
        'rows': len(data_processor.df),
        'cols': len(data_processor.df.columns),
        'headers': data_processor.headers
    })


@stats_bp.route('/transpose', methods=['POST'])
def transpose_data():
    """行列互换"""
    try:
        if data_processor.df is None or data_processor.df.empty:
            return jsonify({'success': False, 'error': '没有数据'})
        
        result = data_processor.transpose_data()
        if not result.get('success'):
            return jsonify({'success': False, 'error': result.get('error', '转置失败')})
        
        preview = data_processor.get_preview(start_row=0, max_rows=50)
        return jsonify({
            'success': True,
            'message': result.get('message', '转置成功'),
            'info': {
                'rows': result.get('rows', 0),
                'cols': result.get('cols', 0)
            },
            'preview': preview
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})