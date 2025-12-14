<p align="center">
  <a href="https://github.com/cv-cat/Spider_XHS" target="_blank" align="center" alt="Go to XHS_Spider Website">
    <picture>
      <img width="220" src="https://github.com/user-attachments/assets/b817a5d2-4ca6-49e9-b7b1-efb07a4fb325" alt="Spider_XHS logo">
    </picture>
  </a>
</p>


<div align="center">
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/python-3.7%2B-blue" alt="Python 3.7+">
    </a>
    <a href="https://nodejs.org/zh-cn/">
        <img src="https://img.shields.io/badge/nodejs-18%2B-blue" alt="NodeJS 18+">
    </a>
</div>



# Spider_XHS

**✨ 专业的小红书数据采集解决方案，支持笔记爬取，保存格式为excel或者media**

**✨ 小红书全域运营解决方法，AI一键改写笔记（图文，视频）直接上传**

## ⭐功能列表

**⚠️ 任何涉及数据注入的操作都是不被允许的，本项目仅供学习交流使用，如有违反，后果自负**

| 模块           | 已实现                                                                             |
|---------------|---------------------------------------------------------------------------------|
| 小红书创作者平台 | ✅ 二维码登录<br/>✅ 手机验证码登录<br/>✅ 上传（图集、视频）作品<br/>✅查看自己上传的作品<br/>✅ **Web可视化管理界面**      |
|    小红书PC    | ✅ 二维码登录<br/> ✅ 手机验证码登录<br/> ✅ 获取无水印图片<br/> ✅ 获取无水印视频<br/> ✅ 获取主页的所有频道<br/>✅ 获取主页推荐笔记<br/>✅ 获取某个用户的信息<br/>✅ 用户自己的信息<br/>✅ 获取某个用户上传的笔记<br/>✅ 获取某个用户所有的喜欢笔记<br/>✅ 获取某个用户所有的收藏笔记<br/>✅ 获取某个笔记的详细内容<br/>✅ 搜索笔记内容<br/>✅ 搜索用户内容<br/>✅ 获取某个笔记的评论<br/>✅ 获取未读消息信息<br/>✅ 获取收到的评论和@提醒信息<br/>✅ 获取收到的点赞和收藏信息<br/>✅ 获取新增关注信息|


## 🌟 功能特性

- ✅ **多维度数据采集**
  - 用户主页信息
  - 笔记详细内容
  - 智能搜索结果抓取
- 🚀 **高性能架构**
  - 自动重试机制
- 🔒 **安全稳定**
  - 小红书最新API适配
  - 异常处理机制
  - proxy代理
- 🎨 **便捷管理**
  - 结构化目录存储
  - 格式化输出（JSON/EXCEL/MEDIA）
- 🛡️ **防风控策略** (新增)
  - **随机延迟**: 每次请求之间增加 2-5 秒的随机等待时间，模拟真人浏览行为。
  - **数量限制**: 支持手动设置抓取笔记的数量，避免一次性大量抓取触发风控。
  - **真人模拟**: 核心逻辑贴近真实用户操作习惯。

## 🎨效果图
### 处理后的所有用户
![image](https://github.com/cv-cat/Spider_XHS/assets/94289429/00902dbd-4da1-45bc-90bb-19f5856a04ad)
### 某个用户所有的笔记
![image](https://github.com/cv-cat/Spider_XHS/assets/94289429/880884e8-4a1d-4dc1-a4dc-e168dd0e9896)
### 某个笔记具体的内容
![image](https://github.com/cv-cat/Spider_XHS/assets/94289429/d17f3f4e-cd44-4d3a-b9f6-d880da626cc8)
### 保存的excel
![image](https://github.com/user-attachments/assets/707f20ed-be27-4482-89b3-a5863bc360e7)

## 🛠️ 快速开始
### ⛳运行环境
- Python 3.7+
- Node.js 18+

### 🎯安装依赖
```
pip install -r requirements.txt
npm install
```

### 🎨配置文件

#### 方式一：自动获取（推荐 🚀）
我们提供了一个自动化脚本来帮助你一键获取 Cookie。
1. 运行以下命令：
   ```bash
   python get_cookie.py
   ```
2. 脚本会自动打开一个浏览器窗口，访问小红书。
3. 请在弹出的窗口中进行登录（推荐扫码）。
4. 登录成功后，脚本会自动检测并将 Cookie 写入 `.env` 文件，无需手动复制。

#### 方式二：手动获取
配置文件在项目根目录.env文件中，将下图自己的登录cookie放入其中，cookie获取➡️在浏览器f12打开控制台，点击网络，点击fetch，找一个接口点开

![image](https://github.com/user-attachments/assets/6a7e4ecb-0432-4581-890a-577e0eae463d)

复制cookie到.env文件中（注意！登录小红书后的cookie才是有效的，不登陆没有用）
![image](https://github.com/user-attachments/assets/5e62bc35-d758-463e-817c-7dcaacbee13c)

### 🚀运行项目
**命令行模式：**
```
python main.py
```

**Web 可视化界面：**
```
python app.py
```
访问地址: http://localhost:5001
✨ **新增功能**：在 Web 界面中点击 "一键自动获取 (推荐)" 按钮，即可自动打开浏览器并获取 Cookie，无需手动复制。

**命令行抓取指定用户笔记（多线程版）：**
```
python crawl_specific_user.py
```
此脚本用于快速抓取指定用户的全部笔记，包含笔记详情和评论，并导出为 Excel。需在代码中修改目标用户 URL。

### 🗝️注意事项
- main.py中的代码是爬虫的入口，可以根据自己的需求进行修改
- apis/xhs_pc_apis.py 中的代码包含了所有的api接口，可以根据自己的需求进行修改
- apis/xhs_creator_apis.py 中的代码包含了小红书创作者平台的api接口，可以根据自己的需求进行修改
- **关于导出密码弹窗二维码**：若需在“导出所有笔记”的弹窗中展示微信二维码，请将您的二维码图片重命名为 `wechat_qr.jpg` 并放入项目的 `static/` 目录下。若未放置图片，弹窗将显示默认的图片占位符。


## 🍥日志
   
| 日期       | 说明                                        |
|----------|-------------------------------------------|
| 23/08/09 | - 首次提交                                    |
| 23/09/13 | - api更改params增加两个字段，修复图片无法下载，有些页面无法访问导致报错 |
| 23/09/16 | - 较大视频出现编码问题，修复视频编码问题，加入异常处理              |
| 23/09/18 | - 代码重构，加入失败重试                             |
| 23/09/19 | - 新增下载搜索结果功能                              |
| 23/10/05 | - 新增跳过已下载功能，获取更详细的笔记和用户信息                 |
| 23/10/08 | - 上传代码☞Pypi，可通过pip install安装本项目           |
| 23/10/17 | - 搜索下载新增排序方式选项（1、综合排序 2、热门排序 3、最新排序）      |
| 23/10/21 | - 新增图形化界面,上传至release v2.1.0               |
| 23/10/28 | - Fix Bug 修复搜索功能出现的隐藏问题                   |
| 25/03/18 | - 更新API，修复部分问题                            |
| 25/06/07 | - 更新search接口，区分视频和图集下载，增加小红书创作者api        |
| 25/07/15 | - 更新 xs version56 & 小红书创作者接口              |
| 25/12/03 | - 新增 Flask Web 可视化界面，支持抓取创作者已发布笔记；新增导出 Excel 功能（含笔记内容和评论）；<br/>- 新增抓取其他用户笔记功能（输入用户主页 URL）；<br/>- 修复 URL 参数解析 bug（处理 token 中包含等号的情况） |
| 25/12/04 | - 验证并优化了 `crawl_specific_user.py` 抓取评论的功能，修复了用户提到的评论为空的问题（经测试，使用正确的 `xsec_token` 即可正常获取）；<br/>- 更新了测试用户 URL，方便进行功能验证 |
| 25/12/05 | - 新增 `get_cookie.py` 脚本，支持通过 Playwright 自动打开浏览器并一键获取 Cookie；<br/>- Web 界面新增"一键自动获取"按钮，支持直接调用脚本，大幅简化配置流程。 |
| 25/12/06 | - 新增防风控策略：支持手动设置抓取数量；增加 2-5 秒随机请求间隔模拟真人操作；<br/>- Web 界面新增抓取数量设置选项。<br/>- **代码重构与优化**：<br/>  1. 修复了抓取笔记详情时点赞、收藏、评论数等字段为空的问题；<br/>  2. 优化 Cookie 管理：移除本地 `.env` 存储，改为仅内存存储，提升安全性；<br/>  3. 优化 Excel 导出：仅支持前端手动导出，取消抓取后自动生成文件的冗余逻辑；<br/>  4. 清理冗余代码：删除了 `crawl_specific_user.py` 等重复脚本，精简了 `main.py` 为示例脚本，精简了项目结构。 |
| 25/12/07 | - 修复自动获取 Cookie 脚本报错 `Event loop is closed` 的问题（原因：`browser.close()` 在 Playwright 上下文关闭后执行；修复：调整代码缩进，将其移至上下文内）。<br/>- **彻底修复自动获取 Cookie 逻辑**：<br/>  1. 废弃了不可靠的页面元素检测，改为基于 API 响应监听的机制；<br/>  2. **严格区分游客与登录用户**：在监听 `/api/sns/web/v1/user/selfinfo` 接口时，增加对 `nickname`（排除"游客"/"Unknown"）和 `guest` 字段的校验，防止未登录时误判为成功；<br/>  3. **优化流程体验**：登录成功后增加 3 秒缓冲等待，确保 Cookie 写入完整后再关闭窗口，彻底解决了“扫码前误判”和“扫码后未获取”的问题。<br/>- **前端界面重构**：<br/>  1. 全新分步式 UI 设计（Step 1 配置 -> Step 2 采集 -> Step 3 分析），操作流程更清晰；<br/>  2. 保留手动输入 Cookie 功能，并在界面显式增加保存按钮；<br/>  3. 预留 AI 分析报告入口（开发中）；<br/>  4. **UI 细节优化**：调整页面元素尺寸（Header、卡片间距等），采用更紧凑的布局风格，完全还原设计稿视觉效果；调整 Cookie 输入框样式（白色背景、增加高度）以提升易用性；优化 Cookie 配置按钮布局为左右并排；<br/>  5. **交互体验优化**：在“用户主页 URL”输入框旁增加“如何获取链接”的帮助入口，点击可查看详细的图文引导弹窗；<br/>  6. **采集结果展示优化**：将笔记采集结果由卡片式布局优化为**表格列表**形式，直观展示标题、发布时间、互动数据（点赞/收藏/评论/分享）；移除冗余字段（阅读量、封面链接、笔记链接），提升数据阅读效率；<br/>  7. **内容深度展示**：新增“笔记内容”摘要展示及“查看详情”功能，点击可查看完整笔记内容及评论列表，并支持时间戳自动转换为可读日期。<br/>- **导出功能增强**：<br/>  1. 拆分“导出 Excel”为“导出前 10 条”和“导出所有笔记”；<br/>  2. “导出所有笔记”增加动态安全验证机制，密码每日更新（算法：`SHA256(YYYYMMDD)` 前 6 位），启动服务时会在控制台打印当日密码。 |
| 25/12/07 | - **修复 Linux 服务器下 Playwright 启动报错问题**：<br/>  1. 针对无图形界面（No XServer）环境，强制开启 `headless=True` 模式；<br/>  2. 添加 `--no-sandbox` 和 `--disable-dev-shm-usage` 启动参数，确保在 Linux 容器/服务器中稳定运行；<br/>  3. **优化无头模式体验**：新增页面截图功能，在 headless 模式下自动保存登录页面截图（`login_qrcode.png`），方便用户查看二维码进行扫码登录。<br/>- **智能环境识别**：脚本现在会自动识别操作系统：<br/>  - **MacOS/Windows**: 自动使用 Headed 模式（弹出浏览器窗口），方便本地操作；<br/>  - **Linux**: 自动使用 Headless 模式（无窗口），并启用服务器兼容参数。 |




## 🔬 调研结论 (Research Findings)

### 1. 小红书 Cookie 失效周期
- **Web Session (web_session):** 这是维持登录状态的关键 Cookie。根据社区反馈和测试，如果经常使用，有效期可能持续数天到两周不等。
- **失效触发条件:** 
  - 长期不活跃（超过 24-48 小时无请求）。
  - IP 地址发生剧烈变化（例如切换 VPN 节点）。
  - 浏览器完全关闭（如果是会话级 Cookie，但这通常被持久化存储）。
  - 服务器端主动风控（检测到异常流量）。
- **建议:** 定期（如每天或每次启动任务前）检查 Cookie 有效性。如果请求返回 401 或重定向至登录页，则需重新获取。

### 2. 通过日志判断抓取状态
在使用 Cookie 进行 API 抓取时，可以通过分析响应日志来判断当前状态：

| 状态 | 关键指标 (Key Indicators) | 示例/说明 |
|------|--------------------------|-----------|
| **抓取成功** | HTTP Status: `200`<br>JSON `success`: `True`<br>JSON `data`: 非空 | `{"success": true, "msg": "成功", "data": {...}}` |
| **Cookie 失效** | HTTP Status: `401` 或 `200`<br>JSON `code`: `-1` (常见)<br>Response URL: 重定向至 `/login` | 响应体可能包含 "未登录" 或 "session expired" 字样。 |
| **被风控/验证码** | HTTP Status: `461` 或 `200`<br>JSON `code`: `300015` 等错误码<br>Header `location`: 包含 `verify` | 响应体可能包含 "verify" 或 "risk" 相关信息，或者直接返回 HTML 验证页面。 |
| **无数据/软限制** | HTTP Status: `200`<br>JSON `success`: `True`<br>JSON `data`: 空列表/对象 | `{"success": true, "msg": "成功", "data": []}` <br>可能是数据真的为空，也可能是账号被“软封禁”看不到内容。 |
| **系统错误** | HTTP Status: `5xx`<br>JSON `success`: `False` | `{"success": false, "msg": "系统繁忙"}` |

---

## 🧸额外说明
1. 感谢star⭐和follow📰！不时更新
2. 作者的联系方式在主页里，有问题可以随时联系我
3. 可以关注下作者的其他项目，欢迎 PR 和 issue
4. 感谢赞助！如果此项目对您有帮助，请作者喝一杯奶茶~~ （开心一整天😊😊）
5. thank you~~~

<div align="center">
  <img src="./author/wx_pay.png" width="400px" alt="微信赞赏码"> 
  <img src="./author/zfb_pay.jpg" width="400px" alt="支付宝收款码">
</div>


## 📈 Star 趋势
<a href="https://www.star-history.com/#cv-cat/Spider_XHS&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=cv-cat/Spider_XHS&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=cv-cat/Spider_XHS&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=cv-cat/Spider_XHS&type=Date" />
 </picture>
</a>

## 🍔 交流群
过期请加作者主页wx

<img width="1000" height="1450" alt="5355a0f82398ee2052f2e659328d737b" src="./author/group.jpg" />


