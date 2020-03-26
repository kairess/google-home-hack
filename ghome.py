import os
import time
import http.server
import socket
import threading

import pychromecast
from gtts import gTTS

# ip address of Google Home must be in same network with the server
ghome_ip = '192.168.35.212'
lang = 'ko'
say = '''
죽는 날까지 하늘을 우러러
한점 부끄럼이 없기를,
잎새에 이는 바람에도
나는 괴로워했다.
별을 노래하는 마음으로
모든 죽어가는 것을 사랑해야지
그리고 나한테 주어진 길을
걸어가야겠다.

오늘밤에도 별이 바람에 스치운다.
'''

# get my local ip address
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect(('8.8.8.8', 80))
    local_ip, _ = s.getsockname()

# set up a simple server
PORT = 8000

class StoppableHTTPServer(http.server.HTTPServer):
    def run(self):
        try:
            print('Server started at %s:%s!' % (local_ip, self.server_address[1]))
            self.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.server_close()

# start server in background
server = StoppableHTTPServer(('', PORT), http.server.SimpleHTTPRequestHandler)
thread = threading.Thread(None, server.run)
thread.start()

# connect to Google Home
ghome = pychromecast.Chromecast(ghome_ip)
print(ghome)
ghome.wait()

# set volume level, no beep sound
volume = ghome.status.volume_level
ghome.set_volume(0)

# create tts mp3
os.makedirs('cache', exist_ok=True)
fname = 'cache/cache.mp3'

tts = gTTS(say, lang=lang)
tts.save(fname)

# ready to serve the mp3 file from server
mc = ghome.media_controller

mp3_path = 'http://%s:%s/%s' % (local_ip, PORT, fname)
mc.play_media(mp3_path, 'audio/mp3')
# mc.play_media('http://www.hochmuth.com/mp3/Tchaikovsky_Nocturne__orch.mp3', 'audio/mp3')

# pause atm
mc.block_until_active()
mc.pause()

# volume up
time.sleep(0.5)
ghome.set_volume(volume)
time.sleep(1)

# play
mc.play()
while not mc.status.player_is_idle:
    time.sleep(1)

# kill all
mc.stop()
ghome.quit_app()
server.shutdown()
os.remove(fname)
thread.join()
