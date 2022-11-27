#!/usr/bin/env bash
# Get the latest code
git pull

# Build a new container
docker build -t vss365today-finder:latest .

# Restart the services
cd ../server
docker stop -t 0 finder image_backup
docker-compose up -d finder image_backup
cd ../finder
