#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QWidget, QMessageBox,
                             QFileDialog, QLineEdit, QSplashScreen)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap

# 获取资源文件的绝对路径
def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和PyInstaller打包后的环境"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        return os.path.join(base_path, relative_path)
    except Exception:
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)

class MetalHUDToggler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Metal HUD 启动器")
        self.setFixedSize(400, 250)  # 减小窗口高度
        
        # 创建主窗口部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建标题标签
        title_label = QLabel("Metal HUD 启动器")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建说明标签
        description_label = QLabel("选择应用程序并使用环境变量启动，直接显示Metal HUD")
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(description_label)
        
        # 创建应用选择部分
        app_select_layout = QHBoxLayout()
        app_select_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.app_path_input = QLineEdit()
        self.app_path_input.setPlaceholderText("选择要启动的应用...")
        self.app_path_input.setMinimumWidth(250)
        app_select_layout.addWidget(self.app_path_input)
        
        browse_button = QPushButton("浏览")
        browse_button.clicked.connect(self.browse_app)
        app_select_layout.addWidget(browse_button)
        
        app_select_widget = QWidget()
        app_select_widget.setLayout(app_select_layout)
        main_layout.addWidget(app_select_widget)
        
        # 创建启动按钮
        launch_button = QPushButton("启动应用并开启Metal HUD")
        launch_button.setFixedSize(250, 40)
        launch_button.clicked.connect(self.launch_app_with_hud)
        launch_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        launch_layout = QHBoxLayout()
        launch_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        launch_layout.addWidget(launch_button)
        
        launch_widget = QWidget()
        launch_widget.setLayout(launch_layout)
        main_layout.addWidget(launch_widget)
        
        # 创建说明标签
        info_label = QLabel("此工具使用环境变量MTL_HUD_ENABLED=1启动应用")
        info_label.setStyleSheet("color: gray;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info_label)
    
    def browse_app(self):
        """打开文件对话框选择应用程序"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择应用程序",
            "/Applications",
            "应用程序 (*.app)"
        )
        if file_path:
            self.app_path_input.setText(file_path)
    
    def launch_app_with_hud(self):
        """使用环境变量启动应用并开启Metal HUD"""
        app_path = self.app_path_input.text().strip()
        
        if not app_path:
            QMessageBox.warning(self, "警告", "请先选择要启动的应用程序")
            return
        
        if not os.path.exists(app_path):
            QMessageBox.warning(self, "警告", "所选应用程序不存在")
            return
        
        try:
            # 使用环境变量方式启动应用
            env = os.environ.copy()
            env["MTL_HUD_ENABLED"] = "1"
            
            # 使用open命令启动应用
            subprocess.Popen(["open", app_path], env=env)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动应用时出错: {str(e)}")


if __name__ == "__main__":
    # 使用异常处理和启动画面来避免启动时的闪退问题
    try:
        # 确保QApplication在任何其他操作之前创建
        app = QApplication(sys.argv)
        
        # 创建启动画面
        # 检查图标文件是否存在，使用resource_path函数获取正确路径
        splash_pixmap = None
        icon_path = resource_path("app_icon.svg")
        if os.path.exists(icon_path):
            splash_pixmap = QPixmap(icon_path)
        else:
            # 尝试加载PNG格式
            icon_path = resource_path("app_icon.png")
            if os.path.exists(icon_path):
                splash_pixmap = QPixmap(icon_path)
            else:
                # 如果找不到图标，创建一个纯色的启动画面
                splash_pixmap = QPixmap(400, 200)
                splash_pixmap.fill(Qt.GlobalColor.white)
        
        splash = QSplashScreen(splash_pixmap)
        splash.show()
        
        # 确保启动画面显示
        app.processEvents()
        
        # 创建主窗口但暂不显示
        window = MetalHUDToggler()
        
        # 使用Qt的单次计时器来延迟显示窗口
        # 这可以让应用完全加载后再显示界面
        def show_main_window():
            splash.finish(window)
            window.show()
            
        # 延迟500毫秒显示主窗口，给系统足够时间初始化
        QTimer.singleShot(500, show_main_window)
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"应用启动错误: {str(e)}")
        sys.exit(1)