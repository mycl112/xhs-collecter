#!/bin/bash

# ==========================================
# 小红书抓取工具 - 阿里云一键部署脚本
# 适配系统: Alibaba Cloud Linux 3 / CentOS 8+
# ==========================================

# 遇到错误立即停止
set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 开始部署小红书抓取工具...${NC}"

# 1. 检查并安装系统依赖
echo -e "${GREEN}📦 [1/6] 安装系统依赖 (含 Python 3.9)...${NC}"
sudo yum update -y

# 启用 CRB 源 (对于某些系统可能是必须的)
# sudo dnf config-manager --set-enabled crb

# 尝试安装 Python 3.9 (Alibaba Cloud Linux 3 / CentOS 8)
echo "正在尝试通过 dnf 安装 python3.9..."
# 尝试启用 EPEL 源，很多时候 python39 在这里面
sudo dnf install -y epel-release

# 尝试安装 python39
sudo dnf install -y python39 python39-pip git nodejs npm \
    libXcomposite libXcursor libXdamage libXext libXi libXtst \
    cups-libs libXScrnSaver libXrandr alsa-lib pango atk at-spi2-atk gtk3 \
    libdrm mesa-libgbm alsa-lib

# 如果上面失败，尝试编译安装 (最稳妥的保底方案)
if ! command -v python3.9 &> /dev/null; then
    echo -e "${RED}⚠️  dnf 未找到 python3.9，正在尝试从源码编译安装 Python 3.9 (这可能需要几分钟)...${NC}"
    sudo dnf install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel make
    cd /tmp
    wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz
    tar xzf Python-3.9.18.tgz
    cd Python-3.9.18
    ./configure --enable-optimizations
    sudo make altinstall
    # 清理
    cd ..
    rm -rf Python-3.9.18 Python-3.9.18.tgz
    
    # 建立软链接，确保 python3.9 命令可用
    if [ -f /usr/local/bin/python3.9 ]; then
        sudo ln -sf /usr/local/bin/python3.9 /usr/bin/python3.9
        sudo ln -sf /usr/local/bin/pip3.9 /usr/bin/pip3.9
    fi
    
    # 回到项目目录
    cd -
fi

# 再次检查
if ! command -v python3.9 &> /dev/null; then
    echo -e "${RED}❌ Python 3.9 安装失败！请尝试手动安装。${NC}"
    # 尝试使用 python3 (如果版本够高)
    PY_VER=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "尝试使用系统默认 python3 (版本: $PY_VER)..."
    PY_CMD="python3"
else
    PY_CMD="python3.9"
fi

# 检查 Python 版本
echo -e "${GREEN}当前 Python 版本: $($PY_CMD --version)${NC}"

# 2. 安装 Python 依赖
echo -e "${GREEN}🐍 [2/6] 安装 Python 依赖 (使用 $PY_CMD)...${NC}"
# 升级 pip
$PY_CMD -m pip install --upgrade pip
# 安装项目依赖
$PY_CMD -m pip install -r requirements.txt
# 安装 gunicorn
$PY_CMD -m pip install gunicorn

# 3. 安装 Playwright 及其浏览器
echo -e "${GREEN}🎭 [3/6] 配置 Playwright 环境...${NC}"
$PY_CMD -m pip install playwright
$PY_CMD -m playwright install chromium
# 安装浏览器依赖 (需要 sudo)
echo "正在安装浏览器依赖 (可能需要几分钟)..."
sudo $PY_CMD -m playwright install-deps chromium

# 4. 配置 PM2 进程守护
echo -e "${GREEN}🔄 [4/6] 配置 PM2 进程守护...${NC}"
# 检查是否已安装 pm2
if ! command -v pm2 &> /dev/null; then
    sudo npm install -g pm2
fi

# 5. 启动服务
echo -e "${GREEN}▶️  [5/6] 启动服务...${NC}"
# 如果已存在则重启，否则启动
if pm2 list | grep -q "xhs-crawler"; then
    echo "服务已存在，正在重启..."
    pm2 restart xhs-crawler
else
    echo "服务未启动，正在创建..."
    # 使用 python3.9 直接启动
    pm2 start app.py --name "xhs-crawler" --interpreter $PY_CMD
fi

# 保存 PM2 配置以便开机自启
pm2 save
# 注意: 'pm2 startup' 通常需要用户手动复制运行一条命令，这里尝试自动生成
# 如果失败，用户可能需要手动执行提示的命令
# pm2 startup systemd | grep "sudo" | bash || echo "⚠️ 自动设置开机自启失败，请根据提示手动设置"

# 6. 完成提示
echo -e "${GREEN}✅ [6/6] 部署完成！${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e "🌐 服务访问地址: http://$(curl -s ifconfig.me):5001"
echo -e "⚠️  重要提示:"
echo -e "1. 请确保阿里云【安全组】已放行 TCP 端口 [5001]"
echo -e "2. 查看日志命令: pm2 logs xhs-crawler"
echo -e "3. 停止服务命令: pm2 stop xhs-crawler"
echo -e "4. 重启服务命令: pm2 restart xhs-crawler"
echo -e "${GREEN}============================================${NC}"
