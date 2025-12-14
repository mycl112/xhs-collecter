import sys
from apis.xhs_pc_apis import XHS_Apis

if __name__ == '__main__':
    """
    此文件为爬虫的入口文件示例。
    由于项目已重构为 Web 服务 (app.py)，此文件仅作为 API 调用参考。
    
    apis/xhs_pc_apis.py 为爬虫的api文件，包含小红书的全部数据接口。
    apis/xhs_creator_apis.py 为小红书创作者中心的api文件。
    """
    
    # 示例：如何直接调用 API
    # 注意：需要有效的 Cookie 才能运行
    # xhs_apis = XHS_Apis()
    # user_url = 'https://www.xiaohongshu.com/user/profile/...'
    # cookie = "..."
    # success, msg, notes = xhs_apis.get_user_all_notes(user_url, cookie)
    # print(f"Success: {success}, Notes count: {len(notes) if notes else 0}")
    
    print("请运行 app.py 启动 Web 服务进行抓取。")
