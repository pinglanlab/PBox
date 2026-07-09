import ctypes 
from ctypes import c_int ,byref ,sizeof 
from ctypes .wintypes import HWND ,DWORD 
import sys 


DWMWA_USE_IMMERSIVE_DARK_MODE =20 
DWMWA_SYSTEMBACKDROP_TYPE =38 


DWMSBT_AUTO =0 
DWMSBT_NONE =1 
DWMSBT_MAINWINDOW =2 
DWMSBT_TRANSIENTWINDOW =3 
DWMSBT_TABBEDWINDOW =4 

class WindowEffect :
    def __init__ (self ):
        self .dwmapi =ctypes .WinDLL ("dwmapi")
        self .user32 =ctypes .WinDLL ("user32")

    def set_mica_effect (self ,hwnd :int ,is_dark :bool =True ):
        if sys .platform !="win32":
            return False 

        try :

            dark_mode =c_int (1 if is_dark else 0 )
            self .dwmapi .DwmSetWindowAttribute (
            HWND (hwnd ),
            DWORD (DWMWA_USE_IMMERSIVE_DARK_MODE ),
            byref (dark_mode ),
            sizeof (dark_mode )
            )



            backdrop_type =c_int (DWMSBT_MAINWINDOW )
            hr =self .dwmapi .DwmSetWindowAttribute (
            HWND (hwnd ),
            DWORD (DWMWA_SYSTEMBACKDROP_TYPE ),
            byref (backdrop_type ),
            sizeof (backdrop_type )
            )

            if hr !=0 :

                DWMWA_MICA_EFFECT =1029 
                mica_on =c_int (1 )
                self .dwmapi .DwmSetWindowAttribute (
                HWND (hwnd ),
                DWORD (DWMWA_MICA_EFFECT ),
                byref (mica_on ),
                sizeof (mica_on )
                )

            return True 
        except Exception as e :
            print (f"Failed to set Mica effect: {e}")
            return False 

    def set_acrylic_effect (self ,hwnd :int ,is_dark :bool =True ):
        if sys .platform !="win32":
            return False 

        try :

            dark_mode =c_int (1 if is_dark else 0 )
            self .dwmapi .DwmSetWindowAttribute (
            HWND (hwnd ),
            DWORD (DWMWA_USE_IMMERSIVE_DARK_MODE ),
            byref (dark_mode ),
            sizeof (dark_mode )
            )


            backdrop_type =c_int (DWMSBT_TRANSIENTWINDOW )
            self .dwmapi .DwmSetWindowAttribute (
            HWND (hwnd ),
            DWORD (DWMWA_SYSTEMBACKDROP_TYPE ),
            byref (backdrop_type ),
            sizeof (backdrop_type )
            )
            return True 
        except Exception as e :
            print (f"Failed to set Acrylic effect: {e}")
            return False 

    def remove_background_effect (self ,hwnd :int ):
        if sys .platform !="win32":
            return 

        try :
            backdrop_type =c_int (DWMSBT_NONE )
            self .dwmapi .DwmSetWindowAttribute (
            HWND (hwnd ),
            DWORD (DWMWA_SYSTEMBACKDROP_TYPE ),
            byref (backdrop_type ),
            sizeof (backdrop_type )
            )
        except :
            pass 
