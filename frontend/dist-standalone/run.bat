@echo off
echo 대형광고물 판정 도구를 시작합니다...
echo.
echo 브라우저에서 http://localhost:8080 으로 접속하세요.
echo 종료하려면 이 창을 닫으세요.
echo.
start http://localhost:8080
python -m http.server 8080
if errorlevel 1 (
    python3 -m http.server 8080
)
pause
