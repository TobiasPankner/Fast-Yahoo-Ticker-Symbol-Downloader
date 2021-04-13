import concurrent.futures
import itertools
import csv
import requests
from constraint import Problem
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TimeRemainingColumn
import time
from argparse import ArgumentParser


def grouper(n, iterable, fillvalue=None):
    """grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"""
    grouper_args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *grouper_args)


def get_symbols(url):
    resp = requests.get(url, timeout=3, allow_redirects=False)

    return resp.json()['finance']['result'][0]['documents']


if __name__ == '__main__':
    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
                'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '=']
    # if the alphabet is not reversed "==" will be first and "aa" last
    alphabet.reverse()

    parser = ArgumentParser(description='Collects almost all symbols from Yahoo Finance.')
    parser.add_argument("-b", "--batchsize", dest="batchsize", default=400, type=int,
                        help="Number of urls in one batch")

    parser.add_argument("-l", "--clength", dest="clength", default=2, type=int,
                        help="The maximum length of combinations to search for")

    parser.add_argument("-t", "--types", dest="types", default="equity,mutualfund,etf,index,future,currency",
                        help="The types of symbols to download (equity,mutualfund,etf,index,future,currency)")

    parser.add_argument("-o", "--outfile", dest="outfile", default="symbols.csv",
                        help="The path of the output file")

    args = parser.parse_args()

    symbols_types = args.types.split(",")

    # final results dict
    results = dict()

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=args.batchsize)

    for i in range(1, args.clength + 1):
        # generates all possible combinations of the alphabet
        prob = Problem()
        prob.addVariables(range(1, i + 1), alphabet)

        urls_to_complete = []
        errors = []
        is_finished = False

        # generate an url for every combination with every symbol type
        for combination in (''.join(c.values()) for c in prob.getSolutionIter()):
            for symbol_type in symbols_types:
                urls_to_complete.append(
                    "https://query1.finance.yahoo.com/v1/finance/lookup?"
                    "formatted=true&"
                    "lang=en-US&"
                    "region=US&"
                    f"query={combination}&"
                    f"type={symbol_type}&"
                    "count=10000&"
                    "start=0&"
                    "corsDomain=finance.yahoo.com"
                )

        print(f"Requesting data from {len(urls_to_complete)} urls")
        with Progress(
                TimeElapsedColumn(),
                BarColumn(),
                "{task.percentage:>3.0f}%",
                TimeRemainingColumn(),
                " {task.completed} / {task.total}"
        ) as progress:

            task = progress.add_task("[red]Getting Symbols...", total=len(urls_to_complete))

            while not is_finished:
                for url_batch in list(grouper(args.batchsize, urls_to_complete)):
                    time1 = time.time()

                    future_to_url = {executor.submit(get_symbols, url): url for url in url_batch if
                                     url is not None}

                    for future in concurrent.futures.as_completed(future_to_url):
                        done_url = future_to_url[future]
                        try:
                            # if the url is in the errors array, remove it
                            try:
                                errors.remove(done_url)
                            except ValueError:
                                pass

                            result = future.result()

                            for r in result:
                                if r['symbol'] not in results:
                                    results[r['symbol']] = {}

                                results[r['symbol']]['symbol'] = r['symbol']
                                try:
                                    results[r['symbol']]['shortName'] = r['shortName']
                                except KeyError:
                                    if 'shortName' not in results[r['symbol']] or results[r['symbol']]['shortName'] == r['symbol']:
                                        results[r['symbol']]['shortName'] = r['symbol']
                                results[r['symbol']]['exchange'] = r['exchange']
                                results[r['symbol']]['type'] = r['quoteType']

                                try:
                                    results[r['symbol']]['rank'] = r['rank']
                                except KeyError:
                                    results[r['symbol']]['rank'] = -1

                            progress.update(task, advance=1)

                        except TypeError as t:
                            print(f"Internal error for: {done_url}")
                            pass
                        except Exception as e:
                            if done_url not in errors:
                                errors.append(done_url)
                            pass

                    time2 = time.time()

                    print("\nBatch completed: ")
                    if len(future_to_url) > 0:
                        print(
                            f"\tTook {round(time2 - time1, 3)}s  ({round((time2 - time1) / (len(future_to_url)), 3)}s per url)")

                    print(f"\tTotal Errors: {len(errors)}")
                    print(f"\tTotal symbols: {len(results)}")

                urls_to_complete = errors

                # if there are no more errors stop the loop
                if len(urls_to_complete) == 0:
                    is_finished = True

        results_arr = list(results.values())

        with open(args.outfile, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, results_arr[0].keys(), extrasaction='ignore')
            w.writeheader()
            w.writerows(results_arr)
