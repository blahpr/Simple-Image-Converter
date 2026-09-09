@echo off

pyinstaller --onefile --add-data "images;images" --icon=images/s.ico --icon=images/s.png --name="Simple Image Converter v2.0" --upx-dir "C:\upx-5.2.1-win64" S.pyw

echo.
pause
