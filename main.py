import json
from base64 import b64decode
from io import BytesIO
from time import sleep
from typing import List

import pytesseract
from PIL import Image
from selenium.webdriver import Chrome, ChromeOptions

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def init_driver() -> Chrome:
    options = ChromeOptions()
    options.headless = True
    driver = Chrome(options=options)
    driver.set_window_size(3000, 4000)
    return driver


def get_page_data(driver: Chrome, url: str) -> List[List[str]]:
    driver.delete_all_cookies()
    driver.get(url)
    sleep(1)

    # increase text size
    script = 'document.styleSheets[0].insertRule("body {font-size: 2em !important;}", 0 )'
    driver.execute_script(script)

    results = []
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

    rows = driver.find_elements_by_css_selector('.table-responsive tr')

    for i, row in enumerate(rows):
        cols = row.find_elements_by_tag_name('td')
        if len(cols) > 1:
            name = cols[1].text.strip()
        else:
            continue
        if '. ' in name[:10]:
            # cut numeration
            name = name.split('. ', 1)[1]
        # if line is blank --> skip
        if len(cols) < 3:
            continue
        image = Image.open(BytesIO(b64decode(cols[2].screenshot_as_base64)))
        text = pytesseract.image_to_string(image, config='--psm 6 -c "tessedit_char_whitelist=0123456789.%"')
        lines = text.strip().splitlines()
        if len(lines) >= 3 and lines[-1] == '%':
            lines = (*lines[:-2], lines[-2] + lines[-1])
        results.append([name, *lines])
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', '-u', metavar='URL', help='pass single url')
    parser.add_argument('--input', '-i', metavar='urls.txt', help='get urls from file (one per line)')
    parser.add_argument('--output', '-o', metavar='out.json', help='save results in json format')
    parser.add_argument('--print', '-p', action='store_true', help='print to stdout each page result')
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
        print(f'processing {i+1} / {len(urls)} url')
        try:
            results[url] = get_page_data(driver, url)
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
