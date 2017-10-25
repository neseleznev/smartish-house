#!/bin/bash
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# I. Python requirements
echo -e "${WHITE}I. Installing python requirements${NC}"
pip3 install -r requirements.txt


# II. System binaries
echo -e "${WHITE}II. Installing system binaries${NC}"
PERMISSION=""
SYSNSPAWN=""
TELNET=""

if [ $(id -u) != 0 ]; then
  PERMISSION=$(which sudo)
  if [ ! -x "$PERMISSION" ]; then
    echo -e "${RED}Without sudo and not a root. Sorry, see you later${NC}"
    exit 1
  fi
fi

SYSNSPAWN=$(which systemd-nspawn)
if [ -z "$SYSNSPAWN" ]; then
  echo -e "Your system does not have ${YELLOW}systemd-nspawn${NC} binary. ${BLUE}Installing...${NC}"
  ${PERMISSION} apt install -y systemd-container
fi

TELNET=$(which telnet)
if [ -z "$TELNET" ]; then
  echo -e "Your system does not have ${YELLOW}telnet${NC} binary. ${BLUE}Installing...${NC}"
  ${PERMISSION} apt install -y telnet
fi


# III. Acestream build and elevate
echo -e "${WHITE}III. Installing AceStream Engine${NC}"
rm -rf cheamstream
git clone https://github.com/miltador/cheapstream

if [ "$1" == "arm" ] || [ "$1" == "x86" ]; then
    cheamstream/build.sh $1
else
    echo -e "${RED}Error!${NC}"
    echo -e "Usage: ./install.sh ${YELLOW}platform${NC}
    Platform must be one of {${BLUE}arm${NC}, ${BLUE}x86${NC}}"
    exit
fi

mv cheapstream/dist/ acestream
rm -rf cheapstream

${PERMISSION} chown root:root acestream/start_acestream.sh
${PERMISSION} chown root:root acestream/stop_acestream.sh
${PERMISSION} chmod 4775 acestream/start_acestream.sh
${PERMISSION} chmod 4775 acestream/stop_acestream.sh


# IV. Player
echo -e "${WHITE}IV. Installing Kodi player${NC}"
KODI=$(which kodi)
if [ -z "$KODI" ]; then
  echo -e "Currently only ${YELLOW}kodi${NC} player is supported. ${BLUE}Installing...${NC}"
  ${PERMISSION} apt install -y kodi
fi

mkdir -p ~/.kodi/userdata  # TODO know how it works under root
cp core/advancedsettings.xml ~/.kodi/userdata


# V. Create config
echo -e "${WHITE}V. Creating config${NC}"
echo "[DEFAULT]
token: xxxxxxxxx:yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
torrent_dir: ~/Torrents" > config.ini

if [ "$1" == "arm" ]; then
    echo "platform: ARM_V7" >> config.ini
else
    echo "platform: LINUX_X86" >> config.ini
fi

echo "
# Uncomment following lines to enable Telegram Webhooks
# [TELEGRAM]
# host: 11.22.33.44 # or domain.com
# key: ./webhook_pkey.key
# cert: ./webhook_cert.pem" >> config.ini

echo -e "Open ${BLUE}./config.ini${NC} and fill it with your parameters"
echo -e "Ciao!"
