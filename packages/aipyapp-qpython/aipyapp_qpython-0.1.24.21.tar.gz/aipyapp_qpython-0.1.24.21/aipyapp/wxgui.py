#!/usr/bin/env python
#coding: utf-8

import os
import sys
import time
import json
import queue
import base64
import mimetypes
import traceback
import threading
import importlib.resources as resources

import wx
import wx.html2
import matplotlib
import matplotlib.pyplot as plt
from rich.console import Console
from wx.lib.newevent import NewEvent
from wx import FileDialog, FD_SAVE, FD_OVERWRITE_PROMPT

from . import __version__
from .aipy.config import ConfigManager
from .aipy import TaskManager, event_bus
from .aipy.i18n import T,set_lang

__PACKAGE_NAME__ = "aipyapp"
ChatEvent, EVT_CHAT = NewEvent()
AVATARS = {'我': '🧑', 'BB-8': '🤖', '图灵': '🧠', '爱派': '🐙'}

matplotlib.use('Agg')

def image_to_base64(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        return None

    try:
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        return None

    data_url = f"data:{mime_type};base64,{encoded_string}"
    return data_url

class AIPython(threading.Thread):
    def __init__(self, gui):
        super().__init__(daemon=True)
        self.gui = gui
        self.tm = gui.tm
        plt.show = self.on_plt_show
        sys.modules["matplotlib.pyplot"] = plt

    def on_plt_show(self, *args, **kwargs):
        filename = f'{time.strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(filename)
        user = 'BB-8'
        content = f'![{filename}]({filename})'
        evt = ChatEvent(user=user, msg=content)
        wx.PostEvent(self.gui, evt)

    def on_display(self, image):
        user = '图灵'
        if image['path']:
            base64_data = image_to_base64(image['path'])
            content = base64_data if base64_data else image['path']
        else:
            content = image['url']

        msg = f'![图片]({content})'
        evt = ChatEvent(user=user, msg=msg)
        wx.PostEvent(self.gui, evt)

    def on_response_complete(self, msg):
        user = '图灵' #msg['llm']
        #content = f"```markdown\n{msg['content']}\n```"
        evt = ChatEvent(user=user, msg=msg['content'])
        wx.PostEvent(self.gui, evt)

    def on_summary(self, summary):
        user = '爱派'
        evt = ChatEvent(user=user, msg=f'结束处理指令 {summary}')
        wx.PostEvent(self.gui, evt)

    def on_exec(self, blocks):
        user = 'BB-8'
        content = f"```python\n{blocks['main']}\n```"
        evt = ChatEvent(user=user, msg=content)
        wx.PostEvent(self.gui, evt)

    def on_result(self, result):
        user = 'BB-8'
        content = json.dumps(result, indent=4, ensure_ascii=False)
        content = f'运行结果如下\n```json\n{content}\n```'
        evt = ChatEvent(user=user, msg=content)
        wx.PostEvent(self.gui, evt)

    def run(self):
        event_bus.register("response_stream", self.on_response_complete)
        event_bus.register("exec", self.on_exec)
        event_bus.register("result", self.on_result)
        event_bus.register("summary", self.on_summary)
        event_bus.register("display", self.on_display)
        while True:
            instruction = self.gui.get_task()
            if instruction in ('/done', 'done'):
                self.tm.done()
            elif instruction in ('/exit', 'exit'):
                break
            else:
                try:
                    self.tm(instruction)
                except Exception as e:
                    traceback.print_exc()
            wx.CallAfter(self.gui.toggle_input)

class CStatusBar(wx.StatusBar):
    def __init__(self, parent):
        super().__init__(parent, style=wx.STB_DEFAULT_STYLE)
        self.parent = parent
        self.SetFieldsCount(2)
        self.SetStatusWidths([-1, 80])

        self.tm = parent.tm
        self.current_llm = self.tm.llm.names['default']
        self.enabled_llm = list(self.tm.llm.names['enabled'])
        self.menu_items = self.enabled_llm
        self.radio_group = []

        self.SetStatusText(f"{self.current_llm} ▾", 1)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)

    def on_click(self, event):
        rect = self.GetFieldRect(1)
        if rect.Contains(event.GetPosition()):
            self.show_menu()

    def show_menu(self):
        self.current_menu = wx.Menu()
        self.radio_group = []
        for label in self.menu_items:
            item = wx.MenuItem(self.current_menu, wx.ID_ANY, label, kind=wx.ITEM_RADIO)
            self.current_menu.Append(item)
            self.radio_group.append(item)
            self.Bind(wx.EVT_MENU, self.on_menu_select, item)

        rect = self.GetFieldRect(1)
        pos = self.ClientToScreen(rect.GetBottomLeft())
        self.PopupMenu(self.current_menu, self.ScreenToClient(pos))

    def on_menu_select(self, event):
        item = self.current_menu.FindItemById(event.GetId())
        label = item.GetItemLabel()
        if self.tm.use(label):
            self.current_llm = label
            self.SetStatusText(f"{label} ▾", 1)
        else:
            wx.MessageBox(f"LLM {label} 不可用", "警告", wx.OK|wx.ICON_WARNING)

class ChatFrame(wx.Frame):
    def __init__(self, tm):
        super().__init__(None, title=f"Python-use: AIPy (v{__version__})", size=(1024, 768))
        
        self.tm = tm
        self.task_queue = queue.Queue()
        self.aipython = AIPython(self)

        icon = wx.Icon(str(resources.files(__PACKAGE_NAME__) / "aipy.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.SetBackgroundColour(wx.Colour(245, 245, 245))
        self.make_menu_bar()
        self.make_panel()
        self.statusbar = CStatusBar(self)
        self.SetStatusBar(self.statusbar)

        self.Bind(EVT_CHAT, self.on_chat)
        self.aipython.start()
        self.Show()

    def make_panel(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        html_file_path = os.path.abspath(resources.files(__PACKAGE_NAME__) / "chatroom.html")
        self.webview = wx.html2.WebView.New(panel)
        self.webview.SetPage(open(html_file_path, 'r', encoding='utf-8').read(), f'file://{self.tm.workdir}')
        self.webview.SetWindowStyleFlag(wx.BORDER_NONE)
        vbox.Add(self.webview, proportion=1, flag=wx.EXPAND | wx.ALL, border=12)

        self.container = wx.Panel(panel)
        vbox.Add(self.container, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=12)

        self.input = wx.TextCtrl(self.container, style=wx.TE_MULTILINE)
        self.input.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.input.SetForegroundColour(wx.Colour(33, 33, 33))
        self.input.SetMinSize((-1, 60))
        self.input.SetWindowStyleFlag(wx.BORDER_SIMPLE)
        self.input.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

        self.send_button = wx.Button(self.container, label="发送", size=(50, -1))
        self.send_button.Bind(wx.EVT_BUTTON, self.on_send)
        self.container.Bind(wx.EVT_SIZE, self.on_container_resize)

        panel.SetSizer(vbox)
        self.panel = panel

    def make_menu_bar(self):
        menu_bar = wx.MenuBar()
        menu_bar.SetBackgroundColour(wx.Colour(240, 240, 240))
        
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_SAVE, "保存聊天记录为 HTML(&S)\tCtrl+S", "保存当前聊天记录为 HTML 文件")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "退出(&Q)\tCtrl+Q", "退出程序")
        self.Bind(wx.EVT_MENU, self.on_save_html, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)

        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_CLEAR, "清空聊天(&C)", "清除所有消息")
        self.Bind(wx.EVT_MENU, self.on_clear_chat, id=wx.ID_CLEAR)

        help_menu = wx.Menu()
        self.ID_WEBSITE = wx.NewIdRef()
        menu_item = wx.MenuItem(help_menu, self.ID_WEBSITE, "官网(&W)\tCtrl+W", "打开官方网站")
        help_menu.Append(menu_item)
        self.ID_FORUM = wx.NewIdRef()
        menu_item = wx.MenuItem(help_menu, self.ID_FORUM, "论坛(&W)\tCtrl+F", "打开官方论坛")
        help_menu.Append(menu_item)
        self.Bind(wx.EVT_MENU, self.on_open_website, id=self.ID_WEBSITE)
        self.Bind(wx.EVT_MENU, self.on_open_website, id=self.ID_FORUM)

        menu_bar.Append(file_menu, "文件(&F)")
        menu_bar.Append(edit_menu, "编辑(&E)")
        menu_bar.Append(help_menu, "帮助(&H)")

        self.SetMenuBar(menu_bar)

    def on_exit(self, event):
        self.task_queue.put('exit')
        self.aipython.join()
        self.Close()

    def on_container_resize(self, event):
        # 获取容器和按钮的大小
        container_size = event.GetSize()
        button_size = self.send_button.GetSize()

        overlap = -10
        self.input.SetSize(container_size)

        button_pos_x = container_size.width - button_size.width + overlap
        if sys.platform == 'darwin':
            button_pos_y = container_size.height - button_size.height - 10
        else:
            button_pos_y = (container_size.height - button_size.height) // 2
        self.send_button.SetPosition((button_pos_x, button_pos_y))

        event.Skip()

    def on_clear_chat(self, event):
        pass

    def on_open_website(self, event):
        if event.GetId() == self.ID_WEBSITE:
            url = "https://aipy.app"
        elif event.GetId() == self.ID_FORUM:
            url = "https://d.aipy.app"
        wx.LaunchDefaultBrowser(url)

    def on_save_html(self, event):
        try:
            html_content = self.webview.GetPageSource()
            self.save_html_content(html_content)
        except Exception as e:
            wx.MessageBox(f"save html error: {e}", "Error")

    def save_html_content(self, html_content):
        with FileDialog(self, "保存聊天记录为 HTML 文件", wildcard="HTML 文件 (*.html)|*.html",
                        style=FD_SAVE | FD_OVERWRITE_PROMPT) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return

            path = dialog.GetPath()
            try:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(html_content)
            except IOError:
                wx.LogError(f"无法保存文件：{path}")

    def on_key_down(self, event):
        keycode = event.GetKeyCode()
        send_shortcut = (event.ControlDown() or event.CmdDown()) and keycode == wx.WXK_RETURN

        if send_shortcut:
            self.send_message()
        else:
            event.Skip()

    def on_send(self, event):
        self.send_message()

    def get_task(self):
        return self.task_queue.get()

    def toggle_input(self):
        if self.container.IsShown():
            self.container.Hide()
            wx.BeginBusyCursor()
            self.SetStatusText("操作进行中，请稍候...", 0)
        else:
            self.container.Show()
            wx.EndBusyCursor()
            self.SetStatusText("操作完成", 0)
        self.panel.Layout()
        self.panel.Refresh()

    def send_message(self):
        text = self.input.GetValue().strip()
        if not text:
            return
        self.append_message('我', text)
        self.input.Clear()
        self.toggle_input()
        self.task_queue.put(text)

    def on_chat(self, event):
        user = event.user
        text = event.msg
        self.append_message(user, text)

    def append_message(self, user, text):
        avatar = AVATARS[user]
        js_code = f'appendMessage("{avatar}", "{user}", {repr(text)});'
        self.webview.RunScript(js_code)

    def refresh_chat(self):
        wx.CallLater(100, lambda: self.browser.RunScript("window.scrollTo(0, document.body.scrollHeight);"))

    def on_stop_task(self, event):
        self.tm.done()
        self.SetStatusText("任务已停止", 0)

def main(args):
    default_config_path = resources.files(__PACKAGE_NAME__) / "default.toml"
    conf = ConfigManager(default_config_path, args.config_dir)
    conf.check_config()
    settings = conf.get_config()

    settings.auto_install = True
    settings.auto_getenv = True

    lang = settings.get('lang')
    if lang: set_lang(lang)

    console = Console(quiet=True, record=True)
    try:
        tm = TaskManager(settings, console=console)
    except Exception as e:
        traceback.print_exc()
        return
    
    app = wx.App()
    ChatFrame(tm)
    app.MainLoop()
