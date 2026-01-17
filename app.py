from flask import Flask, render_template, jsonify, request, send_file, session
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from wtforms import StringField, IntegerField, validators
from apis.xhs_creator_apis import XHS_Creator_Apis
from apis.xhs_pc_apis import XHS_Apis
from xhs_utils.data_util import save_creator_data_to_xlsx
from xhs_utils.crawl_util import fetch_note_detail_task
import os
import sys
import subprocess
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG"
)

app = Flask(__name__, template_folder='.')

# Security configurations
app.config['JSON_AS_ASCII'] = False  # Support Chinese characters
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB upload limit
app.config['SECRET_KEY'] = os.urandom(24)  # Random secret key for session encryption
app.config['WTF_CSRF_ENABLED'] = True  # Enable CSRF protection
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # CSRF token expiration time

# Session configurations
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60  # Session expires after 1 hour
app.config['SESSION_PERMANENT'] = True  # Make sessions permanent
app.config['SESSION_TYPE'] = 'filesystem'  # Use file system for session storage
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(__file__), 'sessions')
app.config['SESSION_FILE_THRESHOLD'] = 500  # Maximum number of sessions to store

# Initialize extensions
csrf = CSRFProtect(app)
Session(app)

# Disable CSRF protection for API endpoints since we're using session-based authentication
# and the frontend is sending the CSRF token in the header

# Use session to store data instead of global variables
# Session keys: 'current_cookies', 'last_crawled_notes'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/save_cookie', methods=['POST'])
@csrf.exempt
def save_cookie():
    try:
        data = request.json
        cookie_str = data.get('cookie')
        
        # Input validation
        if not cookie_str:
            return jsonify({'success': False, 'msg': 'Cookie 不能为空'})
        
        # Store in session instead of global variable
        session['current_cookies'] = cookie_str
            
        return jsonify({'success': True, 'msg': 'Cookie 已保存 (仅会话内存)'})
    except Exception as e:
        logger.error(f"Error in save_cookie: {e}")
        return jsonify({'success': False, 'msg': f'保存Cookie失败: {str(e)}'})

@app.route('/api/auto_cookie', methods=['POST'])
@csrf.exempt
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
                    # Store in session instead of global variable
                    session['current_cookies'] = cookie_str
                    return jsonify({'success': True, 'msg': 'Cookie 获取成功', 'cookie': cookie_str})
            
            return jsonify({'success': False, 'msg': '未检测到成功登录或无法解析 Cookie', 'logs': result.stdout})
        else:
            return jsonify({'success': False, 'msg': '脚本执行出错', 'logs': result.stderr})
            
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'msg': '操作超时 (登录二维码扫描时间过长)'})
    except Exception as e:
        logger.error(f"Error in auto_cookie: {e}")
        return jsonify({'success': False, 'msg': f'自动获取Cookie失败: {str(e)}'})


@app.route('/api/user_notes', methods=['POST'])
@csrf.exempt
def get_user_notes():
    try:
        data = request.json
        
        # Input validation
        user_url = data.get('url')
        if not user_url:
             return jsonify({'success': False, 'msg': '用户主页 URL 不能为空'})
        
        # Validate URL format
        if not (user_url.startswith('https://www.xiaohongshu.com/') or user_url.startswith('http://www.xiaohongshu.com/')):
            return jsonify({'success': False, 'msg': '请输入有效的小红书用户主页 URL'})
             
        # Get cookies from session
        current_cookies = session.get('current_cookies')
        if not current_cookies:
             return jsonify({'success': False, 'msg': '未找到 Cookies，请先设置 Cookie'})

        # Validate and parse crawl_count
        crawl_count_str = data.get('crawl_count')
        crawl_count = None
        if crawl_count_str:
            try:
                crawl_count = int(crawl_count_str)
                if crawl_count <= 0:
                    crawl_count = None
            except ValueError:
                crawl_count = None
        
        # Validate and parse comment_count
        comment_count_str = data.get('comment_count')
        comment_count = 10  # Default value
        if comment_count_str:
            try:
                comment_count = int(comment_count_str)
                # Allow 0 comments, ensure within reasonable range
                comment_count = max(0, min(100, comment_count))
            except ValueError:
                comment_count = 10

        logger.info(f"开始采集用户笔记: {user_url}, 采集数量: {crawl_count}, 评论数量: {comment_count}")
        
        xhs_apis = XHS_Apis()
        # Call get_user_all_notes
        success, msg, notes = xhs_apis.get_user_all_notes(user_url, current_cookies, require_num=crawl_count)
        
        if success:
             # Reuse the enrichment logic
             enriched_notes = []
             with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_note = {executor.submit(fetch_note_detail_task, note, current_cookies, comment_count): note for note in notes}
                for future in as_completed(future_to_note):
                    try:
                        updated_note = future.result()
                        enriched_notes.append(updated_note)
                    except Exception as exc:
                        logger.error(f'处理笔记时发生异常: {exc}')
                        enriched_notes.append(future_to_note[future])

             # Store in session instead of global variable
             session['last_crawled_notes'] = enriched_notes
             logger.info(f"成功采集 {len(enriched_notes)} 条笔记")
             return jsonify({'success': True, 'data': enriched_notes, 'count': len(enriched_notes)})
        else:
             logger.error(f"采集笔记失败: {msg}")
             return jsonify({'success': False, 'msg': msg})
    except Exception as e:
        logger.error(f"API 错误: {e}")
        return jsonify({'success': False, 'msg': f'服务器内部错误: {str(e)}'})

@app.route('/api/my_notes')
def get_my_notes():
    try:
        # Get cookies from session
        current_cookies = session.get('current_cookies')
        if not current_cookies:
             return jsonify({'success': False, 'msg': '未找到 Cookies，请先设置 Cookie'})
            
        # Validate and parse comment_count
        comment_count_str = request.args.get('comment_count')
        comment_count = 10  # Default value
        if comment_count_str:
            try:
                comment_count = int(comment_count_str)
                # Allow 0 comments, ensure within reasonable range
                comment_count = max(0, min(100, comment_count))
            except ValueError:
                comment_count = 10
        
        logger.info(f"开始采集自己的笔记, 评论数量: {comment_count}")
        
        creator_apis = XHS_Creator_Apis()
        # 调用获取所有发布笔记的接口
        success, msg, notes = creator_apis.get_all_publish_note_info(current_cookies)
            
        if success:
            # Enrich notes with details using threading
            # Limit concurrency to 4 to be safe with rate limits
            enriched_notes = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_note = {executor.submit(fetch_note_detail_task, note, current_cookies, comment_count): note for note in notes}
                for future in as_completed(future_to_note):
                    try:
                        updated_note = future.result()
                        enriched_notes.append(updated_note)
                    except Exception as exc:
                        logger.error(f'处理笔记时发生异常: {exc}')
                        enriched_notes.append(future_to_note[future])
            
            # Store in session instead of global variable
            session['last_crawled_notes'] = enriched_notes
            logger.info(f"成功采集 {len(enriched_notes)} 条自己的笔记")
            return jsonify({'success': True, 'data': enriched_notes, 'count': len(enriched_notes)})
        else:
            logger.error(f"采集自己的笔记失败: {msg}")
            return jsonify({'success': False, 'msg': msg})
    except Exception as e:
        logger.error(f"API 错误: {e}")
        return jsonify({'success': False, 'msg': f'服务器内部错误: {str(e)}'})

@app.route('/api/export_excel', methods=['GET', 'POST'])
@csrf.exempt
def export_excel():
    try:
        notes_to_export = []
        
        # Check if data is sent from frontend via POST
        if request.method == 'POST':
            request_data = request.get_json()
            if request_data and 'notes' in request_data:
                notes_to_export = request_data['notes']
                logger.info(f"从前端获取到 {len(notes_to_export)} 条笔记用于导出")
        
        # If no data from frontend, use session data
        if not notes_to_export:
            last_crawled_notes = session.get('last_crawled_notes', [])
            if not last_crawled_notes:
                logger.error("导出失败: 没有可导出的数据")
                return jsonify({'success': False, 'msg': '没有可导出的数据'}), 400
            notes_to_export = last_crawled_notes
            logger.info(f"从会话获取到 {len(notes_to_export)} 条笔记用于导出")
        
        # Get limit from query parameters
        limit = request.args.get('limit', type=int)
        
        if limit and limit > 0:
            notes_to_export = notes_to_export[:limit]
        
        logger.info(f"开始导出Excel: 共 {len(notes_to_export)} 条笔记")

        # Save to a temporary file
        filename = f'xhs_notes_export_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'
        # Ensure temp dir exists
        temp_dir = os.path.join(os.path.dirname(__file__), 'datas', 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            logger.info(f"创建临时目录: {temp_dir}")
            
        file_path = os.path.join(temp_dir, filename)
        
        save_creator_data_to_xlsx(notes_to_export, file_path)
        
        logger.info(f"Excel导出成功: {file_path}")
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        logger.error(f"Excel导出失败: {e}")
        return jsonify({'success': False, 'msg': f'导出失败: {str(e)}'}), 500

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
        logger.error(f"生成每日密码失败: {e}")
        return "123456"  # Fallback password

# Add a route to verify the export password
@app.route('/api/verify_password', methods=['POST'])
@csrf.exempt
def verify_password():
    try:
        data = request.json
        password = data.get('password')
        if not password:
            return jsonify({'success': False, 'msg': '密码不能为空'})
        
        daily_pwd = get_daily_password()
        if password == daily_pwd:
            logger.info("密码验证成功")
            return jsonify({'success': True, 'msg': '密码正确'})
        else:
            logger.warning(f"密码验证失败: 输入密码 '{password}', 正确密码 '{daily_pwd}'")
            return jsonify({'success': False, 'msg': '密码错误，请重试'})
    except Exception as e:
        logger.error(f"密码验证出错: {e}")
        return jsonify({'success': False, 'msg': f'验证出错: {str(e)}'})

if __name__ == '__main__':
    # Log the daily password for user convenience
    daily_pwd = get_daily_password()
    logger.info(f"\n{'='*50}")
    logger.info(f"🔑 今日导出密码 (Today's Password): {daily_pwd}")
    logger.info(f"访问地址: http://127.0.0.1:5007")
    logger.info(f"{'='*50}\n")

    # Run the app
    app.run(host="0.0.0.0", port=5007, debug=False, use_reloader=False)
