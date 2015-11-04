import tornado.web, os, json, logging, random
from sys import argv, exit
from time import sleep
from random import shuffle

from core.vars import BASE_DIR, UNPLAYABLE_FILES
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

		for r, _, files in os.walk(os.path.join(self.conf['media_dir'], "key_sounds")):
			self.key_sounds = [os.path.join(r, f) for f in files if f not in UNPLAYABLE_FILES]
			shuffle(self.key_sounds)
			break

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
		self.stop_video_pad()
		for video_mapping in self.video_mappings:
			self.db.delete("video_%s" % video_mapping.index)

		return super(SplendidIsolation, self).stop()

	def play_main_voiceover(self):
		return self.say(os.path.join("prompts", "splendidisolation2.wav"), interruptable=True)

	def pause_video(self, video, unpause=False, video_callback=None):
		return super(SplendidIsolation, self).pause_video(video, unpause=unpause, video_callback=self.video_listener_callback)

	def press(self, key):
		logging.debug("(press overridden.)")

		try:
			return self.pause() and \
				self.pause_video(self.main_video) and \
				self.play_clip(self.key_sounds[int(key) - 1]) and \
				self.unpause() and \
				self.unpause_video(self.main_video)
		except Exception as e:
			print e, type(e)
		
		return False

	def start(self):
		if not super(SplendidIsolation, self).start():
			return False

		return self.play_video(self.main_video, video_callback=self.video_listener_callback)

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

