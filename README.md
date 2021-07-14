# #vss365 today finder

> [#vss365 today](https://vss365today.com/) prompt tweet finder service

## Required Configuration

- Running instance of [#vss365 today API](https://github.com/le717/vss365today-api/) (`API_DOMAIN`)
  - API key for protected endpoint access (`API_AUTH_TOKEN`)
- Twitter API v1 consumer key and consumer secret, read-only (`TWITTER_APP_KEY`, `TWITTER_APP_SECRET`)

## Install

1. Install Python 3.9+ and [Poetry](https://python-poetry.org/) 1.1.0+
1. Create secret files in appropriate place (default: `secrets`)
1. `$ poetry install`

## Build

1. Modify `configuration/default.json` as required
1. `$ docker build -t vss365today-finder:latest .`

## License

2020 Caleb Ely

[MIT](LICENSE)
