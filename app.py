#包装器
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from chart_generator import generate_chart  # 导入你的核心函数
import io
import base64
from PIL import Image

app = Flask(__name__)
CORS(app)

# 路由1：提供前端页面
@app.route('/')
def index():
    return render_template('index.html')

# 路由2：处理图表生成请求（支持精细控制）
@app.route('/api/chart', methods=['POST'])
def chart_api():
    try:
        data = request.get_json()
        
        # 提取所有参数，提供默认值
        chart_config = {
            'type': 'bar',  # 固定为柱状图
            'title': data.get('title', '柱状图'),
            'data': data.get('data', [10, 20, 15, 30, 25]),
            'x_label': data.get('x_label'),
            'y_label': data.get('y_label'),
            'x_ticks': data.get('x_ticks'),
            'bar_color': data.get('bar_color', '#667eea'),
            'edge_color': data.get('edge_color', '#5a6fd6'),
            'background_color': data.get('background_color', '#ffffff'),
            'bar_width': data.get('bar_width', 0.6),
            'font_size': data.get('font_size', 12),
            'title_font_size': data.get('title_font_size', 16),
            'fig_width': data.get('fig_width', 10),
            'fig_height': data.get('fig_height', 6),
            'show_grid': data.get('show_grid', True),
            'show_values': data.get('show_values', True),
            'custom_colors': data.get('custom_colors')
        }
        
        # 调用核心程序
        image_base64 = generate_chart(chart_config)
        
        return jsonify({
            'success': True,
            'image': image_base64
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# 路由3：处理图表下载
@app.route('/api/download', methods=['POST'])
def download_chart():
    try:
        data = request.get_json()
        file_format = data.get('format', 'png')
        filename = data.get('filename', 'chart')
        
        # 重新生成图表（使用相同的配置）
        image_base64 = generate_chart(data)
        
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        
        image_data = base64.b64decode(image_base64)
        
        if file_format.lower() == 'png':
            return send_file(
                io.BytesIO(image_data),
                mimetype='image/png',
                as_attachment=True,
                download_name=f'{filename}.png'
            )
        elif file_format.lower() in ['jpg', 'jpeg']:
            img = Image.open(io.BytesIO(image_data))
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=95)
            output.seek(0)
            return send_file(
                output,
                mimetype='image/jpeg',
                as_attachment=True,
                download_name=f'{filename}.jpg'
            )
        elif file_format.lower() == 'pdf':
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.utils import ImageReader
            
            img = Image.open(io.BytesIO(image_data))
            output = io.BytesIO()
            c = canvas.Canvas(output, pagesize=letter)
            img_reader = ImageReader(img)
            width, height = letter
            c.drawImage(img_reader, 0, 0, width=width, height=height, preserveAspectRatio=True)
            c.save()
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'{filename}.pdf'
            )
        else:
            return jsonify({'success': False, 'error': 'Unsupported format'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)