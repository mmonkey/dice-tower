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

```
$ python generate_look_back_report.py <bgg-user-name> --week 5 --year 2022
```

**Options**

| Option | Type | Default | Description |
| ------ | ---- | ------- | ----------- |
| user | string | N/A | Required. The BGG username to generate a report for. |
| `--week` | number or string | "current" | The week to look back from. |
| `--year` | number | 2022 (or current year) | The year to look back from. |