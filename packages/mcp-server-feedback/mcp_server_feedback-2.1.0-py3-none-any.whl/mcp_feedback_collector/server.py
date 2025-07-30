"""
交互式反馈收集器 MCP 服务器
AI调用时会汇报工作内容，用户可以提供文本反馈和/或图片反馈
支持GUI和Web两种界面模式，自动适配运行环境
"""

import io
import base64
import os
import sys
import socket
import threading
import queue
import time
import json
import tempfile
import subprocess
import platform
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# 尝试导入GUI相关模块
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

# 导入Web相关模块
try:
    from flask import Flask, render_template_string, request, jsonify, redirect, url_for
    from werkzeug.utils import secure_filename
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

# 导入图片处理模块
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# 导入进程管理模块
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.types import Image as MCPImage

# 创建MCP服务器
mcp = FastMCP(
    "交互式反馈收集器",
    dependencies=["pillow", "flask", "psutil"]
)

# 配置超时时间（秒）
DEFAULT_DIALOG_TIMEOUT = 300  # 5分钟
DIALOG_TIMEOUT = int(os.getenv("MCP_DIALOG_TIMEOUT", DEFAULT_DIALOG_TIMEOUT))

# 显示模式配置
DISPLAY_MODE = os.getenv("MCP_DISPLAY_MODE", "auto").lower()

# 端口配置
DEFAULT_PORT_RANGE = range(8000, 8100)
PORT_RANGE = DEFAULT_PORT_RANGE
WEB_PORT = os.getenv("MCP_WEB_PORT")  # 用户指定的端口


class PortManager:
    """端口和进程管理器"""

    def __init__(self):
        self.pid_file = os.path.join(tempfile.gettempdir(), "mcp_feedback_servers.json")

    def find_free_port(self) -> int:
        """寻找可用端口"""
        # 如果用户指定了端口，优先使用
        if WEB_PORT:
            try:
                port = int(WEB_PORT)
                if not self.is_port_in_use(port):
                    return port
                else:
                    print(f"⚠️ 指定端口{port}被占用，将自动寻找其他端口")
            except ValueError:
                print(f"⚠️ 无效的端口号: {WEB_PORT}")

        # 首先尝试动态分配
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            s.listen(1)
            port = s.getsockname()[1]
            if port not in PORT_RANGE:
                return port

        # 如果动态端口不在范围内，在指定范围内寻找
        for port in PORT_RANGE:
            if not self.is_port_in_use(port):
                return port

        raise Exception("没有可用端口")

    def is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return False
            except OSError:
                return True

    def kill_process_on_port(self, port: int):
        """杀死占用指定端口的进程"""
        try:
            if platform.system() == "Windows":
                # Windows系统
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True, capture_output=True, text=True
                )
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if f':{port}' in line and 'LISTENING' in line:
                            pid = line.split()[-1]
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                            print(f"🔄 已终止占用端口{port}的进程 PID:{pid}")
            else:
                # Linux/Mac系统
                result = subprocess.run(
                    f'lsof -ti:{port}',
                    shell=True, capture_output=True, text=True
                )
                if result.stdout:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            subprocess.run(f'kill -9 {pid}', shell=True)
                            print(f"🔄 已终止占用端口{port}的进程 PID:{pid}")
        except Exception as e:
            print(f"⚠️ 清理端口{port}时出错: {e}")

    def cleanup_old_servers(self):
        """清理所有旧的服务器实例"""
        if not PSUTIL_AVAILABLE:
            print("⚠️ psutil不可用，跳过进程清理")
            return

        current_pid = os.getpid()

        # 清理已记录的服务器
        servers = self.load_servers()
        for pid_str, info in list(servers.items()):
            pid = int(pid_str)
            if pid != current_pid:
                try:
                    # 检查进程是否还存在
                    if psutil.pid_exists(pid):
                        proc = psutil.Process(pid)
                        proc.terminate()
                        proc.wait(timeout=3)
                        print(f"🔄 已终止旧服务器进程 PID:{pid}, Port:{info['port']}")
                except (psutil.NoSuchProcess, psutil.TimeoutExpired, OSError):
                    pass
                finally:
                    del servers[pid_str]

        # 清理所有MCP反馈收集器进程
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['pid'] != current_pid:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'mcp-feedback-collector' in cmdline or 'feedback_server' in cmdline:
                        print(f"🔄 发现旧进程 PID:{proc.info['pid']}, 正在终止...")
                        proc.terminate()
                        proc.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass

        self.save_servers(servers)

    def register_server(self, port: int, pid: int):
        """注册新的服务器实例"""
        servers = self.load_servers()
        servers[str(pid)] = {
            "port": port,
            "pid": pid,
            "start_time": time.time()
        }
        self.save_servers(servers)

    def load_servers(self) -> Dict:
        """加载服务器记录"""
        try:
            with open(self.pid_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_servers(self, servers: Dict):
        """保存服务器记录"""
        try:
            with open(self.pid_file, 'w') as f:
                json.dump(servers, f)
        except Exception as e:
            print(f"⚠️ 保存服务器记录失败: {e}")


def detect_display_environment() -> str:
    """检测显示环境类型"""
    # 如果用户强制指定了模式，优先使用
    if DISPLAY_MODE != "auto":
        if DISPLAY_MODE in ["gui", "web", "cli"]:
            return DISPLAY_MODE
        else:
            print(f"⚠️ 无效的显示模式: {DISPLAY_MODE}，使用自动检测")

    # 检查是否有DISPLAY环境变量（Linux/Mac X11）
    if os.environ.get('DISPLAY'):
        return 'gui'

    # 检查是否是Windows且有GUI
    if platform.system() == "Windows" and GUI_AVAILABLE:
        return 'gui'

    # 检查是否是SSH连接
    if os.environ.get('SSH_CLIENT') or os.environ.get('SSH_TTY'):
        return 'web'

    # 检查是否有Web支持
    if WEB_AVAILABLE:
        return 'web'

    # 最后尝试GUI
    if GUI_AVAILABLE:
        return 'gui'

    return 'cli'


class FeedbackDialog:
    def __init__(self, work_summary: str = "", timeout_seconds: int = DIALOG_TIMEOUT):
        self.result_queue = queue.Queue()
        self.work_summary = work_summary
        self.timeout_seconds = timeout_seconds
        self.selected_images = []  # 支持多张图片
        self.display_mode = detect_display_environment()

        # GUI模式相关
        self.root = None
        self.image_preview_frame = None
        self.text_widget = None

        # Web模式相关
        self.flask_app = None
        self.server_thread = None
        self.port = None
        self.port_manager = PortManager()

    def show_dialog(self):
        """显示反馈收集对话框，自动选择GUI或Web模式"""
        print(f"🎯 检测到显示环境: {self.display_mode}")

        if self.display_mode == 'gui' and GUI_AVAILABLE:
            return self.show_gui_dialog()
        elif self.display_mode == 'web' and WEB_AVAILABLE:
            return self.show_web_dialog()
        else:
            raise Exception(f"不支持的显示环境: {self.display_mode}，请安装相应依赖")

    def show_gui_dialog(self):
        """显示GUI对话框（原tkinter实现）"""
        def run_dialog():
            self.root = tk.Tk()
            self.root.title("🎯 工作完成汇报与反馈收集")
            self.root.geometry("700x800")
            self.root.resizable(True, True)
            self.root.configure(bg="#f5f5f5")

            # 设置窗口图标和样式
            try:
                self.root.iconbitmap(default="")
            except:
                pass

            # 居中显示窗口
            self.root.eval('tk::PlaceWindow . center')

            # 创建界面
            self.create_gui_widgets()

            # 运行主循环
            self.root.mainloop()

        # 在新线程中运行对话框
        dialog_thread = threading.Thread(target=run_dialog)
        dialog_thread.daemon = True
        dialog_thread.start()

        # 等待结果
        try:
            result = self.result_queue.get(timeout=self.timeout_seconds)
            return result
        except queue.Empty:
            return None

    def show_web_dialog(self):
        """显示Web对话框"""
        try:
            # 清理旧服务器
            self.port_manager.cleanup_old_servers()

            # 寻找可用端口
            self.port = self.port_manager.find_free_port()

            # 如果端口被占用，强制清理
            if self.port_manager.is_port_in_use(self.port):
                print(f"⚠️ 端口{self.port}被占用，正在清理...")
                self.port_manager.kill_process_on_port(self.port)
                time.sleep(1)

            # 注册当前服务器
            current_pid = os.getpid()
            self.port_manager.register_server(self.port, current_pid)

            # 创建Flask应用
            self.create_flask_app()

            # 启动Web服务器
            self.start_web_server()

            # 通知用户
            print(f"🌐 反馈收集服务已启动")
            print(f"📍 请在浏览器中打开: http://localhost:{self.port}")
            print(f"⏰ 服务将在{self.timeout_seconds}秒后自动关闭")

            # 等待结果
            try:
                result = self.result_queue.get(timeout=self.timeout_seconds)
                return result
            except queue.Empty:
                return None
            finally:
                # 关闭Web服务器
                self.stop_web_server()

        except Exception as e:
            print(f"❌ Web服务器启动失败: {e}")
            return None

    def create_gui_widgets(self):
        """创建美化的界面组件"""
        # 主框架
        main_frame = tk.Frame(self.root, bg="#f5f5f5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # 标题
        title_label = tk.Label(
            main_frame,
            text="🎯 工作完成汇报与反馈收集",
            font=("Microsoft YaHei", 16, "bold"),
            bg="#f5f5f5",
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 20))

        # 1. 工作汇报区域
        report_frame = tk.LabelFrame(
            main_frame,
            text="📋 AI工作完成汇报",
            font=("Microsoft YaHei", 12, "bold"),
            bg="#ffffff",
            fg="#34495e",
            relief=tk.RAISED,
            bd=2
        )
        report_frame.pack(fill=tk.X, pady=(0, 15))

        report_text = tk.Text(
            report_frame,
            height=5,
            wrap=tk.WORD,
            bg="#ecf0f1",
            fg="#2c3e50",
            font=("Microsoft YaHei", 10),
            relief=tk.FLAT,
            bd=5,
            state=tk.DISABLED
        )
        report_text.pack(fill=tk.X, padx=15, pady=15)

        # 显示工作汇报内容
        report_text.config(state=tk.NORMAL)
        report_text.insert(tk.END, self.work_summary or "本次对话中完成的工作内容...")
        report_text.config(state=tk.DISABLED)

        # 2. 用户反馈文本区域
        feedback_frame = tk.LabelFrame(
            main_frame,
            text="💬 您的文字反馈（可选）",
            font=("Microsoft YaHei", 12, "bold"),
            bg="#ffffff",
            fg="#34495e",
            relief=tk.RAISED,
            bd=2
        )
        feedback_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # 文本输入框
        self.text_widget = scrolledtext.ScrolledText(
            feedback_frame,
            height=6,
            wrap=tk.WORD,
            font=("Microsoft YaHei", 10),
            bg="#ffffff",
            fg="#2c3e50",
            relief=tk.FLAT,
            bd=5,
            insertbackground="#3498db"
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.text_widget.insert(tk.END, "请在此输入您的反馈、建议或问题...")
        self.text_widget.bind("<FocusIn>", self.clear_placeholder)

        # 3. 图片选择区域
        image_frame = tk.LabelFrame(
            main_frame,
            text="🖼️ 图片反馈（可选，支持多张）",
            font=("Microsoft YaHei", 12, "bold"),
            bg="#ffffff",
            fg="#34495e",
            relief=tk.RAISED,
            bd=2
        )
        image_frame.pack(fill=tk.X, pady=(0, 15))

        # 图片操作按钮
        btn_frame = tk.Frame(image_frame, bg="#ffffff")
        btn_frame.pack(fill=tk.X, padx=15, pady=10)

        # 美化的按钮样式
        btn_style = {
            "font": ("Microsoft YaHei", 10, "bold"),
            "relief": tk.FLAT,
            "bd": 0,
            "cursor": "hand2",
            "height": 2
        }

        tk.Button(
            btn_frame,
            text="📁 选择图片文件",
            command=self.select_image_file,
            bg="#3498db",
            fg="white",
            width=15,
            **btn_style
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_frame,
            text="📋 从剪贴板粘贴",
            command=self.paste_from_clipboard,
            bg="#2ecc71",
            fg="white",
            width=15,
            **btn_style
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            btn_frame,
            text="❌ 清除所有图片",
            command=self.clear_all_images,
            bg="#e74c3c",
            fg="white",
            width=15,
            **btn_style
        ).pack(side=tk.LEFT, padx=8)

        # 图片预览区域（支持滚动）
        preview_container = tk.Frame(image_frame, bg="#ffffff")
        preview_container.pack(fill=tk.X, padx=15, pady=(0, 15))

        # 创建滚动画布
        canvas = tk.Canvas(preview_container, height=120, bg="#f8f9fa", relief=tk.SUNKEN, bd=1)
        scrollbar = tk.Scrollbar(preview_container, orient="horizontal", command=canvas.xview)
        self.image_preview_frame = tk.Frame(canvas, bg="#f8f9fa")

        self.image_preview_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.image_preview_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack(side="top", fill="x")
        scrollbar.pack(side="bottom", fill="x")

        # 初始提示
        self.update_image_preview()

        # 4. 操作按钮
        button_frame = tk.Frame(main_frame, bg="#f5f5f5")
        button_frame.pack(fill=tk.X, pady=(15, 0))

        # 主要操作按钮
        submit_btn = tk.Button(
            button_frame,
            text="✅ 提交反馈",
            command=self.submit_feedback,
            font=("Microsoft YaHei", 12, "bold"),
            bg="#27ae60",
            fg="white",
            width=18,
            height=2,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2"
        )
        submit_btn.pack(side=tk.LEFT, padx=(0, 15))

        cancel_btn = tk.Button(
            button_frame,
            text="❌ 取消",
            command=self.cancel,
            font=("Microsoft YaHei", 12),
            bg="#95a5a6",
            fg="white",
            width=18,
            height=2,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT)

        # 说明文字
        info_label = tk.Label(
            main_frame,
            text="💡 提示：您可以只提供文字反馈、只提供图片，或者两者都提供（支持多张图片）",
            font=("Microsoft YaHei", 9),
            fg="#7f8c8d",
            bg="#f5f5f5"
        )
        info_label.pack(pady=(15, 0))

    def clear_placeholder(self, event):
        """清除占位符文本"""
        if self.text_widget.get(1.0, tk.END).strip() == "请在此输入您的反馈、建议或问题...":
            self.text_widget.delete(1.0, tk.END)

    def select_image_file(self):
        """选择图片文件（支持多选）"""
        file_types = [
            ("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
            ("PNG文件", "*.png"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("所有文件", "*.*")
        ]

        file_paths = filedialog.askopenfilenames(
            title="选择图片文件（可多选）",
            filetypes=file_types
        )

        for file_path in file_paths:
            try:
                # 读取并验证图片
                with open(file_path, 'rb') as f:
                    image_data = f.read()

                img = Image.open(io.BytesIO(image_data))
                self.selected_images.append({
                    'data': image_data,
                    'source': f'文件: {Path(file_path).name}',
                    'size': img.size,
                    'image': img
                })

            except Exception as e:
                messagebox.showerror("错误", f"无法读取图片文件 {Path(file_path).name}: {str(e)}")

        self.update_image_preview()

    def paste_from_clipboard(self):
        """从剪贴板粘贴图片"""
        try:
            from PIL import ImageGrab
            img = ImageGrab.grabclipboard()

            if img:
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                image_data = buffer.getvalue()

                self.selected_images.append({
                    'data': image_data,
                    'source': '剪贴板',
                    'size': img.size,
                    'image': img
                })

                self.update_image_preview()
            else:
                messagebox.showwarning("警告", "剪贴板中没有图片数据")

        except Exception as e:
            messagebox.showerror("错误", f"无法从剪贴板获取图片: {str(e)}")

    def clear_all_images(self):
        """清除所有选择的图片"""
        self.selected_images = []
        self.update_image_preview()

    def update_image_preview(self):
        """更新图片预览显示"""
        # 清除现有预览
        for widget in self.image_preview_frame.winfo_children():
            widget.destroy()

        if not self.selected_images:
            # 显示未选择图片的提示
            no_image_label = tk.Label(
                self.image_preview_frame,
                text="未选择图片",
                bg="#f8f9fa",
                fg="#95a5a6",
                font=("Microsoft YaHei", 10)
            )
            no_image_label.pack(pady=20)
        else:
            # 显示所有图片预览
            for i, img_info in enumerate(self.selected_images):
                try:
                    # 创建单个图片预览容器
                    img_container = tk.Frame(self.image_preview_frame, bg="#ffffff", relief=tk.RAISED, bd=1)
                    img_container.pack(side=tk.LEFT, padx=5, pady=5)

                    # 创建缩略图
                    img_copy = img_info['image'].copy()
                    img_copy.thumbnail((100, 80), Image.Resampling.LANCZOS)

                    # 转换为tkinter可用的格式
                    photo = ImageTk.PhotoImage(img_copy)

                    # 图片标签
                    img_label = tk.Label(img_container, image=photo, bg="#ffffff")
                    img_label.image = photo  # 保持引用
                    img_label.pack(padx=5, pady=5)

                    # 图片信息
                    info_text = f"{img_info['source']}\n{img_info['size'][0]}x{img_info['size'][1]}"
                    info_label = tk.Label(
                        img_container,
                        text=info_text,
                        font=("Microsoft YaHei", 8),
                        bg="#ffffff",
                        fg="#7f8c8d"
                    )
                    info_label.pack(pady=(0, 5))

                    # 删除按钮
                    del_btn = tk.Button(
                        img_container,
                        text="×",
                        command=lambda idx=i: self.remove_image(idx),
                        font=("Arial", 10, "bold"),
                        bg="#e74c3c",
                        fg="white",
                        width=3,
                        relief=tk.FLAT,
                        cursor="hand2"
                    )
                    del_btn.pack(pady=(0, 5))

                except Exception as e:
                    print(f"预览更新失败: {e}")

    def remove_image(self, index):
        """删除指定索引的图片"""
        if 0 <= index < len(self.selected_images):
            self.selected_images.pop(index)
            self.update_image_preview()

    def submit_feedback(self):
        """提交反馈"""
        # 获取文本内容
        text_content = self.text_widget.get(1.0, tk.END).strip()
        if text_content == "请在此输入您的反馈、建议或问题...":
            text_content = ""

        # 检查是否有内容
        has_text = bool(text_content)
        has_images = bool(self.selected_images)

        if not has_text and not has_images:
            messagebox.showwarning("警告", "请至少提供文字反馈或图片反馈")
            return

        # 准备结果数据
        result = {
            'success': True,
            'text_feedback': text_content if has_text else None,
            'images': [img['data'] for img in self.selected_images] if has_images else None,
            'image_sources': [img['source'] for img in self.selected_images] if has_images else None,
            'has_text': has_text,
            'has_images': has_images,
            'image_count': len(self.selected_images),
            'timestamp': datetime.now().isoformat()
        }

        self.result_queue.put(result)
        self.root.destroy()

    def cancel(self):
        """取消操作"""
        self.result_queue.put({
            'success': False,
            'message': '用户取消了反馈提交'
        })
        self.root.destroy()

    # ==================== Web模式相关方法 ====================

    def create_flask_app(self):
        """创建Flask应用"""
        if not WEB_AVAILABLE:
            raise Exception("Flask不可用，无法创建Web应用")

        self.flask_app = Flask(__name__)
        self.flask_app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

        # 设置路由
        @self.flask_app.route('/')
        def index():
            return self.render_feedback_page()

        @self.flask_app.route('/submit', methods=['POST'])
        def submit_feedback():
            return self.handle_web_submit()

        @self.flask_app.route('/cancel', methods=['POST'])
        def cancel_feedback():
            return self.handle_web_cancel()

        @self.flask_app.route('/upload', methods=['POST'])
        def upload_image():
            return self.handle_image_upload()

        @self.flask_app.route('/remove_image/<int:index>', methods=['POST'])
        def remove_image(index):
            return self.handle_remove_image(index)

    def start_web_server(self):
        """启动Web服务器"""
        def run_server():
            try:
                self.flask_app.run(
                    host='127.0.0.1',
                    port=self.port,
                    debug=False,
                    use_reloader=False,
                    threaded=True
                )
            except Exception as e:
                print(f"❌ Web服务器运行错误: {e}")

        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()

        # 等待服务器启动
        time.sleep(1)

    def stop_web_server(self):
        """停止Web服务器"""
        try:
            # 通过发送请求来关闭服务器
            import requests
            requests.post(f'http://127.0.0.1:{self.port}/shutdown', timeout=1)
        except:
            pass

        # 强制终止端口上的进程
        if self.port:
            self.port_manager.kill_process_on_port(self.port)

    def render_feedback_page(self):
        """渲染反馈收集页面"""
        html_template = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 工作完成汇报与反馈收集</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: "Microsoft YaHei", Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 24px;
            margin-bottom: 10px;
        }

        .content {
            padding: 30px;
        }

        .section {
            margin-bottom: 30px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            overflow: hidden;
        }

        .section-header {
            background: #f8f9fa;
            padding: 15px 20px;
            font-weight: bold;
            color: #495057;
            border-bottom: 1px solid #e9ecef;
        }

        .section-content {
            padding: 20px;
        }

        .work-summary {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            color: #2c3e50;
            white-space: pre-wrap;
            min-height: 100px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-control {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 5px;
            font-size: 14px;
            font-family: inherit;
            resize: vertical;
        }

        .form-control:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin-right: 10px;
            margin-bottom: 10px;
        }

        .btn-primary {
            background: #3498db;
            color: white;
        }

        .btn-success {
            background: #2ecc71;
            color: white;
        }

        .btn-danger {
            background: #e74c3c;
            color: white;
        }

        .btn-secondary {
            background: #95a5a6;
            color: white;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        .image-upload-area {
            border: 2px dashed #bdc3c7;
            border-radius: 5px;
            padding: 30px;
            text-align: center;
            background: #f8f9fa;
            margin-bottom: 20px;
            transition: all 0.3s;
        }

        .image-upload-area:hover {
            border-color: #3498db;
            background: #ecf0f1;
        }

        .image-preview {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 20px;
        }

        .image-item {
            position: relative;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            overflow: hidden;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .image-item img {
            width: 120px;
            height: 90px;
            object-fit: cover;
            display: block;
        }

        .image-info {
            padding: 8px;
            font-size: 12px;
            color: #7f8c8d;
            text-align: center;
        }

        .image-remove {
            position: absolute;
            top: 5px;
            right: 5px;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
        }

        .button-group {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
        }

        .info-text {
            text-align: center;
            color: #7f8c8d;
            font-size: 14px;
            margin-top: 20px;
        }

        #file-input {
            display: none;
        }

        .upload-buttons {
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 工作完成汇报与反馈收集</h1>
            <p>AI助手工作完成，请提供您的反馈意见</p>
        </div>

        <div class="content">
            <!-- AI工作汇报区域 -->
            <div class="section">
                <div class="section-header">
                    📋 AI工作完成汇报
                </div>
                <div class="section-content">
                    <div class="work-summary">{{ work_summary or "本次对话中完成的工作内容..." }}</div>
                </div>
            </div>

            <!-- 反馈表单 -->
            <form id="feedback-form">
                <!-- 文字反馈区域 -->
                <div class="section">
                    <div class="section-header">
                        💬 您的文字反馈（可选）
                    </div>
                    <div class="section-content">
                        <div class="form-group">
                            <textarea
                                id="text-feedback"
                                name="text_feedback"
                                class="form-control"
                                rows="6"
                                placeholder="请在此输入您的反馈、建议或问题..."></textarea>
                        </div>
                    </div>
                </div>

                <!-- 图片反馈区域 -->
                <div class="section">
                    <div class="section-header">
                        🖼️ 图片反馈（可选，支持多张）
                    </div>
                    <div class="section-content">
                        <div class="image-upload-area" onclick="document.getElementById('file-input').click()">
                            <p>📁 点击选择图片文件或拖拽图片到此处</p>
                            <p style="font-size: 12px; color: #7f8c8d; margin-top: 10px;">
                                支持 PNG、JPG、JPEG、GIF、BMP、WebP 格式
                            </p>
                        </div>

                        <div class="upload-buttons">
                            <button type="button" class="btn btn-primary" onclick="document.getElementById('file-input').click()">
                                📁 选择图片文件
                            </button>
                            <button type="button" class="btn btn-success" onclick="pasteFromClipboard()">
                                📋 从剪贴板粘贴
                            </button>
                            <button type="button" class="btn btn-danger" onclick="clearAllImages()">
                                ❌ 清除所有图片
                            </button>
                        </div>

                        <input type="file" id="file-input" multiple accept="image/*" onchange="handleFileSelect(event)">

                        <div id="image-preview" class="image-preview"></div>
                    </div>
                </div>

                <!-- 操作按钮 -->
                <div class="button-group">
                    <button type="submit" class="btn btn-success" style="font-size: 16px; padding: 15px 30px;">
                        ✅ 提交反馈
                    </button>
                    <button type="button" class="btn btn-secondary" onclick="cancelFeedback()" style="font-size: 16px; padding: 15px 30px;">
                        ❌ 取消
                    </button>
                </div>

                <div class="info-text">
                    💡 提示：您可以只提供文字反馈、只提供图片，或者两者都提供（支持多张图片）
                </div>
            </form>
        </div>
    </div>

    <script>
        let selectedImages = [];

        // 处理文件选择
        function handleFileSelect(event) {
            const files = event.target.files;
            for (let file of files) {
                if (file.type.startsWith('image/')) {
                    addImageFile(file);
                }
            }
        }

        // 添加图片文件
        function addImageFile(file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const imageData = {
                    data: e.target.result,
                    name: file.name,
                    size: file.size,
                    type: file.type
                };
                selectedImages.push(imageData);
                updateImagePreview();
            };
            reader.readAsDataURL(file);
        }

        // 从剪贴板粘贴
        async function pasteFromClipboard() {
            try {
                const clipboardItems = await navigator.clipboard.read();
                for (const clipboardItem of clipboardItems) {
                    for (const type of clipboardItem.types) {
                        if (type.startsWith('image/')) {
                            const blob = await clipboardItem.getType(type);
                            const file = new File([blob], 'clipboard-image.png', { type: type });
                            addImageFile(file);
                            return;
                        }
                    }
                }
                alert('剪贴板中没有图片数据');
            } catch (err) {
                alert('无法访问剪贴板，请使用文件选择功能');
            }
        }

        // 清除所有图片
        function clearAllImages() {
            selectedImages = [];
            updateImagePreview();
        }

        // 删除指定图片
        function removeImage(index) {
            selectedImages.splice(index, 1);
            updateImagePreview();
        }

        // 更新图片预览
        function updateImagePreview() {
            const preview = document.getElementById('image-preview');
            preview.innerHTML = '';

            if (selectedImages.length === 0) {
                preview.innerHTML = '<p style="text-align: center; color: #95a5a6; padding: 20px;">未选择图片</p>';
                return;
            }

            selectedImages.forEach((image, index) => {
                const imageItem = document.createElement('div');
                imageItem.className = 'image-item';

                const img = document.createElement('img');
                img.src = image.data;
                img.alt = image.name;

                const info = document.createElement('div');
                info.className = 'image-info';
                info.textContent = `${image.name}\\n${(image.size / 1024).toFixed(1)} KB`;

                const removeBtn = document.createElement('button');
                removeBtn.className = 'image-remove';
                removeBtn.textContent = '×';
                removeBtn.onclick = () => removeImage(index);

                imageItem.appendChild(img);
                imageItem.appendChild(info);
                imageItem.appendChild(removeBtn);
                preview.appendChild(imageItem);
            });
        }

        // 取消反馈
        function cancelFeedback() {
            if (confirm('确定要取消反馈提交吗？')) {
                fetch('/cancel', { method: 'POST' })
                    .then(() => {
                        alert('已取消反馈提交');
                        window.close();
                    });
            }
        }

        // 提交表单
        document.getElementById('feedback-form').addEventListener('submit', function(e) {
            e.preventDefault();

            const textFeedback = document.getElementById('text-feedback').value.trim();
            const hasText = textFeedback.length > 0;
            const hasImages = selectedImages.length > 0;

            if (!hasText && !hasImages) {
                alert('请至少提供文字反馈或图片反馈');
                return;
            }

            const formData = new FormData();
            formData.append('text_feedback', textFeedback);
            formData.append('image_count', selectedImages.length);

            // 添加图片数据
            selectedImages.forEach((image, index) => {
                // 将base64转换为blob
                const byteCharacters = atob(image.data.split(',')[1]);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], { type: image.type });

                formData.append(`image_${index}`, blob, image.name);
            });

            fetch('/submit', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('反馈提交成功！');
                    window.close();
                } else {
                    alert('提交失败：' + data.message);
                }
            })
            .catch(error => {
                alert('提交失败：' + error.message);
            });
        });

        // 拖拽上传支持
        const uploadArea = document.querySelector('.image-upload-area');

        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.borderColor = '#3498db';
            this.style.background = '#ecf0f1';
        });

        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.style.borderColor = '#bdc3c7';
            this.style.background = '#f8f9fa';
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.borderColor = '#bdc3c7';
            this.style.background = '#f8f9fa';

            const files = e.dataTransfer.files;
            for (let file of files) {
                if (file.type.startsWith('image/')) {
                    addImageFile(file);
                }
            }
        });

        // 初始化预览
        updateImagePreview();
    </script>
</body>
</html>
        '''

        return html_template.replace('{{ work_summary or "本次对话中完成的工作内容..." }}',
                                   self.work_summary or "本次对话中完成的工作内容...")

    def handle_web_submit(self):
        """处理Web表单提交"""
        try:
            text_feedback = request.form.get('text_feedback', '').strip()
            image_count = int(request.form.get('image_count', 0))

            # 检查是否有内容
            has_text = bool(text_feedback)
            has_images = image_count > 0

            if not has_text and not has_images:
                return jsonify({'success': False, 'message': '请至少提供文字反馈或图片反馈'})

            # 处理图片
            images = []
            image_sources = []

            for i in range(image_count):
                file_key = f'image_{i}'
                if file_key in request.files:
                    file = request.files[file_key]
                    if file and file.filename:
                        try:
                            # 验证图片
                            image_data = file.read()
                            img = Image.open(io.BytesIO(image_data))

                            images.append(image_data)
                            image_sources.append(f'Web上传: {secure_filename(file.filename)}')
                        except Exception as e:
                            print(f"图片处理失败: {e}")

            # 准备结果数据
            result = {
                'success': True,
                'text_feedback': text_feedback if has_text else None,
                'images': images if has_images else None,
                'image_sources': image_sources if has_images else None,
                'has_text': has_text,
                'has_images': bool(images),
                'image_count': len(images),
                'timestamp': datetime.now().isoformat()
            }

            self.result_queue.put(result)
            return jsonify({'success': True, 'message': '反馈提交成功'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'提交失败: {str(e)}'})

    def handle_web_cancel(self):
        """处理Web取消操作"""
        self.result_queue.put({
            'success': False,
            'message': '用户取消了反馈提交'
        })
        return jsonify({'success': True, 'message': '已取消'})

    def handle_image_upload(self):
        """处理图片上传"""
        try:
            if 'image' not in request.files:
                return jsonify({'success': False, 'message': '没有图片文件'})

            file = request.files['image']
            if file.filename == '':
                return jsonify({'success': False, 'message': '没有选择文件'})

            # 验证图片
            image_data = file.read()
            img = Image.open(io.BytesIO(image_data))

            # 添加到选择的图片列表
            self.selected_images.append({
                'data': image_data,
                'source': f'Web上传: {secure_filename(file.filename)}',
                'size': img.size,
                'image': img
            })

            return jsonify({'success': True, 'message': '图片上传成功'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'上传失败: {str(e)}'})

    def handle_remove_image(self, index):
        """处理删除图片"""
        try:
            if 0 <= index < len(self.selected_images):
                self.selected_images.pop(index)
                return jsonify({'success': True, 'message': '图片删除成功'})
            else:
                return jsonify({'success': False, 'message': '无效的图片索引'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})


@mcp.tool()
def collect_feedback(work_summary: str = "", timeout_seconds: int = DIALOG_TIMEOUT) -> list:
    """
    收集用户反馈的交互式工具。AI可以汇报完成的工作，用户可以提供文字和/或图片反馈。

    Args:
        work_summary: AI完成的工作内容汇报
        timeout_seconds: 对话框超时时间（秒），默认300秒（5分钟）

    Returns:
        包含用户反馈内容的列表，可能包含文本和图片
    """
    dialog = FeedbackDialog(work_summary, timeout_seconds)
    result = dialog.show_dialog()

    if result is None:
        raise Exception(f"操作超时（{timeout_seconds}秒），请重试")

    if not result['success']:
        raise Exception(result.get('message', '用户取消了反馈提交'))

    # 构建返回内容列表
    feedback_items = []

    # 添加文字反馈
    if result['has_text']:
        from mcp.types import TextContent
        feedback_items.append(TextContent(
            type="text",
            text=f"用户文字反馈：{result['text_feedback']}\n提交时间：{result['timestamp']}"
        ))

    # 添加图片反馈
    if result['has_images']:
        for image_data, source in zip(result['images'], result['image_sources']):
            feedback_items.append(MCPImage(data=image_data, format='png'))

    return feedback_items


@mcp.tool()
def pick_image() -> MCPImage:
    """
    弹出图片选择对话框，让用户选择图片文件或从剪贴板粘贴图片。
    用户可以选择本地图片文件，或者先截图到剪贴板然后粘贴。
    自动检测环境，支持GUI和Web两种模式。
    """
    # 检测显示环境
    display_mode = detect_display_environment()
    print(f"🎯 图片选择模式: {display_mode}")

    if display_mode == 'gui' and GUI_AVAILABLE:
        return pick_image_gui()
    elif display_mode == 'web' and WEB_AVAILABLE:
        return pick_image_web()
    else:
        raise Exception(f"不支持的显示环境: {display_mode}，请安装相应依赖")


def pick_image_gui() -> MCPImage:
    """GUI模式的图片选择"""
    def simple_image_dialog():
        root = tk.Tk()
        root.title("选择图片")
        root.geometry("400x300")
        root.resizable(False, False)
        root.eval('tk::PlaceWindow . center')

        selected_image = {'data': None}

        def select_file():
            file_path = filedialog.askopenfilename(
                title="选择图片文件",
                filetypes=[("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
            )
            if file_path:
                try:
                    with open(file_path, 'rb') as f:
                        selected_image['data'] = f.read()
                    root.destroy()
                except Exception as e:
                    messagebox.showerror("错误", f"无法读取图片: {e}")

        def paste_clipboard():
            try:
                from PIL import ImageGrab
                img = ImageGrab.grabclipboard()
                if img:
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    selected_image['data'] = buffer.getvalue()
                    root.destroy()
                else:
                    messagebox.showwarning("警告", "剪贴板中没有图片")
            except Exception as e:
                messagebox.showerror("错误", f"剪贴板操作失败: {e}")

        def cancel():
            root.destroy()

        # 界面
        tk.Label(root, text="请选择图片来源", font=("Arial", 14, "bold")).pack(pady=20)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="📁 选择图片文件", font=("Arial", 12),
                 width=20, height=2, command=select_file).pack(pady=10)
        tk.Button(btn_frame, text="📋 从剪贴板粘贴", font=("Arial", 12),
                 width=20, height=2, command=paste_clipboard).pack(pady=10)
        tk.Button(btn_frame, text="❌ 取消", font=("Arial", 12),
                 width=20, height=1, command=cancel).pack(pady=10)

        root.mainloop()
        return selected_image['data']

    image_data = simple_image_dialog()

    if image_data is None:
        raise Exception("未选择图片或操作被取消")

    return MCPImage(data=image_data, format='png')


def pick_image_web() -> MCPImage:
    """Web模式的图片选择"""
    # 创建一个简化的反馈对话框，只用于图片选择
    dialog = FeedbackDialog("请选择一张图片", 300)  # 5分钟超时
    result = dialog.show_web_dialog()

    if result is None:
        raise Exception("操作超时，请重试")

    if not result['success']:
        raise Exception(result.get('message', '用户取消了图片选择'))

    if not result['has_images'] or not result['images']:
        raise Exception("未选择图片")

    # 返回第一张图片
    return MCPImage(data=result['images'][0], format='png')


@mcp.tool()
def get_image_info(image_path: str) -> str:
    """
    获取指定路径图片的信息（尺寸、格式等）

    Args:
        image_path: 图片文件路径
    """
    try:
        path = Path(image_path)
        if not path.exists():
            return f"文件不存在: {image_path}"

        with Image.open(path) as img:
            info = {
                "文件名": path.name,
                "格式": img.format,
                "尺寸": f"{img.width} x {img.height}",
                "模式": img.mode,
                "文件大小": f"{path.stat().st_size / 1024:.1f} KB"
            }

        return "\n".join([f"{k}: {v}" for k, v in info.items()])

    except Exception as e:
        return f"获取图片信息失败: {str(e)}"


if __name__ == "__main__":
    mcp.run()


def main():
    """Main entry point for the mcp-feedback-collector command."""
    mcp.run()