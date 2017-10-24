
# Smartish House

Telegram bot responsible for some actions in Helen & Nikita's house.

## Installation
System tools
```
sudo apt-get install -y systemd-container
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

Open Kodi API port
```
mkdir -p ~/.kodi/userdata
cp core/advancedsettings.xml ~/.kodi/userdata
```

Start the bot (Sorry, currently with sudo)
```
sudo python3 bot.py
```
