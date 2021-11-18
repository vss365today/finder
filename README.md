# #vss365 today finder

> [#vss365 today](https://vss365today.com/) prompt tweet finder service

## Required Secrets

- Path to archive downloads directory (`DOWNLOADS_PATH`)
- Path to static prompt images directory (`IMAGES_DIR`)
- Crontab-formatted list of finder run times (`SCHEDULE_TIMES`)
- Twitter API v2 bearer token (`TWITTER_BEARER`)
- Running instance of [#vss365 today API](https://github.com/le717/vss365today-api)
  - Operating domain (`API_DOMAIN`)
  - API key with `has_archive`, `has_broadcast`, `has_host`, `has_prompt`, `has_settings`, and `has_subscription` permissions (`API_AUTH_TOKEN`)

## Development

1. Install [Python](https://www.python.org/) 3.9+, [Poetry](https://poetry.eustace.io/) 1.1.0+, and VS Code
1. Create required secret keys in appropriate place (default: `secrets`)
1. Modify `configuration/default.json` as required
1. Run `poetry install`
1. Launch the app using the provided VS Code launch configuration


## Build

Creating a Docker image will install all required components.
Creating an image is a one-line command:

1. `docker build -t vss365today-finder:latest .`

## License

2020-2021 Caleb Ely

[MIT](LICENSE)
