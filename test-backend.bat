@echo off
echo Testing Backend API
echo ==================

REM Test health endpoint
echo Testing health endpoint...
curl -s http://localhost:5000/api/health

echo.
echo.

REM Test plakat generator
echo Testing plakat generator...
curl -X POST http://localhost:5000/api/process/plakat ^
  -H "Content-Type: application/json" ^
  -d "{\"projects\": [{\"id\": \"CZ.02.3.68/0.0/0.0/20_083/0021933\", \"name\": \"Test projekt\"}], \"orientation\": \"portrait\", \"common_text\": \"Test text\"}"

echo.
echo.
echo Test complete!
pause