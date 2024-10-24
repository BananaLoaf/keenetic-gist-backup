# keenetic-gist-backup

Docker app to regularly backup your Keenetic startup config to a private github gist. Crontab schedule can be edited in `Dockerfile`  

1. Copy `.env.template` as `.env`, fill in all the values
2. Run `docker-compose up --build -d`