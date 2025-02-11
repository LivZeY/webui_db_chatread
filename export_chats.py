import sqlite3
import csv
import json
import os
from datetime import datetime

def export_chats():
    # 数据库连接
    conn = sqlite3.connect('webui.db')
    cursor = conn.cursor()
    
    # 创建导出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = f"exports/{timestamp}"
    os.makedirs(export_dir, exist_ok=True)
    
    # 查询聊天记录
    cursor.execute("""
        SELECT 
            u.name AS username,
            c.chat AS chat_json,
            datetime(c.created_at, 'unixepoch') AS timestamp
        FROM chat c
        JOIN user u ON c.user_id = u.id
    """)
    
    # 创建CSV文件
    csv_path = os.path.join(export_dir, 'chats.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['用户名', '角色', '内容', '时间'])
        
        for row in cursor.fetchall():
            username = row[0]
            timestamp = row[2]
            
            try:
                chat_data = json.loads(row[1])
                messages = chat_data.get('messages', [])
                
                for msg in messages:
                    writer.writerow([
                        username,
                        msg.get('role', 'unknown'),
                        msg.get('content', '').replace('\n', ' '),
                        timestamp
                    ])
            except json.JSONDecodeError as e:
                print(f"解析JSON失败: {e}")
                continue
                
    print(f"导出成功！文件路径: {os.path.abspath(csv_path)}")
    
if __name__ == "__main__":
    export_chats()