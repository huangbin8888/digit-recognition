# 推送到 GitHub

本目录已是一个本地 Git 仓库，包含一次完整提交，分支为 `main`。

## 当前阻塞

当前 WorkBuddy 的 GitHub 连接器令牌是 GitHub App 集成令牌，可以读取账号信息，但**没有创建仓库的权限**：

```
POST https://api.github.com/user/repos
403 Resource not accessible by integration
```

账号 `huangbin8888` 目前也没有任何已有仓库可作为推送目标，因此自动建仓 + 推送这条链路被权限挡住。读写文件本身不需要重新登录连接器。

## 两种方式完成推送

**方式 A（推荐，最省事）**

1. 在 GitHub 网页右上角 `+` → `New repository`，新建名为 `digit-recognition` 的**空仓库**（不要勾选 README / .gitignore / License，保持空仓库），可见性按需选择。
2. 若 GitHub App 的仓库访问范围是「仅选定仓库」，到 `Settings → Applications → Installed GitHub Apps` 里把新仓库加入授权范围。
3. 回到本会话说明仓库已创建，即可用现有连接器把本目录全部文件推送上去（一次提交）。

**方式 B（完全手动）**

在 GitHub 网页建好空仓库后，在本目录执行：

```bash
git remote add origin https://github.com/huangbin8888/digit-recognition.git
git push -u origin main
```

Windows 上首次推送会由 Git Credential Manager 弹出浏览器登录，按提示完成即可。若命令行不便，也可以用 GitHub Desktop 把本目录作为本地仓库发布。

## 推送内容

`README.md`、`MODEL_CARD.md`、`PUSH.md`、`predict.py`、`verify_model.py`、`requirements.txt`、`.gitignore`、`manifest.json`、`model/weights.json`、`model/metadata.json`，共 10 个文件。运行时样本图像、截图、日志与缓存不在推送范围内（见 `.gitignore`）。
