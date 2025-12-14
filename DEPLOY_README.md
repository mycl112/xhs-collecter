# 部署指南 (Deployment Guide) - 阿里云 ECS

本指南将帮助您将小红书抓取工具部署到阿里云 Linux 服务器 (Alibaba Cloud Linux 3 / CentOS 8)。

## 📋 准备工作

1.  **服务器信息**:
    *   公网 IP: `123.56.83.213`
    *   系统: Alibaba Cloud Linux 3.2104 LTS
    *   用户名: 通常为 `root`

2.  **安全组设置 (非常重要!)**:
    *   登录阿里云控制台 -> ECS 实例 -> 安全组 -> 配置规则。
    *   **入方向** -> 添加规则 -> 端口范围: `5001` -> 授权对象: `0.0.0.0/0`。
    *   (如果没有这一步，您将无法通过浏览器访问服务)。

## 🚀 部署步骤

### 第一步：连接服务器
打开终端 (Terminal)，使用 SSH 连接到您的服务器：
```bash
ssh root@123.56.83.213
# 输入您的服务器密码
```

### 第二步：上传代码
您有多种方式将代码上传到服务器：

**方式 A: 使用 Git (推荐)**
如果您的代码托管在 GitHub/Gitee：
```bash
# 在服务器上执行
git clone <您的仓库地址>
cd <项目目录>
```

**方式 B: 使用 SCP (本地上传)**
在您本地电脑的终端执行 (不是在服务器上)：
```bash
# 假设您当前在项目根目录下
scp -r "/Users/zengjun45/Desktop/保存/开发相关/小红书抓取" \
root@123.56.83.213:/root/xhs-crawler/
```

### 第三步：执行一键部署脚本
进入项目目录后，运行我为您准备的部署脚本：

```bash
# 1. 进入上传的基础目录
cd /root/xhs-crawler

# 2. 进入项目子目录 (重要：因为您的本地文件夹名叫"小红书抓取")
# 提示：输入 cd 小红书 然后按 Tab 键可以自动补全中文名
cd "小红书抓取"

# 3. 赋予脚本执行权限
chmod +x deploy.sh

# 4. 运行脚本
./deploy.sh
```

脚本会自动执行以下操作：
1.  安装 Python3, Pip, Git, Node.js 等系统依赖。
2.  安装项目所需的 Python 库 (`requirements.txt`)。
3.  安装 Playwright 及其对应的 Chromium 浏览器环境。
4.  安装 PM2 进程管理工具。
5.  启动服务并在后台运行。

### 第四步：访问服务
部署完成后，在浏览器访问：
```
http://123.56.83.213:5001
```

## 🛠 常用维护命令

*   **查看服务状态**: `pm2 status`
*   **查看实时日志**: `pm2 logs`
*   **重启服务**: `pm2 restart xhs-crawler`
*   **停止服务**: `pm2 stop xhs-crawler`
*   **查看今日导出密码**: 查看日志 `pm2 logs --lines 100` 或直接看 `app.py` 输出。

## ❓ 常见问题

**Q: 打开网址无法访问？**
A: 请务必检查阿里云控制台的**安全组**设置，确保 5001 端口已开放。

**Q: Playwright 报错缺少依赖？**
A: 部署脚本中包含 `playwright install-deps`，如果仍报错，请尝试手动运行 `sudo playwright install-deps`.

**Q: 如何更新代码？**
A: 上传新代码后，只需运行 `pm2 restart xhs-crawler` 即可生效。
