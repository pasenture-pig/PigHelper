#包装器
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from generator import generate_chart  # 导入你的核心函数

app = Flask(__name__)
CORS(app)

# 路由1：提供前端页面
@app.route('/')
def index():
    return render_template('web.html')  #指定html的文件

# 路由2：处理图表生成请求（这是关键！）
@app.route('/api/chart', methods=['POST'])
def chart_api():
    try:
        # 接收前端传来的数据
        data = request.get_json()
        chart_type = data.get('type', 'bar')  # 默认柱状图
        chart_data = data.get('data', [1, 2, 3, 4, 5])  # 默认数据
        
        # 调用你的核心程序
        image_base64 = generate_chart(chart_type, chart_data)
        
        # 返回给前端
        return jsonify({
            'success': True,
            'image': image_base64  # 前端拿到这个base64就能直接显示
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)