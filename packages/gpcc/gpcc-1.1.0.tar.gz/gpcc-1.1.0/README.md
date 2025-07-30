# gpcc

Python library and CLI tool to fetch information from [GCP Browser](https://gpc-browser.gs1.org/).

This is a standardized classifier of products used across companies. The classification, however, cannot be inferred from the product barcode or even packaging. Companies use it only internally.

## Installation

```bash
python3 -m pip install gpcc
```

## CLI usage

```bash
# download latest JSONs for all languages
python3 -m gpcc

# download latest JSON for a specified language
python3 -m gpcc --lang nl

# download into a specified directory
python3 -m gpcc --output ./gpc-dump/

# download files in XML format
python3 -m gpcc --format xml

# download files in XLSX format
python3 -m gpcc --format xlsx
```

## Python usage

```python
import asyncio
import gpcc
from pathlib import Path

async def run():
    langs = await gpcc.get_languages()
    output = Path('gpc-dump')
    
    # Default format is JSON
    await gpcc.fetch_files(output, langs)
    
    # Download files in XML format
    # await gpcc.fetch_files(output, langs, format='xml')
    
    # Download files in XLSX format
    # await gpcc.fetch_files(output, langs, format='xlsx')

asyncio.run(run())
```
