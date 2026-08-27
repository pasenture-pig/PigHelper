from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from chart_generators import ChartFactory, generate_chart
from stats_backend import stats_bp
import io
import base64
from PIL import Image

app = Flask(__name__)
CORS(app)

# 注册统计分析蓝图
app.register_blueprint(stats_bp)

# === 网站主页面 ===
@app.route('/')
def main_index():
    return render_template('main_index.html')

# === 图表工具主页 ===
@app.route('/charts')
def charts_index():
    return render_template('index_graphic.html')

# === 各图表页面 ===
@app.route('/bar-chart')
def bar_chart():
    return render_template('bar_chart.html')

@app.route('/pie-chart')
def pie_chart():
    return render_template('pie_chart.html')

@app.route('/line-chart')
def line_chart():
    return render_template('line_chart.html')

@app.route('/scatter-chart')
def scatter_chart():
    return render_template('scatter_chart.html')

# === 3D图表页面 ===
@app.route('/bar-3d-chart')
def bar_3d_chart():
    return render_template('bar_3d_chart.html')

@app.route('/pie-3d-chart')
def pie_3d_chart():
    return render_template('pie_3d_chart.html')

@app.route('/line-3d-chart')
def line_3d_chart():
    return render_template('line_3d_chart.html')

# === 热力图 ===
@app.route('/heatmap-chart')
def heatmap_chart():
    return render_template('heatmap_chart.html')

# === 曲面热力图 ===
@app.route('/surface-chart')
def surface_chart():
    return render_template('surface_chart.html')

# === 数据统计分析 ===
@app.route('/stats')
def stats():
    return render_template('stats.html')

# === API：生成图表 ===
@app.route('/api/chart', methods=['POST'])
def chart_api():
    try:
        data = request.get_json()
        chart_type = data.get('type', 'bar')
        
        generator = ChartFactory.create(chart_type, data)
        result = generator.generate()
        
        if isinstance(result, dict):
            response_data = {
                'success': True,
                'image': result.get('image', ''),
                'fit_info': result.get('fit_info')
            }
        else:
            response_data = {
                'success': True,
                'image': result
            }
        
        return jsonify(response_data)
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# === API：下载图表 ===
@app.route('/api/download', methods=['POST'])
def download_chart():
    try:
        data = request.get_json()
        file_format = data.get('format', 'png')
        filename = data.get('filename', 'chart')
        chart_type = data.get('type', 'bar')
        
        generator = ChartFactory.create(chart_type, data)
        result = generator.generate()
        
        if isinstance(result, dict):
            image_base64 = result.get('image', '')
        else:
            image_base64 = result
        
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
            return jsonify({'success': False, 'error': '不支持的格式'}), 400
            
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)