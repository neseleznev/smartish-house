# Smartish House

Telegram bot responsible for some actions in Helen & Nikita's house.

## Installation
```
git clone https://github.com/neseleznev/smartish-house
cd smartish-house

./install.sh arm
# or ./install.sh x86
```

The script will install
* python3 requirements
* `telnet`, `systemd-container`, and `kodi` if needed
* AceStream Engine container with elevated launcher

Change `config.ini` file up to your needs

## (Optional) Set Webhook
If you have public IP, you may want to enable Telegram Webhook
in order to avoid network errors. Open `config.ini` and check <b>[TELEGRAM]</b> section.
You will have to generate https certificate, the easiest way is:
```
openssl genrsa -out webhook_pkey.key 2048
# When asked for "Common Name (e.g. server FQDN or YOUR name)"
# you should reply with host ip or domain name
openssl req -new -x509 -days 3650 -key webhook_pkey.key -out webhook_cert.pem
```

## Run
Start the bot
```
python3 bot.py
```
