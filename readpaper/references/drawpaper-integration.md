# ReadPaper 与 DrawPaper 衔接

优先使用本会话可发现的独立 `drawpaper` 技能，先读其 SKILL.md。没有独立安装时读取 `../bundled/drawpaper/WORKFLOW.md`（相对于本文件），所需 references、scripts 和视觉样例随包提供。内置副本没有第二个 SKILL.md，不产生同名技能入口，无需网络安装。

独立 `drawpaper/` 是维护源；仓库 `scripts/sync_drawpaper.py` 同步到 `readpaper/bundled/drawpaper/`。修改绘图流程后同步并运行 `--check`，不独立维护两套规范。

给绘图流程传入已核实的 PDF 路径、版本、slug、主 README、输出目录和核心机制。共享来源笔记，关键公式与连线仍对照原文。绘图规格放该论文 `tmp/`，不新建第二个主文档。

| 材料 | 存放 |
|---|---|
| 关键论文原图及图注 | `figures/originals/`，保留图号和页码索引 |
| 选定生图草稿 | `figures/<slug>-imagegen-draft.png` |
| 终稿 PDF / PNG / TeX | `figures/`，采用一致版本号 |
| 图片依赖、可复用提示词、源码包 | `figures/` 对应素材目录或 `notes/` |
| 未选草稿、规格、编译与 QA 中间物 | `tmp/` |

主 README 索引关联全部材料；核心机制块展示最终完整 PNG，链接 PDF、源码包和原图入口。绘图的长交付说明不另附在六块地图之外；独立 DrawPaper 仍按自身交付方式回复。

内置的是完整绘图指令和资源，不是图像模型或 TeX 引擎。从实际技能目录发现 PDF、imagegen、latex-compile 等能力；没有辅助技能但有对应工具时按工具文档执行，不杜撰调用。

- 缺生图工具时可复用合格同篇草稿，或继续提取原图、制作准确矢量图并明确“未生成生图草稿”；要求新插画而无素材时明确插画未完成。
- 缺编译能力时保留规格与源码，明确 PDF/PNG 终稿未核验；不擅自付费。
- 机制或版本不明确时核对来源，不让生图补科学结构。

以上限制不阻止交付已完成的阅读地图，也不能把部分交付写成整个流程已完成。
