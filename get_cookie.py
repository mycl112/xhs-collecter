import time
import os
import sys
import json
import platform
from loguru import logger
from playwright.sync_api import sync_playwright

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# 全局变量，用于标记是否检测到登录成功
LOGIN_SUCCESS = False
USER_NICKNAME = "Unknown"

def handle_response(response):
    """
    监听网络响应，拦截用户信息接口，判断是否登录成功
    """
    global LOGIN_SUCCESS, USER_NICKNAME
    
    # 只关注用户信息相关的接口
    if "user/selfinfo" in response.url or "user/me" in response.url:
        try:
            # 排除非 200 的响应
            if response.status != 200:
                return
                
            # 获取响应内容
            json_data = response.json()
            data = json_data.get("data", {})
            
            # 核心判断逻辑：
            # 1. success 为 True
            # 2. data 中包含 user_id
            # 3. 必须包含 nickname 且不能是 "游客" 或 "Unknown"
            # 4. 如果有 guest 字段，必须为 False
            
            if not json_data.get("success"):
                return
                
            user_id = data.get("user_id")
            nickname = data.get("nickname")
            is_guest = data.get("guest") # 可能不存在
            
            if not user_id:
                return
                
            # 严格过滤游客
            if is_guest is True:
                logger.debug(f"⚠️ 检测到游客身份信号，忽略...")
                return
                
            if not nickname or nickname == "Unknown" or nickname == "游客" or "未登录" in nickname:
                logger.debug(f"⚠️ 检测到无效昵称 ({nickname})，忽略...")
                return

            LOGIN_SUCCESS = True
            USER_NICKNAME = nickname
            logger.success(f"[监听模式] 捕获到登录成功信号！用户: {USER_NICKNAME}")
        except Exception as e:
            # 忽略解析错误（可能是响应体不是 JSON 等）
            logger.debug(f"⚠️ 解析响应失败: {e}")
            pass

def check_login_status(page):
    """
    主动轮询检测：在浏览器上下文中执行 JS 检查登录状态
    """
    try:
        # 使用 evaluate 执行 fetch 请求，直接利用浏览器当前的 Cookie
        result = page.evaluate("""
            async () => {
                try {
                    const response = await fetch('/api/sns/web/v1/user/selfinfo');
                    if (response.status !== 200) return null;
                    const json = await response.json();
                    return json;
                } catch (e) {
                    return null;
                }
            }
        """)
        
        if result and result.get("success"):
            data = result.get("data", {})
            user_id = data.get("user_id")
            nickname = data.get("nickname")
            is_guest = data.get("guest")
            
            if user_id and (is_guest is not True) and (nickname and nickname != "Unknown" and nickname != "游客" and "未登录" not in nickname):
                return True, nickname
    except Exception as e:
        # 页面可能还没加载好，或者 fetch 失败
        pass
        
    return False, None

def main():
    logger.info("🚀 正在启动浏览器 (监听模式)...")
    
    try:
        with sync_playwright() as p:
            try:
                # Auto-detect environment
                system_name = platform.system()
                is_linux = system_name == "Linux"
                
                # Default to headless on Linux, headed on Mac/Windows
                # If running on Linux server without X, headless=True is required
                headless_mode = True if is_linux else False
                
                launch_args = []
                if is_linux:
                    launch_args = ["--no-sandbox", "--disable-dev-shm-usage"]
                
                logger.info(f"🖥️ 检测到系统: {system_name}, 启动模式: {'Headless (无头)' if headless_mode else 'Headed (有界面)'}")

                browser = p.chromium.launch(
                    headless=headless_mode,
                    args=launch_args
                )
            except Exception as e:
                logger.error(f"❌ 启动浏览器失败: {e}")
                if "executable doesn't exist" in str(e) or "No executable found" in str(e):
                    logger.error("📦 检测到Chromium浏览器未安装，请运行以下命令安装:")
                    logger.error("   playwright install chromium")
                elif "playwright" in str(e).lower():
                    logger.error("📦 检测到Playwright未安装，请运行以下命令安装:")
                    logger.error("   pip install playwright")
                    logger.error("   playwright install chromium")
                else:
                    logger.error("🔧 请尝试运行以下命令修复:")
                    logger.error("   playwright install chromium")
                return

            context = browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = context.new_page()
            
            # 注册响应监听器 (保留被动监听作为双重保障)
            page.on("response", handle_response)
            
            logger.info("🌐 正在打开小红书首页...")
            try:
                page.goto("https://www.xiaohongshu.com")
                # Wait for QR code to render
                page.wait_for_timeout(3000)
                
                if headless_mode:
                    # Take screenshot for headless mode
                    page.screenshot(path="login_qrcode.png")
                    logger.info("📸 已保存登录页面截图至: login_qrcode.png")
                    logger.info("💡 当前为无头模式，请下载该截图并扫描二维码登录")
            except Exception as e:
                logger.error(f"❌ 打开页面失败: {e}")
                browser.close()
                return
            
            logger.info("-" * 50)
            logger.info("👉 请在弹出的浏览器窗口中完成登录（推荐使用手机App扫码）")
            logger.info("👀 脚本正在监听网络请求，等待登录成功信号...")
            logger.info("⏳ 登录成功后，脚本会自动捕获 Cookie 并关闭。")
            logger.info("-" * 50)
            
            max_retries = 300 # 10分钟超时 (2s interval)
            retries = 0
            
            global LOGIN_SUCCESS, USER_NICKNAME
            
            while retries < max_retries:
                # 方式1：检查被动监听的标志位
                if LOGIN_SUCCESS:
                    logger.success(f"[监听模式] 检测到登录成功！用户: {USER_NICKNAME}")
                
                # 方式2：如果被动监听没触发，尝试主动轮询 (Active Polling)
                # 只有当 cookies 中包含 web_session 时才值得去轮询，减少不必要的请求
                else:
                    cookies = context.cookies()
                    has_web_session = any(c['name'] == 'web_session' for c in cookies)
                    if has_web_session:
                        is_logged_in, nickname = check_login_status(page)
                        if is_logged_in:
                            LOGIN_SUCCESS = True
                            USER_NICKNAME = nickname
                            logger.success(f"[主动轮询] 检测到登录成功！用户: {USER_NICKNAME}")

                # 如果任意一种方式检测到成功
                if LOGIN_SUCCESS:
                    logger.info("正在提取 Cookie...")
                    
                    # 稍微等待一下，确保所有 Cookie 都写入完毕
                    time.sleep(3)
                    
                    cookies = context.cookies()
                    cookie_parts = []
                    for cookie in cookies:
                        cookie_parts.append(f"{cookie['name']}={cookie['value']}")
                    cookie_str = "; ".join(cookie_parts)
                    
                    # 再次检查关键字段
                    if "web_session" in cookie_str:
                        print(f"COOKIE_RESULT:{cookie_str}")
                        logger.success(f"Cookie 获取成功！(长度: {len(cookie_str)})")
                        logger.info("👋 浏览器将在 3 秒后关闭...")
                        time.sleep(3)
                        break
                    else:
                        logger.warning("⚠️ 登录成功但 Cookie 似乎不完整 (缺少 web_session)，可能是误判或延迟，继续等待...")
                        # 如果这里失败了，说明虽然 API 返回成功，但 Cookie 还没写好
                        # 我们不重置 LOGIN_SUCCESS，而是继续循环等待 Cookie 出现
                
                if retries % 5 == 0:
                    logger.info(f"⏳ 等待登录中... ({retries*2}s)")
                    
                time.sleep(2)
                retries += 1
                
            if retries >= max_retries:
                logger.error("❌ 登录超时，请重试。")
                
            try:
                browser.close()
            except Exception as e:
                logger.debug(f"关闭浏览器时发生错误: {e}")
                
    except Exception as e:
        logger.error(f"❌ 脚本发生未捕获异常: {e}")
        logger.exception("详细错误信息:")

if __name__ == "__main__":
    main()
