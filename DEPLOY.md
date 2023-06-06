# Hikka deploy guide

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
