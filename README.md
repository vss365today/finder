# #vss365 today finder

> #vss365 prompt tweet finder service for [#vss365 today](https://vss365today.com/)


## Required Configuration

* Running instance of [#vss365 today API](https://github.com/le717/vss365today-api/) (domain configurable)
* Twitter Consumer API keys
* Twitter access token & access token secret

## Install

1. Install Python 3.8+ and [Poetry](https://python-poetry.org/) 1.0.0+
1. Set missing configuration keys in ??
1. Create secret files in appropriate place (default: `/app/secrets`)
1. `poetry install`
1. `poetry run python finder.py`

## Build

1. `docker build -f "Dockerfile" -t vss365today-finder:latest .`

## License

2020 Caleb Ely

[MIT](LICENSE)
