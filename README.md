# Ameath - 桌面宠物（二次开发版）

*"爱弥斯，拉贝尔学部的隧者适格者！不过，那都是生前的事了。现在的我，是电子幽灵哦~"*

<p align="center">
  <img src="gifs/ameath.gif" alt="Ameath 桌面宠物" width="50%">
  </br>
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D4?style=flat-square&logo=windows&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
</p>

> **关于本仓库**
>
> 这是 [Ameath 桌面宠物](https://gitee.com/lzy-buaa-jdi/ameath) 的**个人二次开发分支**，在原版基础上扩展了 AI 对话、音乐播放器、天气、字体与个性化设置等模块。
> 原项目作者为 [sinlatansen](https://gitee.com/lzy-buaa-jdi)，原版采用 MIT 协议，本分支同样遵循 MIT 并保留原始版权声明。
> **原版下载与官方更新请以[上游 Gitee 仓库](https://gitee.com/lzy-buaa-jdi/ameath)为准**，本仓库不接受与原版相关的 issue。

## ✨ 原版功能

- 🐾 **智能运动系统** - 状态机控制（游荡/跟随/好奇/休息），模拟真实宠物的行为模式
- 🖱️ **鼠标跟随** - 智能距离判断，远距离主动跟随，近距离好奇观察
- 💤 **随机休息** - 随机停下休息，模拟真实宠物的作息习惯
- 🌀 **惯性移动** - 流畅自然的运动轨迹，告别生硬的移动
- 🎭 **多态动画** - 移动、待机、拖动等多种动画状态
- 📏 **自由缩放** - 9 档缩放（0.3x ~ 1.9x），适配各种屏幕
- 👻 **透明度调节** - 8 档透明度（30% ~ 100%），随心情调整
- 👆 **鼠标穿透** - 默认开启，不遮挡日常操作
- 🔄 **开机自启** - 支持开机自动运行（exe 移动后自动修复路径）
- 🖥️ **系统托盘** - 完整的右键菜单控制
- 🎯 **高 DPI 适配** - 完美支持高分屏，清晰显示
- 🍃 **轻量级** - 仅依赖 Pillow 和 pystray，无其他冗余依赖

## 🧩 本分支新增

| 模块 | 文件 | 说明 | 来源 |
|---|---|---|---|
| AI 对话 | `ameath/ai_chat.py` | 支持 DeepSeek / MiMo / 智谱 三家 Provider，可切换模型；气泡式流式回复 | 本分支 |
| AI 设置页 | `ameath/settings/ai.py` | Provider 选择、API Key、模型名 | 本分支 |
| 台词系统 | `ameath/taici.txt` | 可自由编辑的随机台词表，换行即一条 | 本分支 |
| 设置面板改版 | `ameath/settings/*` | 拆成 关于 / AI / 音乐 / 个性化 / 更新 五个独立分页 | 本分支 |
| 音乐播放器增强 | `ameath/music_player.py` | 在 `cynic3` 首创、`sinlatansen` 迭代的基础上，加了随机播放、FLAC 支持、单击播放、嵌入式模式（`create_gui=False`） | 上游首创 + 本分支增强 |

## 🎵 关于音乐播放器与语音

这两块**最初都不是本分支写的**，我在别人基础上改了一部分，写清楚归属：

- **音乐播放器**：由上游贡献者 `cynic3` 在 `809c7be` 首创（Tkinter 界面 + `sounddevice` 播放 + 单例 + 后台续播）；之后上游作者 `sinlatansen` 迭代了 9 次（整合进设置窗口标签页、MP3 转码、修复 `sounddevice` API 调用）。
  **本分支的改动**：随机播放（`shuffle_mode`）、FLAC 支持、双击播放改为单击、`create_gui=False` 嵌入式模式（避免重开窗口卡顿）。
- **语音系统**：由 `cynic3` 在 `89100eb` 重构（`sounddevice` 取代 `winsound`，加开关与 0-150% 音量）。**本分支未改动代码**，只换了 `sound/voice/` 里的音频素材。

如果只想看本分支原创的部分：`ai_chat.py`、`settings/ai.py`、`taici.txt`，以及 `music_player.py` 的那几处 diff。

## 📦 运行与安装

### 从源码运行（推荐，方便改造）

```powershell
git clone https://github.com/<你的用户名>/ameath-desktop-pet.git
cd ameath-desktop-pet

# 任选其一：uv（推荐，仓库带 uv.lock）
uv sync
uv run main.py

# 或 venv + pip
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

也可以直接双击 `启动桌宠.bat`。

### 打包成 exe

```powershell
uv run pyinstaller ameath.spec
```

产物在 `dist/`。**打包前请确认 `sound/`、`fonts/` 中的资源已就位**（见下节）。

### 原版 Release

原版打包好的 exe 请前往[上游 Gitee Release](https://gitee.com/lzy-buaa-jdi/ameath/releases) 或原作者提供的[网盘](https://pan.quark.cn/s/9d90dc358cb1?pwd=9HQZ)（提取码 `9HQZ`）下载。本仓库**不托管二进制与音频资源**。

## ⚠️ 资源说明（首次运行必读）

为了遵守版权与仓库体积限制，以下内容**没有**随仓库分发，需要自行准备：

| 目录 | 内容 | 获取方式 |
|---|---|---|
| `sound/music/` | 背景音乐（mp3 / flac / wav） | 自行放入**你有权使用的**音频文件；程序按文件名扫描，无需改代码 |
| `sound/voice/` | 音效与语音 | 同上 |
| `fonts/` | `zpix.ttf` 像素字体 | 从 [zpix 官方仓库](https://github.com/SolidZORO/zpix-pixel-font) 下载后放入 |

目录不存在时程序会跳过对应功能，不会崩溃；但**音乐播放器会显示为空列表**。

## 🔑 AI 对话配置

API Key **不写在代码里**，也不入库。程序读取 `config.json`（已在 `.gitignore` 中）：

```json
{
  "ai_provider": "deepseek",
  "deepseek_api_key": "sk-xxxxxxxx",
  "deepseek_model": "deepseek-chat",
  "mimo_api_key": "",
  "mimo_model": "mimo-v2.5",
  "zhipu_api_key": "",
  "zhipu_model": "glm-4-flash"
}
```

也可以启动后从托盘菜单进入「设置 → AI」填写，配置会写回本地 `config.json`。
**提交代码前请确认 `config.json` 未被 `git add`。**

## 🛠️ 二次开发指引

```
ameath-desktop-pet/
├── main.py                 # 入口
├── ameath/
│   ├── pet.py              # 宠物主窗口：状态机、渲染、鼠标交互
│   ├── constants.py        # 全局常量（尺寸、缩放档位、动画帧配置）
│   ├── config.py           # 配置读写与默认值
│   ├── ai_chat.py          # AI 对话（新增 Provider 从这里扩展）
│   ├── music_player.py     # 音乐播放器（上游 cynic3 首创，本分支增强）
│   ├── voice.py            # 音效通道（上游 cynic3，本分支未改）
│   ├── fonts.py            # 字体加载
│   ├── tray.py             # 系统托盘菜单
│   └── settings/           # 设置面板各分页
├── gifs/                   # 动画素材（随仓库分发）
├── sound/                  # 音频（需自备，见上节）
└── fonts/                  # 字体（需自备，见上节）
```

**改行为**：动 `pet.py` 的状态机分支，各状态的进入条件与权重在 `constants.py`。
**加动画**：把 gif 放进 `gifs/`，在 `constants.py` 注册帧序列。
**加 AI Provider**：在 `ai_chat.py` 里照 `_call_deepseek` 的结构加一个 `_call_xxx`，再到 `config.py` 的 `DEFAULT_CONFIG` 补 key/model 字段。
**改台词**：直接编辑 `ameath/taici.txt`，一行一条。

跑之前建议先 `python -m compileall ameath` 过一遍语法。

## 🤝 贡献

欢迎 fork 后自己改。本仓库是个人分支，Pull Request 会看但不保证合并。
与**原版功能**相关的问题请提给[上游仓库](https://gitee.com/lzy-buaa-jdi/ameath)。

## 特别感谢

- 原项目作者 [sinlatansen](https://gitee.com/lzy-buaa-jdi/ameath)，MIT 协议开源
- 上游贡献者 **cynic3** —— 音乐播放器与语音系统的最初实现者
- 上游贡献者 **EuropeJing** —— 窗口贴靠、单屏/多屏模式、暂停动画等运动逻辑
- B 站 up[@\_BLZ\_](https://b23.tv/LOWldqI) 提供的 gif 素材
- [zpix 像素字体](https://github.com/SolidZORO/zpix-pixel-font)

## 📄 License

[MIT](LICENSE) © 2026 sinlatansen（原始版权）；本分支的修改部分同样以 MIT 发布。
角色形象「爱弥斯」版权归[库洛游戏](https://www.kurogames.com/)所有，本项目仅供个人学习与娱乐，**禁止商用**。

---

*但愿我会让你感到骄傲，但愿我没有让你失望 - Ameath*
