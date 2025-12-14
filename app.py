from flask import Flask, render_template, jsonify, request, send_file
from apis.xhs_creator_apis import XHS_Creator_Apis
from apis.xhs_pc_apis import XHS_Apis
from xhs_utils.data_util import save_creator_data_to_xlsx
from xhs_utils.crawl_util import fetch_note_detail_task
import os
import sys
import subprocess
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

LAST_CRAWLED_NOTES = []
CURRENT_COOKIES = ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/save_cookie', methods=['POST'])
def save_cookie():
    try:
        data = request.json
        cookie_str = data.get('cookie')
        if not cookie_str:
            return jsonify({'success': False, 'msg': 'Cookie 不能为空'})
        
        # Update global variable
        global CURRENT_COOKIES
        CURRENT_COOKIES = cookie_str
        
        # 处理可能存在的特殊字符
        # cookie_str = cookie_str.replace("'", "\\'")
            
        return jsonify({'success': True, 'msg': 'Cookie 已保存 (仅内存)'})
    except Exception as e:
        return jsonify({'success': False, 'msg': str(e)})

@app.route('/api/auto_cookie', methods=['POST'])
def auto_cookie():
    try:
        # Execute get_cookie.py
        script_path = os.path.join(os.path.dirname(__file__), 'get_cookie.py')
        
        # Run the script
        result = subprocess.run(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=360
        )
        
        if result.returncode == 0:
            # Parse cookie from stdout
            if "COOKIE_RESULT:" in result.stdout:
                import re
                match = re.search(r"COOKIE_RESULT:(.*)", result.stdout)
                if match:
                    cookie_str = match.group(1).strip()
                    global CURRENT_COOKIES
                    CURRENT_COOKIES = cookie_str
                    return jsonify({'success': True, 'msg': 'Cookie 获取成功', 'cookie': cookie_str})
            
            return jsonify({'success': False, 'msg': '未检测到成功登录或无法解析 Cookie', 'logs': result.stdout})
        else:
            return jsonify({'success': False, 'msg': '脚本执行出错', 'logs': result.stderr})
            
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'msg': '操作超时'})
    except Exception as e:
        return jsonify({'success': False, 'msg': str(e)})


@app.route('/api/user_notes', methods=['POST'])
def get_user_notes():
    try:
        data = request.json
        user_url = data.get('url')
        if not user_url:
             return jsonify({'success': False, 'msg': '用户主页 URL 不能为空'})
             
        global CURRENT_COOKIES
        if not CURRENT_COOKIES:
             return jsonify({'success': False, 'msg': '未找到 Cookies，请先设置 Cookie'})

        crawl_count_str = data.get('crawl_count')
        crawl_count = int(crawl_count_str) if crawl_count_str and str(crawl_count_str).isdigit() else None

        xhs_apis = XHS_Apis()
        # Call get_user_all_notes
        success, msg, notes = xhs_apis.get_user_all_notes(user_url, CURRENT_COOKIES, require_num=crawl_count)
        
        if success:
             # Reuse the enrichment logic
             enriched_notes = []
             with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_note = {executor.submit(fetch_note_detail_task, note, CURRENT_COOKIES): note for note in notes}
                for future in as_completed(future_to_note):
                    try:
                        updated_note = future.result()
                        enriched_notes.append(updated_note)
                    except Exception as exc:
                        print(f'Task generated an exception: {exc}')
                        enriched_notes.append(future_to_note[future])

             global LAST_CRAWLED_NOTES
             LAST_CRAWLED_NOTES = enriched_notes
             return jsonify({'success': True, 'data': enriched_notes})
        else:
             return jsonify({'success': False, 'msg': msg})
    except Exception as e:
        return jsonify({'success': False, 'msg': str(e)})

@app.route('/api/my_notes')
def get_my_notes():
    try:
        global CURRENT_COOKIES
        if not CURRENT_COOKIES:
             return jsonify({'success': False, 'msg': '未找到 Cookies，请先设置 Cookie'})
            
        creator_apis = XHS_Creator_Apis()
        # 调用获取所有发布笔记的接口
        success, msg, notes = creator_apis.get_all_publish_note_info(CURRENT_COOKIES)
        
        if success:
            # Enrich notes with details using threading
            # Limit concurrency to 4 to be safe with rate limits
            enriched_notes = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_note = {executor.submit(fetch_note_detail_task, note, CURRENT_COOKIES): note for note in notes}
                for future in as_completed(future_to_note):
                    try:
                        updated_note = future.result()
                        enriched_notes.append(updated_note)
                    except Exception as exc:
                        print(f'Task generated an exception: {exc}')
                        enriched_notes.append(future_to_note[future])
            
            global LAST_CRAWLED_NOTES
            LAST_CRAWLED_NOTES = enriched_notes
            return jsonify({'success': True, 'data': enriched_notes})
        else:
            return jsonify({'success': False, 'msg': msg})
    except Exception as e:
        return jsonify({'success': False, 'msg': str(e)})

@app.route('/api/export_excel')
def export_excel():
    try:
        global LAST_CRAWLED_NOTES
        if not LAST_CRAWLED_NOTES:
             return "No data to export", 400
        
        # Get limit from query parameters
        limit = request.args.get('limit', type=int)
        
        notes_to_export = LAST_CRAWLED_NOTES
        if limit and limit > 0:
            notes_to_export = LAST_CRAWLED_NOTES[:limit]

        # Save to a temporary file
        filename = f'xhs_notes_export_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'
        # Ensure temp dir exists
        temp_dir = os.path.join(os.path.dirname(__file__), 'datas', 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        file_path = os.path.join(temp_dir, filename)
        
        save_creator_data_to_xlsx(notes_to_export, file_path)
        
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return str(e), 500

def get_daily_password():
    """
    Generate a daily password based on the current date and SHA-256 hash.
    Format: SHA256(YYYYMMDD)[:6]
    """
    try:
        import hashlib
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        hash_obj = hashlib.sha256(date_str.encode())
        password = hash_obj.hexdigest()[:6]
        return password
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    # Print the daily password for user convenience
    print(f"\n{'='*50}")
    print(f"🔑 今日导出密码 (Today's Password): {get_daily_password()}")
    print(f"{'='*50}\n")

    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)
