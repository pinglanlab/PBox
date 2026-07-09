@echo off
setlocal enabledelayedexpansion
mode con cols=94 lines=30&color 0a&title 创建红蓝工具箱一键启动脚本快捷方式
echo.
echo CNCVE安全团队
echo  官网：https://www.cncve.org.cn/  
echo  微信公众号：凭阑实验室

echo.
echo [+] 获得当前路径:%~dp0
echo.

:: 设置vbs文件和快捷方式名称
set "path=%~dp0PBox.vbs"
set "LinkName=PBox"

:: 检查选择的vbs文件是否存在
if exist "!path!" (
    echo [+] 发现凭阑红蓝工具箱PBox一键启动脚本!
    echo.
    echo [+] 启动脚本路径：
    echo [+] !path!
    echo.
    goto :creat
) else (
    echo [-] 注意,未发现启动脚本PBox.vbs，请注意是否改名,程序退出... 
    echo.
    pause
    exit /b
)

:creat
echo [+] 开始创建快捷方式...
echo.
rem 设置程序的完整路径(必要)
set Program=!path!
rem 程序工作路径
set WorkDir=%~dp0
rem 设置快捷方式说明
set Desc=红蓝工具箱一键启动_by.凭阑实验室
rem 设置快捷方式图标
set icon=%~dp0config\redblue.ico

if not defined WorkDir call:GetWorkDir "%Program%"
(echo Set WshShell=CreateObject("WScript.Shell"^)
echo strDesKtop=WshShell.SpecialFolders("DesKtop"^)
echo Set oShellLink=WshShell.CreateShortcut(strDesKtop^&"\%LinkName%.lnk"^)
echo oShellLink.TargetPath="%Program%"
echo oShellLink.WorkingDirectory="%WorkDir%"
echo oShellLink.WindowStyle=1
echo oShellLink.Description="%Desc%"
echo oShellLink.IconLocation="%icon%"
echo oShellLink.Save)>makelnk.vbs

echo [+] 桌面快捷方式创建成功!!
echo.
start explorer "https://www.cncve.org.cn/"
echo.
makelnk.vbs
del /f /q makelnk.vbs
pause
goto :eof

:GetWorkDir
set WorkDir=%~dp1
set WorkDir=%WorkDir:~0,-1%