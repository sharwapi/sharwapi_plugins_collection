@echo off
::########################################################################
::
:: Launcher for squash-my-commits.ps1
:: This file calls the PowerShell script with the same arguments.
::
:: Usage:
::   .\utils\squash-my-commits.bat [options]
::
:: Options:
::   -S        sign the result with your GPG key (recommended)
::   -Push     force push result to your fork after squash
::   -Ssh      use SSH to fetch from upstream
::   -Https    use HTTPS to fetch from upstream
::   -Verify   check only (do not squash)
::   -Help     display help message
::
:: Example:
::   .\utils\squash-my-commits.bat -S -Push
::
::########################################################################

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0squash-my-commits.ps1" %*
