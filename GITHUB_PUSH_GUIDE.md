# 📤 推送到 GitHub 指南

## 当前状态

- ✅ 本地 Git 仓库已创建
- ✅ 代码已提交（25 个文件）
- ✅ 远程仓库已配置
- ⚠️ 服务器网络无法访问 GitHub（连接超时）

---

## 推送方法

### 方法 1：在本地电脑推送（推荐⭐）

**步骤：**

1. **将代码复制到本地电脑**
   ```bash
   # 可以使用 scp、rsync 或直接复制
   ```

2. **运行推送脚本**
   ```bash
   cd ecommerce-agent
   ./push_to_github.sh
   ```

3. **输入凭证**
   - 用户名：`ledengyun`
   - 密码：你的 GitHub 密码或 Personal Access Token

---

### 方法 2：使用 Git 凭证存储

**配置凭证（推荐）：**

```bash
# 1. 创建 Personal Access Token
# 访问：https://github.com/settings/tokens
# 生成新 Token，勾选 repo 权限

# 2. 存储凭证
git config --global credential.helper store

# 3. 推送
cd /home/admin/.openclaw/workspace/ecommerce-agent
git push -u origin master
# 第一次会提示输入用户名和密码，之后会自动保存
```

---

### 方法 3：使用 SSH（最安全）

**步骤：**

1. **生成 SSH 密钥**
   ```bash
   ssh-keygen -t ed25519 -C "ledengyun@126.com"
   ```

2. **添加公钥到 GitHub**
   - 访问：https://github.com/settings/keys
   - 点击 "New SSH key"
   - 粘贴 `~/.ssh/id_ed25519.pub` 的内容

3. **修改远程仓库为 SSH**
   ```bash
   cd /home/admin/.openclaw/workspace/ecommerce-agent
   git remote set-url origin git@github.com:ledengyun/ecommerce-agent.git
   git push -u origin master
   ```

---

## 快速推送命令

如果你现在就能访问 GitHub，直接运行：

```bash
cd /home/admin/.openclaw/workspace/ecommerce-agent

# 使用 HTTPS 推送
git push -u origin master

# 或使用带凭证的 URL
git push https://ledengyun:YOUR_TOKEN@github.com/ledengyun/ecommerce-agent.git master
```

---

## 使用 Personal Access Token（推荐）

**为什么用 Token：**
- 比密码更安全
- 可以设置权限和过期时间
- 不受 2FA 影响

**创建 Token：**
1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 填写备注（如：ecommerce-agent）
4. 勾选权限：`repo`（完整控制私有仓库）
5. 生成后复制 Token（只显示一次！）

**使用 Token 推送：**
```bash
git push https://ledengyun:ghp_xxxxxxxxxxxx@github.com/ledengyun/ecommerce-agent.git master
```

---

## 仓库信息

- **仓库地址：** https://github.com/ledengyun/ecommerce-agent
- **远程 URL：** `https://github.com/ledengyun/ecommerce-agent.git`
- **分支：** master
- **提交数：** 2 个
- **文件数：** 25 个

---

## 验证推送

推送成功后，访问：
- https://github.com/ledengyun/ecommerce-agent

应该能看到：
- ✅ README.md
- ✅ src/ 目录（所有 Python 模块）
- ✅ config/ 目录
- ✅ scripts/ 目录
- ✅ 所有文档

---

## 常见问题

### Q: 推送时提示认证失败？
**A:** 使用 Personal Access Token 代替密码

### Q: 连接超时？
**A:** 在本地网络好的机器上推送，或配置代理

### Q: 权限错误？
**A:** 确保 Token 有 `repo` 权限

### Q: 如何更新代码？
**A:** 
```bash
git add .
git commit -m "更新说明"
git push
```

---

## 下一步

推送成功后：

1. **验证仓库** - 访问 GitHub 查看文件
2. **创建 Release** - 标记第一个版本 v1.0.0
3. **配置 CI/CD** - 自动测试和部署（可选）
4. **邀请协作者** - 如果有团队成员

---

**当前状态：** 本地已就绪，等待推送到 GitHub 🚀
