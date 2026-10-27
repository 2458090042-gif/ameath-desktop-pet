import ctypes
import threading
import tkinter as tk

# 启用 Windows DPI 感知（解决高DPI屏幕模糊问题）
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def main():
    from ameath.config import load_config
    from ameath.pet import DesktopGif
    from ameath.utils import get_version

    VERSION = get_version()

    root = tk.Tk()
    # 立即隐藏窗口，避免闪烁
    root.withdraw()

    # 创建根窗口后立即加载自定义字体
    from ameath.fonts import _load_zpix_font

    _load_zpix_font()

    class PetManager:
        def __init__(self, master, count):
            self.root = master
            self.pets = []
            self._visible = True
            self._request_quit = False
            self.is_paused = False
            # 从配置文件读取所有设置
            config = load_config()
            self.follow_mouse = config.get("follow_mouse", False)
            self.click_through = config.get("click_through", False)
            self.display_priority = config.get("display_priority", 1)
            self.voice_enabled = config.get("voice_enabled", True)
            self.voice_volume = config.get("voice_volume", 100)
            self._pet_active = True  # 键盘快捷键激活状态（右键桌宠激活，左键别处取消）
            self._create_instances(count)

        def _create_instances(self, count):
            for _ in range(count):
                pet_root = self.root if not self.pets else tk.Toplevel(self.root)
                pet = DesktopGif(pet_root)
                self.pets.append(pet)
                self._apply_state_to_pet(pet)
            self._sync_state_from_primary()

        def _sync_state_from_primary(self):
            if not self.pets:
                return
            primary = self.pets[0]
            self.is_paused = primary.is_paused
            self.follow_mouse = primary.follow_mouse
            self.click_through = primary.click_through
            self.display_priority = primary.display_priority

        def set_instance_count(self, count):
            count = max(1, int(count))
            current = len(self.pets)
            if count > current:
                for _ in range(count - current):
                    pet_root = tk.Toplevel(self.root)
                    pet = DesktopGif(pet_root)
                    self._apply_state_to_pet(pet)
                    self.pets.append(pet)
            elif count < current:
                for pet in self.pets[count:]:
                    try:
                        pet._request_quit = True
                    except Exception:
                        pass
                    try:
                        pet.root.destroy()
                    except Exception:
                        pass
                self.pets = self.pets[:count]
            self._sync_state_from_primary()

        def _apply_state_to_pet(self, pet):
            pet.follow_mouse = self.follow_mouse
            pet.click_through = self.click_through
            pet.set_click_through(self.click_through)
            if self.is_paused and not pet.is_paused:
                pet.toggle_pause()
            pet.set_display_priority(self.display_priority, persist=False)
            if not self._visible:
                pet.root.withdraw()
            # 应用语音设置
            if pet.voice_player:
                pet.voice_player.set_enabled(self.voice_enabled)
                pet.voice_player.set_volume(self.voice_volume)
            # 设置管理器引用
            pet.manager = self

        def set_click_through(self, enable):
            self.click_through = enable
            for pet in self.pets:
                pet.click_through = enable
                pet.set_click_through(enable)

        def set_follow_mouse(self, enable):
            self.follow_mouse = enable
            for pet in self.pets:
                pet.follow_mouse = enable

        def toggle_pause(self):
            for pet in self.pets:
                pet.toggle_pause()
            self._sync_state_from_primary()

        def set_scale(self, index):
            for pet in self.pets:
                pet.set_scale(index)

        def set_transparency(self, index):
            for pet in self.pets:
                pet.set_transparency(index)

        def set_display_priority(self, mode, persist=True):
            self.display_priority = mode
            for pet in self.pets:
                pet.set_display_priority(mode, persist=persist)

        def set_wander_idle_stay_mode(self, mode):
            for pet in self.pets:
                pet.set_wander_idle_stay_mode(mode)

        def set_voice_enabled(self, enabled):
            """设置所有宠物的语音开关"""
            self.voice_enabled = enabled
            for pet in self.pets:
                if pet.voice_player:
                    pet.voice_player.set_enabled(enabled)

        def set_voice_volume(self, volume):
            """设置所有宠物的语音音量"""
            self.voice_volume = volume
            for pet in self.pets:
                if pet.voice_player:
                    pet.voice_player.set_volume(volume)

        def hide_all(self):
            self._visible = False
            for pet in self.pets:
                pet._user_hidden = True  # 标记为用户手动隐藏
                pet.root.withdraw()

        def show_all(self):
            self._visible = True
            for pet in self.pets:
                pet._user_hidden = False  # 清除用户手动隐藏标记
                pet.root.deiconify()

        def is_visible(self):
            return self._visible

        def request_quit(self):
            for pet in self.pets:
                pet._request_quit = True

    # 先创建 app 实例（在后台线程之前）
    try:
        from ameath.tray import create_tray

        config = load_config()
        instance_count = config.get("instance_count", 1)
        app = PetManager(root, instance_count)

        icon = create_tray(app, VERSION)
        if app.pets:
            app.pets[0].app = icon

        # 音乐控制快捷键（GetAsyncKeyState 轮询，无边框窗口也能响应）
        # 提前初始化音乐播放器，让键盘快捷键随时可用
        try:
            from ameath.music_player import MusicPlayer
            # 完整初始化音乐播放器核心（不建GUI），确保双键/快捷键随时可播放
            mp = MusicPlayer(parent=root, create_gui=False)
            if not hasattr(mp, 'music_volume'):
                mp.music_volume = config.get("music_volume", 100)
        except:
            pass

        # 音乐控制操作函数（供轮询调用）
        def _music_prev():
            try:
                from ameath.music_player import MusicPlayer
                if MusicPlayer._instance and MusicPlayer._instance.music_files:
                    MusicPlayer._instance.previous_track()
            except:
                pass

        def _music_next():
            try:
                from ameath.music_player import MusicPlayer
                if MusicPlayer._instance and MusicPlayer._instance.music_files:
                    MusicPlayer._instance.next_track()
            except:
                pass

        def _music_toggle():
            """暂停/播放切换（单击空格）"""
            try:
                from ameath.music_player import MusicPlayer
                if MusicPlayer._instance and MusicPlayer._instance.music_files:
                    MusicPlayer._instance.toggle_play_pause()
            except:
                pass

        def _vol_up():
            ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)      # VK_VOLUME_UP 按下
            ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)      # VK_VOLUME_UP 释放

        def _vol_down():
            ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)      # VK_VOLUME_DOWN 按下
            ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)      # VK_VOLUME_DOWN 释放

        # 音乐控制快捷键（右键桌宠激活，左键点别处取消）
        _key_state = {0x25: False, 0x26: False, 0x27: False, 0x28: False}
        _lbtn_was_down = False

        def _is_mouse_over_pet():
            """检测鼠标是否悬停在任意桌宠窗口上"""
            try:
                mx = root.winfo_pointerx()
                my = root.winfo_pointery()
                for pet in app.pets:
                    if pet.x <= mx <= pet.x + pet.w and pet.y <= my <= pet.y + pet.h:
                        return True
                return False
            except:
                return False

        def _poll_music_keys():
            nonlocal _lbtn_was_down
            import time as _time

            # 检测左键点击：点在桌宠以外 → 取消激活
            lbtn_down = ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000
            if lbtn_down and not _lbtn_was_down:
                if not _is_mouse_over_pet():
                    app._pet_active = False
            _lbtn_was_down = lbtn_down

            # 未激活时跳过快捷键处理
            if not app._pet_active:
                for vk in _key_state:
                    _key_state[vk] = False
                root.after(150, _poll_music_keys)
                return

            try:
                # 方向键 — 按下瞬间触发一次
                for vk, action in [
                    (0x25, _music_prev),   # Left
                    (0x27, _music_next),   # Right
                    (0x26, _vol_up),       # Up → 系统音量+
                    (0x28, _vol_down),     # Down → 系统音量-
                ]:
                    down = ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000
                    if down and not _key_state[vk]:
                        action()
                    _key_state[vk] = down

                # Space (0x20) — 按下即切换暂停/播放
                if ctypes.windll.user32.GetAsyncKeyState(0x20) & 0x0001:
                    _music_toggle()
            except:
                pass
            root.after(30, _poll_music_keys)

        root.after(500, _poll_music_keys)

        # 后台检查版本（非阻塞）- 仅打印日志，不弹窗
        threading.Thread(
            target=lambda: _check_version_print(VERSION), daemon=True
        ).start()

        # 延迟启动托盘，让窗口完全初始化后再显示
        root.update_idletasks()
        root.deiconify()  # 显示窗口（避免边框闪烁）
        root.after(500, lambda: icon.run_detached())

        root.mainloop()

    except ImportError:
        # 没有pystray时正常运行窗口
        print("未安装pystray，将只显示窗口。可运行: pip install pystray")

        # 创建 app（没有托盘时）
        config = load_config()
        instance_count = config.get("instance_count", 1)
        app = PetManager(root, instance_count)

        # 后台检查版本（非阻塞）- 仅打印日志，不弹窗
        threading.Thread(
            target=lambda: _check_version_print(VERSION), daemon=True
        ).start()

        root.deiconify()  # 显示窗口
        root.mainloop()

        # 结束


def _check_version_print(version):
    """检查版本更新并打印结果，不弹设置窗口"""
    from ameath.utils import check_new_version, version_greater_than
    latest = check_new_version()
    if latest and version_greater_than(latest, version):
        print(f"发现新版本: {latest}，当前版本: {version}")


if __name__ == "__main__":
    main()
