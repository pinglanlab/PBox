import sys 
import os 
import logging 
import subprocess 
import keyboard 
import base64 
import threading 
import time 
import traceback 
import logging .handlers 
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QSystemTrayIcon, QMenu,
    QFileDialog, QInputDialog, QLabel, QLineEdit, QAbstractButton, QComboBox,
    QScrollArea, QFrame, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QSettings, QByteArray, QTimer, pyqtSignal, QThread, QObject, QEvent, QVariantAnimation, QEasingCurve, qInstallMessageHandler, QtMsgType, QUrl
from PyQt6.QtGui import QPainter, QPixmap, QShortcut, QKeySequence, QIcon, QDesktopServices 

from config import (
SETTINGS ,THEME ,load_settings ,save_settings ,load_theme ,
load_tools ,load_categories ,save_tools ,save_categories ,DEFAULT_CATEGORIES ,SECONDARY_CATEGORIES ,
export_all_data ,import_all_data
)
from utils import (
ensure_single_instance ,check_environment ,validate_java_path ,run_tool ,
run_tools_batch ,is_tool_favorited ,add_favorite_tool ,remove_favorite_tool ,
save_main_window_geometry ,load_main_window_geometry ,save_main_window_state ,load_main_window_state ,
SearchWorker ,fuzzy_search ,get_favorite_tools ,get_recent_tools 
)
from widgets import (
TitleBar ,SearchBar ,CategoryPanel ,
ToolDialog ,SettingsDialog ,apply_button_icon ,get_ui_icon
)
from core .window_effect import WindowEffect 
from core .modern_grid import ModernToolGrid 

class _RateLimitingHandler (logging .Handler ):
    def __init__ (self ,inner :logging .Handler ,*,window_sec :float =10.0 ,max_per_key :int =20 ):
        super ().__init__ (level =inner .level )
        self ._inner =inner 
        self ._window =float (window_sec )
        self ._max =int (max_per_key )
        self ._state ={}
        self ._lock =threading .Lock ()

    def setFormatter (self ,fmt ):
        try :
            self ._inner .setFormatter (fmt )
        except Exception :
            pass 
        return super ().setFormatter (fmt )

    def _make_key (self ,record :logging .LogRecord ):
        try :
            msg =record .getMessage ()
        except Exception :
            msg =""
        if len (msg )>220 :
            msg =msg [:220 ]
        return (record .levelno ,record .name ,msg )

    def _emit_summary (self ,key ,suppressed :int ):
        try :
            levelno ,name ,msg =key 
            summary =logging .LogRecord (
            name =name ,
            level =levelno ,
            pathname ="",
            lineno =0 ,
            msg =f"[log-suppress] suppressed {suppressed} similar logs in last {int (self ._window )}s: {msg}",
            args =(),
            exc_info =None ,
            func =None ,
            sinfo =None ,
            )
            self ._inner .emit (summary )
        except Exception :
            pass 

    def emit (self ,record :logging .LogRecord ):
        now =time .time ()
        key =self ._make_key (record )
        with self ._lock :
            st =self ._state .get (key )
            if st is None :
                st =[now ,0 ,0 ]
                self ._state [key ]=st 
            win_start ,count ,supp =st [0 ],st [1 ],st [2 ]

            if now -win_start >=self ._window :
                if supp >0 :
                    self ._emit_summary (key ,supp )
                win_start =now 
                count =0 
                supp =0 

            if count <self ._max :
                st [0 ],st [1 ],st [2 ]=win_start ,count +1 ,supp 
                try :
                    self ._inner .emit (record )
                except Exception :
                    pass 
            else :
                st [0 ],st [1 ],st [2 ]=win_start ,count ,supp +1 


_fmt =logging .Formatter ('%(asctime)s - %(levelname)s - %(message)s')
_file =logging .handlers .RotatingFileHandler (
"app.log",maxBytes =2 *1024 *1024 ,backupCount =5 ,encoding ="utf-8"
)
_file .setFormatter (_fmt )
_console =logging .StreamHandler ()
_console .setFormatter (_fmt )

_file_rl =_RateLimitingHandler (_file ,window_sec =10.0 ,max_per_key =30 )
_console_rl =_RateLimitingHandler (_console ,window_sec =10.0 ,max_per_key =30 )

root_logger =logging .getLogger ()
root_logger .setLevel (logging .INFO )
root_logger .handlers .clear ()
root_logger .addHandler (_file_rl )
root_logger .addHandler (_console_rl )

logger =logging .getLogger (__name__ )


def install_log_hooks ():
    def _excepthook (exc_type ,exc ,tb ):
        try :
            lines =traceback .format_exception (exc_type ,exc ,tb )
            logger .error ("Uncaught exception:\n%s","".join (lines ))
        except Exception :
            pass 

        try :
            sys .__excepthook__ (exc_type ,exc ,tb )
        except Exception :
            pass 

    try :
        sys .excepthook =_excepthook 
    except Exception :
        pass 

    def _qt_msg_handler (mode ,context ,message ):
        try :
            try :
                msg =str (message )
            except Exception :
                msg =""

            if mode ==QtMsgType .QtCriticalMsg :
                logger .error ("QtCritical: %s",msg )
            elif mode ==QtMsgType .QtFatalMsg :
                logger .critical ("QtFatal: %s",msg )
        except Exception :
            pass 

    try :
        qInstallMessageHandler (_qt_msg_handler )
    except Exception :
        pass 


class ButtonHoverCursorFilter (QObject ):
    def eventFilter (self ,obj ,event ):
        try :
            if isinstance (obj ,QAbstractButton ):
                if event .type ()==QEvent .Type .Enter :
                    obj .setCursor (Qt .CursorShape .PointingHandCursor )
                elif event .type ()==QEvent .Type .Leave :
                    obj .unsetCursor ()
        except Exception :
            pass 
        return super ().eventFilter (obj ,event )

CURRENT_VERSION ='3.0'

def get_tool_main_category (tool ):
    cat =str (tool .get ("category","")or "").strip ()
    if cat .startswith ("本地工具"):
        return "本地工具"
    if cat .startswith ("网页工具"):
        return "网页工具"
    if cat .startswith ("AI工具"):
        return "AI工具"

    tool_type =str (tool .get ("type","")or "").strip ()
    url =str (tool .get ("url","")or "").strip ()
    if tool_type =="网页"or url :
        return "网页工具"
    return "本地工具"

def infer_web_sub_category (tool ):
    name =str (tool .get ("name","")or "")
    desc =str (tool .get ("description","")or "")
    url =str (tool .get ("url","")or "")
    tags =tool .get ("tags",[])
    if isinstance (tags ,(list ,tuple ,set )):
        tags_text =" ".join ([str (x )for x in tags ])
    else :
        tags_text =str (tags or "")
    text =(name +" "+desc +" "+url +" "+tags_text ).casefold ()

    def has_any (words ):
        return any ((w in text )for w in words )

    if has_any ([
    "webshell","蚁剑","冰蝎","哥斯拉","shell 管理","shell管理"
    ]):
        return "WebShell管理工具"
    if has_any (["抓包","代理","proxy","mitm","burp","fiddler"]):
        return "抓包与代理工具"
    if has_any (["免杀","bypass","av 免杀","杀软绕过"]):
        return "免杀工具"
    if has_any (["爆破","brute","hydra","字典攻击","口令爆破"]):
        return "爆破工具"
    if has_any (["提权","后渗透","横向","内网","c2","beacon"]):
        return "后渗透工具"
    if has_any ([
    "漏洞","cve","exp","poc","漏洞库","seebug","avd","bugbank"
    ]):
        return "漏洞扫描与利用工具"
    if has_any ([
    "fofa","hunter","quake","zoomeye","shodan","0.zone","daydaymap",
    "dnslog","ceye","资产","情报","threat","sandbox",
    "ip138","备案","企查","天眼","qcc","aiqicha","qimai","xiaolanben",
    "云盘搜索","whois","map","测绘","查询"
    ]):
        return "信息收集工具"
    if has_any ([
    "社区","论坛","博客","文库","wiki","freebuf","anquanke","csdn",
    "cnblogs","t00ls","secwiki","知识库","tools论坛","棱角社区"
    ]):
        return "其他工具"
    return "其他工具"

def infer_local_sub_category (tool ):
    name =str (tool .get ("name","")or "")
    desc =str (tool .get ("description","")or "")
    path =str (tool .get ("path","")or "").replace ("\\","/")
    tool_type =str (tool .get ("type","")or "")
    tags =tool .get ("tags",[])
    if isinstance (tags ,(list ,tuple ,set )):
        tags_text =" ".join ([str (x )for x in tags ])
    else :
        tags_text =str (tags or "")
    text =(name +" "+desc +" "+path +" "+tool_type +" "+tags_text ).casefold ()

    def has_any (words ):
        return any ((w in text )for w in words )

    if has_any ([
    "gui_webshell","webshell","冰蝎","蚁剑","哥斯拉","behinder","antsword","godzilla","shell"
    ]):
        return "WebShell管理工具"
    if has_any (["抓包","代理","proxy","mitm","burp","fiddler","proxifier","wireshark","yakit"]):
        return "抓包与代理工具"
    if has_any (["免杀","bypass","av 免杀","杀软绕过"]):
        return "免杀工具"
    if has_any (["爆破","brute","hydra","字典攻击","口令爆破"]):
        return "爆破工具"
    if has_any (["后渗透","内网","横向","提权","c2","beacon","cobalt","quasar","ladon","mimikatz"]):
        return "后渗透工具"
    if has_any (["shiro","spring","struts","log4j","框架漏洞"]):
        return "框架漏洞利用工具"
    if has_any (["漏洞","cve","exp","poc","scan","xray","nuclei","sqlmap","dirsearch"]):
        return "漏洞扫描与利用工具"
    if has_any (["收集","测绘","fofa","hunter","quake","zoomeye","shodan","whois","domain","subdomain"]):
        return "信息收集工具"
    return "其他工具"

def compute_category_counts (tools_list ):
    counts ={}
    counts [""]=len (tools_list )
    # 初始化分类计数
    counts ["本地工具"]=0
    counts ["网页工具"]=0
    counts ["AI工具"]=0
    # 按工具类型分类计数
    for t in tools_list :
        main_cat =get_tool_main_category (t )
        counts [main_cat ]=counts .get (main_cat ,0 )+1

        # 统计二级分类（使用完整路径，避免本地/网页同名子类串计数）
        cat =str (t .get ("category","")or "").strip ()
        if "/"in cat :
            top ,sub =cat .split ("/",1 )
            top =top .strip ()
            sub =sub .strip ()
            if top in ("本地工具","网页工具","AI工具")and sub :
                full_key =f"{top}/{sub}"
                counts [full_key ]=counts .get (full_key ,0 )+1
        elif cat ==main_cat :
            unc_key =f"{main_cat}/其他工具"
            counts [unc_key ]=counts .get (unc_key ,0 )+1
        elif cat and cat not in ("本地工具","网页工具","AI工具"):
            # 兼容历史数据：仅保存了子分类名（如“后渗透工具”）
            full_key =f"{main_cat}/{cat}"
            counts [full_key ]=counts .get (full_key ,0 )+1
    counts ["我的收藏"]=len (get_favorite_tools (tools_list ))
    counts ["最近启动"]=len ([k for k in SETTINGS .get ("recent_tools",[])if any (t ['name']==k [0 ]and t ['category']==k [1 ]for t in tools_list )])
    return counts 

class MainWindow (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()
        if not ensure_single_instance ():
            sys .exit (0 )

        self ._perf_proc =None 

        self .tools =load_tools ()
        self ._normalize_web_uncategorized_tools ()
        # 强制只显示固定一级分类
        self .categories =["最近启动","我的收藏","本地工具","网页工具","AI工具"]
        save_categories (self .categories )

        self .tool_shortcuts ={}
        self .load_shortcuts ()
        self .registered_hotkeys ={}

        self .current_category =""
        self .search_text =""

        self .current_page =1 
        self .page_size =16 
        self .total_pages =1 


        self ._is_restarting =False 

        self .init_ui ()


        self ._btn_cursor_filter =ButtonHoverCursorFilter (self )
        QApplication .instance ().installEventFilter (self ._btn_cursor_filter )

        self .check_java_path ()
        self .init_tray ()
        self .init_shortcuts ()
        self .load_main_window_state_and_geometry ()

        QTimer .singleShot (100 ,self .refresh_grid_layout )

    def _normalize_web_uncategorized_tools (self ):
        changed =False 
        key_updates ={}
        web_subs =set (SECONDARY_CATEGORIES .get ("网页工具",[]))
        local_subs =set (SECONDARY_CATEGORIES .get ("本地工具",[]))
        ai_subs =set (SECONDARY_CATEGORIES .get ("AI工具",[]))
        for t in self .tools :
            try :
                name =str (t .get ("name","")or "")
                cat =str (t .get ("category","")or "").strip ()
                main =get_tool_main_category (t )
                new_cat =cat 
                if main =="网页工具":
                    if cat in ("","网页工具","本地工具","其他工具")or ("?"in cat ):
                        sub =infer_web_sub_category (t )
                        new_cat =f"网页工具/{sub}"
                    elif cat in web_subs :
                        new_cat =f"网页工具/{cat}"
                    elif cat .startswith ("网页工具/"):
                        sub =cat .split ("/",1 )[1 ].strip ()if "/"in cat else ""
                        if sub in web_subs or sub =="其他工具":
                            if sub =="其他工具":
                                sub =infer_web_sub_category (t )
                            new_cat =f"网页工具/{sub}"
                        else :
                            sub =infer_web_sub_category (t )
                            new_cat =f"网页工具/{sub}"
                    elif cat .startswith ("本地工具/"):
                        sub =cat .split ("/",1 )[1 ].strip ()if "/"in cat else ""
                        if sub in web_subs :
                            new_cat =f"网页工具/{sub}"
                        else :
                            sub =infer_web_sub_category (t )
                            new_cat =f"网页工具/{sub}"
                    elif "/"in cat :
                        sub =cat .split ("/",1 )[1 ].strip ()
                        if sub in web_subs :
                            new_cat =f"网页工具/{sub}"
                        else :
                            sub =infer_web_sub_category (t )
                            new_cat =f"网页工具/{sub}"
                    else :
                        sub =infer_web_sub_category (t )
                        new_cat =f"网页工具/{sub}"
                elif main =="AI工具":
                    if cat in ("","AI工具","本地工具","网页工具","其他工具")or ("?"in cat ):
                        new_cat ="AI工具/其他工具"
                    elif cat in ai_subs :
                        new_cat =f"AI工具/{cat}"
                    elif cat .startswith ("AI工具/"):
                        sub =cat .split ("/",1 )[1 ].strip ()if "/"in cat else ""
                        if sub in ai_subs :
                            new_cat =f"AI工具/{sub}"
                        else :
                            new_cat ="AI工具/其他工具"
                    else :
                        new_cat ="AI工具/其他工具"
                else :
                    if cat in ("","本地工具","网页工具","其他工具")or ("?"in cat ):
                        sub =infer_local_sub_category (t )
                        new_cat =f"本地工具/{sub}"
                    elif cat in local_subs :
                        new_cat =f"本地工具/{cat}"
                    elif cat .startswith ("本地工具/"):
                        sub =cat .split ("/",1 )[1 ].strip ()if "/"in cat else ""
                        if sub in local_subs :
                            new_cat =f"本地工具/{sub}"
                        else :
                            sub =infer_local_sub_category (t )
                            new_cat =f"本地工具/{sub}"
                    elif cat .startswith ("网页工具/"):
                        sub =cat .split ("/",1 )[1 ].strip ()if "/"in cat else ""
                        if sub in local_subs :
                            new_cat =f"本地工具/{sub}"
                        else :
                            sub =infer_local_sub_category (t )
                            new_cat =f"本地工具/{sub}"
                    elif "/"in cat :
                        sub =cat .split ("/",1 )[1 ].strip ()
                        if sub in local_subs :
                            new_cat =f"本地工具/{sub}"
                        else :
                            sub =infer_local_sub_category (t )
                            new_cat =f"本地工具/{sub}"
                    else :
                        sub =infer_local_sub_category (t )
                        new_cat =f"本地工具/{sub}"

                if new_cat !=cat :
                    t ["category"]=new_cat 
                    changed =True 
                    if name :
                        key_updates [(name ,cat )]=(name ,new_cat )
            except Exception :
                continue 
        if changed :
            try :
                save_tools (self .tools )
            except Exception :
                pass 
            try :
                for field in ("favorite_tools","recent_tools"):
                    arr =SETTINGS .get (field ,[])
                    if not isinstance (arr ,list ):
                        continue 
                    new_arr =[]
                    for item in arr :
                        if not (isinstance (item ,(list ,tuple ))and len (item )>=2 ):
                            new_arr .append (item )
                            continue 
                        k =(str (item [0 ]),str (item [1 ]))
                        if k in key_updates :
                            nk =key_updates [k ]
                            new_arr .append ([nk [0 ],nk [1 ]])
                        else :
                            new_arr .append ([k [0 ],k [1 ]])
                    SETTINGS [field ]=new_arr 
                save_settings (SETTINGS )
            except Exception :
                pass 

    def _unique_ordered (self ,seq ):
        seen =set ()
        seen_add =seen .add 
        return [x for x in seq if not (x in seen or seen_add (x ))]

    def _cat_sort_key (self ,cat ):
        if cat =="最近启动":
            return 0 
        if cat =="我的收藏":
            return 1 
        return 2 

    def _is_pro_compact_enhanced (self ):
        return (
        SETTINGS .get ("theme","dark")=="pro_compact"and 
        bool (SETTINGS .get ("pro_compact_enhanced",True ))
        )

    def _apply_pro_compact_enhancements (self ):
        enabled =self ._is_pro_compact_enhanced ()
        try :
            self .cb_search_scope .setVisible (enabled )
            if enabled :
                wanted =str (SETTINGS .get ("pro_compact_search_scope","current"))
                idx =self .cb_search_scope .findData (wanted )
                if idx >=0 :
                    self .cb_search_scope .setCurrentIndex (idx )
            else :
                idx =self .cb_search_scope .findData ("current")
                if idx >=0 :
                    self .cb_search_scope .setCurrentIndex (idx )
        except Exception :
            pass 
        try :
            self .lb_context_breadcrumb .setVisible (enabled )
        except Exception :
            pass 

    def _update_context_breadcrumb (self ):
        try :
            if not self ._is_pro_compact_enhanced ():
                self .lb_context_breadcrumb .setText ("")
                return 
            cat =str (getattr (self ,"current_category","")or "")
            cat_text ="全部工具"if not cat else cat 
            scope ="当前分类"
            try :
                scope_data =self .cb_search_scope .currentData ()
                if scope_data =="all":
                    scope ="全部工具"
            except Exception :
                pass 
            kw =str (getattr (self ,"search_text","")or "").strip ()
            if kw :
                self .lb_context_breadcrumb .setText (f"{cat_text} · 搜索范围: {scope} · 关键词: {kw}")
            else :
                self .lb_context_breadcrumb .setText (f"{cat_text} · 搜索范围: {scope}")
        except Exception :
            pass 

    def _set_left_nav_checked (self ,key ):
        try :
            for k ,btn in getattr (self ,"left_nav_buttons",{}).items ():
                btn .setChecked (k ==key )
        except Exception :
            pass 

    def _update_class_controls_visibility (self ):
        try :
            show =(getattr (self ,"left_nav_mode","all")=="all")
            self .class_main_row .setVisible (show )
            self .sub_cat_container .setVisible (show )
        except Exception :
            pass 

    def _on_left_nav_clicked (self ,key ):
        mapping ={
        "all":"",
        "recent":"最近启动",
        "favorite":"我的收藏",
        }
        self .left_nav_mode =key 
        self ._set_left_nav_checked (key )
        self ._update_class_controls_visibility ()
        if key =="all":
            try :
                self .btn_main_local .setChecked (getattr (self ,"last_main_category","本地工具")=="本地工具")
                self .btn_main_web .setChecked (getattr (self ,"last_main_category","本地工具")=="网页工具")
            except Exception :
                pass 
            self ._rebuild_sub_category_buttons (getattr (self ,"last_main_category","本地工具"))
        self .on_cat_selected (mapping .get (key ,""))

    def _on_main_class_selected (self ,main_cat ):
        self .left_nav_mode ="all"
        self .last_main_category =main_cat 
        try :
            self .btn_main_local .setChecked (main_cat =="本地工具")
            self .btn_main_web .setChecked (main_cat =="网页工具")
            self .btn_main_ai .setChecked (main_cat =="AI工具")
        except Exception :
            pass 
        self ._rebuild_sub_category_buttons (main_cat )
        self ._set_left_nav_checked ("all")
        self ._update_class_controls_visibility ()
        self .on_cat_selected (main_cat )

    def _rebuild_sub_category_buttons (self ,main_cat ):
        if not hasattr (self ,"sub_cat_layout"):
            return 
        while self .sub_cat_layout .count ()>0 :
            item =self .sub_cat_layout .takeAt (0 )
            w =item .widget ()
            if w is not None :
                w .deleteLater ()
        self .sub_cat_buttons ={}
        sub_cats =list (SECONDARY_CATEGORIES .get (main_cat ,[]))
        avail_w =max (360 ,self .sub_cat_container .width ()-20 )
        x =0 
        row =0 
        col =0 
        row_h =30 
        h_space =6 
        v_space =2 
        for sub in sub_cats :
            b =QPushButton (sub )
            b .setObjectName ("categoryBtn")
            b .setStyleSheet ("font-size: 12px; padding: 1px 6px;")
            b .setCheckable (True )
            b .clicked .connect (lambda _checked =False ,m =main_cat ,s =sub :self .on_cat_selected (f"{m}/{s}"))
            apply_button_icon (b ,sub )
            fm =b .fontMetrics ()
            bw =max (64 ,fm .horizontalAdvance (sub )+22 )
            if x >0 and x +bw >avail_w :
                row +=1 
                col =0 
                x =0 
            self .sub_cat_layout .addWidget (b ,row ,col )
            self .sub_cat_buttons [sub ]=b 
            x +=bw +h_space 
            col +=1 
        rows =row +1 if sub_cats else 1 
        self .sub_cat_container .setFixedHeight (rows *row_h +(rows -1 )*v_space +2 )
        self .sub_cat_container .updateGeometry ()

    def _refresh_sidebar_counts (self ):
        counts =compute_category_counts (self .tools )
        try :
            self .left_nav_buttons ["all"].setText (f"全部工具 ({counts.get('',0)})")
            self .left_nav_buttons ["recent"].setText (f"最近使用 ({counts.get('最近启动',0)})")
            self .left_nav_buttons ["favorite"].setText (f"我的收藏 ({counts.get('我的收藏',0)})")
            self .btn_main_local .setText (f"本地工具 ({counts.get('本地工具',0)})")
            self .btn_main_web .setText (f"网页工具 ({counts.get('网页工具',0)})")
            self .btn_main_ai .setText (f"AI工具 ({counts.get('AI工具',0)})")
        except Exception :
            pass 

    def init_ui (self ):
        self .setWindowTitle ("凭阑红蓝工具箱PBox")
        self .setWindowIcon (QIcon ("config/redblue.ico"))
        self .setWindowFlag (Qt .WindowType .FramelessWindowHint )
        self .resize (1805 ,1295 )


        self .setAcceptDrops (True )

        central =QWidget ()
        self .setCentralWidget (central )
        main_lay =QVBoxLayout (central )
        main_lay .setContentsMargins (0 ,0 ,0 ,0 )
        main_lay .setSpacing (0 )

        self .title_bar =TitleBar (self )
        main_lay .addWidget (self .title_bar )
        self .title_bar .btn_menu .show ()
        self .title_bar .btn_wx .clicked .connect (self .show_wx_dialog )
        self .title_bar .btn_github .clicked .connect (lambda :QDesktopServices .openUrl (QUrl ("https://github.com/pinglanlab/RedblueBox")))

        content_layout =QHBoxLayout ()
        content_layout .setContentsMargins (0 ,0 ,0 ,0 )
        content_layout .setSpacing (20 )

        self .sidebar =QWidget ()
        self .sidebar .setObjectName ("categoryContainer")
        self .sidebar .setFixedWidth (180 )
        side_lay =QVBoxLayout (self .sidebar )
        side_lay .setContentsMargins (10 ,12 ,10 ,12 )
        side_lay .setSpacing (8 )

        self .left_nav_buttons ={}
        b_all =QPushButton ("全部工具")
        b_all .setObjectName ("categoryBtn")
        b_all .setCheckable (True )
        b_all .clicked .connect (lambda _checked =False :self ._on_left_nav_clicked ("all"))
        apply_button_icon (b_all ,"全部工具")
        side_lay .addWidget (b_all )
        self .left_nav_buttons ["all"]=b_all 

        for key ,txt in [("recent","最近使用"),("favorite","我的收藏")]:
            b =QPushButton (txt )
            b .setObjectName ("categoryBtn")
            b .setCheckable (True )
            b .clicked .connect (lambda _checked =False ,k =key :self ._on_left_nav_clicked (k ))
            apply_button_icon (b ,txt )
            side_lay .addWidget (b )
            self .left_nav_buttons [key ]=b 
        side_lay .addStretch ()

        self .btn_community =QPushButton ("安全社区")
        self .btn_community .setObjectName ("categoryBtn")
        self .btn_community .clicked .connect (lambda :QDesktopServices .openUrl (QUrl ("https://fssp.cncve.org.cn")))
        apply_button_icon (self .btn_community ,"安全社区")
        side_lay .addWidget (self .btn_community )

        self .btn_security_test_side =QPushButton ("安全众测")
        self .btn_security_test_side .setObjectName ("categoryBtn")
        self .btn_security_test_side .clicked .connect (lambda :QDesktopServices .openUrl (QUrl ("https://zc.cncve.org.cn")))
        apply_button_icon (self .btn_security_test_side ,"安全众测")
        side_lay .addWidget (self .btn_security_test_side )

        self .btn_vulnerability_db_side =QPushButton ("安全漏洞")
        self .btn_vulnerability_db_side .setObjectName ("categoryBtn")
        self .btn_vulnerability_db_side .clicked .connect (lambda :QDesktopServices .openUrl (QUrl ("https://www.cncve.org.cn")))
        apply_button_icon (self .btn_vulnerability_db_side ,"安全漏洞")
        side_lay .addWidget (self .btn_vulnerability_db_side )

        self .btn_settings_side =QPushButton ("设置")
        self .btn_settings_side .setObjectName ("categoryBtn")
        self .btn_settings_side .clicked .connect (self .show_settings )
        apply_button_icon (self .btn_settings_side ,"设置")
        side_lay .addWidget (self .btn_settings_side )

        self .btn_about_side =QPushButton ("关于")
        self .btn_about_side .setObjectName ("categoryBtn")
        self .btn_about_side .clicked .connect (self .show_about )
        apply_button_icon (self .btn_about_side ,"关于")
        side_lay .addWidget (self .btn_about_side )

        content_layout .addWidget (self .sidebar )

        right_panel =QWidget ()
        rlayout =QVBoxLayout (right_panel )
        rlayout .setContentsMargins (0 ,0 ,0 ,0 )
        rlayout .setSpacing (0 )

        topbar =QWidget ()
        hl =QHBoxLayout (topbar )
        hl .setContentsMargins (10 ,8 ,10 ,6 )

        self .search_bar =SearchBar ()
        self .search_bar .search_changed .connect (self .on_search )
        self .search_bar .setMinimumWidth (220 )
        self .search_bar .setMaximumWidth (520 )
        hl .addWidget (self .search_bar )

        self .cb_search_scope =QComboBox ()
        self .cb_search_scope .addItem ("当前分类","current")
        self .cb_search_scope .addItem ("全部工具","all")
        wanted_scope =str (SETTINGS .get ("pro_compact_search_scope","current"))
        idx =self .cb_search_scope .findData (wanted_scope )
        if idx >=0 :
            self .cb_search_scope .setCurrentIndex (idx )
        self .cb_search_scope .setFixedWidth (110 )
        self .cb_search_scope .currentIndexChanged .connect (lambda _ :self ._on_search_scope_changed ())
        self .cb_search_scope .hide ()

        self .shortcut_find =QShortcut (QKeySequence ("Ctrl+F"),self )
        self .shortcut_find .activated .connect (self ._focus_search )

        # 将按钮添加到标题栏的下拉菜单中
        self .title_bar .menu .clear ()
        
        # 添加工具
        action_add_tool =self .title_bar .menu .addAction ("添加工具")
        action_add_tool .setIcon (get_ui_icon ("添加工具"))
        action_add_tool .triggered .connect (self .add_tool )
        
        # 记事本
        action_notebook =self .title_bar .menu .addAction ("记事本")
        action_notebook .setIcon (get_ui_icon ("记事本"))
        action_notebook .triggered .connect (self .open_notebook )
        
        # 批量模式
        action_batch_mode =self .title_bar .menu .addAction ("批量模式")
        action_batch_mode .setIcon (get_ui_icon ("批量模式"))
        action_batch_mode .triggered .connect (self .toggle_batch_mode )
        
        # 导入
        action_import =self .title_bar .menu .addAction ("工具导入")
        action_import .setIcon (get_ui_icon ("工具导入"))
        action_import .triggered .connect (self .import_data )
        
        # 导出
        action_export =self .title_bar .menu .addAction ("工具导出")
        action_export .setIcon (get_ui_icon ("工具导出"))
        action_export .triggered .connect (self .export_data )
        
        self .btn_run_batch =QPushButton ("运行选中")
        self .btn_run_batch .setObjectName ("noHoverBtn")
        self .btn_run_batch .setFixedWidth (100 )
        self .btn_run_batch .clicked .connect (self .do_batch_run )
        apply_button_icon (self .btn_run_batch ,"运行选中")
        self .btn_run_batch .hide ()

        self .btn_top_add_tool =QPushButton ("添加工具")
        self .btn_top_add_tool .setObjectName ("noHoverBtn")
        self .btn_top_add_tool .clicked .connect (self .add_tool )
        apply_button_icon (self .btn_top_add_tool ,"添加工具")
        hl .addWidget (self .btn_top_add_tool )

        self .btn_top_notebook =QPushButton ("记事本")
        self .btn_top_notebook .setObjectName ("noHoverBtn")
        self .btn_top_notebook .clicked .connect (self .open_notebook )
        apply_button_icon (self .btn_top_notebook ,"记事本")
        hl .addWidget (self .btn_top_notebook )

        self .btn_top_batch_mode =QPushButton ("批量模式")
        self .btn_top_batch_mode .setObjectName ("noHoverBtn")
        self .btn_top_batch_mode .clicked .connect (self .toggle_batch_mode )
        apply_button_icon (self .btn_top_batch_mode ,"批量模式")
        hl .addWidget (self .btn_top_batch_mode )

        self .btn_top_import =QPushButton ("工具导入")
        self .btn_top_import .setObjectName ("noHoverBtn")
        self .btn_top_import .clicked .connect (self .import_data )
        apply_button_icon (self .btn_top_import ,"工具导入")
        hl .addWidget (self .btn_top_import )

        self .btn_top_export =QPushButton ("工具导出")
        self .btn_top_export .setObjectName ("noHoverBtn")
        self .btn_top_export .clicked .connect (self .export_data )
        apply_button_icon (self .btn_top_export ,"工具导出")
        hl .addWidget (self .btn_top_export )

        hl .addStretch ()
        hl .addWidget (self .btn_run_batch )

        title_lay =self .title_bar .main_layout
        title_lay .insertSpacing (3 ,36 )
        self .search_bar .setMinimumWidth (160 )
        self .search_bar .setMaximumWidth (460 )
        title_lay .insertWidget (4 ,self .search_bar ,1 )
        self .btn_top_add_tool .hide ()
        self .btn_top_notebook .hide ()
        self .btn_top_batch_mode .hide ()
        self .btn_top_import .hide ()
        self .btn_top_export .hide ()
        self .btn_run_batch .hide ()
        topbar .hide ()

        topbar .setLayout (hl )
        rlayout .addWidget (topbar )

        class_main_row =QWidget ()
        self .class_main_row =class_main_row 
        class_main_lay =QHBoxLayout (class_main_row )
        class_main_lay .setContentsMargins (10 ,0 ,10 ,0 )
        class_main_lay .setSpacing (8 )
        self .btn_main_local =QPushButton ("本地工具")
        self .btn_main_local .setObjectName ("categoryBtn")
        self .btn_main_local .setStyleSheet ("font-size: 17px; font-weight: 700; padding: 6px 10px;")
        self .btn_main_local .setCheckable (True )
        self .btn_main_local .clicked .connect (lambda _checked =False :self ._on_main_class_selected ("本地工具"))
        apply_button_icon (self .btn_main_local ,"本地工具")
        self .btn_main_web =QPushButton ("网页工具")
        self .btn_main_web .setObjectName ("categoryBtn")
        self .btn_main_web .setStyleSheet ("font-size: 17px; font-weight: 700; padding: 6px 10px;")
        self .btn_main_web .setCheckable (True )
        self .btn_main_web .clicked .connect (lambda _checked =False :self ._on_main_class_selected ("网页工具"))
        apply_button_icon (self .btn_main_web ,"网页工具")
        self .btn_main_ai =QPushButton ("AI工具")
        self .btn_main_ai .setObjectName ("categoryBtn")
        self .btn_main_ai .setStyleSheet ("font-size: 17px; font-weight: 700; padding: 6px 10px;")
        self .btn_main_ai .setCheckable (True )
        self .btn_main_ai .clicked .connect (lambda _checked =False :self ._on_main_class_selected ("AI工具"))
        apply_button_icon (self .btn_main_ai ,"AI工具")
        class_main_lay .addWidget (self .btn_main_local )
        class_main_lay .addWidget (self .btn_main_web )
        class_main_lay .addWidget (self .btn_main_ai )
        class_main_lay .addStretch ()
        rlayout .addWidget (class_main_row )

        self .sub_cat_container =QWidget ()
        from PyQt6.QtWidgets import QGridLayout as _QGridLayout
        self .sub_cat_layout =_QGridLayout (self .sub_cat_container )
        self .sub_cat_layout .setContentsMargins (10 ,0 ,10 ,0 )
        self .sub_cat_layout .setHorizontalSpacing (6 )
        self .sub_cat_layout .setVerticalSpacing (2 )
        self .sub_cat_layout .setAlignment (Qt .AlignmentFlag .AlignTop |Qt .AlignmentFlag .AlignLeft )
        rlayout .addWidget (self .sub_cat_container )

        self .lb_context_breadcrumb =QLabel ("")
        self .lb_context_breadcrumb .setObjectName ("contextBreadcrumb")
        self .lb_context_breadcrumb .setContentsMargins (10 ,0 ,10 ,6 )
        rlayout .addWidget (self .lb_context_breadcrumb )

        self .tool_grid =ModernToolGrid ()
        self .tool_grid .tool_run .connect (self .run_tool )
        self .tool_grid .tool_edit .connect (self .edit_tool )
        self .tool_grid .tool_delete .connect (self .delete_tool )
        self .tool_grid .favorite_changed .connect (self .on_favorite_changed )
        self .tool_grid .batch_run_requested .connect (self .run_tools_batch )
        rlayout .addWidget (self .tool_grid )

        self .empty_state_label =QLabel ("暂无数据")
        self .empty_state_label .setAlignment (Qt .AlignmentFlag .AlignCenter )
        self .empty_state_label .setStyleSheet ("font-size: 16px; color: #8A8A92; padding: 24px;")
        self .empty_state_label .setSizePolicy (QSizePolicy .Policy .Expanding ,QSizePolicy .Policy .Expanding )
        self .empty_state_label .hide ()
        rlayout .addWidget (self .empty_state_label )


        self .page_widget =QWidget ()
        page_layout =QHBoxLayout (self .page_widget )
        page_layout .setContentsMargins (0 ,5 ,0 ,5 )
        page_layout .setSpacing (0 )

        self .page_controls_widget =QWidget ()
        page_controls_layout =QHBoxLayout (self .page_controls_widget )
        page_controls_layout .setContentsMargins (0 ,0 ,0 ,0 )
        page_controls_layout .setSpacing (6 )

        self .btn_prev =QPushButton ("上一页")
        self .btn_prev .setObjectName ("noHoverBtn")
        self .btn_prev .setFixedWidth (80 )
        self .btn_prev .clicked .connect (self .prev_page )
        apply_button_icon (self .btn_prev ,"上一页")

        self .lb_page =QLabel ("1 / 1")
        self .lb_page .setAlignment (Qt .AlignmentFlag .AlignCenter )

        self .btn_next =QPushButton ("下一页")
        self .btn_next .setObjectName ("noHoverBtn")
        self .btn_next .setFixedWidth (80 )
        self .btn_next .clicked .connect (self .next_page )
        apply_button_icon (self .btn_next ,"下一页")

        self .ed_page_jump =QLineEdit ()
        self .ed_page_jump .setFixedWidth (50 )
        self .ed_page_jump .setPlaceholderText ("页码")
        self .ed_page_jump .setAlignment (Qt .AlignmentFlag .AlignCenter )
        self .ed_page_jump .returnPressed .connect (self .jump_to_page )

        self .btn_jump =QPushButton ("跳转")
        self .btn_jump .setObjectName ("noHoverBtn")
        self .btn_jump .setFixedWidth (60 )
        self .btn_jump .clicked .connect (self .jump_to_page )
        apply_button_icon (self .btn_jump ,"跳转")
        self .lb_perf_bottom =QLabel ("")
        self .lb_perf_bottom .setAlignment (Qt .AlignmentFlag .AlignRight |Qt .AlignmentFlag .AlignVCenter )
        self .lb_perf_bottom .setStyleSheet ("font-size:12px; color:#8A8A92; padding-right: 12px;")

        page_controls_layout .addStretch ()
        page_controls_layout .addWidget (self .btn_prev )
        page_controls_layout .addWidget (self .lb_page )
        page_controls_layout .addWidget (self .btn_next )
        page_controls_layout .addSpacing (20 )
        page_controls_layout .addWidget (self .ed_page_jump )
        page_controls_layout .addWidget (self .btn_jump )
        page_controls_layout .addStretch ()

        page_layout .addWidget (self .page_controls_widget ,1 )
        page_layout .addWidget (self .lb_perf_bottom ,0 ,Qt .AlignmentFlag .AlignRight |Qt .AlignmentFlag .AlignBottom )

        rlayout .addWidget (self .page_widget )

        content_layout .addWidget (right_panel )
        main_lay .addLayout (content_layout )

        self .apply_theme ()
        self .update_cat_panel ()
        self .update_tool_grid ()

        self .init_perf_monitor ()
        self ._apply_pro_compact_enhancements ()
        self ._update_context_breadcrumb ()
        self .left_nav_mode ="all"
        self .last_main_category ="本地工具"
        self ._set_left_nav_checked ("all")
        self .btn_main_local .setChecked (True )
        self .btn_main_web .setChecked (False )
        self .btn_main_ai .setChecked (False )
        self ._rebuild_sub_category_buttons ("本地工具")
        QTimer .singleShot (0 ,lambda :self ._rebuild_sub_category_buttons (getattr (self ,"last_main_category","本地工具")))
        self .on_cat_selected ("")
        self ._update_class_controls_visibility ()

    def _on_search_scope_changed (self ):
        try :
            SETTINGS ["pro_compact_search_scope"]=str (self .cb_search_scope .currentData ()or "current")
            save_settings (SETTINGS )
        except Exception :
            pass 
        if str (getattr (self ,"search_text","")or "").strip ():
            self .update_tool_grid ()
        self ._update_context_breadcrumb ()


    def init_perf_monitor (self ):
        try :
            import psutil 
            self ._perf_proc =psutil .Process (os .getpid ())
            try :
                self ._perf_proc .cpu_percent (None )
            except Exception :
                pass 
        except Exception :
            self ._perf_proc =None 

        self ._perf_timer =QTimer (self )
        self ._perf_timer .setInterval (5000 )
        self ._perf_timer .timeout .connect (self .update_perf_monitor )
        self ._perf_timer .start ()
        self .update_perf_monitor ()


    def update_perf_monitor (self ):
        try :
            target =getattr (self ,"lb_perf_bottom",None )
            if target is None :
                return 

            if self ._perf_proc is None :
                target .setText ("CPU N/A | 内存 N/A")
                return 

            cpu =0.0 
            mem_mb =0.0 
            mem_pct =0.0 
            try :
                cpu =float (self ._perf_proc .cpu_percent (None ))
            except Exception :
                cpu =0.0 
            try :
                mem_mb =float (self ._perf_proc .memory_info ().rss )/1024.0 /1024.0 
            except Exception :
                mem_mb =0.0 

            try :
                import psutil 
                vm =psutil .virtual_memory ()
                if getattr (vm ,"total",0 ):
                    mem_pct =(float (self ._perf_proc .memory_info ().rss )/float (vm .total ))*100.0 
            except Exception :
                mem_pct =0.0 

            target .setText (f"CPU {cpu:.1f}% | 内存 {mem_mb:.0f}MB({mem_pct:.1f}%)")
        except Exception :
            try :
                target =getattr (self ,"lb_perf_bottom",None )
                if target is not None :
                    target .setText ("CPU N/A | 内存 N/A")
            except Exception :
                pass 

    def _focus_search (self ):
        try :
            self .search_bar .search_input .setFocus ()
            self .search_bar .search_input .selectAll ()
        except Exception :
            pass 

    def dragEnterEvent (self ,event ):
        try :
            if event .mimeData ().hasUrls ():
                event .acceptProposedAction ()
                return 
        except Exception :
            pass 
        event .ignore ()

    def dropEvent (self ,event ):
        try :
            if not event .mimeData ().hasUrls ():
                event .ignore ()
                return 

            paths =[]
            for u in event .mimeData ().urls ():
                try :
                    p =u .toLocalFile ()
                except Exception :
                    p =""
                if p :
                    paths .append (p )

            if not paths :
                event .ignore ()
                return 


            self ._open_add_tool_dialog_with_path (paths [0 ])
            event .acceptProposedAction ()
        except Exception as e :
            QMessageBox .warning (self ,"拖拽添加",str (e ))
            event .ignore ()

    def _open_add_tool_dialog_with_path (self ,path :str ):

        if getattr (self ,"current_category","")in ("","最近启动","我的收藏"):
            QMessageBox .information (self ,"提示","此工具分类不允许拖拽添加程序的工具卡片")
            return 


        if not os .path .isfile (path ):
            QMessageBox .information (self ,"提示","仅支持拖拽程序文件添加工具卡片")
            return 

        ext =os .path .splitext (path )[1 ].lower ()
        allowed ={".vbs",".bat",".py",".jar",".exe"}
        if ext not in allowed :
            QMessageBox .information (self ,"提示","仅支持拖拽 vbs/bat/py/jar/exe 文件")
            return 

        self .disable_all_hotkeys ()
        try :
            diag =ToolDialog (self .categories ,None ,self )

            base =os .path .basename (path .rstrip ("\\/"))
            name =os .path .splitext (base )[0 ]if os .path .isfile (path )else base 
            if hasattr (diag ,"ed_name"):
                diag .ed_name .setText (name )
            if hasattr (diag ,"ed_path"):
                diag .ed_path .setText (path )
            if hasattr (diag ,"cb_cat")and getattr (self ,"current_category","")not in ("","最近启动","我的收藏"):
                diag .cb_cat .setCurrentText (self .current_category )


            if hasattr (diag ,"cb_type"):
                type_map ={
                ".py":"Python",
                ".jar":"JAVA8",
                ".exe":"GUI应用",
                ".bat":"批处理",
                ".vbs":"批处理",
                }
                want =type_map .get (ext )
                if want :
                    diag .cb_type .setCurrentText (want )

            if diag .exec ():
                td =diag .get_tool_data ()
                if td ["type"]=="网页":
                    if not td ["name"]or not td ["url"]or not td ["category"]:
                        QMessageBox .warning (self ,"错误","请填写所有必填字段")
                    else :
                        if not self ._add_new_tool (td ):
                            QMessageBox .warning (self ,"错误","保存工具数据失败")
                else :
                    if not td ["name"]or not td ["category"]or not td ["path"]:
                        QMessageBox .warning (self ,"错误","请填写所有必填字段")
                    else :
                        if check_environment (td ["type"]):
                            if not self ._add_new_tool (td ):
                                QMessageBox .warning (self ,"错误","保存工具数据失败")

                if diag .shortcut_key :
                    self .tool_shortcuts [td ['name']]=diag .shortcut_key 
                    self .save_shortcuts ()
        finally :
            self .re_register_hotkeys ()
            self .update_tool_grid ()

    def refresh_grid_layout (self ):
        try :
            self .tool_grid .adjust_card_size ()
            self ._recompute_page_size_if_needed ()
        except Exception as e :
            logger .error (f"刷新卡片布局异常: {e}")

    def _recompute_page_size_if_needed (self ):
        try :
            if SETTINGS .get ("display_mode","scroll")!="paged":
                return 


            if not self .isMaximized ():
                new_page_size =20 
            else :
                grid_size =self .tool_grid .gridSize ()
                if grid_size .width ()<=0 or grid_size .height ()<=0 :
                    return 
                vp =self .tool_grid .viewport ().size ()
                cols =max (1 ,vp .width ()//grid_size .width ())
                rows =max (1 ,vp .height ()//grid_size .height ())
                new_page_size =max (1 ,cols *rows )

            if new_page_size !=self .page_size :
                self .page_size =new_page_size 
                self .current_page =1 
                self .update_tool_grid ()
        except Exception as e :
            logger .error (f"自适应分页数量异常: {e}")

    def resizeEvent (self ,e ):
        super ().resizeEvent (e )

        self ._recompute_page_size_if_needed ()
        try :
            if getattr (self ,"left_nav_mode","all")=="all":
                self ._rebuild_sub_category_buttons (getattr (self ,"last_main_category","本地工具"))
        except Exception :
            pass 

    def prev_page (self ):
        if self .current_page >1 :
            self .current_page -=1 
            self .update_tool_grid ()

    def next_page (self ):
        if self .current_page <self .total_pages :
            self .current_page +=1 
            self .update_tool_grid ()

    def jump_to_page (self ):
        txt =self .ed_page_jump .text ().strip ()
        if not txt .isdigit ():
            return 
        val =int (txt )
        if 1 <=val <=self .total_pages :
            self .current_page =val 
            self .update_tool_grid ()
            self .ed_page_jump .clear ()
        else :
            msg =QMessageBox (self )
            msg .setWindowTitle ("提示")
            msg .setText (f"页码超出范围 (1-{self.total_pages})")
            msg .setIcon (QMessageBox .Icon .Warning )
            ok_btn =msg .addButton ("确定",QMessageBox .ButtonRole .AcceptRole )
            msg .setDefaultButton (ok_btn )
            msg .exec ()

    def import_data (self ):
        try :
            path ,_ =QFileDialog .getOpenFileName (self ,"选择导入文件","","JSON Files (*.json)")
            if path :
                mode ,ok =QInputDialog .getItem (self ,"导入方式","请选择导入方式：",["合并","覆盖"],0 ,False )
                if ok :
                    import_all_data (path ,"overwrite"if mode =="覆盖"else "merge")
                    QMessageBox .information (self ,"导入","导入完成，请重启或刷新")
                    self .reload_data ()
        except Exception as e :
            QMessageBox .warning (self ,"导入错误",str (e ))

    def export_data (self ):
        try :
            path ,_ =QFileDialog .getSaveFileName (self ,"导出为","","JSON Files (*.json)")
            if path :
                export_all_data (path )
                QMessageBox .information (self ,"导出","导出完成！")
        except Exception as e :
            QMessageBox .warning (self ,"导出错误",str (e ))


    def reload_data (self ):
        self .tools =load_tools ()
        self .categories =load_categories ()
        self .apply_theme ()
        self .update_cat_panel ()
        self .update_tool_grid ()
        self .refresh_grid_layout ()

    def apply_theme (self ):
        from config import STYLESHEET 
        try :
            app =QApplication .instance ()
            if app is not None :
                app .setStyleSheet (STYLESHEET )
            else :
                self .setStyleSheet (STYLESHEET )
        except Exception :
            self .setStyleSheet (STYLESHEET )


        try :
            from utils import install_liquid_glass_animations 
            install_liquid_glass_animations (self )
        except Exception :
            pass 

        try :
            from utils import install_red_blue_glass_popup_blur 
            install_red_blue_glass_popup_blur (self )
        except Exception :
            pass 


        theme_name =SETTINGS .get ("theme","dark")
        hwnd =int (self .winId ())
        effect =WindowEffect ()

        if theme_name in ("liquid_glass","red_blue_glass","custom_image"):

            effect .set_acrylic_effect (hwnd ,is_dark =True )
        else :
            effect .remove_background_effect (hwnd )
        self ._apply_pro_compact_enhancements ()
        self ._update_context_breadcrumb ()

    def paintEvent (self ,event ):
        if SETTINGS .get ("theme")=="custom_image":
            image_path =SETTINGS .get ("custom_bg_path","")
            if image_path and os .path .isfile (image_path ):
                painter =QPainter (self )
                pix =QPixmap (image_path )
                if not pix .isNull ():
                    scaled_pix =pix .scaled (self .width (),self .height (),
                    Qt .AspectRatioMode .KeepAspectRatioByExpanding ,
                    Qt .TransformationMode .SmoothTransformation )
                    x =(self .width ()-scaled_pix .width ())//2 
                    y =(self .height ()-scaled_pix .height ())//2 
                    painter .drawPixmap (x ,y ,scaled_pix )
        super ().paintEvent (event )



    def update_cat_panel (self ):
        self ._refresh_sidebar_counts ()
        self ._update_class_controls_visibility ()

    def update_tool_grid (self ):
        from utils import get_favorite_tools ,get_recent_tools ,fuzzy_search 

        category =self .current_category 
        search_text =self .search_text 
        search_scope ="current"
        if self ._is_pro_compact_enhanced ():
            try :
                search_scope =str (self .cb_search_scope .currentData ()or "current")
            except Exception :
                search_scope ="current"

        try :
            if category =="我的收藏":
                filtered =get_favorite_tools (self .tools )
            elif category =="最近启动":
                filtered =get_recent_tools (self .tools )
            elif category =="本地工具":
                filtered =[t for t in self .tools if get_tool_main_category (t )=="本地工具"]
            elif category =="网页工具":
                filtered =[t for t in self .tools if get_tool_main_category (t )=="网页工具"]
            elif category =="AI工具":
                filtered =[t for t in self .tools if get_tool_main_category (t )=="AI工具"]
            elif category :
                # 处理二级分类：兼容“父/子分类”和仅“子分类”两种历史数据格式
                if "/"in category :
                    parent ,sub =category .split ("/",1 )
                    parent =parent .strip ()
                    sub =sub .strip ()
                    if sub =="其他工具":
                        filtered =[
                        t for t in self .tools 
                        if (
                        get_tool_main_category (t )==parent and 
                        str (t .get ("category","")or "").strip ()in (parent ,f"{parent}/其他工具")
                        )
                        ]
                    else :
                        filtered =[
                        t for t in self .tools 
                        if (
                        str (t .get ("category","")or "").strip ()==category or 
                        (
                        str (t .get ("category","")or "").strip ()==sub and 
                        get_tool_main_category (t )==parent 
                        )
                        )
                        ]
                else :
                    filtered =[t for t in self .tools if str (t .get ("category","")or "").strip ()==category ]
            else :
                filtered =self .tools 

            if search_text :
                if search_scope =="all":
                    filtered =fuzzy_search (self .tools ,search_text )
                else :
                    filtered =fuzzy_search (filtered ,search_text )
        except Exception as e :
            logger .error (f"分类筛选失败，已回退到全部工具: {e}")
            self .current_category =""
            filtered =self .tools 
            if search_text :
                filtered =fuzzy_search (filtered ,search_text )


        seen =set ()
        final =[]
        for t in filtered :
            k =(t ['name'],t ['category'])
            if k not in seen :
                seen .add (k )
                final .append (t )


        final .sort (key =lambda x :(-int (x .get ("weight",0 )or 0 ),str (x .get ('name',''))))


        disp =SETTINGS .get ("display_mode","scroll")

        if disp =="paged":
            self .page_widget .show ()
            self .page_controls_widget .show ()
            total_items =len (final )
            if total_items ==0 :
                self .total_pages =1 
                self .current_page =1 
                display_tools =[]
            else :
                self .total_pages =(total_items +self .page_size -1 )//self .page_size 
                if self .current_page >self .total_pages :
                    self .current_page =self .total_pages 
                if self .current_page <1 :
                    self .current_page =1 

                start_idx =(self .current_page -1 )*self .page_size 
                end_idx =start_idx +self .page_size 
                display_tools =final [start_idx :end_idx ]

            self .lb_page .setText (f"{self.current_page} / {self.total_pages}")
            self .btn_prev .setEnabled (self .current_page >1 )
            self .btn_next .setEnabled (self .current_page <self .total_pages )
        else :
            self .page_widget .show ()
            self .page_controls_widget .hide ()
            display_tools =final 

        self .tool_grid .set_final_tools (display_tools )
        is_empty =(len (final )==0 )
        self .tool_grid .setVisible (not is_empty )
        self .empty_state_label .setVisible (is_empty )
        if is_empty :
            cat =str (self .current_category or "").strip ()
            if cat :
                self .empty_state_label .setText (f"{cat} 暂无数据")
            else :
                self .empty_state_label .setText ("暂无数据")


        try :
            from utils import animate_liquid_glass_fade 
            animate_liquid_glass_fade (self .tool_grid )
        except Exception :
            pass 
        self ._update_context_breadcrumb ()
        self .refresh_grid_layout ()

    def on_cat_selected (self ,cat ):
        self .current_category =cat 
        self .current_page =1 
        if cat =="":
            self .left_nav_mode ="all"
            self ._set_left_nav_checked ("all")
        elif cat =="最近启动":
            self .left_nav_mode ="recent"
            self ._set_left_nav_checked ("recent")
        elif cat =="我的收藏":
            self .left_nav_mode ="favorite"
            self ._set_left_nav_checked ("favorite")
        else :
            self .left_nav_mode ="all"
            self ._set_left_nav_checked ("all")
            if cat .startswith ("本地工具"):
                self .last_main_category ="本地工具"
                self .btn_main_local .setChecked (True )
                self .btn_main_web .setChecked (False )
                self .btn_main_ai .setChecked (False )
                self ._rebuild_sub_category_buttons ("本地工具")
                if "/"in cat :
                    sub =cat .split ("/",1 )[1 ]
                    for k ,b in self .sub_cat_buttons .items ():
                        b .setChecked (k ==sub )
                else :
                    for b in self .sub_cat_buttons .values ():
                        b .setChecked (False )
            elif cat .startswith ("网页工具"):
                self .last_main_category ="网页工具"
                self .btn_main_local .setChecked (False )
                self .btn_main_web .setChecked (True )
                self .btn_main_ai .setChecked (False )
                self ._rebuild_sub_category_buttons ("网页工具")
                if "/"in cat :
                    sub =cat .split ("/",1 )[1 ]
                    for k ,b in self .sub_cat_buttons .items ():
                        b .setChecked (k ==sub )
                else :
                    for b in self .sub_cat_buttons .values ():
                        b .setChecked (False )
            elif cat .startswith ("AI工具"):
                self .last_main_category ="AI工具"
                self .btn_main_local .setChecked (False )
                self .btn_main_web .setChecked (False )
                self .btn_main_ai .setChecked (True )
                self ._rebuild_sub_category_buttons ("AI工具")
                if "/"in cat :
                    sub =cat .split ("/",1 )[1 ]
                    for k ,b in self .sub_cat_buttons .items ():
                        b .setChecked (k ==sub )
                else :
                    for b in self .sub_cat_buttons .values ():
                        b .setChecked (False )
        self ._update_class_controls_visibility ()
        try :
            self .update_tool_grid ()
        except Exception as e :
            logger .error (f"切换分类失败: {cat}, {e}")
            self .current_category =""
            self .current_page =1 
            self .update_tool_grid ()

    def on_cat_renamed (self ,old_name ,new_name ):
        old_name =str (old_name or "").strip ()
        new_name =str (new_name or "").strip ()
        if not new_name :
            QMessageBox .warning (self ,"错误","分类名称不能为空")
            return 
        norm =new_name .casefold ()
        if any (str (x ).strip ().casefold ()==norm for x in (self .categories or [])if str (x ).strip ()!=old_name ):
            QMessageBox .warning (self ,"错误",f"分类 '{new_name}' 已存在！")
            return 

        if old_name in self .categories :
            idx =self .categories .index (old_name )
            self .categories [idx ]=new_name 
        if save_tools (self .tools ):
            self .update_cat_panel ()
            self .update_tool_grid ()
        else :
            QMessageBox .warning (self ,"错误","保存工具数据失败")

    def on_cat_deleted (self ,cat ):
        if cat in ("我的收藏","最近启动"):
            QMessageBox .warning (self ,"提示","此分区不允许删除")
            return 
        tools_in_category =[t for t in self .tools if t ["category"]==cat ]
        if not tools_in_category :
            if cat in self .categories :
                self .categories .remove (cat )
                save_categories (self .categories )
                self .update_cat_panel ()
            return 
        else :
            msg =QMessageBox (self )
            msg .setWindowTitle ("确认删除")
            msg .setIcon (QMessageBox .Icon .Question )
            msg .setText (f"分类 '{cat}' 下共有 {len(tools_in_category)} 个工具，删除该分类会一并删除这些工具。\n是否继续？")
            msg .setStandardButtons (QMessageBox .StandardButton .Yes |QMessageBox .StandardButton .No )
            result =msg .exec ()

            if result ==QMessageBox .StandardButton .Yes :
                self .tools =[t for t in self .tools if t ["category"]!=cat ]
                if cat in self .categories :
                    self .categories .remove (cat )
                if save_tools (self .tools )and save_categories (self .categories ):
                    self .current_category =""
                    self .update_cat_panel ()
                    self .update_tool_grid ()
                else :
                    QMessageBox .warning (self ,"错误","保存数据失败，无法完成删除操作。")

    def on_cat_move (self ,cat ,direction ):
        if cat not in self .categories or cat in ("我的收藏","最近启动"):
            return 
        idx =self .categories .index (cat )
        new_idx =idx +direction 
        min_idx =2 if "最近启动"in self .categories and "我的收藏"in self .categories else 0 
        if new_idx <min_idx or new_idx >=len (self .categories ):
            return 
        self .categories .pop (idx )
        self .categories .insert (new_idx ,cat )
        save_categories (self .categories )
        self .update_cat_panel ()

    def on_cat_added (self ,_ ):
        new_cat ,ok =QInputDialog .getText (self ,"新建分类","请输入分类名称:")
        if ok and new_cat .strip ():
            new_cat =new_cat .strip ()

            norm =new_cat .casefold ()
            if any (str (x ).strip ().casefold ()==norm for x in (self .categories or [])):
                QMessageBox .warning (self ,"错误",f"分类 '{new_cat}' 已存在！")
                return 

            self .categories .append (new_cat )
            self .categories =sorted (set (self .categories ),key =self ._cat_sort_key )
            save_categories (self .categories )
            self .update_cat_panel ()

    def on_search (self ,txt ):
        self .search_text =(txt or "").strip ()
        self .current_page =1 
        self .update_tool_grid ()
        self ._update_context_breadcrumb ()
        self .refresh_grid_layout ()

    def disable_all_hotkeys (self ):
        for tool_name ,hotkey in list (self .registered_hotkeys .items ()):
            try :
                keyboard .remove_hotkey (hotkey )
            except :
                pass 
        self .registered_hotkeys .clear ()

    def re_register_hotkeys (self ):
        for nm ,hk in self .tool_shortcuts .items ():
            self .register_hotkey (nm ,hk )

    def add_tool (self ):
        self .disable_all_hotkeys ()
        try :
            diag =ToolDialog (self .categories ,None ,self )
            if diag .exec ():
                td =diag .get_tool_data ()
                if td ["type"]=="网页":
                    if not td ["name"]or not td ["url"]or not td ["category"]:
                        QMessageBox .warning (self ,"错误","请填写所有必填字段")
                    else :
                        if not self ._add_new_tool (td ):
                            QMessageBox .warning (self ,"错误","保存工具数据失败")
                else :
                    if not td ["name"]or not td ["category"]or not td ["path"]:
                        QMessageBox .warning (self ,"错误","请填写所有必填字段")
                    else :
                        if check_environment (td ["type"]):
                            if not self ._add_new_tool (td ):
                                QMessageBox .warning (self ,"错误","保存工具数据失败")

                if diag .shortcut_key :
                    self .tool_shortcuts [td ['name']]=diag .shortcut_key 
                    self .save_shortcuts ()
        except Exception as e :
            QMessageBox .warning (self ,"添加工具异常",str (e ))
        self .re_register_hotkeys ()
        self .update_tool_grid ()

    def _add_new_tool (self ,td ):

        td_name =str (td .get ('name','')).strip ()
        norm =td_name .casefold ()
        for ex in (self .tools or []):
            ex_name =str (ex .get ('name','')).strip ()
            if ex_name and ex_name .casefold ()==norm :
                QMessageBox .warning (self ,"错误","已存在同名工具，工具名称必须唯一")
                return True 

        self .tools .append (td )
        # 不再添加新的分类，保持分类列表固定为["最近启动","我的收藏","本地工具","网页工具"]

        if save_tools (self .tools ):
            self .update_cat_panel ()
            self .update_tool_grid ()
            return True 
        return False 

    def edit_tool (self ,tool_data ):
        self .disable_all_hotkeys ()
        try :
            diag =ToolDialog (self .categories ,tool_data ,self )
            old_name =tool_data ['name']
            if diag .exec ():
                newinfo =diag .get_tool_data ()


                new_name =str (newinfo .get ('name','')).strip ()
                norm =new_name .casefold ()
                idx =self .tools .index (tool_data )
                for i ,ex in enumerate (self .tools or []):
                    if i ==idx :
                        continue 
                    ex_name =str (ex .get ('name','')).strip ()
                    if ex_name and ex_name .casefold ()==norm :
                        QMessageBox .warning (self ,"错误","已存在同名工具，工具名称必须唯一")
                        return 
                self .tools [idx ]=newinfo 

                if not save_tools (self .tools ):
                    QMessageBox .warning (self ,"错误","保存失败！")
                else :
                    self .update_cat_panel ()
                    self .update_tool_grid ()

                new_short =diag .shortcut_key 
                if old_name !=newinfo ['name']:
                    if old_name in self .tool_shortcuts :
                        self .tool_shortcuts .pop (old_name ,None )
                    if old_name in self .registered_hotkeys :
                        self .remove_hotkey (old_name )

                if new_short :
                    self .tool_shortcuts [newinfo ['name']]=new_short 
                else :
                    if newinfo ['name']in self .tool_shortcuts :
                        self .tool_shortcuts .pop (newinfo ['name'],None )
                    self .remove_hotkey (newinfo ['name'])

                self .save_shortcuts ()
        except Exception as e :
            QMessageBox .warning (self ,"编辑工具异常",str (e ))
        self .re_register_hotkeys ()
        self .update_tool_grid ()

    def delete_tool (self ,tool_data ):
        msg =QMessageBox (self )
        msg .setWindowTitle ("确认删除")
        msg .setText (f"确定删除工具 '{tool_data['name']}' 吗？")
        msg .setIcon (QMessageBox .Icon .Question )
        msg .setStandardButtons (QMessageBox .StandardButton .Yes |QMessageBox .StandardButton .No )
        r =msg .exec ()
        if r ==QMessageBox .StandardButton .Yes :
            cat =tool_data ["category"]
            self .tools .remove (tool_data )

            if not save_tools (self .tools ):
                QMessageBox .warning (self ,"错误","保存工具数据失败")
                return 

            nm =tool_data ['name']
            if nm in self .tool_shortcuts :
                self .tool_shortcuts .pop (nm ,None )
            self .remove_hotkey (nm )

            remain =[t for t in self .tools if t ["category"]==cat ]
            if not remain and cat not in DEFAULT_CATEGORIES :
                if cat in self .categories :
                    self .categories .remove (cat )
                save_categories (self .categories )

            self .update_cat_panel ()
            self .update_tool_grid ()
            self .refresh_grid_layout ()

    def run_tool (self ,tool_data ):
        try :
            run_tool (tool_data )
        except Exception as e :
            QMessageBox .warning (self ,"错误",f"运行失败:{e}")

    def run_tools_batch (self ,tools ):
        try :
            succ =run_tools_batch (tools )
            QMessageBox .information (self ,"批量运行",f"已启动 {succ} 个工具")
        except Exception as e :
            QMessageBox .warning (self ,"批量运行",f"发生异常: {e}")

    def on_favorite_changed (self ,tool_data ,is_fav ):
        self .update_cat_panel ()
        self .update_tool_grid ()
        self .refresh_grid_layout ()

    def load_shortcuts (self ):
        s =QSettings ("config/shortcuts.ini",QSettings .Format .IniFormat )
        for t in self .tools :
            val =s .value (f"shortcuts/{t['name']}","")
            if val :
                self .tool_shortcuts [t ['name']]=val 

    def save_shortcuts (self ):
        s =QSettings ("config/shortcuts.ini",QSettings .Format .IniFormat )
        all_keys =s .allKeys ()
        for k in all_keys :
            if k .startswith ("shortcuts/"):
                s .remove (k )
        for nm ,val in self .tool_shortcuts .items ():
            s .setValue (f"shortcuts/{nm}",val )
        s .sync ()

    def init_shortcuts (self ):
        for nm ,hk in self .tool_shortcuts .items ():
            self .register_hotkey (nm ,hk )

    def register_hotkey (self ,tool_name :str ,hotkey :str ):
        self .remove_hotkey (tool_name )
        lower_key =hotkey .lower ()
        for exist_tool ,exist_key in self .registered_hotkeys .items ():
            if exist_key ==lower_key and exist_tool !=tool_name :
                QMessageBox .warning (
                self ,
                "快捷键冲突",
                f"快捷键 '{hotkey}' 已被【{exist_tool}】使用，无法设置给【{tool_name}】。"
                )
                return 
        try :
            def _callback (tn =tool_name ):
                found =[t for t in self .tools if t ['name']==tn ]
                if found :
                    self .run_tool (found [0 ])
            keyboard .add_hotkey (lower_key ,_callback )
            self .registered_hotkeys [tool_name ]=lower_key 
        except Exception as e :
            logger .error (f"注册热键失败: {hotkey} - {e}")

    def remove_hotkey (self ,tool_name :str ):
        if tool_name in self .registered_hotkeys :
            old_hk =self .registered_hotkeys [tool_name ]
            try :
                keyboard .remove_hotkey (old_hk )
            except :
                pass 
            self .registered_hotkeys .pop (tool_name ,None )

    def show_settings (self ):
        diag =SettingsDialog (self )
        diag .settings_changed .connect (self .on_settings_changed )
        try :
            if self .windowHandle ()and self .windowHandle ().screen ():
                ag =self .windowHandle ().screen ().availableGeometry ()
            else :
                ag =QApplication .primaryScreen ().availableGeometry ()
            px =ag .x ()+max (0 ,(ag .width ()-diag .width ())//2 )
            py =ag .y ()+max (0 ,(ag .height ()-diag .height ())//2 )
            diag .move (px ,py )
        except Exception :
            pass 

        diag .exec ()

    def on_settings_changed (self ,new_s ):
        import config 
        from config import SETTINGS ,load_theme 
        old_theme =SETTINGS .get ("theme","dark")
        old_exit_mode =SETTINGS .get ("exit_mode","ask")
        new_theme =new_s .get ("theme","dark")
        new_exit_mode =new_s .get ("exit_mode","ask")

        SETTINGS .clear ()
        SETTINGS .update (new_s )
        global THEME 
        THEME =load_theme (SETTINGS .get ("theme","dark"))
        config .THEME =THEME 


        need_restart =(old_theme !=new_theme )or (old_exit_mode !=new_exit_mode )

        if need_restart :
            msg =QMessageBox (self )
            msg .setWindowTitle ("重启确认")
            msg .setIcon (QMessageBox .Icon .Information )
            msg .setText ("退出模式或主题已更改，需要重启才能生效。程序将立即重启。")
            ok_btn =msg .addButton ("确定",QMessageBox .ButtonRole .AcceptRole )
            msg .setDefaultButton (ok_btn )
            msg .exec ()
            self .restart_application ()
            return 


        self .apply_theme ()
        self .update_tool_grid ()
        self .refresh_grid_layout ()

    def restart_application (self ):
        self ._is_restarting =True 

        try :
            from config import SETTINGS as _SETTINGS 
            save_settings (_SETTINGS )
        except Exception :

            pass 


        import subprocess 
        import sys 


        loader_path =os .path .join (os .path .dirname (os .path .abspath (__file__ )),"loader.py")
        python_exe =sys .executable 


        if sys .platform .startswith ("win"):

            subprocess .Popen ([python_exe ,loader_path ],creationflags =subprocess .CREATE_NEW_PROCESS_GROUP ,close_fds =True )
        else :

            pid =os .fork ()
            if pid >0 :

                os ._exit (0 )
            else :

                os .setsid ()
                pid =os .fork ()
                if pid >0 :
                    os ._exit (0 )
                else :

                    os .execv (python_exe ,[python_exe ,loader_path ])


        self .force_quit ()

    def check_java_path (self ):
        try :
            validate_java_path ()
        except Exception as e :
            QMessageBox .warning (self ,"Java路径",f"检测Java路径失败: {e}")

    def init_tray (self ):
        self .tray_icon =QSystemTrayIcon (self )
        self .tray_icon .setIcon (QIcon ("config/redblue.ico"))
        m =QMenu ()

        try :
            anim =QVariantAnimation (m )
            anim .setDuration (140 )
            anim .setEasingCurve (QEasingCurve .Type .OutCubic )

            def _on_val (v ):
                t =float (v )
                try :
                    m .setWindowOpacity (t )
                except Exception :
                    pass 
                try :
                    p =m .pos ()
                    m .move (p .x (),p .y ()+int (6 *(1.0 -t )))
                except Exception :
                    pass 

            anim .valueChanged .connect (_on_val )

            def _start_anim ():
                try :
                    anim .stop ()
                except Exception :
                    pass 
                try :
                    m .setWindowOpacity (0.0 )
                except Exception :
                    return 
                anim .setStartValue (0.0 )
                anim .setEndValue (1.0 )
                anim .start ()

            m .aboutToShow .connect (_start_anim )
        except Exception :
            pass 

        act_show =m .addAction ("显示主窗口")
        act_show .triggered .connect (self .show_and_focus )
        act_exit =m .addAction ("退出程序")
        act_exit .triggered .connect (self .force_quit )
        self .tray_icon .setContextMenu (m )
        self .tray_icon .activated .connect (self .on_tray_activated )
        self .tray_icon .show ()

    def show_and_focus (self ):
        self .show ()
        self .tray_icon .hide ()

    def on_tray_activated (self ,reason ):
        if reason ==QSystemTrayIcon .ActivationReason .DoubleClick :
            self .show_and_focus ()

    def _cleanup_before_exit (self ):

        if getattr (self ,"_is_exiting",False ):
            return 
        self ._is_exiting =True 

        try :
            self .disable_all_hotkeys ()
        except Exception :
            pass 
        try :

            keyboard .unhook_all_hotkeys ()
        except Exception :
            pass 
        try :
            keyboard .unhook_all ()
        except Exception :
            pass 

        try :
            if hasattr (self ,"tray_icon")and self .tray_icon :
                try :
                    self .tray_icon .hide ()
                except Exception :
                    pass 
        except Exception :
            pass 

    def force_quit (self ):
        try :
            self ._cleanup_before_exit ()
        except Exception :
            pass 
        try :
            QApplication .quit ()
        except Exception :
            pass 

        os ._exit (0 )

    def closeEvent (self ,e ):
        save_main_window_geometry (self .saveGeometry ())
        save_main_window_state (self .saveState ())


        if getattr (self ,"_is_restarting",False ):
            e .accept ()
            self .force_quit ()
            return 

        mode =SETTINGS .get ("exit_mode","ask")
        if mode =="ask":
            msg =QMessageBox (self )
            msg .setWindowTitle ("退出确认")
            msg .setText ("确定要退出吗？")
            msg .setIcon (QMessageBox .Icon .Question )
            b1 =msg .addButton ("最小化到托盘",QMessageBox .ButtonRole .ActionRole )
            b2 =msg .addButton ("退出程序",QMessageBox .ButtonRole .AcceptRole )
            b3 =msg .addButton ("取消",QMessageBox .ButtonRole .RejectRole )
            msg .setDefaultButton (b3 )
            msg .exec ()
            if msg .clickedButton ()==b1 :
                e .ignore ()
                self .hide ()
                self .tray_icon .show ()
            elif msg .clickedButton ()==b2 :
                e .accept ()
                self .force_quit ()
            else :
                e .ignore ()
        elif mode =="tray":
            e .ignore ()
            self .hide ()
            self .tray_icon .show ()
        else :
            e .accept ()
            self .force_quit ()

    def open_notebook (self ):
        try :
            notepad_path =os .path .join ("notepad","eDiary.exe")
            notepad_path =os .path .abspath (notepad_path )
            if sys .platform .startswith ("win"):
                os .startfile (notepad_path )
            else :
                subprocess .Popen ([notepad_path ])
        except Exception as e :
            QMessageBox .warning (self ,"错误",f"运行失败: {e}")

    def toggle_batch_mode (self ):
        is_active =not self .tool_grid .show_select_box 
        self .tool_grid .enable_batch_mode (is_active )
        if is_active :
            self .btn_run_batch .show ()
        else :
            self .btn_run_batch .hide ()

    def do_batch_run (self ):
        selected =self .tool_grid .get_selected_tools ()
        if not selected :
            QMessageBox .information (self ,"提示","未选择任何工具")
            return 

        self .run_tools_batch (selected )

        self .toggle_batch_mode ()

    def show_about (self ):
        """显示关于窗口"""
        about_text = """系统名称：凭阑红蓝工具箱PBox<br>版本：v1.0<br>版权信息：Copyright 2026 <a href="https://www.pinglan.com.cn/">凭阑实验室</a>"""
        msg =QMessageBox (self )
        msg .setWindowTitle ("关于")
        msg .setText (about_text )
        msg .setTextFormat (Qt .TextFormat .RichText )
        msg .setIcon (QMessageBox .Icon .Information )
        msg .exec ()

    def show_wx_dialog (self ):
        """显示微信群聊二维码窗口"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel
        from PyQt6.QtGui import QFont, QPixmap
        
        dialog = QDialog(self)
        dialog.setWindowTitle("微信群聊")
        dialog.setFixedSize(680, 300)
        
        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
        
        fssp_layout = QVBoxLayout()
        fssp_layout.setSpacing(10)
        fssp_img_path = os.path.join(config_dir, "wxfssp.png")
        fssp_pixmap = QPixmap(fssp_img_path)
        fssp_label = QLabel()
        fssp_label.setPixmap(fssp_pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        fssp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fssp_layout.addWidget(fssp_label)
        fssp_text = QLabel("加入FSSP安全攻防认证社区")
        fssp_text.setFont(QFont("Microsoft YaHei", 12))
        fssp_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fssp_layout.addWidget(fssp_text)
        content_layout.addLayout(fssp_layout)
        
        club_layout = QVBoxLayout()
        club_layout.setSpacing(10)
        club_img_path = os.path.join(config_dir, "wxclub.png")
        club_pixmap = QPixmap(club_img_path)
        club_label = QLabel()
        club_label.setPixmap(club_pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        club_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        club_layout.addWidget(club_label)
        club_text = QLabel("加入凭阑实验室安全社区")
        club_text.setFont(QFont("Microsoft YaHei", 12))
        club_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        club_layout.addWidget(club_text)
        content_layout.addLayout(club_layout)
        
        open_layout = QVBoxLayout()
        open_layout.setSpacing(10)
        open_img_path = os.path.join(config_dir, "wxopen.png")
        open_pixmap = QPixmap(open_img_path)
        open_label = QLabel()
        open_label.setPixmap(open_pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        open_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        open_layout.addWidget(open_label)
        open_text = QLabel("加入凭阑开源社区共同维护本软件")
        open_text.setFont(QFont("Microsoft YaHei", 12))
        open_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        open_layout.addWidget(open_text)
        content_layout.addLayout(open_layout)
        
        main_layout.addLayout(content_layout)
        
        dialog.exec()

    def load_main_window_state_and_geometry (self ):
        geo_bytes =load_main_window_geometry ()
        state_bytes =load_main_window_state ()
        if geo_bytes :
            self .restoreGeometry (QByteArray (geo_bytes ))
        if state_bytes :
            self .restoreState (QByteArray (state_bytes ))

def main ():
    install_log_hooks ()
    app =QApplication (sys .argv )
    w =MainWindow ()
    w .show ()
    sys .exit (app .exec ())

if __name__ =="__main__":
    main ()
