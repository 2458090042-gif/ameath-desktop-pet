"""AI 对话设置标签页"""

import tkinter as tk
from tkinter import ttk

from ..config import load_config, save_config
from ..fonts import get_font_config


def create_ai_tab(settings_self, notebook):
    """创建 AI 设置标签页

    Args:
        settings_self: SettingsWindow 实例
        notebook: ttk.Notebook 实例

    Returns:
        tk.Frame: 标签页框架
    """
    colors = settings_self.colors
    fonts = settings_self.fonts

    frame = tk.Frame(notebook, bg=colors["bg"])
    config = load_config()

    # ===== 标题 =====
    title = tk.Label(
        frame,
        text="✨ AI 对话设置",
        font=fonts["title"],
        bg=colors["bg"],
        fg=colors["text"],
        anchor="w",
    )
    title.pack(fill=tk.X, padx=20, pady=(20, 16))

    # ===== API 提供商选择 =====
    provider_frame = tk.Frame(frame, bg=colors["card_bg"], highlightbackground=colors["border"], highlightthickness=1)
    provider_frame.pack(fill=tk.X, padx=20, pady=(0, 12))

    tk.Label(
        provider_frame,
        text="API 提供商",
        font=fonts["base"],
        bg=colors["card_bg"],
        fg=colors["text"],
    ).pack(anchor="w", padx=16, pady=(12, 8))

    provider_var = tk.StringVar(value=config.get("ai_provider", "deepseek"))

    inner = tk.Frame(provider_frame, bg=colors["card_bg"])
    inner.pack(fill=tk.X, padx=16, pady=(0, 12))

    tk.Radiobutton(
        inner,
        text="DeepSeek",
        variable=provider_var,
        value="deepseek",
        font=fonts["base"],
        bg=colors["card_bg"],
        fg=colors["text"],
        selectcolor=colors["card_bg"],
        activebackground=colors["card_bg"],
        activeforeground=colors["accent_dark"],
        cursor="hand2",
    ).pack(side=tk.LEFT, padx=(0, 24))

    tk.Radiobutton(
        inner,
        text="Mimo",
        variable=provider_var,
        value="mimo",
        font=fonts["base"],
        bg=colors["card_bg"],
        fg=colors["text"],
        selectcolor=colors["card_bg"],
        activebackground=colors["card_bg"],
        activeforeground=colors["accent_dark"],
        cursor="hand2",
    ).pack(side=tk.LEFT, padx=(0, 24))

    tk.Radiobutton(
        inner,
        text="智谱 (免费)",
        variable=provider_var,
        value="zhipu",
        font=fonts["base"],
        bg=colors["card_bg"],
        fg="#FB7299",
        selectcolor=colors["card_bg"],
        activebackground=colors["card_bg"],
        activeforeground=colors["accent_dark"],
        cursor="hand2",
    ).pack(side=tk.LEFT)

    # ===== DeepSeek 设置 =====
    ds_frame = tk.Frame(frame, bg=colors["card_bg"], highlightbackground=colors["border"], highlightthickness=1)
    ds_frame.pack(fill=tk.X, padx=20, pady=(0, 12))

    tk.Label(
        ds_frame,
        text="DeepSeek 配置",
        font=fonts["base"],
        bg=colors["card_bg"],
        fg=colors["accent_dark"],
    ).pack(anchor="w", padx=16, pady=(12, 8))

    ds_inner = tk.Frame(ds_frame, bg=colors["card_bg"])
    ds_inner.pack(fill=tk.X, padx=16, pady=(0, 12))

    tk.Label(ds_inner, text="API Key:", font=fonts["base"], bg=colors["card_bg"], fg=colors["text"]).pack(anchor="w")
    ds_key = tk.Entry(
        ds_inner,
        font=fonts["base"],
        bg=colors["bg"],
        fg=colors["text"],
        insertbackground=colors["text"],
        relief=tk.FLAT,
        bd=6,
        show="*",
    )
    ds_key.insert(0, config.get("deepseek_api_key", ""))
    ds_key.pack(fill=tk.X, pady=(4, 8))

    tk.Label(ds_inner, text="模型 (默认 deepseek-chat):", font=fonts["base"], bg=colors["card_bg"], fg=colors["text"]).pack(anchor="w")
    ds_model = tk.Entry(
        ds_inner,
        font=fonts["base"],
        bg=colors["bg"],
        fg=colors["text"],
        insertbackground=colors["text"],
        relief=tk.FLAT,
        bd=6,
    )
    ds_model.insert(0, config.get("deepseek_model", "deepseek-chat"))
    ds_model.pack(fill=tk.X, pady=(4, 0))

    # ===== Mimo 设置 =====
    mimo_frame = tk.Frame(frame, bg=colors["card_bg"], highlightbackground=colors["border"], highlightthickness=1)
    mimo_frame.pack(fill=tk.X, padx=20, pady=(0, 12))

    tk.Label(
        mimo_frame,
        text="Mimo 配置",
        font=fonts["base"],
        bg=colors["card_bg"],
        fg=colors["accent_dark"],
    ).pack(anchor="w", padx=16, pady=(12, 8))

    mimo_inner = tk.Frame(mimo_frame, bg=colors["card_bg"])
    mimo_inner.pack(fill=tk.X, padx=16, pady=(0, 12))

    tk.Label(mimo_inner, text="API Key:", font=fonts["base"], bg=colors["card_bg"], fg=colors["text"]).pack(anchor="w")
    mimo_key = tk.Entry(
        mimo_inner,
        font=fonts["base"],
        bg=colors["bg"],
        fg=colors["text"],
        insertbackground=colors["text"],
        relief=tk.FLAT,
        bd=6,
        show="*",
    )
    mimo_key.insert(0, config.get("mimo_api_key", ""))
    mimo_key.pack(fill=tk.X, pady=(4, 8))

    tk.Label(mimo_inner, text="模型 (默认 mimo-v2.5):", font=fonts["base"], bg=colors["card_bg"], fg=colors["text"]).pack(anchor="w")
    mimo_model = tk.Entry(
        mimo_inner,
        font=fonts["base"],
        bg=colors["bg"],
        fg=colors["text"],
        insertbackground=colors["text"],
        relief=tk.FLAT,
        bd=6,
    )
    mimo_model.insert(0, config.get("mimo_model", "mimo-v2.5"))
    mimo_model.pack(fill=tk.X, pady=(4, 0))

    # ===== 智谱设置 =====
    zhipu_frame = tk.Frame(frame, bg=colors["card_bg"], highlightbackground=colors["border"], highlightthickness=1)
    zhipu_frame.pack(fill=tk.X, padx=20, pady=(0, 12))

    tk.Label(
        zhipu_frame,
        text="智谱配置 (GLM-4-Flash 免费)",
        font=fonts["base"],
        bg=colors["card_bg"],
        fg="#FB7299",
    ).pack(anchor="w", padx=16, pady=(12, 8))

    zhipu_inner = tk.Frame(zhipu_frame, bg=colors["card_bg"])
    zhipu_inner.pack(fill=tk.X, padx=16, pady=(0, 12))

    tk.Label(zhipu_inner, text="API Key:", font=fonts["base"], bg=colors["card_bg"], fg=colors["text"]).pack(anchor="w")
    zhipu_key = tk.Entry(
        zhipu_inner,
        font=fonts["base"],
        bg=colors["bg"],
        fg=colors["text"],
        insertbackground=colors["text"],
        relief=tk.FLAT,
        bd=6,
        show="*",
    )
    zhipu_key.insert(0, config.get("zhipu_api_key", ""))
    zhipu_key.pack(fill=tk.X, pady=(4, 8))

    tk.Label(zhipu_inner, text="模型 (默认 glm-4-flash 免费):", font=fonts["base"], bg=colors["card_bg"], fg=colors["text"]).pack(anchor="w")
    zhipu_model = tk.Entry(
        zhipu_inner,
        font=fonts["base"],
        bg=colors["bg"],
        fg=colors["text"],
        insertbackground=colors["text"],
        relief=tk.FLAT,
        bd=6,
    )
    zhipu_model.insert(0, config.get("zhipu_model", "glm-4-flash"))
    zhipu_model.pack(fill=tk.X, pady=(4, 0))

    # ===== 保存 =====
    def _save_ai_config():
        c = load_config()
        c["ai_provider"] = provider_var.get()
        c["deepseek_api_key"] = ds_key.get().strip()
        c["deepseek_model"] = ds_model.get().strip() or "deepseek-chat"
        c["mimo_api_key"] = mimo_key.get().strip()
        c["mimo_model"] = mimo_model.get().strip() or "mimo-v2.5"
        c["zhipu_api_key"] = zhipu_key.get().strip()
        c["zhipu_model"] = zhipu_model.get().strip() or "glm-4-flash"
        save_config(c)

    # 注册保存回调
    if not hasattr(settings_self, '_save_callbacks'):
        settings_self._save_callbacks = []
    settings_self._save_callbacks.append(_save_ai_config)

    # ===== 底部提示 =====
    tip_frame = tk.Frame(frame, bg=colors["bg"])
    tip_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

    tk.Label(
        tip_frame,
        text="💡 设置好 API Key 后，在托盘菜单或双击桌宠即可打开 AI 对话",
        font=fonts["small"],
        bg=colors["bg"],
        fg=colors["subtext"],
        wraplength=500,
    ).pack(anchor="w")

    return frame


def setup_ai_callbacks(SettingsWindow):
    """注册 AI 设置页的保存回调"""
    original_close = SettingsWindow._on_close

    def _on_close_with_save(self):
        if hasattr(self, '_save_callbacks'):
            for cb in self._save_callbacks:
                try:
                    cb()
                except Exception as e:
                    print(f"保存 AI 设置失败: {e}")
        original_close(self)

    SettingsWindow._on_close = _on_close_with_save
