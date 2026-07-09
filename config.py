import os 
import json 

DEFAULT_CATEGORIES =[
"最近启动",
"我的收藏",
"本地工具",
"网页工具",
"AI工具"
]

# 二级分类结构
SECONDARY_CATEGORIES ={
"本地工具": [
"WebShell管理工具",
"信息收集工具",
"抓包与代理工具",
"漏洞扫描与利用工具",
"框架漏洞利用工具",
"爆破认证工具",
"免杀对抗工具",
"后渗透工具",
"其他工具"
],
"网页工具": [
"漏洞知识库",
"情报检索工具",
"在线扫描工具",
"编码转换工具",
"云沙箱工具",
"文档社区工具",
"资产测绘工具",
"开源工具",
"安全自媒体",
"其他工具"
],
"AI工具": [
"通用对话工具",
"安全检测工具",
"风险研判工具",
"代码审查工具",
"漏洞分析工具",
"样本分析工具",
"报告写作工具",
"其他工具"
]
}

TOOL_TYPES =(
"Python",
"JAVA8",
"JAVA11",
"GUI应用",
"命令行",
"批处理",
"PowerShell",
"网页"
)

CYBERPUNK_THEME ={
"primary":"#00857E",
"secondary":"#2C0236",
"background":"#080018",
"surface":"#120240",
"content_bg":"#1D0633",
"text":"#F2F2F2",
"text_secondary":"#AADDDD",
"border":"#9F00FF",
"hover":"#00A194",
"selected":"#BA00FF80",
"error":"#FF0066",
"success":"#00ffa3",
"header":"#1D0633",
"toolbar":"#1D0633",
"dropdown":"#350066",
"title_bar":"#1D0633",
"title_bar_text":"#F2F2F2",
"title_btn_hover":"#43106B",
"title_btn_close_hover":"#FF0066",
"card_bg":"#120240",
"category_bg":"#1D0633",
"menu_button_text":"#00FFF7"
}

RED_BLUE_GLASS_THEME ={
"primary":"#FF3344",
"secondary":"#002aff",
"background":(
"qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, "
"stop:0 rgba(255, 51, 68, 0.45), stop:1 rgba(0, 42, 255, 0.45))"
),
"surface":"rgba(255, 255, 255, 0.14)",
"content_bg":"rgba(255, 255, 255, 0.09)",
"text":"#FFFFFF",
"text_secondary":"#EEEEEE",
"border":"rgba(255, 255, 255, 0.28)",
"hover":"rgba(200, 180, 255, 0.20)",
"selected":"rgba(225, 215, 255, 0.24)",
"error":"#FF3355",
"success":"#33FF88",
"header":"rgba(255, 255, 255, 0.12)",
"toolbar":"rgba(255, 255, 255, 0.12)",
"dropdown":"rgba(55, 30, 105, 0.92)",
"title_bar":"rgba(255, 255, 255, 0.18)",
"title_bar_text":"#FFFFFF",
"title_btn_hover":"rgba(255, 255, 255, 0.28)",
"title_btn_close_hover":"#AA0033",
"card_bg":"rgba(205, 190, 255, 0.16)",
"category_bg":"rgba(255, 255, 255, 0.10)"
}

Titanium_silver_THEME ={
"primary":"#6F7A89",
"secondary":"#B0B8C1",
"background":"#23272E",
"surface":"#343942",
"content_bg":"#343942",
"text":"#E3E8EE",
"text_secondary":"#AAB4C0",
"border":"#5A626D",
"hover":"#4B535E",
"selected":"#6F7A89AA",
"error":"#D36C6C",
"success":"#80B09C",
"header":"#23272E",
"toolbar":"#343942",
"dropdown":"#343942",
"title_bar":"#23272E",
"title_bar_text":"#E3E8EE",
"title_btn_hover":"#B0B8C1",
"title_btn_close_hover":"#D36C6C",
"card_bg":"#343942",
"category_bg":"#23272E"
}

SANDSTONE_GRAY_THEME ={
"primary":"#B8A47E",
"secondary":"#CFC3B1",
"background":"#F8F6F1",
"surface":"#EFE8DE",
"content_bg":"#EFE8DE",
"text":"#665B4E",
"text_secondary":"#A09281",
"border":"#D7CFC1",
"hover":"#EAD9B7",
"selected":"#B8A47E44",
"error":"#C97E7E",
"success":"#7EBC8C",
"header":"#F8F6F1",
"toolbar":"#EFE8DE",
"dropdown":"#EFE8DE",
"title_bar":"#F8F6F1",
"title_bar_text":"#665B4E",
"title_btn_hover":"#CFC3B1",
"title_btn_close_hover":"#C97E7E",
"card_bg":"#FFFFFF",
"category_bg":"#EFE8DE"
}

LIQUID_GLASS_THEME ={
"primary":"#D4A017",
"secondary":"#F2F2F7",
"background":"#F2F2F7",
"surface":"#FFFFFF",
"content_bg":"rgba(255, 255, 255, 0.8)",
"text":"#000000",
"text_secondary":"#3C3C43",
"border":"rgba(60, 60, 67, 0.15)",
"hover":"#FFF7DB",
"selected":"#FFF1B8",
"error":"#FF3B30",
"success":"#34C759",
"header":"transparent",
"toolbar":"transparent",
"dropdown":"#FFFFFF",
"title_bar":"transparent",
"title_bar_text":"#000000",
"title_btn_hover":"rgba(0, 0, 0, 0.05)",
"title_btn_close_hover":"#FF3B30",
"card_bg":"#FFFFFF",
"category_bg":"rgba(255, 255, 255, 0.6)",
"menu_button_text":"#D4A017",
"scrollbar":"#C1C1C1",
"scrollbar_hover":"#A8A8A8"
}

PRO_COMPACT_THEME ={
"primary":"#0071E3",
"secondary":"#F5F5F7",
"background":"#F2F2F7",
"surface":"#FFFFFF",
"content_bg":"#F7F8FA",
"text":"#1D1D1F",
"text_secondary":"#6E6E73",
"border":"#D9D9DE",
"hover":"#EAF2FF",
"selected":"#DCEBFF",
"error":"#D92C20",
"success":"#2E9B62",
"header":"#FFFFFF",
"toolbar":"#FFFFFF",
"dropdown":"#FFFFFF",
"title_bar":"#FFFFFF",
"title_bar_text":"#1D1D1F",
"title_btn_hover":"#EEF0F3",
"title_btn_close_hover":"#E5484D",
"card_bg":"#FFFFFF",
"category_bg":"#F5F5F7",
"menu_button_text":"#0071E3",
"scrollbar":"#C7C7CC",
"scrollbar_hover":"#9D9DA3"
}

THEMES ={
"dark":{
"primary":"#2B5DCD",
"secondary":"#1E1E1E",
"background":"#121212",
"surface":"#000000",
"content_bg":"#000000",
"text":"#FFFFFF",
"text_secondary":"#B3B3B3",
"border":"#2F2F2F",
"hover":"#333333",
"selected":"#2B5DCD33",
"error":"#CF6679",
"success":"#4CAF50",
"header":"#000000",
"toolbar":"#000000",
"dropdown":"#000000",
"title_bar":"#000000",
"title_bar_text":"#FFFFFF",
"title_btn_hover":"#383838",
"title_btn_close_hover":"#E81123",
"card_bg":"#000000",
"category_bg":"#000000"
},
"light":{
"primary":"#A69F95",
"secondary":"#F5F5F5",
"background":"#FFFFFF",
"surface":"#FFFFFF",
"content_bg":"#FFFFFF",
"text":"#333333",
"text_secondary":"#666666",
"border":"#E0E0E0",
"hover":"#F5F5F5",
"selected":"#A69F9533",
"error":"#D9534F",
"success":"#5CB85C",
"header":"#FFFFFF",
"toolbar":"#FFFFFF",
"dropdown":"#FFFFFF",
"title_bar":"#FFFFFF",
"title_bar_text":"#333333",
"title_btn_hover":"#F0F0F0",
"title_btn_close_hover":"#B92727",
"card_bg":"#FFFFFF",
"category_bg":"#FFFFFF"
},
"eye_care":{
"primary":"#8FBF60",
"secondary":"#F3F3E7",
"background":"#F7F6E9",
"surface":"#F7F6E9",
"content_bg":"#F7F6E9",
"text":"#3B3B2A",
"text_secondary":"#6D6D57",
"border":"#B3B190",
"hover":"#E8E7D3",
"selected":"#8FBF6044",
"error":"#C9302C",
"success":"#5CB85C",
"header":"#F7F6E9",
"toolbar":"#F7F6E9",
"dropdown":"#F7F6E9",
"title_bar":"#F7F6E9",
"title_bar_text":"#3B3B2A",
"title_btn_hover":"#E8E7D3",
"title_btn_close_hover":"#AF3F3F",
"card_bg":"#F7F6E9",
"category_bg":"#F7F6E9"
},
"pink":{
"primary":"#FF7EB6",
"secondary":"#FFF0F7",
"background":"#FFF9FB",
"surface":"#FFF9FB",
"content_bg":"#FFF9FB",
"text":"#4F4F4F",
"text_secondary":"#767676",
"border":"#FFE4EF",
"hover":"#FFF0F7",
"selected":"#FF7EB644",
"error":"#FF4E6E",
"success":"#4CAF50",
"header":"#FFF9FB",
"toolbar":"#FFF9FB",
"dropdown":"#FFF9FB",
"title_bar":"#FFF9FB",
"title_bar_text":"#4F4F4F",
"title_btn_hover":"#FFE4EF",
"title_btn_close_hover":"#FF4E6E",
"card_bg":"#FFFFFF",
"category_bg":"#FFF9FB"
},
"blue":{
"primary":"#2196F3",
"secondary":"#E3F2FD",
"background":"#EAF2F8",
"surface":"#FFFFFF",
"content_bg":"#EAF2F8",
"text":"#2C3E50",
"text_secondary":"#546E7A",
"border":"#BBDEFB",
"hover":"#E3F2FD",
"selected":"#2196F333",
"error":"#F44336",
"success":"#4CAF50",
"header":"#EAF2F8",
"toolbar":"#EAF2F8",
"dropdown":"#FFFFFF",
"title_bar":"#EAF2F8",
"title_bar_text":"#2C3E50",
"title_btn_hover":"#E3F2FD",
"title_btn_close_hover":"#EF5350",
"card_bg":"#FFFFFF",
"category_bg":"#EAF2F8"
},
"cyberpunk":CYBERPUNK_THEME ,
"red_blue_glass":RED_BLUE_GLASS_THEME ,
"Titanium_silver":Titanium_silver_THEME ,
"sandstone_gray":SANDSTONE_GRAY_THEME ,
"liquid_glass":LIQUID_GLASS_THEME ,
"pro_compact":PRO_COMPACT_THEME ,
"custom_image":{},
"modern":{
"primary":"#6366F1",
"secondary":"#8B5CF6",
"background":"#1E1B4B",
"surface":"#2D3748",
"content_bg":"#1A202C",
"text":"#F7FAFC",
"text_secondary":"#A0AEC0",
"border":"#4A5568",
"hover":"#4A5568",
"selected":"#6366F144",
"error":"#F56565",
"success":"#48BB78",
"header":"#2D3748",
"toolbar":"#2D3748",
"dropdown":"#2D3748",
"title_bar":"#2D3748",
"title_bar_text":"#F7FAFC",
"title_btn_hover":"#4A5568",
"title_btn_close_hover":"#F56565",
"card_bg":"#2D3748",
"category_bg":"#1A202C",
"menu_button_text":"#6366F1",
"scrollbar":"#4A5568",
"scrollbar_hover":"#718096"
}
}

def load_theme (theme_name ):
    if theme_name =="custom_image":

        base =dict (THEMES .get ("dark",{}))
        base .update (THEMES .get ("red_blue_glass",{}))
        base ["background"]="transparent"
        return base 

    base =dict (THEMES .get ("dark",{}))
    theme =THEMES .get (theme_name )
    if isinstance (theme ,dict ):
        base .update (theme )

    return base 

DEFAULT_SETTINGS ={
"confirm_exit":True ,
"theme":"modern",
"font_size":12 ,
"java8_path":"Java_path/Java_8_win/bin",
"java11_path":"Java_path/Java_11_win/bin",
"python_path":"python3/python.exe",
"exit_mode":"ask",
"display_mode":"scroll",
"cli_python_interpreters":[],
"cli_java_interpreters":[],
"cli_default_python":"",
"cli_default_java":"",
"favorite_tools":[],
"recent_tools":[],
"main_window_geometry":None ,
"main_window_state":None ,
"auto_theme_mode":"manual",
"custom_bg_path":"",
"pro_compact_enhanced":True ,
"pro_compact_search_scope":"current"
}

SETTINGS_FILE ="config/settings.json"
TOOLS_FILE ="config/tools.json"
CATEGORIES_FILE ="config/categories.json"
HOTKEYS_FILE ="config/hotkeys.json"

def load_settings ():
    if not os .path .exists ("config"):
        os .makedirs ("config",exist_ok =True )
    if not os .path .isfile (SETTINGS_FILE ):
        try :
            with open (SETTINGS_FILE ,"w",encoding ="utf-8")as f :
                json .dump (DEFAULT_SETTINGS ,f ,ensure_ascii =False ,indent =2 )
        except Exception as err :
            print (f"生成默认settings.json时出错: {err}")
        return DEFAULT_SETTINGS .copy ()
    else :
        try :
            with open (SETTINGS_FILE ,"r",encoding ="utf-8")as f :
                user_cfg =json .load (f )
            final_cfg ={**DEFAULT_SETTINGS ,**user_cfg }
            if "cli_python_interpreters"not in final_cfg :
                final_cfg ["cli_python_interpreters"]=[]
            if "cli_java_interpreters"not in final_cfg :
                final_cfg ["cli_java_interpreters"]=[]
            if "cli_default_python"not in final_cfg :
                final_cfg ["cli_default_python"]=""
            if "cli_default_java"not in final_cfg :
                final_cfg ["cli_default_java"]=""


            legacy =final_cfg .get ("custom_interpreters",None )
            if isinstance (legacy ,list )and legacy :
                py_names ={str (x .get ("name",""))for x in final_cfg .get ("cli_python_interpreters",[])if isinstance (x ,dict )}
                java_names ={str (x .get ("name",""))for x in final_cfg .get ("cli_java_interpreters",[])if isinstance (x ,dict )}
                for ci in legacy :
                    if not isinstance (ci ,dict ):
                        continue 
                    name =str (ci .get ("name","")).strip ()
                    path =str (ci .get ("path","")).strip ()
                    typ =str (ci .get ("type","")).strip ().lower ()
                    if not name or not path :
                        continue 
                    if typ =="python":
                        if name not in py_names :
                            final_cfg ["cli_python_interpreters"].append ({"name":name ,"path":path })
                            py_names .add (name )
                    elif typ =="java":
                        if name not in java_names :
                            final_cfg ["cli_java_interpreters"].append ({"name":name ,"path":path })
                            java_names .add (name )


            if "custom_interpreters"in final_cfg :
                try :
                    del final_cfg ["custom_interpreters"]
                except Exception :
                    pass 
            if "favorite_tools"not in final_cfg :
                final_cfg ["favorite_tools"]=[]
            if "recent_tools"not in final_cfg :
                final_cfg ["recent_tools"]=[]
            if "main_window_geometry"not in final_cfg :
                final_cfg ["main_window_geometry"]=None 
            if "main_window_state"not in final_cfg :
                final_cfg ["main_window_state"]=None 
            if "auto_theme_mode"not in final_cfg :
                final_cfg ["auto_theme_mode"]="manual"
            if "custom_bg_path"not in final_cfg :
                final_cfg ["custom_bg_path"]=""
            return final_cfg 
        except Exception as err :
            print (f"读取settings.json出错: {err}")
            return DEFAULT_SETTINGS .copy ()

def save_settings (settings_dict :dict ):
    try :

        if not os .path .exists ("config"):
            os .makedirs ("config",exist_ok =True )


        if "custom_interpreters"in settings_dict :
            try :
                del settings_dict ["custom_interpreters"]
            except Exception :
                pass 
        with open (SETTINGS_FILE ,"w",encoding ="utf-8")as f :
            json .dump (settings_dict ,f ,ensure_ascii =False ,indent =2 )
        return True 
    except Exception as err :
        print (f"保存settings.json出错: {err}")
        return False 

def fix_paths (settings_dict :dict ):
    for key in ["python_path","java8_path","java11_path"]:
        val =settings_dict .get (key ,"").strip ()
        if val and not os .path .isabs (val ):
            abs_val =os .path .abspath (val )
            settings_dict [key ]=abs_val 
    for arr_key in ["cli_python_interpreters","cli_java_interpreters"]:
        if arr_key in settings_dict and isinstance (settings_dict [arr_key ],list ):
            for ci in settings_dict [arr_key ]:
                if isinstance (ci ,dict )and "path"in ci and ci ["path"]and not os .path .isabs (ci ["path"]):
                    ci ["path"]=os .path .abspath (ci ["path"])

SETTINGS =load_settings ()
fix_paths (SETTINGS )
THEME =load_theme (SETTINGS .get ("theme","dark"))

_dropdown_bg =THEME .get ("dropdown",THEME .get ("surface","#222"))
try :
    _db =str (_dropdown_bg ).strip ().lower ()
    if _db in ("transparent","rgba(0, 0, 0, 0)","rgba(0,0,0,0)"):
        _dropdown_bg ="rgba(20, 20, 28, 0.92)"
except Exception :
    _dropdown_bg ="rgba(20, 20, 28, 0.92)"

STYLESHEET =(
f"QMainWindow {{"
f"    background: {THEME['background'] if SETTINGS.get('theme')=='red_blue_glass' else (THEME['background'] if SETTINGS.get('theme')!='custom_image' else 'transparent')};"
f"    border-radius: 16px;"
f"}}"
f"QWidget {{"
f"    color: {THEME['text']};"
f"    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;"
f"    font-size: 13px;"
f"}}"
f"QWidget#categoryContainer {{"
f"    background-color: {THEME['category_bg']};"
f"    border-right: 1px solid {THEME['border']};"
f"}}"
f"QWidget#toolCard {{"
f"    background-color: {THEME['card_bg']};"
f"    border: 1px solid {THEME['border']};"
f"    border-radius: 12px;"
f"    margin: 4px;"
f"    padding: 8px;"
f"}}"
f"QWidget#toolCard:hover {{"
f"    border: 1px solid {THEME['primary']};"
f"    background-color: {THEME['hover']};"
f"}}"
f"QWidget#toolGridContainer {{"
f"    background-color: {THEME['content_bg']};"
f"}}"
f"QWidget#titleBar {{"
f"    background-color: {THEME['title_bar']};"
f"    border-bottom: 1px solid {THEME['border']};"
f"    border-top-left-radius: 16px;"
f"    border-top-right-radius: 16px;"
f"}}"
f"QWidget#titleBar QLabel {{"
f"    color: {THEME['title_bar_text']};"
f"    font-size: 15px;"
f"    font-weight: 600;"
f"    background-color: transparent;"
f"}}"
f"QPushButton#titleButton {{"
f"    background-color: transparent;"
f"    border: none;"
f"    border-radius: 6px;"
f"    min-width: 30px;"
f"    max-width: 30px;"
f"    min-height: 24px;"
f"    max-height: 24px;"
f"    color: {THEME['title_bar_text']};"
f"}}"
f"QPushButton#titleButton:hover {{"
f"    background-color: {THEME['title_btn_hover']};"
f"}}"
f"QPushButton#closeButton:hover {{"
f"    background-color: {THEME['title_btn_close_hover']};"
f"    color: white;"
f"}}"
f"QToolBar {{"
f"    background-color: {THEME['toolbar']};"
f"    border: none;"
f"    padding: 8px;"
f"}}"
f"QToolButton {{"
f"    background-color: transparent;"
f"    color: {THEME['text']};"
f"    border: 1px solid transparent;"
f"    border-radius: 8px;"
f"    padding: 6px;"
f"}}"
f"QToolButton:hover {{"
f"    background-color: {THEME['hover']};"
f"}}"
f"QPushButton {{"
f"    background-color: {THEME['primary']};"
f"    color: #FFFFFF;"
f"    border: none;"
f"    border-radius: 8px;"
f"    padding: 8px 16px;"
f"    font-weight: 600;"
f"}}"
f"QPushButton:hover {{"
f"    background-color: {THEME['primary']}DD;"
f"}}"
f"QPushButton:pressed {{"
f"    background-color: {THEME['primary']}AA;"
f"}}"
f"QPushButton:focus {{"
f"    border: 2px solid {THEME['primary']};"
f"    background-color: {THEME['primary']}55;"
f"}}"
f"QPushButton#noHoverBtn:hover {{"
f"    background-color: {THEME['primary']};"
f"}}"
f"QPushButton#noHoverBtn:pressed {{"
f"    background-color: {THEME['primary']};"
f"}}"
f"QPushButton#noHoverBtn:focus {{"
f"    border: none;"
f"    background-color: {THEME['primary']};"
f"}}"
f"QToolTip {{"
f"    background-color: {THEME['card_bg']};"
f"    color: {THEME['text']};"
f"    border: 1px solid {THEME['primary']};"
f"    border-radius: 12px;"
f"    padding: 10px 12px;"
f"    font-size: 12px;"
f"}}"
f"QMenu {{"
f"    background-color: {_dropdown_bg};"
f"    border: 1px solid {THEME['border']};"
f"    border-radius: 12px;"
f"    padding: 6px;"
f"}}"
f"QMenu::item {{"
f"    padding: 8px 14px;"
f"    border-radius: 10px;"
f"    color: {THEME['text']};"
f"}}"
f"QMenu::item:disabled {{"
f"    color: {THEME.get('text_secondary', THEME['text'])};"
f"}}"
f"QMenu::item:hover {{"
f"    background-color: {THEME['hover']};"
f"    color: {THEME['text']};"
f"}}"
f"QMenu::item:selected {{"
f"    background-color: {THEME['hover']};"
f"    color: {THEME['text']};"
f"}}"
f"QMenu::separator {{"
f"    height: 1px;"
f"    background-color: {THEME['border']};"
f"    margin: 4px 8px;"
f"}}"
f"QPushButton#categoryBtn {{"
f"    background-color: transparent;"
f"    text-align: left;"
f"    font-size: 12px;"
f"    padding: 12px 20px;"
f"    border-radius: 12px;"
f"    margin: 2px 8px;"
f"    color: {THEME['text']};"
f"    border: none;"
f"}}"
f"QPushButton#categoryBtn:hover {{"
f"    background-color: transparent;"
f"    font-weight: bold;"
f"}}"
f"QPushButton#categoryBtn:checked {{"
f"    background-color: transparent;"
f"    color: {THEME['text']};"
f"    font-weight: bold;"
f"}}"
f"QLineEdit {{"
f"    background-color: {THEME['surface']};"
f"    border: 1px solid {THEME['border']};"
f"    border-radius: 8px;"
f"    padding: 8px 12px;"
f"    color: {THEME['text']};"
f"}}"
f"QLineEdit:focus {{"
f"    border: 1px solid {THEME['primary']};"
f"    background-color: {THEME['surface']};"
f"}}"
f"QComboBox {{"
f"    background-color: {THEME['surface']};"
f"    border: 1px solid {THEME['border']};"
f"    border-radius: 8px;"
f"    padding: 6px 36px 6px 12px;"
f"    color: {THEME['text']};"
f"}}"
f"QComboBox QAbstractItemView {{"
f"    background-color: {_dropdown_bg};"
f"    border: 1px solid {THEME['border']};"
f"    selection-background-color: {THEME['hover']};"
f"    selection-color: {THEME['text']};"
f"    outline: 0;"
f"}}"
f"QComboBoxPrivateContainer {{"
f"    background-color: {_dropdown_bg};"
f"    border: 1px solid {THEME['border']};"
f"    border-radius: 12px;"
f"    padding: 6px;"
f"}}"
f"QComboBoxPrivateContainer QListView {{"
f"    background-color: {_dropdown_bg};"
f"    border: none;"
f"    outline: 0;"
f"}}"
f"QFrame#qt_combobox_popup {{"
f"    background-color: {_dropdown_bg};"
f"    border: 1px solid {THEME['border']};"
f"    border-radius: 12px;"
f"}}"
f"QAbstractItemView, QListView {{"
f"    background-color: {_dropdown_bg};"
f"    alternate-background-color: {_dropdown_bg};"
f"    border: 1px solid {THEME['border']};"
f"    selection-background-color: {THEME['hover']};"
f"    selection-color: {THEME['text']};"
f"    outline: 0;"
f"}}"
f"QAbstractItemView::item, QListView::item {{"
f"    color: {THEME['text']};"
f"}}"
f"QAbstractItemView::item:disabled, QListView::item:disabled {{"
f"    color: {THEME.get('text_secondary', THEME['text'])};"
f"}}"
f"QAbstractItemView::item:hover, QListView::item:hover {{"
f"    background-color: {THEME['hover']};"
f"    color: {THEME['text']};"
f"}}"
f"QComboBox QAbstractItemView::item {{"
f"    padding: 8px 12px;"
f"    border-radius: 6px;"
f"}}"
f"QComboBox QAbstractItemView::item:selected {{"
f"    background-color: {THEME['hover']};"
f"    color: {THEME['text']};"
f"}}"
f"QComboBox::drop-down {{"
f"    subcontrol-origin: padding;"
f"    subcontrol-position: top right;"
f"    width: 32px;"
f"    border-left: 1px solid {THEME['border']};"
f"    background-color: rgba(255, 255, 255, 0.08);"
f"    border-top-right-radius: 8px;"
f"    border-bottom-right-radius: 8px;"
f"}}"
f"QComboBox::down-arrow {{"
f"    width: 14px;"
f"    height: 14px;"
f"    margin-right: 9px;"
f"    background: transparent;"
f"    image: url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24'><path fill='%23E7E7F2' d='M7.41 8.59 12 13.17l4.59-4.58L18 10l-6 6-6-6z'/></svg>\");"
f"}}"
f"QScrollArea {{"
f"    background-color: transparent;"
f"    border: none;"
f"}}"
f"QScrollBar:vertical {{"
f"    border: none;"
f"    background: transparent;"
f"    width: 8px;"
f"    margin: 0;"
f"}}"
f"QScrollBar::handle:vertical {{"
f"    background: {THEME.get('scrollbar', THEME['text_secondary'])};"
f"    border-radius: 4px;"
f"    min-height: 20px;"
f"}}"
f"QScrollBar::handle:vertical:hover {{"
f"    background: {THEME.get('scrollbar_hover', THEME.get('scrollbar', THEME['text_secondary']))};"
f"}}"
f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{"
f"    height: 0px;"
f"}}"
f"QMenu {{"
f"    background-color: {_dropdown_bg};"
f"    border: 1px solid {THEME['border']};"
f"    color: {THEME['text']};"
f"    padding: 6px;"
f"    border-radius: 12px;"
f"}}"
f"QMenu::item {{"
f"    padding: 8px 24px;"
f"    border-radius: 6px;"
f"    color: {THEME['text']};"
f"}}"
f"QMenu::item:selected {{"
f"    background-color: {THEME['hover']};"
f"    color: {THEME['text']};"
f"}}"
f"QDialog {{"
f"    background: {THEME['surface']};"
f"    border-radius: 16px;"
f"}}"
f"QDialog#settingsDialog {{"
f"    background: {THEME['background'] if SETTINGS.get('theme')=='red_blue_glass' else THEME['surface']};"
f"    border-radius: 16px;"
f"}}"
f"QFrame#settingsPanel {{"
f"    background: {THEME['background'] if SETTINGS.get('theme')=='red_blue_glass' else THEME['surface']};"
f"    border: none;"
f"    border-radius: 18px;"
f"}}"
f"QDialog#settingsDialog QPushButton#titleButton {{"
f"    min-width: 22px;"
f"    max-width: 22px;"
f"    min-height: 18px;"
f"    max-height: 18px;"
f"    border-radius: 5px;"
f"    padding: 0px;"
f"}}"
f"QDialog#toolDialog {{"
f"    background: {THEME['background'] if SETTINGS.get('theme')=='red_blue_glass' else THEME['surface']};"
f"    border-radius: 16px;"
f"}}"
f"QDialog#settingsDialog QPushButton, QDialog#toolDialog QPushButton, QMessageBox QPushButton {{"
f"    background-color: rgba(255, 255, 255, 0.18);"
f"    color: {THEME['text']};"
f"    border: 1px solid {THEME['border']};"
f"    border-radius: 10px;"
f"    padding: 8px 16px;"
f"    font-weight: 600;"
f"}}"
f"QDialog#settingsDialog QPushButton:hover, QDialog#toolDialog QPushButton:hover, QMessageBox QPushButton:hover {{"
f"    background-color: rgba(255, 255, 255, 0.24);"
f"}}"
f"QDialog#settingsDialog QPushButton:pressed, QDialog#toolDialog QPushButton:pressed, QMessageBox QPushButton:pressed {{"
f"    background-color: rgba(255, 255, 255, 0.14);"
f"}}"
f"QLabel#contextBreadcrumb {{"
f"    color: {THEME.get('text_secondary', THEME['text'])};"
f"    font-size: 12px;"
f"    padding: 2px 6px;"
f"}}"
f"QMessageBox {{"
f"    background: {THEME['background'] if SETTINGS.get('theme')=='red_blue_glass' else THEME['surface']};"
f"}}"
f"QMessageBox QLabel {{"
f"    color: {THEME['text']};"
f"}}"
)

def load_tools ():
    try :
        if os .path .exists (TOOLS_FILE ):
            with open (TOOLS_FILE ,'r',encoding ='utf-8')as f :
                raw =json .load (f )
            base_dir =os .path .dirname (os .path .abspath (__file__ ))
            def _normalize_tool (t ):
                if not isinstance (t ,dict ):
                    return None 
                tool =dict (t )
                key_map ={
                "tool_name":"name",
                "title":"name",
                "tool_title":"name",
                "tool_category":"category",
                "cate":"category",
                "tool_type":"type",
                "env":"type",
                "env_type":"type",
                "tool_path":"path",
                "file":"path",
                "filepath":"path",
                "tool_params":"params",
                "param":"params",
                "args":"params",
                "tool_url":"url",
                "link":"url",
                "tool_desc":"description",
                "desc":"description",
                "priority":"weight",
                "order":"weight",
                "tag":"tags",
                }
                for oldk ,newk in key_map .items ():
                    if newk not in tool and oldk in tool :
                        tool [newk ]=tool .get (oldk )

                if "name"not in tool :
                    tool ["name"]=""
                if "category"not in tool :
                    tool ["category"]=""
                if "type"not in tool :
                    tool ["type"]=""
                if "path"not in tool :
                    tool ["path"]=""
                if "params"not in tool :
                    tool ["params"]=""
                if "url"not in tool :
                    tool ["url"]=""
                if "description"not in tool :
                    tool ["description"]=""

                try :
                    tool ["weight"]=int (tool .get ("weight",0 )or 0 )
                except Exception :
                    tool ["weight"]=0 

                tags =tool .get ("tags",[])
                if isinstance (tags ,str ):
                    tags =[x .strip ()for x in tags .split (",")if x .strip ()]
                if not isinstance (tags ,list ):
                    tags =[]
                tool ["tags"]=tags 

                if "group"not in tool :
                    tool ["group"]=""
                return tool 

            tools =[]
            if isinstance (raw ,list ):
                tools =raw 
            elif isinstance (raw ,dict ):
                if isinstance (raw .get ("tools"),list ):
                    tools =raw .get ("tools")
                elif isinstance (raw .get ("data"),list ):
                    tools =raw .get ("data")
                elif isinstance (raw .get ("items"),list ):
                    tools =raw .get ("items")

            out =[]
            for t in tools :
                tool =_normalize_tool (t )
                if not tool :
                    continue 
                p_original =tool .get ('path','')
                if p_original :
                    p_norm =str (p_original ).replace ('\\','/').strip ()
                    if (
                    p_norm .startswith ('/tools/')or 
                    p_norm .startswith ('\\tools\\')or 
                    p_norm .startswith ('/tools\\')or 
                    p_norm .startswith ('\\tools/')
                    ):
                        rel_part =p_norm .lstrip ('/\\')
                        abs_path =os .path .join (base_dir ,rel_part )
                        tool ['path']=abs_path 
                out .append (tool )
            return out 
    except Exception as e :
        print (f"加载工具数据失败: {e}")
    return []

def save_tools (tools ):
    try :
        os .makedirs (os .path .dirname (TOOLS_FILE ),exist_ok =True )
        base_dir =os .path .dirname (os .path .abspath (__file__ ))
        base_tools_dir =os .path .join (base_dir ,"tools")
        out_list =[]
        for t in tools :
            clone =t .copy ()
            p =clone .get ('path','')
            if not p :
                out_list .append (clone )
                continue 
            abs_path =os .path .abspath (p )
            try :
                if os .path .commonprefix ([
                os .path .normcase (abs_path ),
                os .path .normcase (base_tools_dir )
                ])==os .path .normcase (base_tools_dir ):
                    rel2base =os .path .relpath (abs_path ,base_dir )
                    clone ['path']="/"+rel2base .replace ("\\","/")
                else :
                    clone ['path']=abs_path 
            except ValueError :
                clone ['path']=abs_path 
            if "tags"not in clone :
                clone ["tags"]=[]
            if "group"not in clone :
                clone ["group"]=""
            out_list .append (clone )
        with open (TOOLS_FILE ,'w',encoding ='utf-8')as f :
            json .dump (out_list ,f ,ensure_ascii =False ,indent =2 )
        return True 
    except Exception as e :
        print (f"保存工具数据失败: {e}")
        return False 

def load_categories ():
    try :
        if not os .path .exists ("config"):
            os .makedirs ("config",exist_ok =True )
        if not os .path .exists (CATEGORIES_FILE ):
            with open (CATEGORIES_FILE ,"w",encoding ='utf-8')as f :
                json .dump ({"categories":DEFAULT_CATEGORIES },f ,ensure_ascii =False ,indent =2 )
            return DEFAULT_CATEGORIES 
        with open (CATEGORIES_FILE ,"r",encoding ="utf-8")as f :
            data =json .load (f )
            if isinstance (data ,dict )and "categories"in data :
                return data ["categories"]
    except Exception as e :
        print (f"加载分类数据出错: {e}")
    return DEFAULT_CATEGORIES 

def save_categories (categories_list ):
    try :
        if not os .path .exists ("config"):
            os .makedirs ("config",exist_ok =True )
        with open (CATEGORIES_FILE ,"w",encoding ="utf-8")as f :
            json .dump ({"categories":categories_list },f ,ensure_ascii =False ,indent =2 )
        return True 
    except Exception as e :
        print (f"保存分类数据出错: {e}")
        return False 

def export_all_data (filepath :str ):
    data ={
    "tools":load_tools (),
    "categories":load_categories (),
    "settings":load_settings (),
    }
    if os .path .exists (HOTKEYS_FILE ):
        with open (HOTKEYS_FILE ,"r",encoding ="utf-8")as f :
            data ["hotkeys"]=json .load (f )
    with open (filepath ,"w",encoding ="utf-8")as f :
        json .dump (data ,f ,ensure_ascii =False ,indent =2 )

def import_all_data (filepath :str ,mode ="merge"):
    with open (filepath ,"r",encoding ="utf-8")as f :
        data =json .load (f )
    if mode =="overwrite":
        if "tools"in data :
            tools =data .get ("tools")
            if isinstance (tools ,list ):
                save_tools (tools )
            elif isinstance (tools ,dict )and isinstance (tools .get ("tools"),list ):
                save_tools (tools .get ("tools"))
        if "categories"in data :
            save_categories (data ["categories"])
        if "settings"in data :
            save_settings (data ["settings"])
        if "hotkeys"in data :
            with open (HOTKEYS_FILE ,"w",encoding ="utf-8")as f2 :
                json .dump (data ["hotkeys"],f2 ,ensure_ascii =False ,indent =2 )
    else :
        old_tools =load_tools ()
        tool_keys ={(t ['name'],t ['category'])for t in old_tools }
        add_tools =[]
        incoming =data .get ("tools",[])
        if isinstance (incoming ,dict )and isinstance (incoming .get ("tools"),list ):
            incoming =incoming .get ("tools")
        for t in incoming :
            try :
                if (t ['name'],t ['category'])not in tool_keys :
                    add_tools .append (t )
            except Exception :
                continue 
        save_tools (old_tools +add_tools )
        old_cats =set (load_categories ())
        new_cats =set (data .get ("categories",[]))
        save_categories (list (old_cats |new_cats ))
        old_set =load_settings ()
        old_set .update (data .get ("settings",{}))
        save_settings (old_set )
        if "hotkeys"in data :
            if os .path .exists (HOTKEYS_FILE ):
                with open (HOTKEYS_FILE ,"r",encoding ="utf-8")as f2 :
                    old_map =json .load (f2 )
            else :
                old_map ={}
            old_map .update (data ["hotkeys"])
            with open (HOTKEYS_FILE ,"w",encoding ="utf-8")as f2 :
                json .dump (old_map ,f2 ,ensure_ascii =False ,indent =2 )
