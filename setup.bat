@echo off
echo Building the Tkinter application...
echo.
pyinstaller --onefile --add-data "images;images" --icon=images/s.ico --icon=images/s.png --name="Simple Image Converter v1.2" --upx-dir "C:\upx-4.2.4-win64" S.pyw
echo.
pause
