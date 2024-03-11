@echo off

rem Get the internal IP address using PowerShell
for /f "usebackq tokens=*" %%a in (`powershell "(Get-CimInstance -ClassName Win32_NetworkAdapterConfiguration | Where-Object { $_.IPEnabled -eq 'True' }).IPAddress[0]"`) do set LocalIP=%%a

rem Write the IP address to the .env file in folder a
echo EXPO_PUBLIC_API_URL=http://%LocalIP%:3000/api > ".\risenchiropractic-body-recognition-mobile\.env.local"

echo Local IP address set in .env file.

start cmd /k "cd .\risenchiropractic-body-recognition-mobile & npm run start"
start cmd /k "cd .\risenchiropractic-body-recognition-backend\Yangseng_API & npm run start"
echo Running scripts in the background...
