set path=C:\Users\USER\__dev__\python\UcGeorge\sanfoundry-scraper
set pypath=C:\ProgramData\Anaconda3
set pippath=C:\ProgramData\Anaconda3\Scripts

%pippath%\pip.exe install -r %path%\requirements.txt
cls
%pypath%\python.exe %path%\main.py