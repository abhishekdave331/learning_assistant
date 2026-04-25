@echo off
set BASE=https://adaptive-learning-backend-442541165615.us-central1.run.app

echo === Health Check ===
curl -s %BASE%/health
echo.

echo.
echo === Start Session (derivatives, beginner) ===
curl -s -X POST %BASE%/start-session ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"demo_test\",\"topic\":\"derivatives in calculus\",\"skill_level\":\"beginner\"}"
echo.
