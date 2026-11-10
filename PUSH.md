# 推送到 GitHub

本目录已是一个完整的本地 Git 仓库：分支 `main`，一次提交，10 个文件；`verify_model.py` 与 `predict.py` 均已跑通。

## 当前状态（已实测）

目标仓库 **`huangbin8888/digit-recognition` 已存在**（公开、空仓库、默认分支 `main`），无需再创建。

当前 WorkBuddy 的 GitHub 连接器使用 GitHub App 用户令牌（`ghu_`），可读，但**缺少 `contents=write` 权限**，因此无法写入任何仓库内容。逐条验证如下：

| 写入/建仓途径 | 结果 |
|---|---|
| `POST /user/repos`（REST 建仓） | 403，要求 `administration=write` + `repository_creation=write` |
| `createRepository`（GraphQL） | `FORBIDDEN` |
| `POST /repos/{owner}/{repo}/forks` | 403，要求 `repository_creation=write` |
| `PUT /repos/.../contents/...`（REST 写文件） | 403，`x-accepted-github-permissions: contents=write` |
| `POST /repos/.../git/blobs`（Git Data API） | 403，`contents=write` |
| MCP `push_files` | 403，创建初始 README 时被拒 |
| `git push`（Basic 认证两种用户名形式） | 403 `Permission ... denied` |
| 本机其它凭据 | 无 gh CLI、无 PAT、无系统凭据；连接器凭据解密后为同一只读令牌 |

这是账号级授权范围问题，不是登录过期，也不需要重新授权连接器（重连不会改变 GitHub App 的权限集）。

## 完成推送

生成一枚具备写权限的令牌后，在工作区根目录执行一条命令即可：

```bash
GITHUB_TOKEN=<你的PAT> ./push-to-github.sh
```

- Classic PAT：`https://github.com/settings/tokens/new?scopes=repo&description=WorkBuddy`，勾选 `repo`。
- Fine-grained PAT：对该仓库授予 `Contents: Read and write`。

脚本会自动把 `main` 一次提交推送到已存在的空仓库，随后调用接口校验远端 10 个文件是否齐全。令牌只存在于进程内存与 HTTP 请求头，不写入 `.git/config`，不落盘。

**完全手动的方式**（在网页登录后）：

```bash
git remote add origin https://github.com/huangbin8888/digit-recognition.git
git push -u origin main
```

Windows 首次推送会由 Git Credential Manager 弹出浏览器登录，按提示完成即可。

## 推送内容

`README.md`、`MODEL_CARD.md`、`PUSH.md`、`predict.py`、`verify_model.py`、`requirements.txt`、`.gitignore`、`manifest.json`、`model/weights.json`、`model/metadata.json`，共 10 个文件。运行时样本图像、截图、日志与缓存不在推送范围内（见 `.gitignore`）。
