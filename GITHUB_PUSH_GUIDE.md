# 将xhs-collecter推送到自己的GitHub仓库

## 操作步骤：

1. **创建自己的GitHub仓库**
   - 登录GitHub
   - 点击右上角的"+"号，选择"New repository"
   - 填写仓库名称（比如xhs-collecter）
   - 选择公开或私有
   - 点击"Create repository"

2. **复制仓库URL**
   - 创建完成后，复制仓库的HTTPS或SSH URL
   - 格式：`https://github.com/your-username/your-repo-name.git`

3. **添加新的远程仓库**
   ```bash
   # 使用HTTPS URL
   git remote add origin https://github.com/your-username/your-repo-name.git
   
   # 或使用SSH URL（需要配置SSH密钥）
   # git remote add origin git@github.com:your-username/your-repo-name.git
   ```

4. **推送代码到新仓库**
   ```bash
   git push -u origin main
   ```

## 注意事项：

- 确保已安装Git并配置好用户信息
  ```bash
  git config --global user.name "Your Name"
  git config --global user.email "your-email@example.com"
  ```

- 如果使用SSH URL，需要先配置SSH密钥

- 首次推送时需要输入GitHub账号密码或SSH密钥密码