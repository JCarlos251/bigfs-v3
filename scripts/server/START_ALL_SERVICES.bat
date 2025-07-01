@echo off
echo Iniciando BIGFSv3...

start cmd /k "start_nameserver.bat"
timeout /t 2

start cmd /k "start_namenode.bat"
timeout /t 2

start cmd /k "start_datanode1.bat"
timeout /t 1

start cmd /k "start_datanode2.bat"
timeout /t 1

start cmd /k "start_datanode3.bat"
timeout /t 1

start cmd /k "start_datanode4.bat"
