# Dice Tower


### Getting Started

```
$ pip install -r requirements.txt
```


### Look Back Reports
Given any week of the year, the look back report will fetch a user's video review contributions
from BoardGameGeek, the user's collection ratings and comments for the given week 1 year ago,
5 years ago and 10 years ago.


**Usage**

Generate look back reports in month 5 (May), 1 year, 5 years and 10 years before 2022: 
```
$ python generate_look_back_report.py <bgg-user-name> --month 5 --year 2022
```


Generate look back reports for all months, 1 year, 5 years and 10 years before 2022: 
```
$ python generate_look_back_report.py <bgg-user-name> --month all --year 2022
```


**Options**

| Option | Type | Default | Description |
| ------ | ---- | ------- | ----------- |
| user | string | N/A | Required. The BGG username to generate a report for. |
| `--month` | number or string | "current" | The month to look back from. |
| `--week` | number or string | "current" | The week to look back from. Ignored if month option is provided. |
| `--year` | number | 2022 (or current year) | The year to look back from. |


### Known Issues

Currently, there is a [known issue](https://github.com/lcosmin/boardgamegeek/issues/67) with one of the dependancies of
this repository. [The fix](https://github.com/lcosmin/boardgamegeek/pull/68) must be manually applied for things to work
correctly.