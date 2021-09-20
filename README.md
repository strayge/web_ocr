## Requirements

#### 1. python packages
```sh
pip install -r requirements.txt
```
#### 2. tesseract

Windows installer available [here](https://github.com/UB-Mannheim/tesseract/actions/runs/1119350562)
(required github login)

#### 3. chrome driver

download from [here](https://chromedriver.chromium.org/downloads)

### Options
```
usage: main.py [-h] [--url URL] [--input urls.txt] [--output out.json] [--print]

optional arguments:
  -h, --help            show this help message and exit
  --url URL, -u URL     pass single url
  --input urls.txt, -i urls.txt
                        get urls from file (one per line)
  --output out.json, -o out.json
                        save results in json format
  --print, -p           print to stdout each page result
```

### Example

#### single url in terminal
```sh
python main.py -u 'http://www.primorsk.vybory.izbirkom.ru/region/izbirkom?action=show&root=12000001&tvd=4014001103304&vrn=100100067795849&prver=0&pronetvd=null&region=1&sub_region=1&type=242&report_mode=null'
```

#### batch processing
```sh
python main.py -i in.txt -o results.json
```

#### JSON output example

```json
{
  "http://www.primorsk.vybory.izbirkom.ru/region/izbirkom?action\u003dshow\u0026root\u003d552000002\u0026tvd\u003d4554026217797\u0026vrn\u003d100100067795849\u0026prver\u003d0\u0026pronetvd\u003dnull\u0026region\u003d55\u0026sub_region\u003d55\u0026type\u003d242\u0026report_mode\u003dnull\n": [
    [
      "Дата голосования:  18.09.2016"
    ],
    [
      "Наименование избирательной комиссии",
      "УИК №370"
    ],
    [
      "Число избирателей, внесенных в список избирателей на момент окончания голосования",
      "2342"
    ],
    ...
    [
      "Политическая партия \"ПАТРИОТЫ РОССИИ\"",
      "2",
      "0.32%"
    ],
    [
      "Политическая партия СПРАВЕДЛИВАЯ РОССИЯ",
      "49",
      "7.13%"
    ]
  ],
  "http://www.primorsk.vybory.izbirkom.ru/region/izbirkom?action\u003dshow\u0026root\u003d12000001\u0026tvd\u003d4014001103304\u0026vrn\u003d100100067795849\u0026prver\u003d0\u0026pronetvd\u003dnull\u0026region\u003d1\u0026sub_region\u003d1\u0026type\u003d242\u0026report_mode\u003dnull\n": [
    [
      "Дата голосования:  18.09.2016"
    ],
    [
      "Наименование избирательной комиссии",
      "УИК №1"
    ],
    [
      "Число избирателей, внесенных в список избирателей на момент окончания голосования",
      "2584"
    ],
    [
      "Число избирательных бюллетеней, полученных участковой избирательной комиссией",
      "2328"
    ],
    ...
    [
      "Политическая партия \"ПАТРИОТЫ РОССИИ\"",
      "0",
      "0.00%"
    ],
    [
      "Политическая партия СПРАВЕДЛИВАЯ РОССИЯ",
      "56",
      "2.65%"
    ]
  ]
}
```