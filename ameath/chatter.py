"""本地撩骚 - 爱弥斯时不时冒一句台词，不耗 token"""

import random
import tkinter as tk

PHRASES = [
    "好无聊呀~", "嗯…今天做什么好呢？", "嘿嘿~", "盯——",
    "好想出去玩呀~", "呼啊…好困…", "你终于来啦~", "我一直在这里哦~",
    "飘来飘去~", "唔…好安静呀", "嘿嘿嘿~", "你看我干嘛~",
    "别盯着人家看啦~", "哼！", "好耶~",
    "要不要聊聊天？", "戳我干嘛~", "再戳我就生气啦！",
    "好无聊，陪我玩嘛~", "你在看什么呀？", "我也想看——",
    "诶嘿~被发现啦", "嘻嘻，今天心情不错~", "呜…好累呀", "想吃东西了…",
    "才不是在等你呢！", "哼！我可没在想你哦！",
    "只是刚好路过而已！", "你管我在干嘛！", "我、我才不无聊呢！",
    "转圈圈~转圈圈~", "今天是美好的一天~", "呼~呼~",
    "好像有什么好玩的事情~", "偷偷看你一眼~", "被发现啦！",
    "你又在看电脑啦？", "都盯多久了…休息一下嘛~",
    "屏幕有我好看吗？", "又在敲代码了…人类的爱好真奇怪~",
    "已经这个点了还在忙呀？",
    "咦？我刚刚想说什么来着…", "这里是哪里来着？算了不管了~",
    "刚才好像听到什么声音…是错觉吧~", "一不小心就发呆了~",
    "啊…忘了要做什么了…",
    "穿墙真好玩~你要不要试试？", "人类的身体好麻烦呀~还是当幽灵好！",
    "我能飘过去你能吗~", "嘶…这个电脑有点烫…",
    "我在你电脑里哦~开玩笑的啦！",
]


class ChatterBox:
    """本地台词机 - 在宠物底部显示气泡"""

    def __init__(self, pet):
        self.pet = pet
        self.root = pet.root
        self._timer = None
        self._label = None

    def start(self):
        # 首次测试：10秒后显示
        self._timer = self.root.after(10000, self._show_random)

    def stop(self):
        if self._timer is not None:
            self.root.after_cancel(self._timer)
            self._timer = None
        self._hide()

    def _schedule_next(self):
        if self.pet._request_quit:
            return
        self._timer = self.root.after(random.randint(30000, 60000), self._show_random)

    def _show_random(self):
        if self.pet._request_quit or not self.root.winfo_exists():
            return
        if self.pet._user_hidden or self.pet.is_paused:
            self._schedule_next()
            return

        phrase = random.choice(PHRASES)
        self._hide()

        # 紧贴宠物窗口底部显示标签
        lbl = tk.Label(
            self.root,
            text=phrase,
            font=("Microsoft YaHei UI", 9),
            bg="#25254a", fg="#f0eef8",
            padx=8, pady=2,
        )
        # 放在左上角
        lbl.place(x=0, y=0, anchor="nw")
        lbl.lift()
        self._label = lbl

        self.root.after(5000, self._hide)
        self._schedule_next()

    def _hide(self):
        if self._label is not None:
            try:
                self._label.destroy()
            except Exception:
                pass
            self._label = None
