# Requirements for scraper can all be found in this document:
https://docs.google.com/document/d/15skALRR8v3GfDVkvOkVMEpcKhR75-JUHUP_54GW-X-4/edit#heading=h.pm3cn4ukur7w
## Run scraper on main directory: BT4103-Capstone-Team17

## tesseract-ocr is required to be installed on your system to extract texts from images
### Install tesseract-ocr on Mac using Homebrew:
```brew install tesseract```

### Install tesseract-ocr on Linux: 
```sudo apt install tesseract-ocr```

### Install tesseract-ocr on windows:
https://stackoverflow.com/questions/46140485/tesseract-installation-in-windows

## Install dependencies: 
```pip3 install -r scraper/requirements.txt```

## Run scraper: 
```python3 -m scraper.src.main```

## Total run time: ~19 minutes 
Function that takes the longest time to run: # Extract text from images 
from sraper_action.py
