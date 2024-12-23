import ctypes
import os
from queue import Queue
import shutil
import stat
import subprocess
import sys
import requests
import urllib.parse
import zipfile
from bs4 import BeautifulSoup

from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QFont, QFontDatabase, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QFileDialog, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidgetItem, QMainWindow, QMessageBox, QStatusBar, QVBoxLayout, QWidget, QSystemTrayIcon, QPushButton, QScrollArea, QComboBox, QCheckBox
from tendo import singleton

import style_sheet
from widgets.custom_dialogs import *
from widgets.custom_widgets import *
from widgets.trainer_management import *
from threads.download_display_thread import *
from threads.download_trainers_thread import *
from threads.other_threads import *
from threads.update_trainers_thread import *


class GameCheatsManager(QMainWindow):

    def __init__(self):
        super().__init__()

        # Single instance check and basic UI setup
        try:
            self.single_instance_checker = singleton.SingleInstance()
        except singleton.SingleInstanceException:
            sys.exit(1)
        except Exception as e:
            print(str(e))

        self.setWindowTitle("Game Cheats Manager")
        self.setWindowIcon(QIcon(resource_path("assets/logo.ico")))
        self.setMinimumSize(1024, 600)

        # Version and links
        self.appVersion = "2.2.0"
        self.githubLink = "https://github.com/dyang886/Game-Cheats-Manager"
        self.updateLink = "https://api.github.com/repos/dyang886/Game-Cheats-Manager/releases/latest"
        self.bilibiliLink = "https://space.bilibili.com/256673766"

        # Variable management
        self.trainerSearchEntryPrompt = tr("搜索修改器...")
        self.downloadSearchEntryPrompt = tr("搜索可下载的修改器...")
        self.trainerDownloadPath = os.path.normpath(settings["downloadPath"])

        self.trainers = {}  # Store installed trainers: {trainer name: trainer path}
        self.searchable = True
        self.downloadable = False
        self.downloadQueue = Queue()
        self.currentlyDownloading = False
        self.currentlyUpdatingTrainers = False
        self.currentlyUpdatingFling = False
        self.currentlyUpdatingXiaoXing = False
        self.currentlyUpdatingTrans = False

        # Window references
        self.settings_window = None
        self.about_window = None
        self.trainer_manage_window = None

        # 创建主窗口布局
        self.setupUI()
        
        # 显示版权警告
        if settings["showWarning"]:
            dialog = CopyRightWarning(self)
            dialog.show()

        # 检查更新
        if settings['checkAppUpdate']:
            self.versionFetcher = VersionFetchWorker(self.updateLink)
            self.versionFetcher.versionFetched.connect(lambda latest_version: self.send_notification(True, latest_version))
            self.versionFetcher.fetchFailed.connect(lambda: self.send_notification(False))
            self.versionFetcher.start()

        # 加载已安装的修改器
        self.show_cheats()
        # 初始化显示
        self.show_installed()

        # 加载插件
        self.plugins = []
        self.load_plugins()

    def load_plugins(self):
        """加载所有可用的插件"""
        from plugins import available_plugins
        
        for plugin_class in available_plugins:
            try:
                plugin = plugin_class()
                plugin.initialize(self)
                self.plugins.append(plugin)
                print(f"已加载插件: {plugin.name} v{plugin.version}")
            except Exception as e:
                print(f"加载插件失败: {str(e)}")

    def setupUI(self):
        # 创建中央部件
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        mainLayout = QHBoxLayout(centralWidget)
        mainLayout.setSpacing(0)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        # 创建左侧导航栏
        self.setupLeftNav(mainLayout)
        
        # 创建右侧主内容区
        self.setupMainContent(mainLayout)

        # 设置状态栏
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

    def setupLeftNav(self, mainLayout):
        leftNavWidget = QWidget()
        leftNavWidget.setFixedWidth(200)
        leftNavWidget.setStyleSheet("""
            QWidget {
                background-color: #202020;
                color: white;
            }
        """)
        leftNavLayout = QVBoxLayout(leftNavWidget)
        leftNavLayout.setSpacing(2)
        leftNavLayout.setContentsMargins(0, 0, 0, 0)

        # 添加导航按钮
        navButtons = [
            ("已安装", self.show_installed),
            ("扩展", self.show_plugins),
            ("下载", self.show_downloads),
            ("设置", self.open_settings),
            ("关于", self.open_about)
        ]

        for text, slot in navButtons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 12px 20px;
                    border: none;
                    background: transparent;
                    color: white;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #2d2d2d;
                }
                QPushButton:pressed {
                    background-color: #3d3d3d;
                }
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(slot)
            leftNavLayout.addWidget(btn)

        leftNavLayout.addStretch()
        mainLayout.addWidget(leftNavWidget)

    def setupMainContent(self, mainLayout):
        mainContentWidget = QWidget()
        mainContentLayout = QVBoxLayout(mainContentWidget)
        mainContentLayout.setSpacing(0)
        mainContentLayout.setContentsMargins(0, 0, 0, 0)

        # 主内容区域 - 使用网格布局显示修改器
        self.contentScrollArea = QScrollArea()
        self.contentScrollArea.setWidgetResizable(True)
        self.contentScrollArea.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1f1f1f;
            }
        """)

        self.contentWidget = QWidget()
        self.contentLayout = QGridLayout(self.contentWidget)
        self.contentLayout.setSpacing(10)
        self.contentLayout.setContentsMargins(10, 10, 10, 10)

        self.contentScrollArea.setWidget(self.contentWidget)
        mainContentLayout.addWidget(self.contentScrollArea)

        # 创建隐藏的功能组件
        self.setupHiddenWidgets(mainContentLayout)

        # 创建下载相关的组件
        self.setupDownloadWidgets(mainContentLayout)

        # 创建设置相关的组件
        self.setupSettingsWidgets(mainContentLayout)

        mainLayout.addWidget(mainContentWidget)

    def setupHiddenWidgets(self, mainContentLayout):
        # 创建一个隐藏的容器来存放功能组件
        self.hiddenContainer = QWidget()
        hiddenLayout = QVBoxLayout(self.hiddenContainer)
        hiddenLayout.setSpacing(0)
        hiddenLayout.setContentsMargins(0, 0, 0, 0)

        # 创建修改器列表（用于保持功能）
        self.flingListBox = MultilingualListWidget(self.hiddenContainer)
        self.flingListBox.itemActivated.connect(self.launch_trainer)
        hiddenLayout.addWidget(self.flingListBox)

        # 创建启动和删除按钮（用于保持功能）
        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(6)

        self.launchButton = CustomButton(tr("启动"), self.hiddenContainer)
        self.launchButton.clicked.connect(self.launch_trainer)
        buttonLayout.addWidget(self.launchButton)

        self.deleteButton = CustomButton(tr("删除"), self.hiddenContainer)
        self.deleteButton.clicked.connect(self.delete_trainer)
        buttonLayout.addWidget(self.deleteButton)

        hiddenLayout.addLayout(buttonLayout)

        # 隐藏容器但保留功能
        self.hiddenContainer.hide()
        mainContentLayout.addWidget(self.hiddenContainer)

    def setupDownloadWidgets(self, mainContentLayout):
        # 创建一个容器来存放所有下载相关的组件
        self.downloadContainer = QWidget()
        downloadLayout = QVBoxLayout(self.downloadContainer)
        downloadLayout.setSpacing(5)
        downloadLayout.setContentsMargins(20, 5, 20, 5)

        # 下载路径设置
        pathSettingsWidget = QWidget(self.downloadContainer)
        pathSettingsLayout = QVBoxLayout(pathSettingsWidget)
        pathSettingsLayout.setSpacing(2)
        pathSettingsLayout.setContentsMargins(0, 0, 0, 0)

        pathSettingsLayout.addWidget(QLabel(tr("修改器下载路径:")))
        pathInputLayout = QHBoxLayout()
        pathInputLayout.setSpacing(5)

        self.downloadPathEntry = QLineEdit(self.downloadContainer)
        self.downloadPathEntry.setReadOnly(True)
        self.downloadPathEntry.setText(self.trainerDownloadPath)
        self.downloadPathEntry.setFixedHeight(25)
        pathInputLayout.addWidget(self.downloadPathEntry)

        self.fileDialogButton = CustomButton("...", self.downloadContainer)
        self.fileDialogButton.setFixedSize(25, 25)
        self.fileDialogButton.clicked.connect(self.change_path)
        pathInputLayout.addWidget(self.fileDialogButton)

        pathSettingsLayout.addLayout(pathInputLayout)
        downloadLayout.addWidget(pathSettingsWidget)

        # 下载搜索框
        searchWidget = QWidget(self.downloadContainer)
        searchLayout = QHBoxLayout(searchWidget)
        searchLayout.setContentsMargins(0, 0, 0, 0)

        searchPixmap = QPixmap(search_path).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        searchLabel = QLabel(searchWidget)
        searchLabel.setPixmap(searchPixmap)
        searchLayout.addWidget(searchLabel)

        self.downloadSearchEntry = QLineEdit(self.downloadContainer)
        self.downloadSearchEntry.setPlaceholderText(self.downloadSearchEntryPrompt)
        self.downloadSearchEntry.returnPressed.connect(self.on_download_search)
        self.downloadSearchEntry.setFixedHeight(25)
        searchLayout.addWidget(self.downloadSearchEntry)

        downloadLayout.addWidget(searchWidget)

        # 下载列表
        self.downloadListBox = MultilingualListWidget(self.downloadContainer)
        self.downloadListBox.itemActivated.connect(self.on_download_start)
        self.downloadListBox.setMinimumHeight(100)
        downloadLayout.addWidget(self.downloadListBox)

        # 将容器添加到主布局但初始隐藏
        self.downloadContainer.hide()
        mainContentLayout.addWidget(self.downloadContainer)

    def setupSettingsWidgets(self, mainContentLayout):
        # 创建设置页面容器
        self.settingsContainer = QWidget()
        self.settingsContainer.setParent(self.contentWidget)  # 设置父对象
        settingsLayout = QVBoxLayout(self.settingsContainer)
        settingsLayout.setSpacing(10)
        settingsLayout.setContentsMargins(20, 10, 20, 10)

        # 创建设置选项
        # 1. 主题设置
        themeGroup = QWidget()
        themeLayout = QVBoxLayout(themeGroup)
        themeLayout.setSpacing(5)
        themeLayout.setContentsMargins(0, 0, 0, 10)
        
        themeLabel = QLabel(tr("主题"))
        themeLabel.setStyleSheet("font-weight: bold;")
        themeLayout.addWidget(themeLabel)
        
        self.themeComboBox = QComboBox()
        self.themeComboBox.addItems([tr("黑色"), tr("白色")])
        self.themeComboBox.setCurrentText(tr("黑色") if settings["theme"] == "black" else tr("白色"))
        self.themeComboBox.currentTextChanged.connect(self.on_theme_changed)
        themeLayout.addWidget(self.themeComboBox)
        
        settingsLayout.addWidget(themeGroup)

        # 2. 语言设置
        langGroup = QWidget()
        langLayout = QVBoxLayout(langGroup)
        langLayout.setSpacing(5)
        langLayout.setContentsMargins(0, 0, 0, 10)
        
        langLabel = QLabel(tr("语言"))
        langLabel.setStyleSheet("font-weight: bold;")
        langLayout.addWidget(langLabel)
        
        self.langComboBox = QComboBox()
        self.langComboBox.addItems([tr("简体中文"), tr("繁体中文"), "English"])
        self.langComboBox.setCurrentText(settings["language"])
        self.langComboBox.currentTextChanged.connect(self.on_language_changed)
        langLayout.addWidget(self.langComboBox)
        
        settingsLayout.addWidget(langGroup)

        # 3. 自动更新设置
        updateGroup = QWidget()
        updateLayout = QVBoxLayout(updateGroup)
        updateLayout.setSpacing(5)
        updateLayout.setContentsMargins(0, 0, 0, 10)
        
        updateLabel = QLabel(tr("自动更新"))
        updateLabel.setStyleSheet("font-weight: bold;")
        updateLayout.addWidget(updateLabel)
        
        self.checkAppUpdateBox = QCheckBox(tr("检查软件更新"))
        self.checkAppUpdateBox.setChecked(settings["checkAppUpdate"])
        self.checkAppUpdateBox.stateChanged.connect(self.on_check_app_update_changed)
        updateLayout.addWidget(self.checkAppUpdateBox)
        
        self.autoUpdateTransBox = QCheckBox(tr("自动更新翻译"))
        self.autoUpdateTransBox.setChecked(settings["autoUpdateTranslations"])
        self.autoUpdateTransBox.stateChanged.connect(self.on_auto_update_trans_changed)
        updateLayout.addWidget(self.autoUpdateTransBox)
        
        self.autoUpdateFlingDataBox = QCheckBox(tr("自动更新Fling数据"))
        self.autoUpdateFlingDataBox.setChecked(settings["autoUpdateFlingData"])
        self.autoUpdateFlingDataBox.stateChanged.connect(self.on_auto_update_fling_data_changed)
        updateLayout.addWidget(self.autoUpdateFlingDataBox)
        
        self.autoUpdateFlingTrainersBox = QCheckBox(tr("自动更新Fling修改器"))
        self.autoUpdateFlingTrainersBox.setChecked(settings["autoUpdateFlingTrainers"])
        self.autoUpdateFlingTrainersBox.stateChanged.connect(self.on_auto_update_fling_trainers_changed)
        updateLayout.addWidget(self.autoUpdateFlingTrainersBox)
        
        self.autoUpdateXiaoXingDataBox = QCheckBox(tr("自动更新小幸数据"))
        self.autoUpdateXiaoXingDataBox.setChecked(settings["autoUpdateXiaoXingData"])
        self.autoUpdateXiaoXingDataBox.stateChanged.connect(self.on_auto_update_xiaoxing_data_changed)
        updateLayout.addWidget(self.autoUpdateXiaoXingDataBox)
        
        settingsLayout.addWidget(updateGroup)

        # 4. 其他设置
        otherGroup = QWidget()
        otherLayout = QVBoxLayout(otherGroup)
        otherLayout.setSpacing(5)
        otherLayout.setContentsMargins(0, 0, 0, 10)
        
        otherLabel = QLabel(tr("其他"))
        otherLabel.setStyleSheet("font-weight: bold;")
        otherLayout.addWidget(otherLabel)
        
        self.showWarningBox = QCheckBox(tr("显示版权警告"))
        self.showWarningBox.setChecked(settings["showWarning"])
        self.showWarningBox.stateChanged.connect(self.on_show_warning_changed)
        otherLayout.addWidget(self.showWarningBox)
        
        settingsLayout.addWidget(otherGroup)

        # 添加弹性空间
        settingsLayout.addStretch()

        # 将容器添加到主布局但初始隐藏
        self.settingsContainer.hide()
        mainContentLayout.addWidget(self.settingsContainer)

    def show_installed(self):
        # 清空当前内容
        self.clearContent()
        
        # 显示已安装的修改器
        self.show_trainer_cards()

    def show_downloads(self):
        # 清空当前内容
        self.clearContent()
        
        # 显示下载界面
        self.downloadContainer.show()
        self.contentLayout.addWidget(self.downloadContainer, 0, 0, 1, -1)
        
    def on_download_search(self):
        keyword = self.downloadSearchEntry.text()
        if keyword and self.searchable:
            self.download_display(keyword)
            
    def download_display(self, keyword):
        """显示下载搜索结果"""
        self.downloadListBox.clear()
        self.downloadable = False
        self.statusbar.showMessage(tr("正在搜索..."))
        
        # 禁用搜索相关组件
        self.disable_download_widgets()
        
        # 开始搜索
        display_thread = DownloadDisplayThread(keyword, self)
        display_thread.message.connect(self.on_message)
        display_thread.messageBox.connect(self.on_message_box)
        display_thread.finished.connect(self.on_display_finished)
        display_thread.start()
        
    def on_download_start(self, item):
        index = self.downloadListBox.row(item)
        if index >= 0 and self.downloadable:
            self.enqueue_download(index, self.trainers, self.trainerDownloadPath, False, None, None)

    def enqueue_download(self, index, trainers, trainerDownloadPath, update, trainerPath, updateUrl):
        self.downloadQueue.put((index, trainers, trainerDownloadPath, update, trainerPath, updateUrl))
        if not self.currentlyDownloading:
            self.start_next_download()

    def start_next_download(self):
        if not self.downloadQueue.empty():
            self.currentlyDownloading = True
            self.disable_download_widgets()
            self.downloadListBox.clear()
            self.downloadable = False
            self.searchable = False

            index, trainers, trainerDownloadPath, update, trainerPath, updateUrl = self.downloadQueue.get()
            download_thread = DownloadTrainersThread(index, trainers, trainerDownloadPath, update, trainerPath, updateUrl, self)
            download_thread.message.connect(self.on_message)
            download_thread.messageBox.connect(self.on_message_box)
            download_thread.finished.connect(self.on_download_finished)
            download_thread.start()
        else:
            self.currentlyDownloading = False

    def on_message(self, message, type=None):
        item = QListWidgetItem(message)

        if type == "clear":
            self.downloadListBox.clear()
        elif type == "success":
            item.setBackground(QColor(0, 255, 0, 20))
            self.downloadListBox.addItem(item)
        elif type == "failure":
            item.setBackground(QColor(255, 0, 0, 20))
            self.downloadListBox.addItem(item)
        else:
            self.downloadListBox.addItem(item)

    def on_message_box(self, type, title, text):
        if type == "info":
            QMessageBox.information(self, title, text)
        elif type == "error":
            QMessageBox.critical(self, title, text)

    def on_display_finished(self, status):
        # 0: success; 1: failure
        if status:
            self.downloadable = False
        else:
            self.downloadable = True

        self.searchable = True
        self.enable_download_widgets()

    def on_download_finished(self, status):
        self.downloadable = False
        self.searchable = True
        self.enable_download_widgets()
        self.show_cheats()
        self.currentlyDownloading = False
        self.start_next_download()

    def show_plugins(self):
        """显示扩展页面"""
        # 清空当前内容
        self.clearContent()
        
        # 创建扩展页面布局
        row = 0
        col = 0
        max_cols = max(1, (self.contentWidget.width() - 40) // 220)
        
        # 显示已加载的插件
        if not self.plugins:
            # 如果没有插件，显示提示信息
            noPluginLabel = QLabel(tr("暂无已安装的扩展"))
            noPluginLabel.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 14px;
                }
            """)
            noPluginLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.contentLayout.addWidget(noPluginLabel, 0, 0, 1, -1)
            return
            
        for plugin in self.plugins:
            card = PluginCard(
                name=plugin.name,
                description=plugin.description,
                version=plugin.version,
                author=plugin.author,
                parent=self.contentWidget
            )
            self.contentLayout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def show_trainer_cards(self):
        row = 0
        col = 0
        max_cols = max(1, (self.contentWidget.width() - 40) // 220)
        
        for trainer_name, trainer_path in self.trainers.items():
            card = TrainerCard(
                name=trainer_name,
                description=tr("路径: ") + trainer_path,
                parent=self.contentWidget
            )
            card.launch_clicked.connect(self.launch_trainer_by_name)
            card.delete_clicked.connect(self.delete_trainer_by_name)
            
            self.contentLayout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def update_list(self):
        search_text = self.searchEntry.text().lower()
        if search_text == "":
            self.show_trainer_cards()
            return

        # 同时更新隐藏的列表（保持数据同步）
        self.flingListBox.clear()
        
        # 清空当前内容
        self.clearContent()
        
        # 显示搜索结果
        row = 0
        col = 0
        max_cols = max(1, (self.contentWidget.width() - 40) // 220)
        
        for trainer_name, trainer_path in self.trainers.items():
            if search_text in trainer_name.lower():
                self.flingListBox.addItem(trainer_name)
                
                card = TrainerCard(
                    name=trainer_name,
                    description=tr("路径: ") + trainer_path,
                    parent=self.contentWidget
                )
                card.launch_clicked.connect(self.launch_trainer_by_name)
                card.delete_clicked.connect(self.delete_trainer_by_name)
                
                self.contentLayout.addWidget(card, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 在窗口调整大小时重新布局卡片
        current_tab = self.getCurrentTab()
        if current_tab == "installed":
            self.show_installed()
        elif current_tab == "plugins":
            self.show_plugins()
        elif current_tab == "downloads":
            self.show_downloads()

    def getCurrentTab(self):
        """根据当前显示的内容判断前标签"""
        if self.downloadContainer.isVisible():
            return "downloads"
        elif self.settingsContainer.isVisible():
            return "settings"
        elif len(self.plugins) > 0 and any(isinstance(self.contentLayout.itemAt(i).widget(), PluginCard) for i in range(self.contentLayout.count())):
            return "plugins"
        elif self.contentLayout.count() > 0:
            return "installed"
        return "plugins"  # 默认显示插件页面

    def clearContent(self):
        # 隐藏所有容器
        self.downloadContainer.hide()
        self.settingsContainer.hide()
        
        # 清除内容区域的所有部件
        while self.contentLayout.count():
            item = self.contentLayout.takeAt(0)
            widget = item.widget()
            if widget and widget not in [self.downloadContainer, self.settingsContainer]:
                widget.deleteLater()

    # ===========================================================================
    # Core functions
    # ===========================================================================
    def closeEvent(self, event):
        # 清理插件
        for plugin in self.plugins:
            try:
                plugin.cleanup()
            except Exception as e:
                print(f"清理插件失败: {str(e)}")
        
        super().closeEvent(event)
        os._exit(0)

    def send_notification(self, success, latest_version=0):
        tray_icon = QSystemTrayIcon(QIcon(resource_path("assets/logo.ico")), self)
        tray_icon.show()

        if success and latest_version > self.appVersion:
            tray_icon.showMessage(
                tr('Update Available'),
                tr('New version found: {old_version} ➜ {new_version}').format(
                    old_version=self.appVersion,
                    new_version=latest_version
                ) + '\n' + tr('Please navigate to `Options` ➜ `About` to download the latest version.'),
                QSystemTrayIcon.MessageIcon.Information
            )
        elif not success:
            tray_icon.showMessage(
                tr('Update Check Failed'),
                tr('Failed to check for software update. You can navigate to `Options` ➜ `About` to check for updates manually.'),
                QSystemTrayIcon.MessageIcon.Warning
            )

        self.versionFetcher.quit()

    def init_settings(self):
        if settings["theme"] == "black":
            style = style_sheet.black
        elif settings["theme"] == "white":
            style = style_sheet.white

        style = style.format(
            check_mark=checkMark_path,
            drop_down_arrow=dropDownArrow_path,
            scroll_bar_top=upArrow_path,
            scroll_bar_bottom=downArrow_path,
            scroll_bar_left=leftArrow_path,
            scroll_bar_right=rightArrow_path,
        )
        self.setStyleSheet(style)

    def on_enter_press(self):
        keyword = self.downloadSearchEntry.text()
        if keyword and self.searchable:
            self.download_display(keyword)

    def disable_download_widgets(self):
        self.downloadSearchEntry.setEnabled(False)
        self.fileDialogButton.setEnabled(False)

    def enable_download_widgets(self):
        self.downloadSearchEntry.setEnabled(True)
        self.fileDialogButton.setEnabled(True)

    def disable_all_widgets(self):
        self.fileDialogButton.setEnabled(False)
        self.launchButton.setEnabled(False)
        self.deleteButton.setEnabled(False)

    def enable_all_widgets(self):
        self.fileDialogButton.setEnabled(True)
        self.launchButton.setEnabled(True)
        self.deleteButton.setEnabled(True)

    def show_cheats(self):
        self.flingListBox.clear()
        self.trainers = {}
        entries = sorted(
            os.scandir(self.trainerDownloadPath),
            key=lambda dirent: sort_trainers_key(dirent.name)
        )

        for trainer in entries:
            trainerPath = os.path.normpath(trainer.path)
            if os.path.isfile(trainerPath):
                trainerName, trainerExt = os.path.splitext(os.path.basename(trainerPath))
                if trainerExt.lower() == ".exe" and os.path.getsize(trainerPath) != 0:
                    self.flingListBox.addItem(trainerName)
                    self.trainers[trainerName] = trainerPath
            else:
                exe_exclusions = ["flashplayer_22.0.0.210_ax_debug.exe"]
                trainerName = os.path.basename(trainerPath)
                exe_file_path = None
                for file in os.scandir(trainerPath):
                    filePath = os.path.normpath(file.path)
                    fileExt = os.path.splitext(file.name)[1]
                    if file.is_file() and fileExt.lower() == ".exe" and file.name not in exe_exclusions:
                        exe_file_path = filePath
                        break
                if exe_file_path:
                    self.flingListBox.addItem(trainerName)
                    self.trainers[trainerName] = exe_file_path

    def launch_trainer(self):
        try:
            selection = self.flingListBox.currentRow()
            if selection != -1:
                trainerName = self.flingListBox.item(selection).text()
                trainerPath = os.path.normpath(self.trainers[trainerName])
                trainerDir = os.path.dirname(trainerPath)

                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", trainerPath, None, trainerDir, 1
                )
        except Exception as e:
            print(str(e))

    def delete_trainer(self):
        index = self.flingListBox.currentRow()
        if index != -1:
            trainerName = self.flingListBox.item(index).text()
            trainerPath = self.trainers[trainerName]

            msg_box = QMessageBox(
                QMessageBox.Icon.Question,
                tr('Delete trainer'),
                tr('Are you sure you want to delete ') + f"{trainerName}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                self
            )

            yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
            yes_button.setText(tr("Confirm"))
            no_button = msg_box.button(QMessageBox.StandardButton.No)
            no_button.setText(tr("Cancel"))
            reply = msg_box.exec()

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    os.chmod(trainerPath, stat.S_IWRITE)
                    parent_dir = os.path.dirname(trainerPath)
                    if os.path.basename(parent_dir) == trainerName:
                        shutil.rmtree(parent_dir)
                    else:
                        os.remove(trainerPath)
                    self.flingListBox.takeItem(index)
                    self.show_cheats()
                except PermissionError as e:
                    QMessageBox.critical(self, tr("Error"), tr("Trainer is currently in use, please close any programs using the file and try again."))

    def findWidgetInStatusBar(self, statusbar, widgetName):
        for widget in statusbar.children():
            if widget.objectName() == widgetName:
                return widget
        return None

    def change_path(self):
        self.downloadListBox.clear()
        self.disable_all_widgets()
        folder = QFileDialog.getExistingDirectory(self, tr("Change trainer download path"))

        if folder:
            changedPath = os.path.normpath(os.path.join(folder, "GCM Trainers"))
            if self.downloadPathEntry.text() == changedPath:
                QMessageBox.critical(self, tr("Error"), tr("Please choose a new path."))
                self.on_message(tr("Failed to change trainer download path."), "failure")
                self.enable_all_widgets()
                return

            self.downloadListBox.addItem(tr("Migrating existing trainers..."))
            migration_thread = PathChangeThread(self.trainerDownloadPath, changedPath, self)
            migration_thread.finished.connect(self.on_migration_finished)
            migration_thread.error.connect(self.on_migration_error)
            migration_thread.start()

        else:
            self.downloadListBox.addItem(tr("No path selected."))
            self.enable_all_widgets()
            return

    def on_migration_error(self, error_message):
        QMessageBox.critical(self, tr("Error"), tr("Error migrating trainers: ") + error_message)
        self.on_message(tr("Failed to change trainer download path."), "failure")
        self.show_cheats()
        self.enable_all_widgets()

    def on_migration_finished(self, new_path):
        self.trainerDownloadPath = new_path
        settings["downloadPath"] = self.trainerDownloadPath
        apply_settings(settings)
        self.show_cheats()
        self.on_message(tr("Migration complete!"), "success")
        self.downloadPathEntry.setText(self.trainerDownloadPath)
        self.enable_all_widgets()

    def on_status_load(self, widgetName, message):
        statusWidget = StatusMessageWidget(widgetName, message)
        self.statusbar.addWidget(statusWidget)

    def on_status_update(self, widgetName, newMessage, state):
        target = self.findWidgetInStatusBar(self.statusbar, widgetName)
        target.update_message(newMessage, state)

    def on_interval_finished(self, widgetName):
        target = self.findWidgetInStatusBar(self.statusbar, widgetName)
        if target:
            target.deleteLater()

        if widgetName == "fling":
            self.currentlyUpdatingFling = False
        elif widgetName == "xiaoxing":
            self.currentlyUpdatingXiaoXing = False
        elif widgetName == "translations":
            self.currentlyUpdatingTrans = False
        elif widgetName == "trainerUpdate":
            self.currentlyUpdatingTrainers = False

    # ===========================================================================
    # Menu functions
    # ===========================================================================
    def open_settings(self):
        self.show_settings()

    def import_files(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, tr("Select trainers you want to import"), "", "Executable Files (*.exe)")
        if file_names:
            for file_name in file_names:
                try:
                    dst = os.path.join(self.trainerDownloadPath, os.path.basename(file_name))
                    if os.path.exists(dst):
                        os.chmod(dst, stat.S_IWRITE)
                    shutil.copy(file_name, dst)
                    print("Trainer copied: ", file_name)
                except Exception as e:
                    QMessageBox.critical(self, tr("Failure"), tr("Failed to import trainer: ") + f"{file_name}\n{str(e)}")
                self.show_cheats()

            msg_box = QMessageBox(
                QMessageBox.Icon.Question,
                tr("Delete original trainers"),
                tr("Do you want to delete the original trainer files?"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                self
            )

            yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
            yes_button.setText(tr("Yes"))
            no_button = msg_box.button(QMessageBox.StandardButton.No)
            no_button.setText(tr("No"))
            reply = msg_box.exec()

            if reply == QMessageBox.StandardButton.Yes:
                for file_name in file_names:
                    try:
                        os.remove(file_name)
                    except Exception as e:
                        QMessageBox.critical(self, tr("Failure"), tr("Failed to delete original trainer: ") + f"{file_name}\n{str(e)}")

    def open_trainer_directory(self):
        os.startfile(self.trainerDownloadPath)

    def add_whitelist(self):
        msg_box = QMessageBox(
            QMessageBox.Icon.Question,
            tr("Administrator Access Required"),
            tr("To proceed with adding the trainer download paths to the Windows Defender whitelist, administrator rights are needed. A User Account Control (UAC) prompt will appear for permission.") +
            "\n\n" + tr("Would you like to continue?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            self
        )

        yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
        yes_button.setText(tr("Yes"))
        no_button = msg_box.button(QMessageBox.StandardButton.No)
        no_button.setText(tr("No"))
        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            paths = [DOWNLOAD_TEMP_DIR, settings["downloadPath"]]

            try:
                subprocess.run([elevator_path, 'whitelist'] + paths, check=True, shell=True)
                QMessageBox.information(self, tr("Success"), tr("Successfully added paths to Windows Defender whitelist."))

            except subprocess.CalledProcessError:
                QMessageBox.critical(self, tr("Failure"), tr("Failed to add paths to Windows Defender whitelist."))

    def open_about(self):
        if self.about_window is not None and self.about_window.isVisible():
            self.about_window.raise_()
            self.about_window.activateWindow()
        else:
            self.about_window = AboutDialog(self)
            self.about_window.show()

    def open_trainer_management(self):
        if self.trainer_manage_window is not None and self.trainer_manage_window.isVisible():
            self.trainer_manage_window.raise_()
            self.trainer_manage_window.activateWindow()
        else:
            self.trainer_manage_window = TrainerManagementDialog(self)
            self.trainer_manage_window.show()

    def launch_trainer_by_name(self, trainer_name):
        try:
            if trainer_name in self.trainers:
                trainer_path = os.path.normpath(self.trainers[trainer_name])
                trainer_dir = os.path.dirname(trainer_path)

                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", trainer_path, None, trainer_dir, 1
                )
        except Exception as e:
            print(str(e))

    def delete_trainer_by_name(self, trainer_name):
        if trainer_name in self.trainers:
            trainer_path = self.trainers[trainer_name]

            msg_box = QMessageBox(
                QMessageBox.Icon.Question,
                tr('删除修改器'),
                tr('确定要删除 ') + f"{trainer_name}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                self
            )

            yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
            yes_button.setText(tr("确定"))
            no_button = msg_box.button(QMessageBox.StandardButton.No)
            no_button.setText(tr("取消"))
            reply = msg_box.exec()

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    os.chmod(trainer_path, stat.S_IWRITE)
                    parent_dir = os.path.dirname(trainer_path)
                    if os.path.basename(parent_dir) == trainer_name:
                        shutil.rmtree(parent_dir)
                    else:
                        os.remove(trainer_path)
                    self.show_installed()  # 刷新显示
                except PermissionError as e:
                    QMessageBox.critical(self, tr("错误"), tr("修改器在使用中，请关闭所有相关程序后重试。"))

    def download_trainer_by_name(self, trainer_name):
        # 使用原有的下载功能
        self.downloadListBox.clear()
        self.downloadListBox.addItem(trainer_name)
        self.on_download_start(self.downloadListBox.item(0))

    def show_settings(self):
        # 清空前内容
        self.clearContent()
        
        # 显示设置界面
        self.settingsContainer.show()
        self.contentLayout.addWidget(self.settingsContainer, 0, 0, 1, -1)

    def on_theme_changed(self, theme):
        settings["theme"] = "black" if theme == tr("黑色") else "white"
        apply_settings(settings)
        self.init_settings()

    def on_language_changed(self, language):
        settings["language"] = language
        apply_settings(settings)
        QMessageBox.information(self, tr("重启生效"), tr("语言设置将在重启后生效"))

    def on_check_app_update_changed(self, state):
        settings["checkAppUpdate"] = bool(state)
        apply_settings(settings)

    def on_auto_update_trans_changed(self, state):
        settings["autoUpdateTranslations"] = bool(state)
        apply_settings(settings)

    def on_auto_update_fling_data_changed(self, state):
        settings["autoUpdateFlingData"] = bool(state)
        apply_settings(settings)

    def on_auto_update_fling_trainers_changed(self, state):
        settings["autoUpdateFlingTrainers"] = bool(state)
        apply_settings(settings)

    def on_auto_update_xiaoxing_data_changed(self, state):
        settings["autoUpdateXiaoXingData"] = bool(state)
        apply_settings(settings)

    def on_show_warning_changed(self, state):
        settings["showWarning"] = bool(state)
        apply_settings(settings)

    def fetch_trainer_translations(self):
        if not self.currentlyUpdatingTrans:
            self.currentlyUpdatingTrans = True
            fetch_trainer_details_thread = FetchTrainerTranslations(self)
            fetch_trainer_details_thread.message.connect(self.on_status_load)
            fetch_trainer_details_thread.update.connect(self.on_status_update)
            fetch_trainer_details_thread.finished.connect(self.on_interval_finished)
            fetch_trainer_details_thread.start()

    def fetch_fling_data(self):
        if not self.currentlyUpdatingFling:
            self.currentlyUpdatingFling = True
            fetch_fling_site_thread = FetchFlingSite(self)
            fetch_fling_site_thread.message.connect(self.on_status_load)
            fetch_fling_site_thread.update.connect(self.on_status_update)
            fetch_fling_site_thread.finished.connect(self.on_interval_finished)
            fetch_fling_site_thread.start()

    def update_fling_trainers(self):
        if not self.currentlyUpdatingTrainers:
            self.currentlyUpdatingTrainers = True
            trainer_update_thread = UpdateFlingTrainers(self.trainers, self)
            trainer_update_thread.message.connect(self.on_status_load)
            trainer_update_thread.update.connect(self.on_status_update)
            trainer_update_thread.updateTrainer.connect(self.on_trainer_update)
            trainer_update_thread.finished.connect(self.on_interval_finished)
            trainer_update_thread.start()

    def fetch_xiaoxing_data(self):
        if not self.currentlyUpdatingXiaoXing:
            self.currentlyUpdatingXiaoXing = True
            fetch_xiaoxing_site_thread = FetchXiaoXingSite(self)
            fetch_xiaoxing_site_thread.message.connect(self.on_status_load)
            fetch_xiaoxing_site_thread.update.connect(self.on_status_update)
            fetch_xiaoxing_site_thread.finished.connect(self.on_interval_finished)
            fetch_xiaoxing_site_thread.start()

    def on_main_interval(self):
        if settings["autoUpdateTranslations"]:
            self.fetch_trainer_translations()
        if settings["autoUpdateFlingData"]:
            self.fetch_fling_data()
        if settings["autoUpdateFlingTrainers"]:
            self.update_fling_trainers()
        if settings["autoUpdateXiaoXingData"]:
            self.fetch_xiaoxing_data()

    def on_trainer_update(self, trainerPath, updateUrl):
        self.enqueue_download(None, None, self.trainerDownloadPath, True, trainerPath, updateUrl)


class SearchWorker(QThread):
    searchComplete = pyqtSignal(list)  # 搜索完成信号，传递结果列表
    searchFailed = pyqtSignal(str)     # 搜索失败信号，传递错误信息

    def __init__(self, keyword):
        super().__init__()
        self.keyword = keyword

    def run(self):
        try:
            # 使用原有的搜索逻辑
            results = []
            search_url = f"https://flingtrainer.com/search/{self.keyword}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://flingtrainer.com/',
                'Origin': 'https://flingtrainer.com'
            }
            
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            trainer_links = soup.find_all('a', class_='trainer-link')
            
            for link in trainer_links:
                trainer_name = link.text.strip()
                if trainer_name:
                    results.append(trainer_name)
                    
            self.searchComplete.emit(results)
        except Exception as e:
            self.searchFailed.emit(str(e))

class DownloadWorker(QThread):
    downloadComplete = pyqtSignal(str)  # 下载完成信号，传递修改器名称
    downloadFailed = pyqtSignal(str)    # 下载失败信号，传递错误信息
    
    def __init__(self, trainer_name, download_path):
        super().__init__()
        self.trainer_name = trainer_name
        self.download_path = download_path
        
    def run(self):
        try:
            # 使用原有的下载逻辑
            download_url = f"https://flingtrainer.com/download/{urllib.parse.quote(self.trainer_name)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://flingtrainer.com/',
                'Origin': 'https://flingtrainer.com'
            }
            
            # 创建临时下载目录
            if not os.path.exists(DOWNLOAD_TEMP_DIR):
                os.makedirs(DOWNLOAD_TEMP_DIR)
                
            # 下载文件
            temp_file = os.path.join(DOWNLOAD_TEMP_DIR, f"{self.trainer_name}.zip")
            response = requests.get(download_url, headers=headers, stream=True)
            response.raise_for_status()
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            # 解压文件
            target_dir = os.path.join(self.download_path, self.trainer_name)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                
            with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
                
            # 清理临时文件
            os.remove(temp_file)
            
            self.downloadComplete.emit(self.trainer_name)
        except Exception as e:
            self.downloadFailed.emit(str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 加载选定的字体
    primary_font_path = font_config[settings["language"]]
    primary_font_id = QFontDatabase.addApplicationFont(primary_font_path)
    primary_font_families = QFontDatabase.applicationFontFamilies(primary_font_id)
    custom_font = QFont(primary_font_families[0], 10)
    custom_font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    app.setFont(custom_font)

    mainWin = GameCheatsManager()
    mainWin.show()

    # Center window
    qr = mainWin.frameGeometry()
    cp = mainWin.screen().availableGeometry().center()
    qr.moveCenter(cp)
    mainWin.move(qr.topLeft())

    sys.exit(app.exec())

