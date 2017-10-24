
# Smartish House

Telegram bot responsible for some actions in Helen & Nikita's house.

## Installation
System tools
```
sudo apt-get install -y telnet systemd-container
```

First lines are common for every distribution
```
git clone https://github.com/neseleznev/smartish-house
cd smartish-house

git clone https://github.com/miltador/cheapstream
cd cheapstream
```

Next line is platform-specific
```
# Raspbery Pi (Debian-based Linux arm-v7)
./build.sh arm
# Debian-based Linux x86 (x86-64 also)
./build.sh x86
```

```
cd ..
mv cheapstream/dist/ acestream
rm -rf cheapstream
```

Install Kodi and configure API port
```
sudo apt-get install kodi
mkdir -p ~/.kodi/userdata
cp core/advancedsettings.xml ~/.kodi/userdata
```

## Configs
Change the following content with your token and preferences,
then execute
```
echo '[DEFAULT]
token: xxxxxxxxx:yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
torrent_dir: Torrents
platform: ARM_V7
;platform: LINUX_X86
' > config.ini
```

## Run
Start the bot (Sorry, currently with sudo)
```
sudo python3 bot.py
```
