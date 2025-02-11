from flask import Flask, render_template, request, send_from_directory
import sqlite3
import os
import csv
import json
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['EXPORT_FOLDER'] = 'exports'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html',
                            message_type='danger',
                            message='未选择文件')
    
    file = request.files['file']
    if file.filename == '':
        return render_template('index.html',
                            message_type='danger',
                            message='无效的文件名')
    
    if file and file.filename.endswith('.db'):
        filename = 'webui.db'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return render_template('index.html',
                            message_type='success',
                            message='上传成功！请选择导出格式',
                            show_export=True)
    
    return render_template('index.html',
                        message_type='danger',
                        message='仅支持.db文件')

@app.route('/export')
def export_data():
    format_type = request.args.get('format', 'csv')
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = os.path.join(app.config['EXPORT_FOLDER'], timestamp)
        os.makedirs(export_dir, exist_ok=True)
        
        conn = sqlite3.connect(os.path.join(app.config['UPLOAD_FOLDER'], 'webui.db'))
        cursor = conn.cursor()
        
        # 获取数据
        cursor.execute("""
            SELECT
                u.name AS username,
                c.chat AS chat_json,
                datetime(c.created_at, 'unixepoch') AS timestamp
            FROM chat c
            JOIN user u ON c.user_id = u.id
        """)
        
        all_data = []
        for row in cursor.fetchall():
            username = row[0]
            timestamp = row[2]
            
            try:
                chat_data = json.loads(row[1])
                messages = chat_data.get('messages', [])
                
                for msg in messages:
                    all_data.append({
                        "username": username,
                        "role": msg.get('role', 'unknown'),
                        "content": msg.get('content', ''),
                        "timestamp": timestamp
                    })
            except Exception as e:
                print(f"Error processing {username}'s chat: {str(e)}")
                continue
        
        # 导出文件
        if format_type == 'json':
            filename = 'chats.json'
            filepath = os.path.join(export_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
        else:
            filename = 'chats.csv'
            filepath = os.path.join(export_dir, filename)
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['用户名', '角色', '内容', '时间'])
                for item in all_data:
                    writer.writerow([
                        item['username'],
                        item['role'],
                        item['content'].replace('\n', ' '),
                        item['timestamp']
                    ])
        
        return send_from_directory(export_dir, filename, as_attachment=True)
    except Exception as e:
        return f"导出失败: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=False)