"""音乐播放器标签页"""

import random
import tkinter as tk

from ..config import load_config, save_config


def create_music_tab(settings_window, parent):
    """创建音乐播放器标签页 - 歌姬偶像风格

    采用懒加载：打开设置窗口时不立即构建播放器UI（构建约需1秒，会卡住桌宠），
    等用户切换到音乐标签页时才由 init_music_tab_if_needed 初始化。
    """
    frame = tk.Frame(parent, bg=settings_window.colors["bg"])
    frame._lazy_music = True
    return frame


def init_music_tab_if_needed(settings_window):
    """懒加载初始化音乐标签页UI。返回是否执行了初始化"""
    music_frame = getattr(settings_window, "music_frame", None)
    if music_frame is None or not getattr(music_frame, "_lazy_music", False):
        return False

    settings_window.music_player_embedded = MusicPlayerEmbedded(
        music_frame, settings_window.colors, settings_window.fonts, settings_window
    )
    music_frame._lazy_music = False
    return True


class MusicPlayerEmbedded:
    """内嵌音乐播放器 - 歌姬偶像风格"""

    def __init__(self, parent, colors, fonts, settings_window=None):
        self.parent = parent
        self.colors = colors
        self.fonts = fonts
        self.settings_window = settings_window
        self.config = load_config()

        from ..music_player import MusicPlayer
        import tkinter as tk

        dummy_frame = tk.Frame(parent)
        self.core_player = MusicPlayer(
            parent=dummy_frame,
            position_unlock_callback=None,
            create_gui=False,  # 嵌入式UI接管界面，避免重复构建播放器GUI拖慢打开速度
        )

        self.music_files = self.core_player.music_files
        self.current_index = self.core_player.current_index
        self.is_playing = self.core_player.is_playing
        self.is_paused = self.core_player.is_paused

        self.music_volume = self.config.get("music_volume", 100)
        self.music_enabled = self.config.get("music_enabled", False)

        self.core_player.music_volume = self.music_volume

        # 确保初始随机播放状态同步到核心播放器
        self._sync_shuffle_mode_from_config()

        self._create_ui()
        self._load_music_files()
        self._start_progress_loop()

    def _sync_shuffle_mode_from_config(self):
        """从配置读取随机播放状态并同步到核心播放器"""
        from ..music_player import MusicPlayer as CoreMusicPlayer
        shuffle = self.config.get("shuffle_mode", False)
        self.core_player.shuffle_mode = shuffle
        CoreMusicPlayer._shared_shuffle_mode = shuffle

    def _create_ui(self):
        """创建音乐播放器UI - 歌姬偶像风格"""
        main_frame = tk.Frame(self.parent, bg=self.colors["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ===== 演出曲目列表 =====
        playlist_frame = tk.LabelFrame(
            main_frame,
            text="🎵 演出曲目",
            font=self.fonts["subtitle"],
            padx=15,
            pady=12,
            bg=self.colors["card_bg"],
            fg=self.colors["accent_dark"],
            bd=1,
            relief=tk.SOLID,
        )
        playlist_frame.pack(fill=tk.X, pady=(0, 10), ipady=2)

        list_container = tk.Frame(playlist_frame, bg=self.colors["card_bg"])
        list_container.pack(fill=tk.X, pady=5)

        scrollbar = tk.Scrollbar(list_container, bg=self.colors["card_bg"])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            list_container,
            yscrollcommand=scrollbar.set,
            bg=self.colors["bg"],
            fg=self.colors["text"],
            selectbackground=self.colors["accent"],
            selectforeground="white",
            font=self.fonts["base"],
            bd=2,
            relief=tk.SUNKEN,
            highlightthickness=0,
            activestyle="none",
            height=10,
            width=45,
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind("<ButtonRelease-1>", self._on_single_click)

        self.music_folder = self._get_user_music_folder()

        folder_label = tk.Label(
            playlist_frame,
            text=f"📁 打开歌曲文件夹: {self.music_folder}",
            font=self.fonts["small"],
            bg=self.colors["card_bg"],
            fg=self.colors["accent"],
            cursor="hand2",
        )
        folder_label.pack(pady=(3, 0))
        folder_label.bind("<Button-1>", lambda e: self._open_music_folder())

        refresh_btn = tk.Label(
            playlist_frame,
            text="🔄 点击刷新歌曲列表",
            font=self.fonts["small"],
            bg=self.colors["card_bg"],
            fg=self.colors["subtext"],
            cursor="hand2",
        )
        refresh_btn.pack(pady=(2, 0))
        refresh_btn.bind("<Button-1>", lambda e: self._refresh_list())

        # ===== 演出控制台 =====
        console_frame = tk.LabelFrame(
            main_frame,
            text="🎮 演出控制台",
            font=self.fonts["subtitle"],
            padx=15,
            pady=12,
            bg=self.colors["card_bg"],
            fg=self.colors["accent_dark"],
            bd=1,
            relief=tk.SOLID,
        )
        console_frame.pack(fill=tk.X, pady=(0, 10), ipady=5)

        btn_row = tk.Frame(console_frame, bg=self.colors["card_bg"])
        btn_row.pack(fill=tk.X, pady=(0, 8))

        base_btn = {
            "bg": self.colors["accent"],
            "fg": "white",
            "activebackground": self.colors["accent_dark"],
            "activeforeground": "white",
            "font": self.fonts["control"],
            "relief": tk.FLAT,
            "bd": 0,
            "cursor": "hand2",
            "height": 1,
        }

        self.prev_btn = tk.Button(
            btn_row,
            text="◀◀ 上一曲",
            width=10,
            command=self._previous_track,
            **base_btn,
            state=tk.NORMAL if self.music_enabled else tk.DISABLED,
        )
        self.prev_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.play_btn = tk.Button(
            btn_row,
            text="▶ 演出开始",
            width=12,
            command=self._toggle_play,
            **base_btn,
            state=tk.NORMAL if self.music_enabled else tk.DISABLED,
        )
        self.play_btn.pack(side=tk.LEFT, padx=4)

        self.next_btn = tk.Button(
            btn_row,
            text="下一曲 ▶▶",
            width=10,
            command=self._next_track,
            **base_btn,
            state=tk.NORMAL if self.music_enabled else tk.DISABLED,
        )
        self.next_btn.pack(side=tk.LEFT, padx=(8, 0))

        # 播放模式切换（顺序/随机）
        self.shuffle_mode = self.config.get("shuffle_mode", False)
        mode_text = "📋 顺序" if not self.shuffle_mode else "🔀 随机"
        self.mode_btn = tk.Button(
            btn_row,
            text=mode_text,
            width=9,
            command=self._toggle_mode,
            **{**base_btn, "bg": "#B388FF"},
            state=tk.NORMAL if self.music_enabled else tk.DISABLED,
        )
        self.mode_btn.pack(side=tk.LEFT, padx=(8, 0))

        # 进度条
        progress_row = tk.Frame(console_frame, bg=self.colors["card_bg"])
        progress_row.pack(fill=tk.X, pady=(8, 5))

        tk.Label(
            progress_row,
            text="演出进度:",
            font=self.fonts["control"],
            bg=self.colors["card_bg"],
            fg=self.colors["text"],
        ).pack(side=tk.LEFT)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = tk.Scale(
            progress_row,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.progress_var,
            length=280,
            font=self.fonts["small"],
            bg=self.colors["card_bg"],
            fg=self.colors["text"],
            highlightthickness=0,
            troughcolor="#E0C8D4",
            activebackground=self.colors["accent"],
            sliderrelief=tk.RAISED,
            width=14,
            state=tk.NORMAL if self.music_enabled else tk.DISABLED,
        )
        self._seeking = False
        self.progress_bar.pack(side=tk.LEFT, padx=(5, 8), fill=tk.X, expand=True)
        self.progress_bar.bind("<ButtonPress-1>", self._on_seek_start)
        self.progress_bar.bind("<ButtonRelease-1>", self._on_seek)

        self.time_label = tk.Label(
            progress_row,
            text="0:00 / 0:00",
            font=self.fonts["control"],
            bg=self.colors["card_bg"],
            fg=self.colors["accent_dark"],
            width=12,
        )
        self.time_label.pack(side=tk.LEFT)

        # ===== 音效设定 =====
        settings_frame = tk.LabelFrame(
            main_frame,
            text="🔧 音效设定",
            font=self.fonts["subtitle"],
            padx=15,
            pady=12,
            bg=self.colors["card_bg"],
            fg=self.colors["accent_dark"],
            bd=1,
            relief=tk.SOLID,
        )
        settings_frame.pack(fill=tk.X, pady=(0, 10), ipady=5)

        volume_row = tk.Frame(settings_frame, bg=self.colors["card_bg"])
        volume_row.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            volume_row,
            text="场馆音量: ",
            font=self.fonts["control"],
            bg=self.colors["card_bg"],
            fg=self.colors["text"],
        ).pack(side=tk.LEFT)

        self.volume_var = tk.IntVar(value=self.music_volume)
        volume_scale = tk.Scale(
            volume_row,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            command=self._on_volume_change,
            length=250,
            font=self.fonts["small"],
            bg=self.colors["card_bg"],
            fg=self.colors["text"],
            highlightthickness=0,
            troughcolor=self.colors["tab_bg"],
            activebackground=self.colors["accent"],
            sliderrelief=tk.FLAT,
            state=tk.NORMAL if self.music_enabled else tk.DISABLED,
        )
        volume_scale.pack(side=tk.LEFT, padx=(5, 10))

        self.volume_label = tk.Label(
            volume_row,
            text=f"{self.music_volume}%",
            font=self.fonts["control"],
            bg=self.colors["card_bg"],
            fg=self.colors["accent_dark"],
            width=5,
        )
        self.volume_label.pack(side=tk.LEFT)

        self.action_buttons = []

    def _get_user_music_folder(self):
        """获取用户音乐文件夹路径"""
        import os
        import shutil
        from ..utils import resource_path

        music_folder = os.path.normpath(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "sound",
                "music",
            )
        )

        if not os.path.exists(music_folder):
            os.makedirs(music_folder, exist_ok=True)
            bundled_music = resource_path("sound/music")
            if os.path.exists(bundled_music):
                for file in os.listdir(bundled_music):
                    if file.lower().endswith((".wav", ".mp3", ".flac")):
                        src = os.path.join(bundled_music, file)
                        dst = os.path.join(music_folder, file)
                        shutil.copy2(src, dst)

        return music_folder

    def _open_music_folder(self):
        """打开音乐文件夹"""
        import os
        import subprocess
        try:
            subprocess.Popen(f'explorer "{self.music_folder}"', shell=True)
        except Exception as e:
            print(f"打开文件夹失败: {e}")

    def _load_music_files(self):
        """加载音乐文件列表"""
        import os
        music_dir = self.music_folder
        self.music_files = []

        if os.path.exists(music_dir):
            for file in sorted(os.listdir(music_dir)):
                if file.lower().endswith((".wav", ".mp3", ".flac")):
                    self.music_files.append(os.path.join(music_dir, file))

        self.core_player.music_files = self.music_files
        self.core_player.load_music_files_internal()
        self._update_listbox()

    def _update_listbox(self):
        """更新列表框显示"""
        import os
        self.listbox.delete(0, tk.END)
        for file in self.music_files:
            self.listbox.insert(tk.END, f" ♪ {os.path.basename(file)}")

        if self.current_index >= 0 and self.current_index < len(self.music_files):
            self.listbox.selection_set(self.current_index)
            self.listbox.see(self.current_index)

    def _on_seek_start(self, event):
        """开始拖动进度条，暂停UI更新防止覆盖"""
        self._seeking = True

    def _on_seek(self, event):
        """鼠标松开进度条时跳转到指定位置"""
        self._seeking = False
        if not self.music_files or self.current_index < 0:
            return
        if not self.is_playing and not self.is_paused:
            return
        value = self.progress_var.get()
        self.core_player.on_progress_change(value)

    def _on_volume_change(self, value):
        """音量改变"""
        volume = int(float(value))
        self.music_volume = volume
        self.volume_label.config(text=f"{volume}%")
        self.core_player.music_volume = volume
        self.core_player.apply_current_volume()

        config = load_config()
        config["music_volume"] = volume
        save_config(config)

        if self.settings_window and hasattr(self.settings_window, 'music_volume_var'):
            self.settings_window.music_volume_var.set(volume)

    def _on_single_click(self, event):
        """单击播放"""
        if not self.music_enabled:
            return
        selection = self.listbox.curselection()
        if selection:
            self.current_index = selection[0]
            self._play_current()

    def _toggle_play(self):
        """播放/暂停切换"""
        if not self.music_enabled:
            return
        if self.is_playing:
            self._pause()
        elif self.is_paused:
            # 从暂停位置继续
            self.core_player.toggle_play_pause()
            self.is_playing = self.core_player.is_playing
            self.is_paused = self.core_player.is_paused
            self.play_btn.config(text="⏸ 暂停演出")
        else:
            self._play_current()

    def _play_current(self):
        """播放当前选中的歌曲"""
        if not self.music_files:
            return

        if self.current_index < 0:
            self.current_index = random.randint(0, len(self.music_files) - 1)
            self._update_listbox()

        self.core_player.current_index = self.current_index
        self.core_player.music_files = self.music_files
        self.core_player.play_current_track()

        self.is_playing = self.core_player.is_playing
        self.is_paused = self.core_player.is_paused
        self.play_btn.config(text="⏸ 暂停演出")

    def _pause(self):
        """暂停播放"""
        self.core_player.toggle_play_pause()
        self.is_playing = self.core_player.is_playing
        self.is_paused = self.core_player.is_paused
        self.play_btn.config(text="▶ 继续演出")

    def _previous_track(self):
        """上一首"""
        if not self.music_files:
            return
        self.current_index = (self.current_index - 1) % len(self.music_files)
        self._update_listbox()
        if self.is_playing:
            self._play_current()

    def _next_track(self):
        """下一首"""
        if not self.music_files:
            return
        if self.shuffle_mode:
            n = len(self.music_files)
            if n > 1:
                idx = random.randint(0, n - 2)
                if idx >= self.current_index:
                    idx += 1
                self.current_index = idx
            else:
                self.current_index = 0
        else:
            self.current_index = (self.current_index + 1) % len(self.music_files)
        self._update_listbox()
        if self.is_playing:
            self._play_current()

    def _toggle_mode(self):
        """切换播放模式（顺序/随机）"""
        self.shuffle_mode = not self.shuffle_mode
        mode_text = "📋 顺序" if not self.shuffle_mode else "🔀 随机"
        self.mode_btn.config(text=mode_text)
        config = load_config()
        config["shuffle_mode"] = self.shuffle_mode
        save_config(config)
        if hasattr(self.core_player, 'shuffle_mode'):
            self.core_player.shuffle_mode = self.shuffle_mode
            # 同步共享变量，确保键盘快捷键（← →）也使用正确的模式
            self.core_player._sync_to_shared()

    def _start_progress_loop(self):
        """启动进度更新循环"""
        self._update_progress_ui()

    def _update_progress_ui(self):
        """更新进度UI"""
        try:
            if self.core_player.is_playing and not self.core_player.is_paused:
                if self.play_btn.cget("text") != "⏸ 暂停演出":
                    self.play_btn.config(text="⏸ 暂停演出")

                if self.core_player.total_length > 0 and self.core_player.sample_rate:
                    current_ms = int(
                        self.core_player.current_position
                        * 1000
                        / self.core_player.sample_rate
                    )
                    if not self._seeking:
                        progress = (
                            (current_ms / self.core_player.total_length) * 100
                            if self.core_player.total_length > 0
                            else 0
                        )
                        self.progress_var.set(min(progress, 100))

                    self.time_label.config(
                        text=f"{self._format_time(current_ms)} / {self._format_time(self.core_player.total_length)}"
                    )
            else:
                if (
                    self.core_player.is_paused
                    and self.play_btn.cget("text") != "▶ 继续演出"
                ):
                    self.play_btn.config(text="▶ 继续演出")

            if hasattr(self, "parent") and self.parent.winfo_exists():
                self.parent.after(100, self._update_progress_ui)
        except Exception as e:
            if hasattr(self, "parent"):
                try:
                    if self.parent.winfo_exists():
                        self.parent.after(100, self._update_progress_ui)
                except Exception:
                    pass

    def _format_time(self, ms):
        """格式化时间显示"""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"

    def _refresh_list(self):
        """刷新音乐列表"""
        self._load_music_files()
