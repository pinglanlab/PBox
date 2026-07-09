# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.12.4 (tags/v3.12.4:8e8a4ba, Jun  6 2024, 19:30:16) [MSC v.1940 64 bit (AMD64)]
# Embedded file name: d:\th21\widgets.py
# Compiled at: 2026-01-04 11:04:43
# Size of source mod 2**32: 40073 bytes
import sys, os, subprocess
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QScrollArea, QWidget, QToolButton, QMenu, QDialog, QFileDialog, QMessageBox, QInputDialog, QCheckBox, QGridLayout, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect, QSize, QMimeData, QEvent, QSettings
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QDragEnterEvent, QDropEvent
from config import SETTINGS, TOOL_TYPES, THEME, save_settings, load_settings, save_categories, save_tools, DEFAULT_CATEGORIES, add_custom_interpreter, del_custom_interpreter
from utils import fuzzy_search, is_tool_favorited, add_favorite_tool, remove_favorite_tool, get_favorite_tools, get_recent_tools, SearchWorker, tool_has_tag, add_tag_to_tool, remove_tag_from_tool, edit_tags_for_tool, auto_group_tools
from core.env_manager import EnvManager
FORBIDDEN_CATEGORIES = [
 "", "最近启动", "我的收藏", "全部工具"]
FORBIDDEN_HOTKEYS = {
 'ctrl+c',  'ctrl+v',  'ctrl+x',  'ctrl+z',  'ctrl+y',  'ctrl+f'}
if sys.platform.startswith("win"):
    CREATE_NEW_CONSOLE = 16
else:
    CREATE_NEW_CONSOLE = 0

class TitleBar(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("titleBar")
        self.init_ui()

    def init_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)
        self.title_label = QLabel("天狐渗透工具箱-社区版V2.0纪念版", self)
        self.title_label.setStyleSheet("font-size:16px; font-weight:bold; padding-left:10px;")
        lay.addWidget(self.title_label)
        self.team_info = QLabel("ONE-FOX安全团队   By.狐狸   官网: https://www.one-fox.cn/", self)
        self.team_info.setStyleSheet("font-size:14px; padding-right:20px;")
        lay.addWidget(self.team_info)
        lay.addStretch()
        self.btn_min = QPushButton("🗕")
        self.btn_min.setObjectName("titleButton")
        self.btn_min.clicked.connect(self.parent.showMinimized)
        self.btn_max = QPushButton("🗖")
        self.btn_max.setObjectName("titleButton")
        self.btn_max.clicked.connect(self.toggle_maximize)
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("titleButton")
        self.btn_close.clicked.connect(self.handle_close)
        lay.addWidget(self.btn_min)
        lay.addWidget(self.btn_max)
        lay.addWidget(self.btn_close)
        self.setFixedHeight(60)
        self.dragging = False
        self.drag_position = None

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.btn_max.setText("🗖")
        else:
            self.parent.showMaximized()
            self.btn_max.setText("🗗")

    def handle_close(self):
        self.parent.close()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = e.globalPosition().toPoint() - self.parent.pos()

    def mouseMoveEvent(self, e):
        if self.dragging:
            if not self.parent.isMaximized():
                self.parent.move(e.globalPosition().toPoint() - self.drag_position)

    def mouseReleaseEvent(self, e):
        self.dragging = False

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.toggle_maximize()


class SearchBar(QFrame):
    search_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.emit_search)

    def init_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        lab_icon = QLabel("🔍", self)
        lay.addWidget(lab_icon)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索工具...")
        self.search_input.textChanged.connect(self.on_text_changed)
        lay.addWidget(self.search_input)

    def on_text_changed(self, text):
        self.search_timer.stop()
        self.search_timer.start(300)

    def emit_search(self):
        self.search_changed.emit(self.search_input.text())


class CategoryButton(QPushButton):

    def __init__(self, text, parent=None, is_user_category=True, category_key=None):
        super().__init__(text, parent)
        self.setObjectName("categoryBtn")
        self.setCheckable(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)
        self.is_user_category = is_user_category
        self.category_key = category_key
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def show_menu(self, pos):
        menu = QMenu(self)
        act_add = QAction("新建分类", menu)
        act_add.triggered.connect(self.add_cat)
        menu.addAction(act_add)
        if self.category_key not in ('我的收藏', '最近启动'):
            if self.category_key != "":
                menu.addSeparator()
                act_rename = QAction("重命名", menu)
                act_del = QAction("删除", menu)
                act_up = QAction("上移", menu)
                act_down = QAction("下移", menu)
                menu.addAction(act_rename)
                menu.addAction(act_del)
                menu.addSeparator()
                menu.addAction(act_up)
                menu.addAction(act_down)
                act_rename.triggered.connect(self.rename_cat)
                act_del.triggered.connect(self.del_cat)
                act_up.triggered.connect(self.move_up)
                act_down.triggered.connect(self.move_down)
        menu.exec(self.mapToGlobal(pos))

    def add_cat(self):
        p = self.parent()
        while p:
            if hasattr(p, "category_added"):
                p.category_added.emit("")
            else:
                p = p.parent()

    def rename_cat(self):
        raw_text = self.text().replace("📁 ", "").replace("🗒 ", "")
        idx = raw_text.rfind("(")
        if idx != -1:
            raw_text = raw_text[None[:idx]].strip()
        diag = QInputDialog(self)
        diag.setWindowTitle("重命名分类")
        diag.setLabelText("新的分类名称:")
        diag.setTextValue(raw_text.strip())
        if diag.exec() == QDialog.DialogCode.Accepted:
            newval = diag.textValue().strip()
            if newval:
                if hasattr(self.parent(), "category_renamed"):
                    self.parent().category_renamed.emit(raw_text, newval)

    def del_cat(self):
        raw_text = self.text().replace("📁 ", "").replace("🗒 ", "")
        idx = raw_text.rfind("(")
        if idx != -1:
            raw_text = raw_text[None[:idx]].strip()
        if hasattr(self.parent(), "category_deleted"):
            self.parent().category_deleted.emit(raw_text)

    def move_up(self):
        if hasattr(self.parent(), "category_move"):
            self.parent().category_move.emit(self.category_key, -1)

    def move_down(self):
        if hasattr(self.parent(), "category_move"):
            self.parent().category_move.emit(self.category_key, 1)


class CategoryPanel(QFrame):
    category_selected = pyqtSignal(str)
    category_renamed = pyqtSignal(str, str)
    category_deleted = pyqtSignal(str)
    category_added = pyqtSignal(str)
    category_move = pyqtSignal(str, int)

    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.current_button = None
        self.buttons = {}
        self.extra_btns = {}
        self.init_ui()

    def init_ui(self):
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_panel_menu)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.container = QWidget()
        self.container.setObjectName("categoryContainer")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(10)
        all_btn = CategoryButton("🗒 全部工具", self, is_user_category=False, category_key="")
        all_btn.clicked.connect(lambda: self.on_click(all_btn, ""))
        all_btn.setChecked(True)
        self.buttons[""] = all_btn
        self.container_layout.addWidget(self._wrap_cat_row(all_btn))
        self.update_categories(self.categories)
        self.container_layout.addStretch()
        self.scroll.setWidget(self.container)
        lay.addWidget(self.scroll)
        self.setLayout(lay)

    def show_panel_menu(self, pos):
        menu = QMenu(self)
        act_add = QAction("新建分类", menu)
        act_add.triggered.connect(lambda: self.category_added.emit(""))
        menu.addAction(act_add)
        menu.exec(self.mapToGlobal(pos))

    def _wrap_cat_row(self, btn, extra_btn=None):
        row = QWidget()
        hl = QHBoxLayout(row)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(0)
        hl.addWidget(btn)
        if extra_btn:
            hl.addStretch()
            hl.addWidget(extra_btn)
        return row

    def update_categories(self, categories, category_counts=None):
        if category_counts is None:
            category_counts = {}
        else:
            current_cat = ""
            if hasattr(self, "current_button"):
                if self.current_button:
                    raw_text = self.current_button.text().replace("📁 ", "").replace("🗒 ", "")
                    idx = raw_text.rfind("(")
                    if idx != -1:
                        raw_text = raw_text[None[:idx]].strip()
                    elif raw_text == "全部工具":
                        current_cat = ""
                    else:
                        current_cat = raw_text
            for c, btn in list(self.buttons.items()):
                if c != "":
                    widget = btn.parentWidget()
                    self.container_layout.removeWidget(widget)
                    widget.deleteLater()
                    del self.buttons[c]
            else:
                self.extra_btns.clear()
                ordered = []
                if "最近启动" in categories:
                    ordered.append("最近启动")
                if "我的收藏" in categories:
                    ordered.append("我的收藏")
                ordered += [cat for cat in categories if cat not in ('我的收藏', '最近启动') if cat]

            for cat in ordered:
                cc = category_counts.get(cat, 0)
                text = f"📁 {cat}"
                if cc > 0:
                    text += f" ({cc})"
                is_user_cat = cat not in DEFAULT_CATEGORIES or cat in ('我的收藏', '最近启动')
                cb = CategoryButton(text,
                  self, is_user_category=is_user_cat, category_key=cat)
                cb.clicked.connect(lambda _, b=cb, n=cat: self.on_click(b, n))
                self.buttons[cat] = cb
                self.container_layout.insertWidget(self.container_layout.count() - 1, self._wrap_cat_row(cb))
            else:
                all_count = category_counts.get("", None)
                if all_count is not None:
                    self.buttons[""].setText(f"🗒 全部工具 ({all_count})")
                else:
                    self.buttons[""].setText("🗒 全部工具")
                if current_cat in self.buttons:
                    self.on_click(self.buttons[current_cat], current_cat)
                else:
                    self.on_click(self.buttons[""], "")

    def on_click(self, btn, cat):
        for b in self.buttons.values():
            if b != btn:
                b.setChecked(False)
            btn.setChecked(True)
            self.current_button = btn
            self.category_selected.emit(cat)


class ToolDialog(QDialog):

    def __init__(self, categories, tool_data=None, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.tool_data = tool_data
        self.shortcut_key = ""
        self.custom_interpreters = SETTINGS.get("custom_interpreters", [])
        self.init_ui()
        self.setModal(True)

    def init_ui(self):
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)
        self.title_bar = TitleBar(self)
        if not self.tool_data:
            self.title_bar.title_label.setText("添加工具")
        else:
            self.title_bar.title_label.setText("编辑工具")
        main_lay.addWidget(self.title_bar)
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setSpacing(10)
        lay.setContentsMargins(10, 10, 10, 10)
        lb_name = QLabel("工具名称:")
        lay.addWidget(lb_name)
        self.ed_name = QLineEdit()
        if self.tool_data:
            self.ed_name.setText(self.tool_data["name"])
        lay.addWidget(self.ed_name)
        lb_type = QLabel("工具类型:")
        lay.addWidget(lb_type)
        self.cb_type = QComboBox()
        self.refresh_type_choices()
        if self.tool_data:
            self.cb_type.setCurrentText(self.tool_data["type"])
        self.cb_type.currentTextChanged.connect(self.on_type_changed)
        lay.addWidget(self.cb_type)
        self.custom_interp_widget = QWidget()
        custom_interp_lay = QVBoxLayout(self.custom_interp_widget)
        custom_interp_lay.setContentsMargins(0, 0, 0, 0)
        custom_interp_lay.setSpacing(3)
        self.lb_custom_interpreter = QLabel("")
        custom_interp_lay.addWidget(self.lb_custom_interpreter)
        h_interp = QHBoxLayout()
        self.cb_custom_interpreter = QComboBox()
        h_interp.addWidget(self.cb_custom_interpreter)
        self.btn_add_custom_interpreter = QPushButton("新增自定义解释器")
        self.btn_add_custom_interpreter.clicked.connect(self.add_custom_interpreter_clicked)
        h_interp.addWidget(self.btn_add_custom_interpreter)
        self.btn_del_custom_interpreter = QPushButton("删除选中解释器")
        self.btn_del_custom_interpreter.clicked.connect(self.del_custom_interpreter_clicked)
        h_interp.addWidget(self.btn_del_custom_interpreter)
        custom_interp_lay.addLayout(h_interp)
        self.custom_interp_widget.hide()
        lay.addWidget(self.custom_interp_widget)
        lb_path = QLabel("工具路径:")
        lay.addWidget(lb_path)
        hpath = QHBoxLayout()
        self.ed_path = QLineEdit()
        if self.tool_data:
            self.ed_path.setText(self.tool_data.get("path", ""))
        hpath.addWidget(self.ed_path)
        self.btn_browse = QPushButton("浏览")
        self.btn_browse.clicked.connect(self.browse_file)
        hpath.addWidget(self.btn_browse)
        lay.addLayout(hpath)
        self.lb_url = QLabel("网页地址:")
        lay.addWidget(self.lb_url)
        self.ed_url = QLineEdit()
        if self.tool_data:
            self.ed_url.setText(self.tool_data.get("url", ""))
        lay.addWidget(self.ed_url)
        self.lb_url.hide()
        self.ed_url.hide()
        lb_cat = QLabel("工具分类:")
        lay.addWidget(lb_cat)
        self.cb_cat = QComboBox()
        self.cb_cat.setEditable(True)
        filtered_categories = [cat for cat in self.categories if cat not in ('最近启动',
                                                                             '我的收藏')]
        self.cb_cat.addItems(sorted(filtered_categories))
        if self.tool_data:
            self.cb_cat.setCurrentText(self.tool_data["category"])
        lay.addWidget(self.cb_cat)
        lb_params = QLabel("启动参数:")
        lay.addWidget(lb_params)
        self.ed_params = QLineEdit()
        if self.tool_data:
            self.ed_params.setText(self.tool_data.get("params", ""))
        lay.addWidget(self.ed_params)
        lb_desc = QLabel("工具描述:")
        lay.addWidget(lb_desc)
        self.ed_desc = QLineEdit()
        if self.tool_data:
            self.ed_desc.setText(self.tool_data.get("description", ""))
        lay.addWidget(self.ed_desc)
        lb_tags = QLabel("标签 (最多3个, 每个≤10字符, 英文逗号分隔):")
        lay.addWidget(lb_tags)
        self.ed_tags = QLineEdit()
        self.ed_tags.setPlaceholderText("如：内网, 提权, webshell")
        if self.tool_data:
            if self.tool_data.get("tags"):
                self.ed_tags.setText(", ".join(self.tool_data.get("tags", [])[None[:3]]))
        lay.addWidget(self.ed_tags)
        lab_tip = QLabel("多个标签请用英文逗号 , 分隔；每个标签最多10字符，最多3个标签")
        lab_tip.setStyleSheet("color: #888; font-size: 11px; padding-left:3px;")
        lay.addWidget(lab_tip)
        lb_weight = QLabel("显示权重(0-10):")
        lay.addWidget(lb_weight)
        self.cb_weight = QComboBox()
        self.cb_weight.addItems([str(i) for i in range(11)])
        if self.tool_data:
            self.cb_weight.setCurrentText(str(self.tool_data.get("weight", 0)))
        lay.addWidget(self.cb_weight)
        lb_short = QLabel("快捷键:")
        lay.addWidget(lb_short)
        hshort = QHBoxLayout()
        self.ed_shortcut = QLineEdit()
        self.ed_shortcut.setPlaceholderText("按下组合键或手动输入")
        if self.tool_data:
            if hasattr(self.parent(), "tool_shortcuts"):
                exist = self.parent().tool_shortcuts.get(self.tool_data["name"], "")
                if exist:
                    self.ed_shortcut.setText(exist)
                    self.shortcut_key = exist
        btn_clear = QPushButton("清除")
        btn_clear.clicked.connect(self.clear_short)
        hshort.addWidget(self.ed_shortcut)
        hshort.addWidget(btn_clear)
        lay.addLayout(hshort)
        hbtn = QHBoxLayout()
        self.btn_save = QPushButton("保存")
        self.btn_save.clicked.connect(self._on_save_clicked)
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        hbtn.addWidget(self.btn_save)
        hbtn.addWidget(self.btn_cancel)
        lay.addLayout(hbtn)
        main_lay.addWidget(content)
        self.setMinimumWidth(500)
        self.on_type_changed(self.cb_type.currentText())

    def refresh_type_choices(self):
        self.cb_type.clear()
        basic_types = list(TOOL_TYPES)
        py_customs = [c for c in self.custom_interpreters if c["type"] == "python"]
        java_customs = [c for c in self.custom_interpreters if c["type"] == "java"]
        for c in py_customs:
            basic_types.append(f'Python({c["name"]})')
        else:
            for c in java_customs:
                basic_types.append(f'Java({c["name"]})')
            else:
                self.cb_type.addItems(basic_types)

    def update_custom_interpreter_box(self, interp_type):
        customs = [c for c in self.custom_interpreters if c["type"] == interp_type]
        self.cb_custom_interpreter.clear()
        for c in customs:
            self.cb_custom_interpreter.addItem(f'{c["name"]}  [{c["path"]}]', c)
        else:
            if interp_type == "python":
                self.lb_custom_interpreter.setText("选择自定义Python解释器:")
            else:
                self.lb_custom_interpreter.setText("选择自定义Java路径:")

    def on_type_changed(self, t):
        is_web = t == "网页"
        self.lb_url.setVisible(is_web)
        self.ed_url.setVisible(is_web)
        self.ed_path.setVisible(not is_web)
        self.btn_browse.setVisible(not is_web)
        self.ed_params.setVisible(not is_web)
        show_custom = False
        interp_type = None
        if t.startswith("Python("):
            show_custom = True
            interp_type = "python"
        else:
            if t.startswith("Java("):
                show_custom = True
                interp_type = "java"
            elif show_custom:
                self.update_custom_interpreter_box(interp_type)
                self.custom_interp_widget.show()
            else:
                self.custom_interp_widget.hide()

    def add_custom_interpreter_clicked(self):
        interp_types_map = {'Python解释器':"python", 
         'Java路径':"java"}
        items = list(interp_types_map.keys())
        interp_type, ok1 = QInputDialog.getItem(self, "选择类型", "解释器类型：", items, 0, False)
        if not ok1:
            return
        else:
            name, ok2 = QInputDialog.getText(self, "名称", "自定义名称：")
            if ok2:
                return name.strip() or None
            elif interp_types_map[interp_type] == "python":
                path, ok3 = QFileDialog.getOpenFileName(self, "选择Python可执行文件")
            else:
                if interp_types_map[interp_type] == "java":
                    path = QFileDialog.getExistingDirectory(self, "选择Java目录")
                    ok3 = bool(path)
                else:
                    path = ""
                    ok3 = False
            return ok3 and path or None
        if interp_types_map[interp_type] == "java":
            if not os.path.isdir(path):
                QMessageBox.warning(self, "错误", "Java路径请选择目录！")
                return
        for ci in self.custom_interpreters:
            if ci["name"] == name:
                if ci["type"] == interp_types_map[interp_type]:
                    QMessageBox.warning(self, "错误", "已存在同名自定义解释器")
                    return                     return None
                add_custom_interpreter(SETTINGS, name, path, interp_types_map[interp_type])
                save_settings(SETTINGS)
                self.custom_interpreters = SETTINGS.get("custom_interpreters", [])
                self.refresh_type_choices()
                QMessageBox.information(self, "成功", "新增自定义解释器成功！")
                self.on_type_changed(self.cb_type.currentText())

    def del_custom_interpreter_clicked(self):
        idx = self.cb_custom_interpreter.currentIndex()
        if idx < 0:
            QMessageBox.warning(self, "错误", "没有选中要删除的自定义解释器！")
            return
        else:
            ci = self.cb_custom_interpreter.itemData(idx)
            return ci or None
        if del_custom_interpreter(SETTINGS, ci["name"], ci["type"]):
            save_settings(SETTINGS)
            self.custom_interpreters = SETTINGS.get("custom_interpreters", [])
            self.refresh_type_choices()
            QMessageBox.information(self, "成功", "已删除自定义解释器")
            self.on_type_changed(self.cb_type.currentText())

    def browse_file(self):
        fi, _ = QFileDialog.getOpenFileName(self, "选择工具文件")
        if fi:
            self.ed_path.setText(fi)

    def clear_short(self):
        self.ed_shortcut.clear()
        self.shortcut_key = ""
        if self.tool_data:
            if hasattr(self.parent(), "tool_shortcuts"):
                nm = self.tool_data["name"]
                if nm in self.parent().tool_shortcuts:
                    del self.parent().tool_shortcuts[nm]
                    sets = QSettings("config/shortcuts.ini", QSettings.Format.IniFormat)
                    sets.remove(f"shortcuts/{nm}")
                    sets.sync()
                    self.parent().init_shortcuts()

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
            if self.tool_data:
                sets = QSettings("config/shortcuts.ini", QSettings.Format.IniFormat)
                sets.setValue(f'shortcuts/{self.tool_data["name"]}', final)
                sets.sync()
                if hasattr(self.parent(), "tool_shortcuts"):
                    self.parent().tool_shortcuts[self.tool_data["name"]] = final
                    self.parent().init_shortcuts()
        else:
            super().keyPressEvent(e)

    def check_conflict(self, newval):
        if not hasattr(self.parent(), "tool_shortcuts"):
            return False
        curr = self.tool_data["name"] if self.tool_data else None
        for nm, val in self.parent().tool_shortcuts.items():
            if val == newval and nm != curr:
                return                 return True
            return False

    def _on_save_clicked(self):
        tags_str = self.ed_tags.text().strip()
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        if len(tags) > 3:
            QMessageBox.warning(self, "标签数量超限", "最多只能填写3个标签！")
            return
        long_tags = [t for t in tags if len(t) > 10]
        if long_tags:
            QMessageBox.warning(self, "标签超长", "每个标签最多10个字符！")
            return
        val = self.ed_shortcut.text().strip()
        forbidden = val.lower().replace(" ", "")
        if forbidden:
            if forbidden in FORBIDDEN_HOTKEYS:
                QMessageBox.warning(self, "快捷键冲突", "此快捷键为系统常用快捷键，禁止使用")
                return
        if val:
            if self.check_conflict(val):
                QMessageBox.warning(self, "快捷键冲突", "此快捷键已被其它工具占用")
                return
        self.accept()

    def get_tool_data(self):
        data = {}
        data["name"] = self.ed_name.text().strip()
        data["category"] = self.cb_cat.currentText().strip()
        data["type"] = self.cb_type.currentText()
        data["description"] = self.ed_desc.text().strip()
        data["weight"] = int(self.cb_weight.currentText())
        tags_str = self.ed_tags.text().strip()
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        tags = tags[None[:3]]
        tags = [t[None[:10]] for t in tags]
        data["tags"] = tags
        if data["type"] == "网页":
            data["url"] = self.ed_url.text().strip()
            data["path"] = ""
            data["params"] = ""
        else:
            data["path"] = self.ed_path.text().strip()
            data["params"] = self.ed_params.text().strip()
            data["url"] = ""
        if data["type"].startswith("Python("):
            data["custom_interpreter_name"] = data["type"][7[:-1]]
            data["custom_interpreter_type"] = "python"
        else:
            if data["type"].startswith("Java("):
                data["custom_interpreter_name"] = data["type"][5[:-1]]
                data["custom_interpreter_type"] = "java"
            else:
                data["custom_interpreter_name"] = ""
                data["custom_interpreter_type"] = ""
        if hasattr(self.parent(), "tool_shortcuts"):
            if self.tool_data and self.tool_data["name"] in self.parent().tool_shortcuts:
                if not self.shortcut_key or self.tool_data["name"] != data["name"]:
                    if self.tool_data["name"] in self.parent().tool_shortcuts:
                        del self.parent().tool_shortcuts[self.tool_data["name"]]
        else:
            self.parent().init_shortcuts()
        if self.shortcut_key:
            self.parent().tool_shortcuts[data["name"]] = self.shortcut_key
        return data


class SettingsDialog(QDialog):
    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        ml = QVBoxLayout(self)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)
        self.title_bar = TitleBar(self)
        self.title_bar.title_label.setText("设置")
        ml.addWidget(self.title_bar)
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setSpacing(10)
        lay.setContentsMargins(10, 10, 10, 10)
        self.chk_confirm = QCheckBox("退出时确认对话框")
        self.chk_confirm.setChecked(SETTINGS.get("confirm_exit", True))
        lay.addWidget(self.chk_confirm)
        lb_exit = QLabel("退出模式:")
        lay.addWidget(lb_exit)
        self.cb_exit = QComboBox()
        self.cb_exit.addItems(["每次询问", "最小化到托盘", "直接退出"])
        cc = SETTINGS.get("exit_mode", "ask")
        if cc == "tray":
            self.cb_exit.setCurrentText("最小化到托盘")
        else:
            if cc == "quit":
                self.cb_exit.setCurrentText("直接退出")
            else:
                self.cb_exit.setCurrentText("每次询问")
        lay.addWidget(self.cb_exit)
        lb_theme = QLabel("主题:")
        lay.addWidget(lb_theme)
        self.cb_theme = QComboBox()
        self.cb_theme.addItems([
         '深色',  '浅色',  '护眼',  '粉色',  '蓝色',  'cyberpunk', 
         '红蓝渐变',  '钛银金属',  '砂岩暖灰',  '自定义背景'])
        theme_map = {
         'dark': '"深色"', 
         'light': '"浅色"', 
         'eye_care': '"护眼"', 
         'pink': '"粉色"', 
         'blue': '"蓝色"', 
         'cyberpunk': '"cyberpunk"', 
         'red_blue_glass': '"红蓝渐变"', 
         'Titanium_silver': '"钛银金属"', 
         'sandstone_gray': '"砂岩暖灰"', 
         'custom_image': '"自定义背景"'}
        now_th = SETTINGS.get("theme", "dark")
        if now_th in theme_map:
            self.cb_theme.setCurrentText(theme_map[now_th])
        else:
            self.cb_theme.setCurrentText("深色")
        lay.addWidget(self.cb_theme)
        self.bg_path_widget = QWidget()
        bg_lay = QHBoxLayout(self.bg_path_widget)
        bg_lay.setContentsMargins(0, 0, 0, 0)
        bg_lay.setSpacing(5)
        self.ed_bg_path = QLineEdit(SETTINGS.get("custom_bg_path", ""))
        bg_lay.addWidget(self.ed_bg_path)
        self.btn_browse_bg = QPushButton("浏览")
        self.btn_browse_bg.clicked.connect(self.browse_bg_image)
        bg_lay.addWidget(self.btn_browse_bg)
        self.bg_path_widget.hide()
        lay.addWidget(self.bg_path_widget)
        self.cb_theme.currentTextChanged.connect(self.on_theme_changed)
        self.on_theme_changed(self.cb_theme.currentText())
        lb_mode = QLabel("工具卡片显示模式:")
        lay.addWidget(lb_mode)
        self.cb_display_mode = QComboBox()
        self.cb_display_mode.addItems(["scroll(滚动)", "paged(分页)"])
        if SETTINGS.get("display_mode", "scroll") == "paged":
            self.cb_display_mode.setCurrentText("paged(分页)")
        else:
            self.cb_display_mode.setCurrentText("scroll(滚动)")
        lay.addWidget(self.cb_display_mode)
        lb_py = QLabel("自定义Python路径(可选):")
        lay.addWidget(lb_py)
        hpy = QHBoxLayout()
        self.ed_py = QLineEdit(SETTINGS.get("python_path", ""))
        hpy.addWidget(self.ed_py)
        btn_browse_py = QPushButton("浏览")
        btn_browse_py.clicked.connect(self.browse_py)
        hpy.addWidget(btn_browse_py)
        lay.addLayout(hpy)
        lb_j8 = QLabel("Java 8路径(可选):")
        lay.addWidget(lb_j8)
        hj8 = QHBoxLayout()
        self.ed_j8 = QLineEdit(SETTINGS.get("java8_path", "Java_path/Java_8_win/bin"))
        hj8.addWidget(self.ed_j8)
        btn_j8 = QPushButton("浏览")
        btn_j8.clicked.connect(lambda: self.browse_dir(self.ed_j8))
        hj8.addWidget(btn_j8)
        lay.addLayout(hj8)
        lb_j11 = QLabel("Java 11路径(可选):")
        lay.addWidget(lb_j11)
        hj11 = QHBoxLayout()
        self.ed_j11 = QLineEdit(SETTINGS.get("java11_path", "Java_path/Java_11_win/bin"))
        hj11.addWidget(self.ed_j11)
        btn_j11 = QPushButton("浏览")
        btn_j11.clicked.connect(lambda: self.browse_dir(self.ed_j11))
        hj11.addWidget(btn_j11)
        lay.addLayout(hj11)
        hb_btn = QHBoxLayout()
        btn_reset = QPushButton("重置")
        btn_reset.clicked.connect(self.reset_settings)
        hb_btn.addWidget(btn_reset)
        hb_btn.addStretch()
        btn_save = QPushButton("保存")
        btn_save.clicked.connect(self.save_settings)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        hb_btn.addWidget(btn_save)
        hb_btn.addWidget(btn_cancel)
        lay.addLayout(hb_btn)
        ml.addWidget(content)
        self.setLayout(ml)
        self.setMinimumWidth(520)

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
            if ext not in ('.png', '.jpg', '.jpeg', '.bmp', '.gif'):
                QMessageBox.warning(self, "错误", "仅支持png, jpg, jpeg, bmp, gif图片格式！")
                return
            self.ed_bg_path.setText(fi)

    def on_theme_changed(self, txt):
        if txt == "自定义背景":
            self.bg_path_widget.show()
        else:
            self.bg_path_widget.hide()
            self.ed_bg_path.setText("")

    def reset_settings(self):
        from config import DEFAULT_SETTINGS
        msg = QMessageBox(self)
        msg.setWindowTitle("确认重置")
        msg.setText("确定要将所有设置重置为默认值吗？不会删除已添加的工具和分类。")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        r = msg.exec()
        if r == QMessageBox.StandardButton.Yes:
            self.chk_confirm.setChecked(DEFAULT_SETTINGS["confirm_exit"])
            if DEFAULT_SETTINGS["exit_mode"] == "tray":
                self.cb_exit.setCurrentText("最小化到托盘")
            else:
                if DEFAULT_SETTINGS["exit_mode"] == "quit":
                    self.cb_exit.setCurrentText("直接退出")
                else:
                    self.cb_exit.setCurrentText("每次询问")
            theme_map = {'dark': '"深色"', 
             'light': '"浅色"', 
             'eye_care': '"护眼"', 
             'pink': '"粉色"', 
             'blue': '"蓝色"', 
             'cyberpunk': '"cyberpunk"', 
             'red_blue_glass': '"红蓝渐变"', 
             'Titanium_silver': '"钛银金属"', 
             'sandstone_gray': '"砂岩暖灰"', 
             'custom_image': '"自定义背景"'}
            df_theme = theme_map.get(DEFAULT_SETTINGS["theme"], "深色")
            self.cb_theme.setCurrentText(df_theme)
            if DEFAULT_SETTINGS["display_mode"] == "paged":
                self.cb_display_mode.setCurrentText("paged(分页)")
            else:
                self.cb_display_mode.setCurrentText("scroll(滚动)")
            self.ed_py.setText(DEFAULT_SETTINGS["python_path"])
            self.ed_j8.setText(DEFAULT_SETTINGS["java8_path"])
            self.ed_j11.setText(DEFAULT_SETTINGS["java11_path"])
            self.ed_bg_path.setText("")

    def save_settings(self):
        from config import SETTINGS, save_settings
        exit_map = {'每次询问':"ask", 
         '最小化到托盘':"tray", 
         '直接退出':"quit"}
        ex = exit_map.get(self.cb_exit.currentText(), "ask")
        theme_map = {
         '深色': '"dark"', 
         '浅色': '"light"', 
         '护眼': '"eye_care"', 
         '粉色': '"pink"', 
         '蓝色': '"blue"', 
         'cyberpunk': '"cyberpunk"', 
         '红蓝渐变': '"red_blue_glass"', 
         '钛银金属': '"Titanium_silver"', 
         '砂岩暖灰': '"sandstone_gray"', 
         '自定义背景': '"custom_image"'}
        themetxt = self.cb_theme.currentText()
        theme_key = theme_map.get(themetxt, "dark")
        dsp = "scroll"
        if self.cb_display_mode.currentText() == "paged(分页)":
            dsp = "paged"
        else:
            new_s = dict(SETTINGS)
            new_s["confirm_exit"] = self.chk_confirm.isChecked()
            new_s["exit_mode"] = ex
            new_s["python_path"] = self.ed_py.text().strip()
            new_s["java8_path"] = self.ed_j8.text().strip()
            new_s["java11_path"] = self.ed_j11.text().strip()
            new_s["display_mode"] = dsp
            if theme_key == "custom_image":
                bg_path = self.ed_bg_path.text().strip()
                ext = os.path.splitext(bg_path)[1].lower()
                if bg_path:
                    if not os.path.isfile(bg_path):
                        QMessageBox.warning(self, "错误", "必须选择一张图片作为自定义背景！")
                        return
                    if ext not in ('.png', '.jpg', '.jpeg', '.bmp', '.gif'):
                        QMessageBox.warning(self, "错误", "仅支持png, jpg, jpeg, bmp, gif图片格式！")
                        return
                    new_s["custom_bg_path"] = bg_path
                else:
                    pass
            new_s["custom_bg_path"] = ""
        new_s["theme"] = theme_key
        old_theme = SETTINGS.get("theme")
        old_display_mode = SETTINGS.get("display_mode", "scroll")
        need_restart = False
        if theme_key != old_theme:
            need_restart = True
        if dsp != old_display_mode:
            need_restart = True
        if save_settings(new_s):
            self.settings_changed.emit(new_s)
        if need_restart:
            msg = QMessageBox(self)
            msg.setWindowTitle("提示")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("主题或显示模式已更改，需重启才能完全生效。是否立即重启？")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            rr = msg.exec()
            if rr == QMessageBox.StandardButton.Ok:
                self.close()
                if hasattr(self.parent(), "close"):
                    self.parent().close()
                try:
                    subprocess.Popen(["cscript.exe", "天狐渗透工具箱-社区版V2.0纪念版.vbs"], shell=True)
                except:
                    pass

        self.accept()
