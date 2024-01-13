# MCloud-scraper
<p align="center">
  <img src="https://raw.githubusercontent.com/Kseen715/imgs/main/favicon.ico" />
</p>

## Description

This is proof-of-concept project, that theoretically should "mine" public cloud 
links from the internet for further investigation.

## Usage

Script written for Python 3.12, but should work on other versions.

To install necessary requirements, run:
```
python3 pip install -r requirements.txt
```

You can use ```--help``` argument to see full command palette:
```
python3 run.py --help
```

On my machine, I can run 20 workers without any problems, but you can try to
increase this number. Also, you can use sequential mode, which is much slower,
but more accurate.

My machine can work at speed ~120url/s and it requires ~50Mb/s of internet
connection. Sequential mode requires ~70*10^12 years to check all possible
combinations.

## Examples

Run 20 workers and save output to ```output.txt``` file:
```
python3 run.py -w 20 -o output.txt
```

Run 10 workers and use sequential mode (aka brute-force):
```
python3 run.py -sw 10
```

Run extractor, to receive sequential if of the link:
```
python3 run.py -e https://cloud.mail.ru/public/ceY5/Sy9n2TNCa
```

Run checker, to check if links is valid:
```
python3 run.py -c -o output.txt
```


