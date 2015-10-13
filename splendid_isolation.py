import tornado.web, os, logging, random
from sys import argv, exit
from time import time, sleep

from core.vars import BASE_DIR
from core.api import MPServerAPI
from core.utils import get_config
from core.video_pad import MPVideoPad

class SplendidIsolation(MPServerAPI, MPVideoPad):
	def __init__(self):
		MPServerAPI.__init__(self)

		self.conf['d_files']['vid'] = {
			'log' : os.path.join(BASE_DIR, ".monitor", "%s.log.txt" % self.conf['rpi_id'])
		}

		MPVideoPad.__init__(self)
		logging.basicConfig(filename=self.conf['d_files']['module']['log'], level=logging.DEBUG)

	def start(self):
		if not super(SplendidIsolation, self).start():
			return False

		return self.start_video_pad()

	def play_main_voiceover(self):
		return self.say(os.path.join("prompts", "main_voiceover.wav"), interruptable=True)

	def map_pin_to_tone(self, pin):
		logging.debug("(map_pin_to_tone overridden.)")
		return random.randint(0, 2)

	def press(self, key):
		logging.debug("(press overridden.)")
		key = self.map_pin_to_tone(key)

		try:
			return self.pause() and \
				self.play_clip(os.path.join("key_sounds", "key_sound_%d.wav" % key)) and \
				self.unpause()
		except Exception as e:
			print e, type(e)
		
		return False

	def run_script(self):
		super(SplendidIsolation, self).run_script()
		self.play_main_voiceover()

if __name__ == "__main__":
	res = False
	si = SplendidIsolation()

	if argv[1] in ['--stop', '--restart']:
		res = si.stop()
		sleep(5)

	if argv[1] in ['--start', '--restart']:
		res = si.start()

	exit(0 if res else -1)

