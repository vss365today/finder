#!/usr/bin/env bash
# Get the latest code
git pull

# Build a new container
docker build -t vss365today-finder:latest .

# Restart the service
cd ../server
docker stop -t 0 finder
docker-compose up -d finder
cd ../finder
