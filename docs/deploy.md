# Hikka deploy guide

Create Hikka systemd:
```bash
sudo nano /etc/systemd/system/hikka.service
```

```
[Unit]
Description=Uvicorn instance to serve Hikka
After=network.target

[Service]
User=debian
Group=www-data
WorkingDirectory=/home/debian/hikka
Environment="PATH=/home/debian/hikka/venv/bin"
ExecStart=/home/debian/hikka/venv/bin/uvicorn run:app --port=8888

[Install]
WantedBy=multi-user.target
```

Nginx:
```bash
sudo nano /etc/nginx/sites-available/api.hikka.io.conf
```

```
limit_req_zone $binary_remote_addr zone=ip:10m rate=10r/s;

server {
    server_name api.hikka.io;
    listen 80;

    client_max_body_size 2M;

    location / {
        limit_req zone=ip burst=10 delay=10;
s
        proxy_pass http://localhost:8888;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Note: it's possible to use $http_cf_connecting_ip or $http_x_forwarded_for instead of $binary_remote_addr

```bash
sudo ln -s /etc/nginx/sites-available/api.hikka.io.conf /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

Sync systemd:
```
[Unit]
Description=Hikka sync service
After=multi-user.target

[Service]
Type=idle
ExecStart=/home/debian/hikka/venv/bin/python3 /home/debian/hikka/sync.py
WorkingDirectory=/home/debian/hikka
User=debian

[Install]
WantedBy=multi-user.target
```

## Meilisearh

1. Install Meilisearch
```bash
curl -L https://install.meilisearch.com | sh
```

2. Get and edit Meilisearch config
```bash
curl https://raw.githubusercontent.com/meilisearch/meilisearch/latest/config.toml > config.toml
```

3. Create systemd service
```bash
sudo nano /etc/systemd/system/meilisearch.service
```

Service example:
```
[Unit]
Description=Hikka Meilisearch
After=systemd-user-sessions.service

[Service]
Type=simple
WorkingDirectory=/home/debian/hikka-meilisearch
ExecStart=/home/debian/hikka-meilisearch/meilisearch --config-file-path /home/debian/hikka-meilisearch/config.toml
User=debian
Group=debian

[Install]
WantedBy=multi-user.target
```

4. Start service
```bash
sudo systemctl enable meilisearch
sudo systemctl start meilisearch
```

## PostgreSQL

1. Install Posrgres
```bash
sudo apt install postgresql postgresql-contrib
```

2. Create user and database
```bash
sudo -u postgres psql
create database hikka;
create user hikka_admin with encrypted password 'password';
grant all privileges on database hikka to hikka_admin;
```
