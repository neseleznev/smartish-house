import os
import sys

TORRENT_SERVER_PORT = 8880
KODI_PORT = 8080
VLC_PORT = 8881

ACESTREAM_DIR = os.path.join(
    os.path.dirname(os.path.realpath(sys.argv[0])),
    'acestream')
ACESTREAM_START = os.path.join(ACESTREAM_DIR, 'start_acestream.sh')
ACESTREAM_STOP = os.path.join(ACESTREAM_DIR, 'stop_acestream.sh')
ACESTREAM_LOG = os.path.join(ACESTREAM_DIR, 'acestream.log')
ACESTREAM_CACHE = os.path.join(
    ACESTREAM_DIR, 'androidfs', 'data', 'data',
    'org.acestream.media', 'files', '.ACEStream', '.acestream_cache')
