import matplotlib.pyplot as plt
import io
import base64

def generate_chart(chart_type, data):
    """
    你的核心逻辑：接收图表类型和数据，返回图片的base64编码
    """
    plt.figure(figsize=(6, 4))
    
    if chart_type == 'bar':
        plt.bar(range(len(data)), data)
    elif chart_type == 'line':
        plt.plot(data)
    elif chart_type == 'pie':
        plt.pie(data)
    
    # 把图表保存到内存中，而不是保存为文件
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    
    # 转成base64，方便在网页中直接显示
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return image_base64