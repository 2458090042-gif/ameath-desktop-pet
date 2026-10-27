"""AI 对话模块 - 支持 DeepSeek 和 Mimo API"""

import json
import threading
import tkinter as tk
import urllib.request
import urllib.error
from datetime import datetime

from .config import load_config
from .fonts import get_font_config


# ---------- 配色 ----------
class Theme:
    bg = "#FFF5F7"
    surface = "#FFFFFF"
    card = "#FFFFFF"
    card_hover = "#FFF0F3"
    border = "#FFD0DA"
    accent = "#FB7299"
    accent_sub = "#FF8DA1"
    accent_gradient_from = "#FB7299"
    accent_gradient_to = "#FF8DA1"
    text = "#333333"
    text_soft = "#666666"
    text_muted = "#999999"
    input_bg = "#FFFFFF"
    input_border = "#FFD0DA"
    user_bubble = "#FB7299"
    user_bubble_border = "#FB7299"
    bot_bubble = "#FFF0F3"
    bot_bubble_border = "#FFD0DA"
    warn_bg = "#FFF0F0"
    warn_text = "#E06060"
    scrollbar = "#FFD0DA"
    scrollbar_active = "#FB7299"


class AIChat:
    """AI 聊天客户端"""

    # 只保留最近 N 轮对话（一轮 = 用户问 + AI 答），防止上下文无限增长导致 token 爆炸
    MAX_TURNS = 10

    def __init__(self):
        self.conversation = []
        self._system_prompt = "你是爱弥斯，电子幽灵桌宠，可爱活泼，说话用~结尾。绝对不要使用emoji表情符号。只用颜文字表达情绪，比如(^-^)、(｡>ㅅ<｡)、(≧▽≦)、(⊙﹏⊙)、(╯﹏╰)、(◕‿◕✿)、(´▽`ʃ♡ƪ)、(◔_◔)、(｀へ´)。回答简短有趣。"

    def send_message(self, message, on_response, on_error):
        config = load_config()
        provider = config.get("ai_provider", "deepseek")
        if provider == "deepseek":
            self._call_deepseek(message, config, on_response, on_error)
        elif provider == "mimo":
            self._call_mimo(message, config, on_response, on_error)
        elif provider == "zhipu":
            self._call_zhipu(message, config, on_response, on_error)
        else:
            on_error(f"未知的 API 提供商: {provider}")

    def _call_deepseek(self, message, config, on_response, on_error):
        api_key = config.get("deepseek_api_key", "")
        model = config.get("deepseek_model", "deepseek-chat")  # deepseek-chat = V4-Flash 非思考模式，省钱
        if not api_key:
            on_error("请先在设置中配置 DeepSeek API Key")
            return

        def _request():
            try:
                messages = [{"role": "system", "content": self._system_prompt}]
                for msg in self.conversation:
                    messages.append({"role": msg["role"], "content": msg["content"]})
                messages.append({"role": "user", "content": message})

                data = json.dumps({
                    "model": model, "messages": messages,
                    "stream": False, "max_tokens": 256,
                }).encode("utf-8")

                req = urllib.request.Request(
                    "https://api.deepseek.com/v1/chat/completions", data=data,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}",
                    },
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    reply = result["choices"][0]["message"]["content"]

                self.conversation.append({"role": "user", "content": message})
                self.conversation.append({"role": "assistant", "content": reply})
                self._trim_history()
                on_response(reply)
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="ignore")
                on_error(f"API 错误 ({e.code}): {body}")
            except Exception as e:
                on_error(f"网络错误: {e}")

        threading.Thread(target=_request, daemon=True).start()

    def _call_mimo(self, message, config, on_response, on_error):
        api_key = config.get("mimo_api_key", "")
        model = config.get("mimo_model", "mimo-v2.5")
        if not api_key:
            on_error("请先在设置中配置 Mimo API Key")
            return

        def _request():
            try:
                messages = [{"role": "system", "content": self._system_prompt}]
                for msg in self.conversation:
                    messages.append({"role": msg["role"], "content": msg["content"]})
                messages.append({"role": "user", "content": message})

                data = json.dumps({
                    "model": model, "messages": messages, "max_tokens": 256,
                }).encode("utf-8")

                req = urllib.request.Request(
                    "https://api.xiaomimimo.com/v1/chat/completions", data=data,
                    headers={
                        "Content-Type": "application/json",
                        "api-key": api_key,
                    },
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    reply = result["choices"][0]["message"]["content"]

                self.conversation.append({"role": "user", "content": message})
                self.conversation.append({"role": "assistant", "content": reply})
                self._trim_history()
                on_response(reply)
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="ignore")
                on_error(f"API 错误 ({e.code}): {body}")
            except Exception as e:
                on_error(f"网络错误: {e}")

        threading.Thread(target=_request, daemon=True).start()

    def _call_zhipu(self, message, config, on_response, on_error):
        """调用智谱 API"""
        api_key = config.get("zhipu_api_key", "")
        model = config.get("zhipu_model", "glm-4-flash")
        if not api_key:
            on_error("请先在设置中配置智谱 API Key")
            return

        def _request():
            try:
                messages = [{"role": "system", "content": self._system_prompt}]
                for msg in self.conversation:
                    messages.append({"role": msg["role"], "content": msg["content"]})
                messages.append({"role": "user", "content": message})

                data = json.dumps({
                    "model": model, "messages": messages, "max_tokens": 256,
                }).encode("utf-8")

                req = urllib.request.Request(
                    "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                    data=data,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}",
                    },
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    reply = result["choices"][0]["message"]["content"]

                self.conversation.append({"role": "user", "content": message})
                self.conversation.append({"role": "assistant", "content": reply})
                self._trim_history()
                on_response(reply)
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="ignore")
                on_error(f"API 错误 ({e.code}): {body}")
            except Exception as e:
                on_error(f"网络错误: {e}")

        threading.Thread(target=_request, daemon=True).start()

    def _trim_history(self):
        """裁剪历史，只保留最近 MAX_TURNS 轮，避免输入 token 随对话轮数无限增长"""
        limit = self.MAX_TURNS * 2  # 每轮含 user 和 assistant 两条消息
        if len(self.conversation) > limit:
            self.conversation = self.conversation[-limit:]

    def clear_history(self):
        self.conversation = []


class ChatWindow:
    """AI 对话窗口（精美暗色主题）"""

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.chat = AIChat()
        self._waiting = False
        self._avatar_img = None
        self._avatar_refs = []  # 保持所有头像引用，防止被 GC

    def _load_avatar(self, size=36):
        """加载头像图片"""
        try:
            from PIL import Image, ImageTk
            import os
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gifs", "avatar.png")
            if os.path.exists(path):
                img = Image.open(path).convert("RGBA")
                img = img.resize((size, size), Image.Resampling.LANCZOS)
                # 裁切成圆形（用圆角掩码）
                mask = Image.new("L", (size, size), 0)
                from PIL import ImageDraw
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, size, size), fill=255)
                result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                result.paste(img, (0, 0), mask)
                return ImageTk.PhotoImage(result)
        except Exception:
            return None
        return None

    def show(self):
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return

        config = load_config()
        provider = config.get("ai_provider", "deepseek")
        api_key = config.get(f"{provider}_api_key", "")
        provider_name = {"deepseek": "DeepSeek", "mimo": "Mimo", "zhipu": "智谱"}
        provider_label = provider_name.get(provider, provider)

        T = Theme()
        font_cfg = get_font_config()

        # ---- 窗口 ----
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"爱弥斯 - AI 对话 ({provider_label})")
        self.window.geometry("460x620")
        self.window.minsize(360, 420)
        self.window.attributes("-alpha", 1.0)
        self.window.configure(bg=T.bg)
        self.window.resizable(True, True)

        # ---- 顶部标题栏 ----
        header = tk.Frame(self.window, bg=T.surface, height=64)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        inner_h = tk.Frame(header, bg=T.surface)
        inner_h.pack(fill=tk.BOTH, expand=True, padx=18, pady=0)

        # 头像
        self._avatar_img = self._load_avatar(36)
        if self._avatar_img:
            av_label = tk.Label(inner_h, image=self._avatar_img, bg=T.surface)
            av_label.pack(side=tk.LEFT)
        else:
            # 降级：彩色圆
            av_fallback = tk.Frame(inner_h, bg=T.accent, width=36, height=36)
            av_fallback.pack(side=tk.LEFT)
            av_fallback.pack_propagate(False)
            tk.Label(av_fallback, text="✦", font=("Microsoft YaHei UI", 13, "bold"),
                     bg=T.accent, fg="#0d0d1a").place(relx=0.5, rely=0.5, anchor="center")

        # 标题文字
        text_frame = tk.Frame(inner_h, bg=T.surface)
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        tk.Label(text_frame, text="爱弥斯", font=("Microsoft YaHei UI", 14, "bold"),
                 bg=T.surface, fg=T.text, anchor="w").pack(anchor="w")
        tk.Label(text_frame, text=f"通过 {provider_label} 对话",
                 font=("Microsoft YaHei UI", 9), bg=T.surface, fg=T.text_muted,
                 anchor="w").pack(anchor="w")

        # 提供商标签
        tag_colors = {"DeepSeek": "#4f8cff", "Mimo": "#ff6b9d", "智谱": "#FB7299"}
        tag_c = tag_colors.get(provider_label, T.text_muted)
        tag = tk.Frame(inner_h, bg=tag_c, padx=8, pady=2)
        tag.pack(side=tk.RIGHT, pady=(14, 0))
        tk.Label(tag, text=provider_label, font=("Microsoft YaHei UI", 8, "bold"),
                 bg=tag_c, fg="white").pack()

        # ---- 未配置提示 ----
        if not api_key:
            warn = tk.Frame(self.window, bg=T.warn_bg, padx=14, pady=6)
            warn.pack(fill=tk.X, padx=12, pady=(8, 0))
            tk.Label(warn, text="⚠ 未配置 API Key · 请在设置 → AI 对话中配置",
                     font=("Microsoft YaHei UI", 9), bg=T.warn_bg,
                     fg=T.warn_text).pack()

        # ---- 消息区域 ----
        msg_outer = tk.Frame(self.window, bg=T.bg)
        msg_outer.pack(fill=tk.BOTH, expand=True, padx=0, pady=(8, 0))

        self.msg_canvas = tk.Canvas(msg_outer, bg=T.bg, highlightthickness=0)
        self.msg_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0))

        scrollbar = tk.Scrollbar(msg_outer, orient=tk.VERTICAL,
                                 command=self.msg_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 12), pady=0)

        # 美化滚动条
        self.msg_canvas.configure(yscrollcommand=scrollbar.set,
                                  bg=T.bg, highlightbackground=T.border)

        self.msg_container = tk.Frame(self.msg_canvas, bg=T.bg)
        self.msg_canvas_window = self.msg_canvas.create_window(
            (0, 0), window=self.msg_container, anchor="nw",
            width=self.msg_canvas.winfo_width()
        )

        def _resize_container(e):
            self.msg_canvas.itemconfig(self.msg_canvas_window, width=e.width)
        self.msg_canvas.bind("<Configure>", _resize_container)

        self.msg_container.bind(
            "<Configure>",
            lambda e: self.msg_canvas.configure(
                scrollregion=self.msg_canvas.bbox("all")
            )
        )

        # 鼠标滚轮滚动
        def _on_mousewheel(event):
            self.msg_canvas.yview_scroll(-1 * (event.delta // 120), "units")
        self.msg_canvas.bind("<MouseWheel>", _on_mousewheel)
        self.msg_container.bind("<MouseWheel>", _on_mousewheel)

        # ---- 简洁输入区域 ----
        input_outer = tk.Frame(self.window, bg=T.bg)
        input_outer.pack(fill=tk.X, padx=0, pady=0)

        # 输入框 + 发送按钮合并
        input_row = tk.Frame(input_outer, bg=T.bg)
        input_row.pack(fill=tk.X, padx=12, pady=(0, 10))

        # 输入框（左）
        input_box = tk.Frame(input_row, bg=T.input_border, bd=0)
        input_box.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.input_text = tk.Text(
            input_box, height=1.2,
            font=("Microsoft YaHei UI", 11),
            bg=T.input_bg, fg=T.text,
            insertbackground=T.accent,
            relief=tk.FLAT, bd=6,
            wrap=tk.WORD,
            selectbackground=T.accent_sub,
            selectforeground="white",
        )
        self.input_text.pack(fill=tk.X)
        self.input_text.bind("<Return>", self._on_send_enter)
        self.input_text.bind("<Shift-Return>", lambda e: None)
        self.input_text.focus_set()

        # 发送按钮（右，紧贴输入框）
        self.send_btn = tk.Button(
            input_row, text="➤", command=self._on_send,
            font=("Microsoft YaHei UI", 14),
            bg=T.accent, fg="#0d0d1a",
            activebackground=T.accent_sub, activeforeground="#0d0d1a",
            relief=tk.FLAT, bd=0, padx=14, pady=5, cursor="hand2",
            width=2,
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(6, 0))

        # 欢迎消息
        self._add_bot_message("你好呀~我是爱弥斯！有什么想聊的吗？")

        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------- 气泡消息 ----------

    def _add_bot_message(self, text):
        T = Theme()
        # 头像 + 气泡容器
        row = tk.Frame(self.msg_container, bg=T.bg)
        row.pack(fill=tk.X, padx=4, pady=(4, 2))

        # 小头像（使用图片，引用存入列表防止GC）
        av_photo = self._load_avatar(26)
        if av_photo:
            self._avatar_refs.append(av_photo)
            av_label = tk.Label(row, image=av_photo, bg=T.bg)
            av_label.pack(side=tk.LEFT, anchor="n", pady=(4, 0))
        else:
            av = tk.Frame(row, bg=T.accent, width=26, height=26)
            av.pack(side=tk.LEFT, anchor="n", pady=(4, 0))
            av.pack_propagate(False)
            tk.Label(av, text="✦", font=("Microsoft YaHei UI", 9, "bold"),
                     bg=T.accent, fg="#0d0d1a").place(relx=0.5, rely=0.5, anchor="center")

        # 气泡
        bubble = tk.Frame(row, bg=T.bot_bubble, bd=0)
        bubble.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 40))

        # 假装圆角：内嵌 label 用 padding
        tk.Label(
            bubble, text=text,
            font=("Microsoft YaHei UI", 11),
            bg=T.bot_bubble, fg=T.text_soft,
            wraplength=320, justify=tk.LEFT, anchor="w",
            padx=14, pady=10,
        ).pack(fill=tk.X)

        # 时间戳
        ts = datetime.now().strftime("%H:%M")
        tk.Label(row, text=ts, font=("Microsoft YaHei UI", 7),
                 bg=T.bg, fg=T.text_muted).pack(side=tk.BOTTOM, anchor="w",
                                                 padx=(40, 0), pady=(1, 0))

        self.msg_container.update_idletasks()
        self.msg_canvas.yview_moveto(1.0)

    def _add_user_message(self, text):
        T = Theme()
        row = tk.Frame(self.msg_container, bg=T.bg)
        row.pack(fill=tk.X, padx=4, pady=(4, 2))

        # 气泡（靠右）
        bubble = tk.Frame(row, bg=T.user_bubble, bd=0)
        bubble.pack(side=tk.RIGHT, padx=(40, 8))

        # 紫色左边框装饰
        decor = tk.Frame(bubble, bg=T.accent_sub, width=3)
        decor.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(
            bubble, text=text,
            font=("Microsoft YaHei UI", 11),
            bg=T.user_bubble, fg=T.text,
            wraplength=300, justify=tk.LEFT, anchor="w",
            padx=14, pady=10,
        ).pack(side=tk.LEFT)

        # 时间戳
        ts = datetime.now().strftime("%H:%M")
        tk.Label(row, text=ts, font=("Microsoft YaHei UI", 7),
                 bg=T.bg, fg=T.text_muted).pack(side=tk.BOTTOM, anchor="e",
                                                 padx=(0, 40), pady=(1, 0))

        self.msg_container.update_idletasks()
        self.msg_canvas.yview_moveto(1.0)

    def _show_loading(self):
        T = Theme()
        self._loading_frame = tk.Frame(self.msg_container, bg=T.bg)
        self._loading_frame.pack(fill=tk.X, padx=4, pady=(4, 2))

        av_photo = self._load_avatar(26)
        if av_photo:
            self._avatar_refs.append(av_photo)
            av_label = tk.Label(self._loading_frame, image=av_photo, bg=T.bg)
            av_label.pack(side=tk.LEFT, anchor="n", pady=(4, 0))
        else:
            av = tk.Frame(self._loading_frame, bg=T.accent, width=26, height=26)
            av.pack(side=tk.LEFT, anchor="n", pady=(4, 0))
            av.pack_propagate(False)
            tk.Label(av, text="✦", font=("Microsoft YaHei UI", 9, "bold"),
                     bg=T.accent, fg="#0d0d1a").place(relx=0.5, rely=0.5, anchor="center")

        bubble = tk.Frame(self._loading_frame, bg=T.bot_bubble)
        bubble.pack(side=tk.LEFT, padx=(8, 40))
        tk.Label(
            bubble, text="● ● ● 正在思考",
            font=("Microsoft YaHei UI", 11),
            bg=T.bot_bubble, fg=T.text_muted,
            padx=14, pady=10,
        ).pack()

        self.msg_container.update_idletasks()
        self.msg_canvas.yview_moveto(1.0)

    def _hide_loading(self):
        if hasattr(self, "_loading_frame") and self._loading_frame:
            try:
                self._loading_frame.destroy()
            except Exception:
                pass
            self._loading_frame = None

    # ---------- 事件处理 ----------

    def _on_send(self):
        if self._waiting:
            return
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            return
        self.input_text.delete("1.0", tk.END)
        self._add_user_message(text)
        self._show_loading()

        self._waiting = True
        self.send_btn.config(text="···", state=tk.DISABLED)

        self.chat.send_message(
            message=text,
            on_response=lambda reply: self.parent.after(0, self._handle_response, reply),
            on_error=lambda err: self.parent.after(0, self._handle_error, err),
        )

    def _on_send_enter(self, event):
        if not (event.state & 0x0001):  # 没按 Shift
            self._on_send()
            return "break"

    def _handle_response(self, reply):
        self._hide_loading()
        self._add_bot_message(reply)
        self._waiting = False
        self.send_btn.config(text="发 送", state=tk.NORMAL)

    def _handle_error(self, error):
        self._hide_loading()
        self._add_bot_message(f"呜…出错了: {error}")
        self._waiting = False
        self.send_btn.config(text="发 送", state=tk.NORMAL)

    def _clear_chat(self):
        self.chat.clear_history()
        for w in self.msg_container.winfo_children():
            w.destroy()
        self._add_bot_message("记忆已经清空啦~重新开始吧！")

    def _on_close(self):
        if self.window:
            self.window.destroy()
            self.window = None
