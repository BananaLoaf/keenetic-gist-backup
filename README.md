# keenetic-gist-backup

Docker app to regularly backup your Keenetic config to a private github gist. Crontab schedule is defined in SCHEDULE variable  

1. Copy `.env.template` as `.env`, fill in all the values
2. Run `docker-compose up --build -d`