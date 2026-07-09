import os
from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QScrollArea, QDialog, QFileDialog, QMessageBox, QInputDialog, QCheckBox, QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QKeySequence, QIcon

from config import SETTINGS, TOOL_TYPES, SECONDARY_CATEGORIES, DEFAULT_SETTINGS, save_settings

FORBIDDEN_HOTKEYS = {
    "ctrl+c", "ctrl+v", "ctrl+x", "ctrl+z", "ctrl+y", "ctrl+f"
}

ICON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "icons")
UI_ICON_MAP = {
    "菜单": "title_menu.svg",
    "全部工具": "nav_all.svg",
    "分类": None,
    "最近使用": "nav_recent.svg",
    "我的收藏": "nav_favorite.svg",
    "社区": "nav_community.svg",
    "安全社区": "nav_community.svg",
    "设置": "nav_settings.svg",
    "关于": "nav_about.svg",
    "最小化": "title_minimize.svg",
    "窗口化": "title_maximize.svg",
    "退出": "title_close.svg",
    "搜索": "搜索.svg",
    "添加工具": "添加工具.svg",
    "记事本": "记事本.svg",
    "批量模式": "批量模式.svg",
    "GitHub": "github.svg",
    "微信群聊": "wx.svg",
    "工具导入": "工具导入.svg",
    "工具导出": "工具导出.svg",
    "安全众测": "nav_security_test.svg",
    "漏洞知识库": "nav_vulnerability_db.svg",
    "安全漏洞": "nav_vulnerability_db.svg",
    "运行选中": None,
    "本地工具": "nav_local.svg",
    "网页工具": "nav_web.svg",
    "AI工具": "AI工具.svg",
    "上一页": None,
    "下一页": None,
    "跳转": None,
    "浏览": None,
    "清除": None,
    "保存": None,
    "取消": None,
    "新增Python": "新增Python.svg",
    "删除Python": "删除Python.svg",
    "新增Java": None,
    "删除Java": None,
    "重置": None,
    "WebShell管理工具": None,
    "信息收集工具": "搜索.svg",
    "抓包与代理工具": "包容网关_inclusive-gateway.svg",
    "漏洞扫描与利用工具": None,
    "框架漏洞利用工具": "API 应用_api-app.svg",
    "爆破工具": None,
    "免杀工具": None,
    "后渗透工具": None,
    "其他工具": "其他工具.svg",
    "未分类": None,
}


ICON_ALIAS_MAP = {
    "抓包与代理工具": "抓包与代理工具.svg",
    "框架漏洞利用工具": "框架漏洞利用工具.svg",
    "免杀工具": "免杀工具.svg",
}


def get_ui_icon(name):
    key = str(name or "").strip()
    file_name = UI_ICON_MAP.get(key) or ICON_ALIAS_MAP.get(key)
    if not file_name:
        return QIcon()

    icon_path = os.path.join(ICON_DIR, file_name)
    if not os.path.exists(icon_path):
        return QIcon()

    icon = QIcon(icon_path)
    if icon.isNull():
        return QIcon()
    return icon


def apply_button_icon(button, name, size=16):
    button.setIcon(get_ui_icon(name))
    button.setIconSize(QSize(size, size))


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("titleBar")
        self._dragging = False
        self._drag_offset = None
        self.init_ui()

    def init_ui(self):
        lay = QHBoxLayout(self)
        self.main_layout = lay
        lay.setContentsMargins(10, 0, 6, 0)
        lay.setSpacing(2)

        self.logo_label = QLabel(self)
        try:
            icon = QIcon("config/redblue.ico")
            if not icon.isNull():
                self.logo_label.setPixmap(icon.pixmap(18, 18))
        except Exception:
            pass
        self.logo_label.setFixedSize(20, 20)
        lay.addWidget(self.logo_label)

        self.title_label = QLabel("凭阑红蓝工具箱PBox", self)
        self.title_label.setStyleSheet("font-size:15px; font-weight:700;")
        lay.addWidget(self.title_label)

        self.perf_label = QLabel("", self)
        self.perf_label.setStyleSheet("font-size:12px; color:#8A8A92;")
        lay.addWidget(self.perf_label)

        lay.addStretch()

        self.btn_wx = QPushButton("")
        self.btn_wx.setObjectName("titleButton")
        self.btn_wx.setToolTip("微信群聊")
        apply_button_icon(self.btn_wx, "微信群聊", 12)
        self.btn_wx.setText("")
        self.btn_wx.setFixedSize(30, 24)
        self.btn_wx.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        lay.addWidget(self.btn_wx)
        
        self.btn_github = QPushButton("")
        self.btn_github.setObjectName("titleButton")
        self.btn_github.setToolTip("GitHub")
        apply_button_icon(self.btn_github, "GitHub", 12)
        self.btn_github.setText("")
        self.btn_github.setFixedSize(30, 24)
        self.btn_github.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        lay.addWidget(self.btn_github)

        self.btn_menu = QPushButton("☰")
        self.btn_menu.setObjectName("titleButton")
        self.btn_menu.setToolTip("菜单")
        self.menu = QMenu(self)
        self.btn_menu.clicked.connect(self.show_menu_popup)
        apply_button_icon(self.btn_menu, "菜单", 12)
        self.btn_menu.setText("")
        self.btn_menu.setFixedSize(30, 24)
        self.btn_menu.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        lay.addWidget(self.btn_menu)

        self.btn_min = QPushButton("─")
        self.btn_min.setObjectName("titleButton")
        self.btn_min.clicked.connect(self.parent.showMinimized)
        apply_button_icon(self.btn_min, "最小化", 12)
        self.btn_min.setText("")
        self.btn_min.setFixedSize(30, 24)
        self.btn_min.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        lay.addWidget(self.btn_min)

        self.btn_max = QPushButton("□")
        self.btn_max.setObjectName("titleButton")
        self.btn_max.clicked.connect(self.toggle_maximize)
        apply_button_icon(self.btn_max, "窗口化", 12)
        self.btn_max.setText("")
        self.btn_max.setFixedSize(30, 24)
        self.btn_max.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        lay.addWidget(self.btn_max)

        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("titleButton")
        self.btn_close.clicked.connect(self.parent.close)
        apply_button_icon(self.btn_close, "退出", 12)
        self.btn_close.setText("")
        self.btn_close.setFixedSize(30, 24)
        self.btn_close.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        lay.addWidget(self.btn_close)

        self.setFixedHeight(50)

    def show_menu_popup(self):
        try:
            pos = self.btn_menu.mapToGlobal(self.btn_menu.rect().bottomLeft())
            self.menu.exec(pos)
        except Exception:
            pass

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self.parent is not None:
            self._dragging = True
            self._drag_offset = e.globalPosition().toPoint() - self.parent.pos()

    def mouseMoveEvent(self, e):
        if self._dragging and self.parent is not None and not self.parent.isMaximized():
            self.parent.move(e.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, _e):
        self._dragging = False


class SearchBar(QFrame):
    search_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索工具...")
        self.search_input.textChanged.connect(self.search_changed.emit)
        self.search_input.setMinimumWidth(0)
        self.search_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        lay.addWidget(self.search_input)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


class CategoryPanel(QFrame):
    category_selected = pyqtSignal(str)
    category_renamed = pyqtSignal(str, str)
    category_deleted = pyqtSignal(str)
    category_added = pyqtSignal(str)
    category_move = pyqtSignal(str, int)

    def __init__(self, categories=None, parent=None):
        super().__init__(parent)
        self.categories = categories or []

    def update_categories(self, categories, category_counts=None):
        self.categories = categories or []


class ToolDialog(QDialog):
    def __init__(self, categories, tool_data=None, parent=None):
        super().__init__(parent)
        self.categories = categories or []
        self.tool_data = tool_data or {}
        self.shortcut_key = ""
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("工具")
        self.resize(560, 620)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        lay.addWidget(QLabel("工具名称:"))
        self.ed_name = QLineEdit(self.tool_data.get("name", ""))
        lay.addWidget(self.ed_name)

        lay.addWidget(QLabel("工具类型:"))
        self.cb_type = QComboBox()
        self.cb_type.addItems(list(TOOL_TYPES))
        if self.tool_data.get("type"):
            self.cb_type.setCurrentText(str(self.tool_data.get("type", "")))
        self.cb_type.currentTextChanged.connect(self.on_type_changed)
        lay.addWidget(self.cb_type)

        self.lb_url = QLabel("网页地址:")
        lay.addWidget(self.lb_url)
        self.ed_url = QLineEdit(self.tool_data.get("url", ""))
        lay.addWidget(self.ed_url)

        self.lb_path = QLabel("工具路径:")
        lay.addWidget(self.lb_path)
        hpath = QHBoxLayout()
        self.ed_path = QLineEdit(self.tool_data.get("path", ""))
        hpath.addWidget(self.ed_path)
        self.btn_browse = QPushButton("浏览")
        self.btn_browse.setObjectName("noHoverBtn")
        self.btn_browse.clicked.connect(self.browse_file)
        apply_button_icon(self.btn_browse, "浏览")
        hpath.addWidget(self.btn_browse)
        lay.addLayout(hpath)

        lay.addWidget(QLabel("工具分类:"))
        hcat = QHBoxLayout()
        self.cb_main_cat = QComboBox()
        self.cb_main_cat.addItems(["本地工具", "网页工具", "AI工具"])
        self.cb_main_cat.currentTextChanged.connect(self.update_sub_categories)
        hcat.addWidget(self.cb_main_cat)

        self.cb_sub_cat = QComboBox()
        self.cb_sub_cat.currentTextChanged.connect(self._sync_category_text)
        hcat.addWidget(self.cb_sub_cat)
        lay.addLayout(hcat)

        self.cb_cat = QComboBox()
        self.cb_cat.setEditable(True)
        self.cb_cat.hide()
        lay.addWidget(self.cb_cat)

        lay.addWidget(QLabel("启动参数:"))
        self.ed_params = QLineEdit(self.tool_data.get("params", ""))
        lay.addWidget(self.ed_params)

        lay.addWidget(QLabel("工具描述:"))
        self.ed_desc = QLineEdit(self.tool_data.get("description", ""))
        lay.addWidget(self.ed_desc)

        lay.addWidget(QLabel("标签(英文逗号分隔，最多3个):"))
        tags = self.tool_data.get("tags", []) or []
        self.ed_tags = QLineEdit(", ".join([str(t) for t in tags][:3]))
        lay.addWidget(self.ed_tags)

        lay.addWidget(QLabel("显示权重(0-10):"))
        self.cb_weight = QComboBox()
        self.cb_weight.addItems([str(i) for i in range(11)])
        self.cb_weight.setCurrentText(str(self.tool_data.get("weight", 0)))
        lay.addWidget(self.cb_weight)

        lay.addWidget(QLabel("快捷键:"))
        hshort = QHBoxLayout()
        self.ed_shortcut = QLineEdit()
        self.ed_shortcut.setPlaceholderText("按下组合键或手动输入")
        if hasattr(self.parent(), "tool_shortcuts"):
            old_name = str(self.tool_data.get("name", ""))
            if old_name:
                old_shortcut = str(self.parent().tool_shortcuts.get(old_name, ""))
                if old_shortcut:
                    self.ed_shortcut.setText(old_shortcut)
                    self.shortcut_key = old_shortcut
        btn_clear = QPushButton("清除")
        btn_clear.setObjectName("noHoverBtn")
        btn_clear.clicked.connect(self.clear_short)
        apply_button_icon(btn_clear, "清除")
        hshort.addWidget(self.ed_shortcut)
        hshort.addWidget(btn_clear)
        lay.addLayout(hshort)

        hbtn = QHBoxLayout()
        hbtn.addStretch()
        btn_save = QPushButton("保存")
        btn_save.setObjectName("noHoverBtn")
        btn_save.clicked.connect(self._on_save_clicked)
        btn_cancel = QPushButton("取消")
        btn_cancel.setObjectName("noHoverBtn")
        btn_cancel.clicked.connect(self.reject)
        apply_button_icon(btn_save, "保存")
        apply_button_icon(btn_cancel, "取消")
        hbtn.addWidget(btn_save)
        hbtn.addWidget(btn_cancel)
        lay.addLayout(hbtn)

        self._apply_category_text(str(self.tool_data.get("category", "")).strip())
        self.on_type_changed(self.cb_type.currentText())

    def update_sub_categories(self, main_cat):
        self.cb_sub_cat.blockSignals(True)
        self.cb_sub_cat.clear()
        self.cb_sub_cat.addItem("请选择二级分类")
        for sub_cat in SECONDARY_CATEGORIES.get(main_cat, []):
            self.cb_sub_cat.addItem(sub_cat)
        self.cb_sub_cat.blockSignals(False)
        self._sync_category_text()

    def _sync_category_text(self):
        main_cat = self.cb_main_cat.currentText().strip()
        sub_cat = self.cb_sub_cat.currentText().strip()
        if sub_cat and sub_cat != "请选择二级分类":
            self.cb_cat.setCurrentText(f"{main_cat}/{sub_cat}")
        else:
            self.cb_cat.setCurrentText(main_cat)

    def _apply_category_text(self, category):
        category = str(category or "").strip()
        main_cat = "本地工具"
        sub_cat = "请选择二级分类"
        if category.startswith("网页工具"):
            main_cat = "网页工具"
        elif category.startswith("AI工具"):
            main_cat = "AI工具"
        if "/" in category:
            _, sub_cat = category.split("/", 1)
            sub_cat = sub_cat.strip()

        self.cb_main_cat.blockSignals(True)
        self.cb_main_cat.setCurrentText(main_cat)
        self.cb_main_cat.blockSignals(False)
        self.update_sub_categories(main_cat)

        idx = self.cb_sub_cat.findText(sub_cat)
        self.cb_sub_cat.setCurrentIndex(idx if idx >= 0 else 0)
        self._sync_category_text()

    def on_type_changed(self, t):
        is_web = str(t).strip() == "网页"
        self.lb_url.setVisible(is_web)
        self.ed_url.setVisible(is_web)
        self.lb_path.setVisible(not is_web)
        self.ed_path.setVisible(not is_web)
        self.btn_browse.setVisible(not is_web)
        self.ed_params.setVisible(not is_web)

    def browse_file(self):
        fi, _ = QFileDialog.getOpenFileName(self, "选择工具文件")
        if fi:
            self.ed_path.setText(fi)

    def clear_short(self):
        self.ed_shortcut.clear()
        self.shortcut_key = ""

    def keyPressEvent(self, e):
        if self.ed_shortcut.hasFocus():
            mods = []
            if e.modifiers() & Qt.KeyboardModifier.ControlModifier:
                mods.append("Ctrl")
            if e.modifiers() & Qt.KeyboardModifier.AltModifier:
                mods.append("Alt")
            if e.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                mods.append("Shift")
            if e.key() in (Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_Shift):
                return
            keystr = QKeySequence(e.key()).toString()
            if not keystr:
                return
            final = "+".join(mods + [keystr])
            forbidden = final.strip().lower().replace(" ", "")
            if forbidden in FORBIDDEN_HOTKEYS:
                QMessageBox.warning(self, "快捷键冲突", "此快捷键为系统常用快捷键，禁止使用")
                self.ed_shortcut.clear()
                return
            if self.check_conflict(final):
                QMessageBox.warning(self, "快捷键冲突", "此快捷键已被其它工具占用")
                self.ed_shortcut.clear()
                return
            self.ed_shortcut.setText(final)
            self.shortcut_key = final
        else:
            super().keyPressEvent(e)

    def check_conflict(self, newval):
        parent = self.parent()
        if not hasattr(parent, "tool_shortcuts"):
            return False
        curr = str(self.tool_data.get("name", "")) if self.tool_data else None
        for nm, val in parent.tool_shortcuts.items():
            if str(val) == str(newval) and str(nm) != str(curr):
                return True
        return False

    def _on_save_clicked(self):
        tags_str = self.ed_tags.text().strip()
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        if len(tags) > 3:
            QMessageBox.warning(self, "标签数量超限", "最多只能填写3个标签")
            return
        if any(len(t) > 10 for t in tags):
            QMessageBox.warning(self, "标签超长", "每个标签最多10个字符")
            return

        val = self.ed_shortcut.text().strip()
        forbidden = val.lower().replace(" ", "")
        if forbidden in FORBIDDEN_HOTKEYS:
            QMessageBox.warning(self, "快捷键冲突", "此快捷键为系统常用快捷键，禁止使用")
            return
        if val and self.check_conflict(val):
            QMessageBox.warning(self, "快捷键冲突", "此快捷键已被其它工具占用")
            return

        self.shortcut_key = val
        self.accept()

    def get_tool_data(self):
        data = {}
        data["name"] = self.ed_name.text().strip()
        data["category"] = self.cb_cat.currentText().strip()
        data["type"] = self.cb_type.currentText().strip()
        data["description"] = self.ed_desc.text().strip()
        data["weight"] = int(self.cb_weight.currentText())
        tags = [t.strip() for t in self.ed_tags.text().strip().split(",") if t.strip()]
        data["tags"] = [t[:10] for t in tags[:3]]

        if data["type"] == "网页":
            data["url"] = self.ed_url.text().strip()
            data["path"] = ""
            data["params"] = ""
        else:
            data["path"] = self.ed_path.text().strip()
            data["params"] = self.ed_params.text().strip()
            data["url"] = ""

        data["custom_interpreter_name"] = ""
        data["custom_interpreter_type"] = ""
        return data


class SettingsDialog(QDialog):
    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("设置")
        self.setObjectName("settingsDialog")

        ml = QVBoxLayout(self)
        ml.setContentsMargins(12, 12, 12, 12)
        ml.setSpacing(8)

        panel = QFrame(self)
        panel.setObjectName("settingsPanel")
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(8, 8, 8, 8)
        pl.setSpacing(6)

        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(10)

        self.chk_confirm = QCheckBox("退出时确认对话框")
        self.chk_confirm.setChecked(SETTINGS.get("confirm_exit", True))
        lay.addWidget(self.chk_confirm)

        lay.addWidget(QLabel("退出模式:"))
        self.cb_exit = QComboBox()
        self.cb_exit.addItems(["每次询问", "最小化到托盘", "直接退出"])
        cc = SETTINGS.get("exit_mode", "ask")
        if cc == "tray":
            self.cb_exit.setCurrentText("最小化到托盘")
        elif cc == "quit":
            self.cb_exit.setCurrentText("直接退出")
        else:
            self.cb_exit.setCurrentText("每次询问")
        lay.addWidget(self.cb_exit)

        lay.addWidget(QLabel("主题:"))
        self.cb_theme = QComboBox()
        self.cb_theme.addItems([
            "清爽", "深色", "浅色", "护眼", "粉色", "蓝色", "cyberpunk",
            "红蓝渐变", "钛银金属", "砂岩暖灰", "现代", "Pro Compact(苹果/小米)", "自定义背景"
        ])
        theme_map = {
            "dark": "深色",
            "light": "浅色",
            "eye_care": "护眼",
            "pink": "粉色",
            "blue": "蓝色",
            "cyberpunk": "cyberpunk",
            "red_blue_glass": "红蓝渐变",
            "Titanium_silver": "钛银金属",
            "sandstone_gray": "砂岩暖灰",
            "liquid_glass": "清爽",
            "modern": "现代",
            "pro_compact": "Pro Compact(苹果/小米)",
            "custom_image": "自定义背景",
        }
        self.cb_theme.setCurrentText(theme_map.get(SETTINGS.get("theme", "dark"), "深色"))
        lay.addWidget(self.cb_theme)

        self.chk_pro_enhanced = QCheckBox("Pro Compact 启用增强交互（面包屑/搜索范围）")
        self.chk_pro_enhanced.setChecked(bool(SETTINGS.get("pro_compact_enhanced", True)))
        lay.addWidget(self.chk_pro_enhanced)

        pro_search_row = QHBoxLayout()
        self.lb_pro_search_scope = QLabel("Pro Compact 搜索范围:")
        pro_search_row.addWidget(self.lb_pro_search_scope)
        self.cb_pro_search_scope = QComboBox()
        self.cb_pro_search_scope.addItems(["当前分类", "全部工具"])
        if str(SETTINGS.get("pro_compact_search_scope", "current")) == "all":
            self.cb_pro_search_scope.setCurrentText("全部工具")
        else:
            self.cb_pro_search_scope.setCurrentText("当前分类")
        pro_search_row.addWidget(self.cb_pro_search_scope)
        lay.addLayout(pro_search_row)

        self.bg_path_widget = QWidget()
        bg_lay = QHBoxLayout(self.bg_path_widget)
        bg_lay.setContentsMargins(0, 0, 0, 0)
        bg_lay.setSpacing(5)
        self.ed_bg_path = QLineEdit(SETTINGS.get("custom_bg_path", ""))
        bg_lay.addWidget(self.ed_bg_path)
        self.btn_browse_bg = QPushButton("浏览")
        self.btn_browse_bg.setObjectName("noHoverBtn")
        self.btn_browse_bg.clicked.connect(self.browse_bg_image)
        apply_button_icon(self.btn_browse_bg, "浏览")
        bg_lay.addWidget(self.btn_browse_bg)
        self.bg_path_widget.hide()
        lay.addWidget(self.bg_path_widget)

        self.cb_theme.currentTextChanged.connect(self.on_theme_changed)
        self.on_theme_changed(self.cb_theme.currentText())

        lay.addWidget(QLabel("工具卡片显示模式:"))
        self.cb_display_mode = QComboBox()
        self.cb_display_mode.addItems(["scroll(滚动)", "paged(分页)"])
        if SETTINGS.get("display_mode", "scroll") == "paged":
            self.cb_display_mode.setCurrentText("paged(分页)")
        else:
            self.cb_display_mode.setCurrentText("scroll(滚动)")
        lay.addWidget(self.cb_display_mode)

        lay.addWidget(QLabel("自定义Python路径(可选):"))
        hpy = QHBoxLayout()
        self.ed_py = QLineEdit(SETTINGS.get("python_path", ""))
        hpy.addWidget(self.ed_py)
        btn_browse_py = QPushButton("浏览")
        btn_browse_py.setObjectName("noHoverBtn")
        btn_browse_py.clicked.connect(self.browse_py)
        apply_button_icon(btn_browse_py, "浏览")
        hpy.addWidget(btn_browse_py)
        lay.addLayout(hpy)

        lay.addWidget(QLabel("Java 8路径(可选):"))
        hj8 = QHBoxLayout()
        self.ed_j8 = QLineEdit(SETTINGS.get("java8_path", "Java_path/Java_8_win/bin"))
        hj8.addWidget(self.ed_j8)
        btn_j8 = QPushButton("浏览")
        btn_j8.setObjectName("noHoverBtn")
        btn_j8.clicked.connect(lambda: self.browse_dir(self.ed_j8))
        apply_button_icon(btn_j8, "浏览")
        hj8.addWidget(btn_j8)
        lay.addLayout(hj8)

        lay.addWidget(QLabel("Java 11路径(可选):"))
        hj11 = QHBoxLayout()
        self.ed_j11 = QLineEdit(SETTINGS.get("java11_path", "Java_path/Java_11_win/bin"))
        hj11.addWidget(self.ed_j11)
        btn_j11 = QPushButton("浏览")
        btn_j11.setObjectName("noHoverBtn")
        btn_j11.clicked.connect(lambda: self.browse_dir(self.ed_j11))
        apply_button_icon(btn_j11, "浏览")
        hj11.addWidget(btn_j11)
        lay.addLayout(hj11)

        lay.addWidget(QLabel("命令行默认调用(程序内部打开CMD/PowerShell后生效):"))
        self.cli_python_list = list(SETTINGS.get("cli_python_interpreters", []) or [])
        self.cli_java_list = list(SETTINGS.get("cli_java_interpreters", []) or [])

        cli_py_row = QHBoxLayout()
        self.cb_cli_py = QComboBox()
        cli_py_row.addWidget(self.cb_cli_py)
        btn_add_cli_py = QPushButton("新增Python")
        btn_add_cli_py.setObjectName("noHoverBtn")
        btn_add_cli_py.clicked.connect(self.add_cli_python)
        apply_button_icon(btn_add_cli_py, "新增Python")
        cli_py_row.addWidget(btn_add_cli_py)
        btn_del_cli_py = QPushButton("删除Python")
        btn_del_cli_py.setObjectName("noHoverBtn")
        btn_del_cli_py.clicked.connect(self.del_cli_python)
        apply_button_icon(btn_del_cli_py, "删除Python")
        cli_py_row.addWidget(btn_del_cli_py)
        lay.addLayout(cli_py_row)

        cli_java_row = QHBoxLayout()
        self.cb_cli_java = QComboBox()
        cli_java_row.addWidget(self.cb_cli_java)
        btn_add_cli_java = QPushButton("新增Java")
        btn_add_cli_java.setObjectName("noHoverBtn")
        btn_add_cli_java.clicked.connect(self.add_cli_java)
        apply_button_icon(btn_add_cli_java, "新增Java")
        cli_java_row.addWidget(btn_add_cli_java)
        btn_del_cli_java = QPushButton("删除Java")
        btn_del_cli_java.setObjectName("noHoverBtn")
        btn_del_cli_java.clicked.connect(self.del_cli_java)
        apply_button_icon(btn_del_cli_java, "删除Java")
        cli_java_row.addWidget(btn_del_cli_java)
        lay.addLayout(cli_java_row)

        self.refresh_cli_defaults()

        hb_btn = QHBoxLayout()
        btn_reset = QPushButton("重置")
        btn_reset.setObjectName("noHoverBtn")
        btn_reset.clicked.connect(self.reset_settings)
        apply_button_icon(btn_reset, "重置")
        hb_btn.addWidget(btn_reset)
        hb_btn.addStretch()

        btn_save = QPushButton("保存")
        btn_save.setObjectName("noHoverBtn")
        btn_save.clicked.connect(self.save_settings)
        btn_cancel = QPushButton("取消")
        btn_cancel.setObjectName("noHoverBtn")
        btn_cancel.clicked.connect(self.reject)
        apply_button_icon(btn_save, "保存")
        apply_button_icon(btn_cancel, "取消")
        hb_btn.addWidget(btn_save)
        hb_btn.addWidget(btn_cancel)
        lay.addLayout(hb_btn)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.StyledPanel)
        scroll.setWidget(content)

        pl.addWidget(scroll)
        ml.addWidget(panel)

        self.setMinimumWidth(520)
        try:
            from PyQt6.QtWidgets import QApplication
            scr = QApplication.primaryScreen()
            if scr:
                ag = scr.availableGeometry()
                self.setMaximumSize(max(520, ag.width() - 120), max(460, ag.height() - 120))
                self.resize(min(680, ag.width() - 120), min(760, ag.height() - 120))
        except Exception:
            pass

    def browse_py(self):
        fi, _ = QFileDialog.getOpenFileName(self, "选择Python可执行文件")
        if fi:
            self.ed_py.setText(fi)

    def browse_dir(self, line_edit):
        d = QFileDialog.getExistingDirectory(self, "选择目录")
        if d:
            line_edit.setText(d)

    def browse_bg_image(self):
        fi, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)")
        if fi:
            ext = os.path.splitext(fi)[1].lower()
            if ext not in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
                QMessageBox.warning(self, "错误", "仅支持png, jpg, jpeg, bmp, gif图片格式")
                return
            self.ed_bg_path.setText(fi)

    def on_theme_changed(self, txt):
        if txt == "自定义背景":
            self.bg_path_widget.show()
        else:
            self.bg_path_widget.hide()
            self.ed_bg_path.setText("")
        is_pro = (txt == "Pro Compact(苹果/小米)")
        self.chk_pro_enhanced.setVisible(is_pro)
        self.lb_pro_search_scope.setVisible(is_pro)
        self.cb_pro_search_scope.setVisible(is_pro)

    def reset_settings(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("确认重置")
        msg.setText("确定要将所有设置重置为默认值吗？不会删除已添加的工具和分类。")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msg.exec() != QMessageBox.StandardButton.Yes:
            return

        self.chk_confirm.setChecked(DEFAULT_SETTINGS.get("confirm_exit", True))
        exit_mode = DEFAULT_SETTINGS.get("exit_mode", "ask")
        self.cb_exit.setCurrentText("最小化到托盘" if exit_mode == "tray" else ("直接退出" if exit_mode == "quit" else "每次询问"))

        theme_map = {
            "dark": "深色", "light": "浅色", "eye_care": "护眼", "pink": "粉色", "blue": "蓝色",
            "cyberpunk": "cyberpunk", "red_blue_glass": "红蓝渐变", "Titanium_silver": "钛银金属",
            "sandstone_gray": "砂岩暖灰", "liquid_glass": "清爽", "modern": "现代",
            "pro_compact": "Pro Compact(苹果/小米)", "custom_image": "自定义背景"
        }
        self.cb_theme.setCurrentText(theme_map.get(DEFAULT_SETTINGS.get("theme", "dark"), "深色"))
        self.cb_display_mode.setCurrentText("paged(分页)" if DEFAULT_SETTINGS.get("display_mode", "scroll") == "paged" else "scroll(滚动)")
        self.ed_py.setText(DEFAULT_SETTINGS.get("python_path", ""))
        self.ed_j8.setText(DEFAULT_SETTINGS.get("java8_path", ""))
        self.ed_j11.setText(DEFAULT_SETTINGS.get("java11_path", ""))
        self.ed_bg_path.setText("")
        self.chk_pro_enhanced.setChecked(bool(DEFAULT_SETTINGS.get("pro_compact_enhanced", True)))
        self.cb_pro_search_scope.setCurrentText("全部工具" if str(DEFAULT_SETTINGS.get("pro_compact_search_scope", "current")) == "all" else "当前分类")

        self.cli_python_list = list(DEFAULT_SETTINGS.get("cli_python_interpreters", []) or [])
        self.cli_java_list = list(DEFAULT_SETTINGS.get("cli_java_interpreters", []) or [])
        self.refresh_cli_defaults()

    def refresh_cli_defaults(self):
        self.cb_cli_py.clear()
        self.cb_cli_py.addItem("(不指定)", "")
        for item in self.cli_python_list:
            nm = str(item.get("name", "")).strip()
            p = str(item.get("path", "")).strip()
            if nm and p:
                self.cb_cli_py.addItem(f"{nm}  [{p}]", nm)

        self.cb_cli_java.clear()
        self.cb_cli_java.addItem("(不指定)", "")
        for item in self.cli_java_list:
            nm = str(item.get("name", "")).strip()
            p = str(item.get("path", "")).strip()
            if nm and p:
                self.cb_cli_java.addItem(f"{nm}  [{p}]", nm)

        want_py = str(SETTINGS.get("cli_default_python", "")).strip()
        idx_py = self.cb_cli_py.findData(want_py)
        if idx_py >= 0:
            self.cb_cli_py.setCurrentIndex(idx_py)

        want_java = str(SETTINGS.get("cli_default_java", "")).strip()
        idx_java = self.cb_cli_java.findData(want_java)
        if idx_java >= 0:
            self.cb_cli_java.setCurrentIndex(idx_java)

    def add_cli_python(self):
        name, ok = QInputDialog.getText(self, "名称", "Python解释器名称：")
        if not ok or not name.strip():
            return
        path, _ = QFileDialog.getOpenFileName(self, "选择Python可执行文件")
        if not path:
            return
        self.cli_python_list.append({"name": name.strip(), "path": path})
        self.refresh_cli_defaults()

    def del_cli_python(self):
        key = str(self.cb_cli_py.currentData() or "").strip()
        if not key:
            return
        self.cli_python_list = [x for x in self.cli_python_list if str(x.get("name", "")).strip() != key]
        self.refresh_cli_defaults()

    def add_cli_java(self):
        name, ok = QInputDialog.getText(self, "名称", "Java解释器名称：")
        if not ok or not name.strip():
            return
        path = QFileDialog.getExistingDirectory(self, "选择Java目录")
        if not path:
            return
        self.cli_java_list.append({"name": name.strip(), "path": path})
        self.refresh_cli_defaults()

    def del_cli_java(self):
        key = str(self.cb_cli_java.currentData() or "").strip()
        if not key:
            return
        self.cli_java_list = [x for x in self.cli_java_list if str(x.get("name", "")).strip() != key]
        self.refresh_cli_defaults()

    def save_settings(self):
        exit_map = {"每次询问": "ask", "最小化到托盘": "tray", "直接退出": "quit"}
        ex = exit_map.get(self.cb_exit.currentText(), "ask")

        theme_map = {
            "清爽": "liquid_glass", "深色": "dark", "浅色": "light", "护眼": "eye_care", "粉色": "pink",
            "蓝色": "blue", "cyberpunk": "cyberpunk", "红蓝渐变": "red_blue_glass", "钛银金属": "Titanium_silver",
            "砂岩暖灰": "sandstone_gray", "现代": "modern", "Pro Compact(苹果/小米)": "pro_compact", "自定义背景": "custom_image"
        }
        theme_key = theme_map.get(self.cb_theme.currentText(), "dark")

        new_s = dict(SETTINGS)
        new_s["confirm_exit"] = self.chk_confirm.isChecked()
        new_s["exit_mode"] = ex
        new_s["python_path"] = self.ed_py.text().strip()
        new_s["java8_path"] = self.ed_j8.text().strip()
        new_s["java11_path"] = self.ed_j11.text().strip()
        new_s["display_mode"] = "paged" if self.cb_display_mode.currentText() == "paged(分页)" else "scroll"
        new_s["pro_compact_enhanced"] = bool(self.chk_pro_enhanced.isChecked())
        new_s["pro_compact_search_scope"] = "all" if self.cb_pro_search_scope.currentText() == "全部工具" else "current"

        new_s["cli_python_interpreters"] = list(self.cli_python_list)
        new_s["cli_java_interpreters"] = list(self.cli_java_list)
        new_s["cli_default_python"] = str(self.cb_cli_py.currentData() or "").strip()
        new_s["cli_default_java"] = str(self.cb_cli_java.currentData() or "").strip()

        if theme_key == "custom_image":
            bg_path = self.ed_bg_path.text().strip()
            ext = os.path.splitext(bg_path)[1].lower()
            if not bg_path or not os.path.isfile(bg_path):
                QMessageBox.warning(self, "错误", "必须选择一张图片作为自定义背景")
                return
            if ext not in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
                QMessageBox.warning(self, "错误", "仅支持png, jpg, jpeg, bmp, gif图片格式")
                return
            new_s["custom_bg_path"] = bg_path
        else:
            new_s["custom_bg_path"] = ""

        new_s["theme"] = theme_key

        if save_settings(new_s):
            self.settings_changed.emit(new_s)
        self.accept()
