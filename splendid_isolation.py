import os, pygame, logging
from sys import argv, exit
from time import time, sleep

from core.api import MPServerAPI
from core.video_pad import MPVideoPad
from core.utils import get_config

class SplendidIsolation(MPServerAPI, MPVideoPad):
	def __init__(self):
		SplendidIsolation.__init__(self)
		
		self.gpio_mappings = xrange(3, 6)
		logging.basicConfig(filename=self.conf['d_files']['module']['log'], level=logging.DEBUG)

	def start(self):
		if not super(SplendidIsolation, self).start():
			return False

		self.conf['d_files']['vp'] = {
			'pid' : os.path.join(BASE_DIR, ".monitor", "vp.pid.txt"),
			'log' : self.conf['d_files']['module']['log']
		}
		self.conf['video_pad'] = get_config('video_pad')

		MPVideoPad.__init__(self)

		# this blocks because video pad needs to be on the main thread!
		self.start_video_pad()

	def play_main_voiceover(self):
		return self.say(os.path.join("prompts", "main_voiceover.wav"))

	def interrupt_video(self):
		logging.info("Interrupting the video!")

		# interrupt video here!  How? TBD...
		return False

	def map_pin_to_key(self, pin):
		return (pin - 3)

	def map_pin_to_tone(self, pin):
		logging.debug("(map_pin_to_tone overridden.)")
		return self.map_pin_to_key(pin)

	def play_tone(self, tone):
		logging.debug("(play_tone overridden.)")

		if self.play_audio(os.path.join(self.conf['media_dir'], "key_sounds", "key_sound_%d.wav" % tone)):
			return self.interrupt_video()

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

