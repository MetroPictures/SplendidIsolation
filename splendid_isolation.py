import tornado.web, os, json, logging, random
from sys import argv, exit
from time import sleep

from core.vars import BASE_DIR
from core.api import MPServerAPI
from core.utils import get_config
from core.video_pad import MPVideoPad

class SplendidIsolation(MPServerAPI, MPVideoPad):
	def __init__(self):
		MPServerAPI.__init__(self)

		self.main_video = "splendid_isolation.mp4"		
		self.conf['d_files'].update({
			'vid' : {
				'log' : os.path.join(BASE_DIR, ".monitor", "%s.log.txt" % self.conf['rpi_id'])
			},
			'video_listener_callback' : {
				'log' : os.path.join(BASE_DIR, ".monitor", "%s.log.txt" % self.conf['rpi_id']),
				'pid' : os.path.join(BASE_DIR, ".monitor", "video_listener_callback.pid.txt")
			}
		})

		MPVideoPad.__init__(self)
		logging.basicConfig(filename=self.conf['d_files']['module']['log'], level=logging.DEBUG)

	def video_listener_callback(self, info):
		try:
			video_info = json.loads(self.db.get("video_%d" % info['index']))
			video_info.update(info['info'])
		except Exception as e:
			video_info = info['info']

		self.db.set("video_%d" % info['index'], json.dumps(video_info))		
		logging.info("VIDEO INFO UPDATED: %s" % self.db.get("video_%d" % info['index']))

	def stop(self):
		if not super(SplendidIsolation, self).stop():
			return False

		return self.stop_video_pad()

	def play_main_voiceover(self):
		self.play_video(self.main_video, video_callback=self.video_listener_callback)
		return self.say(os.path.join("prompts", "main_voiceover.wav"), interruptable=True)

	def map_key_to_tone(self, key):
		logging.debug("(map_pin_to_tone overridden.)")
		return random.randint(0, 2)

	def pause_video(self, video, unpause=False, video_callback=None):
		return super(SplendidIsolation, self).pause_video(video, unpause=unpause, video_callback=self.video_listener_callback)

	def press(self, key):
		logging.debug("(press overridden.)")
		key = self.map_key_to_tone(key)

		try:
			return self.pause() and \
				self.pause_video(self.main_video) and \
				self.play_clip(os.path.join("key_sounds", "key_sound_%d.wav" % key)) and \
				self.unpause() and \
				self.unpause_video(self.main_video)
		except Exception as e:
			print e, type(e)
		
		return False

	def reset_for_call(self):
		for video_mapping in self.video_mappings:
			self.db.delete("video_%s" % video_mapping.index)

		super(SplendidIsolation, self).reset_for_call()

	def on_hang_up(self):
		self.stop_video_pad()
		return super(SplendidIsolation, self).on_hang_up()

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

