from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QListWidget, 
    QListWidgetItem, QPushButton, QWidget, QVBoxLayout
)
from zhon.cedict import simp, trad
import os

from config import *


class CustomButton(QPushButton):
    def __init__(self, text, parent=None):
        super(CustomButton, self).__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        if enabled:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ForbiddenCursor)

        if self.underMouse():
            QApplication.restoreOverrideCursor()
            QApplication.setOverrideCursor(self.cursor().shape())

    def setDisabled(self, disabled):
        super().setDisabled(disabled)
        if disabled:
            self.setCursor(Qt.CursorShape.ForbiddenCursor)
        else:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        if self.underMouse():
            QApplication.restoreOverrideCursor()
            QApplication.setOverrideCursor(self.cursor().shape())

    def enterEvent(self, event):
        super().enterEvent(event)
        QApplication.restoreOverrideCursor()
        QApplication.setOverrideCursor(self.cursor().shape())

    def leaveEvent(self, event):
        super().leaveEvent(event)
        QApplication.restoreOverrideCursor()


class StatusMessageWidget(QWidget):
    def __init__(self, widgetName, message):
        super().__init__()
        self.setObjectName(widgetName)

        self.layout = QHBoxLayout()
        self.layout.setSpacing(3)
        self.setLayout(self.layout)

        self.messageLabel = QLabel(message)
        self.layout.addWidget(self.messageLabel)

        self.loadingLabel = QLabel(".")
        self.loadingLabel.setFixedWidth(20)
        self.layout.addWidget(self.loadingLabel)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_loading_animation)
        self.timer.start(500)

    def update_loading_animation(self):
        current_text = self.loadingLabel.text()
        new_text = '.' * ((len(current_text) % 3) + 1)
        self.loadingLabel.setText(new_text)

    def update_message(self, newMessage, state="load"):
        self.messageLabel.setText(newMessage)
        if state == "load":
            if not self.loadingLabel.isVisible():
                self.loadingLabel.show()
            if not self.timer.isActive():
                self.timer.start(500)
            self.messageLabel.setStyleSheet("")
        elif state == "error":
            self.timer.stop()
            self.loadingLabel.hide()
            self.messageLabel.setStyleSheet("QLabel { color: red; }")


class MultilingualListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QListWidget {
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3d3d3d;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
        """)

        # 加载不同语言的字体
        self.english_font = QFont(QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont(font_config['English']))[0], 10)
        self.chinese_font = QFont(QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont(font_config['简体中文']))[0], 10)

    def addItem(self, text):
        if isinstance(text, QListWidgetItem):
            item = text
            text = item.text()
        else:
            item = QListWidgetItem(text)
            
        if any(ord(c) > 127 for c in text):  # 检查是否包含非ASCII字符
            item.setFont(self.chinese_font)
        else:
            item.setFont(self.english_font)
            
        super().addItem(item)


class AlertWidget(QWidget):
    def __init__(self, parent, message, alert_type):
        super().__init__(parent)
        self.message = message
        self.alert_type = alert_type
        self.margin = 10
        self.colors = {
            "info": "#3498db",     # Blue
            "success": "#007110",  # Green
            "warning": "#f1c40f",  # Yellow
            "error": "#e74c3c",    # Red
        }
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.label = QLabel(self.message, self)
        self.label.setStyleSheet("""
            color: white;
            padding: 10px;
            font-weight: bold;
        """)
        self.label.adjustSize()

        # Adjust the size of the custom widget
        alert_width = self.label.width()
        alert_height = self.label.height()
        self.setFixedSize(alert_width, alert_height)
        self.label.move(0, 0)

        # Add to the parent window's active alerts list
        if hasattr(self.parent(), "active_alerts"):
            self.parent().active_alerts.append(self)
            self.enforce_alert_limit()
            self.move_to_top_right()

    def enforce_alert_limit(self):
        """Ensure the total height of alerts doesn't exceed the parent window height."""
        if self.parent():
            max_alerts = (self.parent().height() - self.margin) // (self.height() + self.margin)
            while len(self.parent().active_alerts) > max_alerts:
                self.parent().active_alerts[0].close()

    def move_to_top_right(self):
        """Position the alert at the top-right corner below the previous alerts."""
        if self.parent():
            dialog_rect = self.parent().geometry()
            for index, alert in enumerate(self.parent().active_alerts):
                alert_x = dialog_rect.topRight().x() - alert.width() - self.margin
                alert_y = dialog_rect.topRight().y() + self.margin + index * (alert.height() + self.margin)
                alert.move(alert_x, alert_y)

    def close(self):
        """Override close to remove the alert from the parent's active list."""
        if hasattr(self.parent(), "active_alerts") and self in self.parent().active_alerts:
            self.parent().active_alerts.remove(self)
            self.move_to_top_right()
        super().close()

    def paintEvent(self, event):
        """Draw the rounded rectangle background."""
        painter = QPainter(self)
        painter.setBrush(QColor(self.colors[self.alert_type]))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 5, 5)


class TrainerCard(QWidget):
    launch_clicked = pyqtSignal(str)  # 发送trainer_name
    delete_clicked = pyqtSignal(str)  # 发送trainer_name

    def __init__(self, name, description="", icon_path=None, parent=None):
        super().__init__(parent)
        self.name = name
        self.description = description
        self.icon_path = icon_path
        self.setupUI()

    def setupUI(self):
        self.setFixedSize(200, 280)
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: white;
                border-radius: 8px;
            }
            QWidget:hover {
                background-color: #3d3d3d;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        # 图标
        iconLabel = QLabel()
        if self.icon_path and os.path.exists(self.icon_path):
            pixmap = QPixmap(self.icon_path)
        else:
            pixmap = QPixmap(resource_path("assets/logo.png"))
        scaledPixmap = pixmap.scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        iconLabel.setPixmap(scaledPixmap)
        iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(iconLabel)

        # 名称
        nameLabel = QLabel(self.name)
        nameLabel.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
        """)
        nameLabel.setWordWrap(True)
        nameLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(nameLabel)

        # 描述
        if self.description:
            descLabel = QLabel(self.description)
            descLabel.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #cccccc;
                }
            """)
            descLabel.setWordWrap(True)
            descLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(descLabel)

        # 按钮区域
        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(8)

        launchBtn = CustomButton(tr("启动"))
        launchBtn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                background-color: #0078d4;
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1a86d9;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
            QPushButton:disabled {
                background-color: #333333;
                color: #666666;
            }
        """)
        launchBtn.clicked.connect(lambda: self.launch_clicked.emit(self.name))
        buttonLayout.addWidget(launchBtn)

        deleteBtn = CustomButton(tr("删除"))
        deleteBtn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                background-color: #333333;
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QPushButton:pressed {
                background-color: #292929;
            }
            QPushButton:disabled {
                background-color: #333333;
                color: #666666;
            }
        """)
        deleteBtn.clicked.connect(lambda: self.delete_clicked.emit(self.name))
        buttonLayout.addWidget(deleteBtn)

        layout.addLayout(buttonLayout)
        layout.addStretch()


class DownloadTrainerCard(TrainerCard):
    download_clicked = pyqtSignal(str)  # 发送trainer_name

    def __init__(self, name, description="", icon_path=None, parent=None):
        super().__init__(name, description, icon_path, parent)

    def setupUI(self):
        self.setFixedSize(200, 280)
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: white;
                border-radius: 8px;
            }
            QWidget:hover {
                background-color: #3d3d3d;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        # 图标
        iconLabel = QLabel()
        if self.icon_path and os.path.exists(self.icon_path):
            pixmap = QPixmap(self.icon_path)
        else:
            pixmap = QPixmap(resource_path("assets/logo.png"))
        scaledPixmap = pixmap.scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        iconLabel.setPixmap(scaledPixmap)
        iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(iconLabel)

        # 名称
        nameLabel = QLabel(self.name)
        nameLabel.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
        """)
        nameLabel.setWordWrap(True)
        nameLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(nameLabel)

        # 描述
        if self.description:
            descLabel = QLabel(self.description)
            descLabel.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #cccccc;
                }
            """)
            descLabel.setWordWrap(True)
            descLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(descLabel)

        # 下载按钮
        downloadBtn = CustomButton(tr("下载"))
        downloadBtn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                background-color: #0078d4;
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 12px;
                width: 100%;
            }
            QPushButton:hover {
                background-color: #1a86d9;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
            QPushButton:disabled {
                background-color: #333333;
                color: #666666;
            }
        """)
        downloadBtn.clicked.connect(lambda: self.download_clicked.emit(self.name))
        layout.addWidget(downloadBtn)
        layout.addStretch()


class PluginCard(QWidget):
    """插件卡片组件"""
    
    def __init__(self, name, description="", version="", author="", parent=None):
        super().__init__(parent)
        self.name = name
        self.description = description
        self.version = version
        self.author = author
        self.setupUI()

    def setupUI(self):
        self.setFixedSize(200, 280)
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: white;
                border-radius: 8px;
            }
            QWidget:hover {
                background-color: #3d3d3d;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        # 图标
        iconLabel = QLabel()
        try:
            pixmap = QPixmap(resource_path("assets/plugin.png"))
        except:
            # 如果找不到插件图标，使用默认图标
            pixmap = QPixmap(resource_path("assets/logo.png"))
        scaledPixmap = pixmap.scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        iconLabel.setPixmap(scaledPixmap)
        iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(iconLabel)

        # 名称
        nameLabel = QLabel(self.name)
        nameLabel.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
        """)
        nameLabel.setWordWrap(True)
        nameLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(nameLabel)

        # 描述
        if self.description:
            descLabel = QLabel(self.description)
            descLabel.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #cccccc;
                }
            """)
            descLabel.setWordWrap(True)
            descLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(descLabel)

        # 版本和作者信息
        infoLayout = QHBoxLayout()
        infoLayout.setSpacing(10)

        if self.version:
            versionLabel = QLabel(f"v{self.version}")
            versionLabel.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #0078d4;
                }
            """)
            infoLayout.addWidget(versionLabel)

        if self.author:
            authorLabel = QLabel(self.author)
            authorLabel.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #888888;
                }
            """)
            infoLayout.addWidget(authorLabel)

        layout.addLayout(infoLayout)
        layout.addStretch()
