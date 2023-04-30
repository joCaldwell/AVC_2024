from Camera import Camera
import Config

class Data(object):
    def __init__(self):
        self._camera = Camera(Config.num_regions,show=Config.show, internet_cam=Config.internet_cam)

        self.cam = None 
        self.encoder = [] #[l,r]
        self.sonar = [] #[l,fl,f,fr,r]
        self.lidar = None
        self.mag = []

    def get_data(self):
        self.cam = self._camera.get_buckets()