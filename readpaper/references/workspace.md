# 工作区与初始化

用户指定目录就使用该目录；已有精读工作区就在其内加入论文。普通软件仓库且未指定位置时，在其下新建 `paper-reading/`，避免把软件 README 改成论文台账。当前是用户为精读选择的空目录时直接使用。

默认 slug 为 `<短名>-<arXiv编号>`，全小写，例 `lewm-2603.19312`、`matrix_game_3.0-2604.08995`；paper 与 analyse 使用同一 slug。无 arXiv 编号时不伪造，使用用户指定的稳定 slug，并显式传 `--allow-custom-slug`。

```text
<root>/
├── AGENTS.md
├── README.md
├── paper/
│   ├── README.md
│   └── <slug>/
├── analyse/
│   └── <slug>/
│       ├── README.md
│       ├── notes/
│       ├── figures/
│       └── tmp/
├── ideas/
└── archive/
```

只在初始化时补建 `paper/` 的空目录和说明文件；不写入、复制、移动、下载或更改其中的论文。初始化后把 `paper/` 视为只读原料。外部 PDF 可以直接读取，在主文档记实际来源，不为目录外观复制 PDF。用户明确要求导入原文时该指示优先，但仍不覆盖已有原文。

单篇产出只放 `analyse/<slug>/`，跨论文想法放 `ideas/`，临时物放该论文 `tmp/`。`archive/` 只建空目录，不擅自迁移、删除或归档已有文件。

## 执行

先读项目规则，再运行绝对路径脚本：

```bash
python3 /absolute/readpaper/scripts/init_workspace.py \
  --root /absolute/paper-reading \
  --slug lewm-2603.19312 \
  --title '论文原题' \
  --venue-year '2026' \
  --focus '长程任务世界模型、记忆与移动操纵'
```

仅初始化工作区可不传 slug。脚本只创建缺失文件，已有 AGENTS、README、笔记与 PDF 不覆盖。兼容格式总台账追加尚不存在的 slug，初始为“待读”，已有状态绝不降级。README 不兼容时保留原文并提示，按项目规则处理，不另造第四类 README。

新 AGENTS 来自 `assets/AGENTS.template.md`，默认保留工程/控制基础较强、理论从符号开始的教学偏好，研究方向使用 `--focus`，不带个人学校、公司、账号或路径。已有 AGENTS 不自动追加或替换；当前用户明确授权的技能行为适用于本次任务。用户另要求长期更新规则时再针对性编辑。

## 三类 README

- 根 README：`slug | 标题 | 会议/年份 | 状态 | 一句话贡献 | 与主线的关系`。状态为“待读 / 在读 / 已验收 / 弃读”，真正开始读全文后才改为在读。
- paper/README：20 行以内，说明原料用途、slug 与只读边界。
- analyse/<slug>/README：固定六节：一句话贡献；开卷地图；验收问题 + 我的答案 + 你的判词；错题本；我的疑问与批判；文件索引。第 5 节由用户表达，agent 不代写用户观点。

`notes/map.md` 仅在阅读后写真实地图，其内容原样归入主 README 第 2 节。这是显式要求的一份地图存档，不再复制第三份。索引用 `路径 | 这是什么 | 日期`，尽量用相对路径便于迁移；聊天交付文件时用可点击绝对路径。
