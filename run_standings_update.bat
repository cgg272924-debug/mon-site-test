@echo off
cd /d "c:\Users\bdl69\Desktop\ol_match_analyzer"
"c:\Users\bdl69\Desktop\ol_match_analyzer\venv\Scripts\python.exe" "scraping/get_league1_standings_home_away.py" >> "scraping/logs/hourly_update.log" 2>&1
