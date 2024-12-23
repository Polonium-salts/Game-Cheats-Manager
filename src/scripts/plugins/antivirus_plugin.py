import os
import subprocess
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from .base_plugin import BasePlugin
from config import tr, elevator_path

class AntiVirusPlugin(BasePlugin):
    """防报毒插件"""
    
    @property
    def name(self) -> str:
        return tr("防报毒插件")
        
    @property
    def description(self) -> str:
        return tr("自动为修改器添加Windows Defender白名单，防止被误报为病毒")
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def author(self) -> str:
        return "GCM Team"
        
    def initialize(self, app):
        self.app = app
        self.setup_whitelist_button()
        
    def cleanup(self):
        pass
        
    def setup_whitelist_button(self):
        """添加白名单按钮到设置页面"""
        # 创建防病毒设置组
        antivirusGroup = QWidget()
        antivirusLayout = QVBoxLayout(antivirusGroup)
        antivirusLayout.setSpacing(5)
        antivirusLayout.setContentsMargins(0, 0, 0, 10)
        
        antivirusLabel = QLabel(tr("防病毒设置"))
        antivirusLabel.setStyleSheet("font-weight: bold;")
        antivirusLayout.addWidget(antivirusLabel)
        
        # 添加白名单按钮
        self.whitelistButton = QPushButton(tr("添加到Windows Defender白名单"))
        self.whitelistButton.clicked.connect(self.add_to_whitelist)
        self.whitelistButton.setStyleSheet("""
            QPushButton {
                padding: 8px;
                background-color: #0078d4;
                border: none;
                border-radius: 4px;
                color: white;
            }
            QPushButton:hover {
                background-color: #1a86d9;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
        """)
        antivirusLayout.addWidget(self.whitelistButton)
        
        # 将防病毒设置组添加到设置页面
        self.app.settingsContainer.layout().insertWidget(
            self.app.settingsContainer.layout().count() - 1,  # 在弹性空间之前插入
            antivirusGroup
        )
        
    def add_to_whitelist(self):
        """添加到Windows Defender白名单"""
        msg_box = QMessageBox(
            QMessageBox.Icon.Question,
            tr("需要管理员权限"),
            tr("添加Windows Defender白名单需要管理员权限，将会弹出UAC权限请求窗口。") +
            "\n\n" + tr("是否继续？"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            self.app
        )

        yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
        yes_button.setText(tr("是"))
        no_button = msg_box.button(QMessageBox.StandardButton.No)
        no_button.setText(tr("否"))
        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            paths = [
                self.app.trainerDownloadPath,  # 修改��下载目录
                os.path.join(os.environ["APPDATA"], "GCM Settings"),  # 设置目录
                os.path.join(os.environ["TEMP"], "GameCheatsManagerTemp")  # 临时目录
            ]

            try:
                subprocess.run([elevator_path, 'whitelist'] + paths, check=True, shell=True)
                QMessageBox.information(
                    self.app,
                    tr("成功"),
                    tr("已成功添加到Windows Defender白名单！")
                )
            except subprocess.CalledProcessError:
                QMessageBox.critical(
                    self.app,
                    tr("失败"),
                    tr("添加Windows Defender白名单失败！")
                ) 