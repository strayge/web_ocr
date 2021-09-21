import json
from base64 import b64decode
from hashlib import md5
from io import BytesIO
from pathlib import Path
from time import sleep, time
from typing import List, Optional

import pytesseract
from PIL import Image
from selenium.webdriver import Chrome, ChromeOptions


def init_driver() -> Chrome:
    options = ChromeOptions()
    options.headless = True
    driver = Chrome(options=options)
    driver.set_window_size(60000, 6000)
    return driver


def ocr_cell(cell, save_name: Optional[str] = None) -> List[str]:
    image = Image.open(BytesIO(b64decode(cell.screenshot_as_base64)))
    if save_name:
        image.save(Path('screenshots') / f'{save_name}.png')
    text = pytesseract.image_to_string(image, config='--psm 6 -c "tessedit_char_whitelist=0123456789.%"')
    lines = text.strip().splitlines()
    if len(lines) >= 3 and lines[-1] == '%':
        lines = (*lines[:-2], lines[-2] + lines[-1])
    return lines


def cut_numeration(text: str) -> str:
    if '. ' in text[:10]:
        text = text.split('. ', 1)[1]
    return text


def gen_img_name(url: str, num1: int, num2: Optional[int] = None) -> str:
    url_hash = md5(url.encode()).hexdigest()[:16]
    if num2 is None:
        return f'{url_hash}_{num1:03d}'
    return f'{url_hash}_{num1:03d}_{num2:03d}'


def get_page_data(driver: Chrome, url: str, debug=False) -> List[List[str]]:
    driver.delete_all_cookies()
    t1 = time()
    driver.get(url)
    t2 = time()
    print(f'load: {t2 - t1:.2f} sec')
    sleep(1)

    # increase readability
    script = '''
        document.styleSheets[0].insertRule("td {
            font-size: 2em !important;
            max-width: 100% !important;
            background-color: #ffffff !important;
        }", 0 );
        document.styleSheets[0].insertRule("table {
            height: max-content !important;
            width: max-content !important;
        }", 0 )
    '''
    driver.execute_script(script.replace('\n', ''))

    results = []

    # text above table
    head_rows = driver.find_elements_by_css_selector('.table-borderless tr')
    for row in head_rows:
        cols = row.find_elements_by_tag_name('td')
        line = []
        for col in cols:
            text = col.text.strip()
            if text:
                line.append(text)
        if line:
            results.append(line)

    small_tables = driver.find_elements_by_css_selector('.table-responsive')
    big_tables = driver.find_elements_by_css_selector('.table-bordered')

    if small_tables:
        table = small_tables[0]
        rows = table.find_elements_by_css_selector('tr')
        for i, row in enumerate(rows):
            cells = row.find_elements_by_tag_name('td')
            if len(cells) < 3:  # skip empty lines
                continue
            name = cut_numeration(cells[1].text.strip())
            results.append([name, *ocr_cell(cells[2], save_name=gen_img_name(url, i) if debug else None)])

    elif big_tables:
        table = big_tables[0]
        headers = table.find_elements_by_css_selector('th')
        results.append([h.text for h in headers][1:])
        rows = table.find_elements_by_css_selector('tr')
        for i, row in enumerate(rows):
            print(f'row {i + 1} / {len(rows)}')
            cells = row.find_elements_by_css_selector('td')
            if len(cells) < 3:  # skip empty lines
                continue
            result = [cut_numeration(cells[1].text)]
            for j, cell in enumerate(cells[2:]):
                result.append(ocr_cell(cell, save_name=gen_img_name(url, i, j) if debug else None))
            results.append(result)

    else:
        print('no tables found')

    t3 = time()
    print(f'processed: {t3 - t2:.2f} sec')
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', '-u', metavar='URL', help='pass single url')
    parser.add_argument('--input', '-i', metavar='urls.txt', help='get urls from file (one per line)')
    parser.add_argument('--output', '-o', metavar='out.json', help='save results in json format')
    parser.add_argument('--print', '-p', action='store_true', help='print to stdout each page result')
    parser.add_argument('--debug', action='store_true', help='some debug info / images')
    args = parser.parse_args()

    if not args.output:
        args.print = True

    if args.input:
        with open(args.input, 'rt') as f:
            urls = f.readlines()
    elif args.url:
        urls = [args.url]
    else:
        print('ERR: specify --url or --input file')
        return

    driver = init_driver()
    results = {}
    for i, url in enumerate(urls):
        if not url:
            continue
        print(f'processing url {i + 1} / {len(urls)}')
        try:
            results[url] = get_page_data(driver, url, debug=args.debug)
        except Exception as e:
            print(f'ERR: {e!r}')
            continue
        if args.print:
            print(f'URL: {url}')
            for line in results[url]:
                print(line)

    if args.output:
        with open(args.output, 'wt') as f:
            json.dump(results, f)


if __name__ == '__main__':
    main()
