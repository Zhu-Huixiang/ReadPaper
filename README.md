# ReadPaper + DrawPaper

中文科研论文精读与架构绘图工作流。目标是让读者能自己复述、批判和提出下一步，并通过八道验收题。

**ReadPaper 自带完整 DrawPaper 工作流与素材；DrawPaper 也能单独安装使用。** 开卷时自动建立目录、README 和 AGENTS.md，读论文后生成六块地图及论文架构图。后续使用随读答疑、验收和落盘模式继续学习。

## 安装

在 Codex 中对 skill-installer 说：

```text
把 https://github.com/Zhu-Huixiang/ReadPaper 中的 readpaper 和 drawpaper 两个 skill 安装到我的技能目录。
```

也可以下载本仓库，将 `readpaper/` 与 `drawpaper/` 两个文件夹完整放进当前 Codex 的用户技能目录。当前官方目录为 `~/.agents/skills/`；已有环境使用 `~/.codex/skills/` 时沿用该环境的技能目录，不重复安装到两处。安装后若没有出现，重新打开 Codex。

只想精读时可仅安装 `readpaper/`，内置绘图资源完整保留；只想画图时只安装 `drawpaper/`。不要只复制 SKILL.md，否则会缺模板、脚本与资源。目录约定参考 [Codex 官方技能文档](https://developers.openai.com/codex/skills)。

## 使用

```text
使用 $readpaper，在当前目录建立精读工作区，带我读这篇论文，并画出架构图。
```

默认研究方向是世界模型、长程记忆与移动操纵；可以在请求中给出自己的方向。Skill 的发布版不包含作者个人身份、账号或机器路径。

| 模式 | 说法 | 得到什么 |
|---|---|---|
| 开卷 | 带我读 <slug> | 六块开卷地图、八道验收题、论文架构图 |
| 随读答疑 | 解释这个公式 / 再具体点 | 从当前卡点出发的小步讲解 |
| 验收 | 验收 <slug>，附八题答案 | 逐题判词、错题本、台账状态更新 |
| 落盘 | 落盘 | 一份主题文档，自动更新主文档索引 |

单独绘图：

```text
使用 $drawpaper，给这篇论文画一张方法架构图，包含训练和部署流程。
```

## 自动建立的工作区

```text
paper-reading/
├── AGENTS.md
├── README.md                  # 论文总台账
├── paper/
│   ├── README.md
│   └── <slug>/                # 用户提供的论文原料
├── analyse/<slug>/
│   ├── README.md              # 每篇论文唯一主线文档
│   ├── notes/                # 地图、讲解、推导
│   ├── figures/              # 原图、草稿、PDF/PNG/TeX 终稿
│   └── tmp/                  # 规格、构建与检查中间文件
├── ideas/                    # 跨论文想法
└── archive/                  # 不自动迁移或删除旧文件
```

初始化脚本只补建缺失项，保留已有规则、笔记、PDF 和验收状态；不会移动原文或覆盖项目 README。普通概念问答不会创建工作区。

仅初始化，也可手动运行（Python 3.9+，标准库）：

```bash
python3 readpaper/scripts/init_workspace.py \
  --root /path/to/paper-reading \
  --slug example-2603.12345 \
  --title '论文原题' \
  --focus '你的研究方向'
```

## 绘图交付与运行条件

DrawPaper 交付论文关键原图、选定生图草稿、单页 PDF、完整 PNG 预览、TikZ 源文件和图片依赖。插画版保留草稿视觉素材，文字、公式和连线用矢量排版精修；编译后检查最新整图及密集局部。

阅读和初始化不需要第三方 Python 包。完整绘图需要宿主具备 PDF 阅读、内置图像生成、LaTeX（中文图推荐 XeLaTeX）及 Poppler；图像能力由宿主提供，仓库不包含模型或 API 凭据。辅助 PDF/imagegen/latex-compile 技能可通过当前环境发现。缺少工具时会明确未完成项，不能把草稿冒充核验后的终稿。

`drawpaper/assets/` 是视觉参考与可编辑示例，不是新论文的科学证据，不代表实验复现结果。

## 维护与验证

`drawpaper/` 是绘图流程维护源；ReadPaper 的内置副本由脚本同步，不需要维护两份不同规则。

```bash
python3 scripts/sync_drawpaper.py
python3 scripts/sync_drawpaper.py --check
python3 -m unittest discover -s tests -v
```

仓库测试覆盖初始化、重跑保护、已有论文与状态保留、冲突和路径安全；测试通过不代表任意论文都已完成科学与视觉核验。
