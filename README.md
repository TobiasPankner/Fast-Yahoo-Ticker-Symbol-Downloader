# Fast-Yahoo-Ticker-Symbol-Downloader
Downloads (alsmost) all the symbols from Yahoo Finance.  
This project does pretty much the same thing as [Yahoo-ticker-symbol-downloader](https://github.com/Benny-/Yahoo-ticker-symbol-downloader) by [Benny-](https://github.com/Benny-), but uses a different url and multiprocessing to retrieve the data.  
Because of this, this program is _**a lot**_ faster.

## Speed Comparison
|                                |  time | symbols collected |
|--------------------------------|:-----:|:-----------------:|
| Yahoo-ticker-symbol-downloader | 1 min |              5200 |
| Fast-Yahoo-Ticker-Symbol-Downloader                 | 1 min |            325000 |  

Both tested with the same Download speed on the same machine.  

## Usage
```
usage: symbol_downloader.py [-h] [-b BATCHSIZE] [-l CLENGTH] [-t TYPES] [-o OUTFILE]

Collects almost all symbols from Yahoo Finance.

optional arguments:
  -h, --help            show this help message and exit
  -b BATCHSIZE, --batchsize BATCHSIZE
                        Number of urls in one batch
  -l CLENGTH, --clength CLENGTH
                        The maximum length of combinations to search for
  -t TYPES, --types TYPES
                        The types of symbols to download (equity,mutualfund,etf,index,future,currency)
  -o OUTFILE, --outfile OUTFILE
                        The path of the output file
```  
Notes:  
batchsize should be reduced if you have a slow connection or a weak CPU  
clencht has deminishing returns, meaning a clength of 5 takes much longer than a clength of 4 but will not get many more results.  

Examples:  
Default arguments, saves symbols in the same folder: `py symbol_downloader.py`  
Only download futures and etfs to a specific folder: `py symbol_downloader.py -t etf,future -o E:/Desktop/symbols.csv`  
