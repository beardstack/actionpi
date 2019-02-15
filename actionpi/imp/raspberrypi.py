import logging
import subprocess
import psutil

from actionpi import AbstractIO, AbstractCamera, AbstractSystem

try:
    from gpiozero import Button
except (ImportError, ModuleNotFoundError) as e:
    raise ImportError("No module gpiozero installed")

try:
    from picamera import PiCamera
except (ImportError, ModuleNotFoundError) as e:
    raise ImportError("No module picamera installed")

class RaspberryPiCamera(AbstractCamera):

    def _start(self):
        if self._camera is None:
            self._camera = PiCamera(resolution= (self._width, self._heigth), framerate=self._fps)
            self._camera.start_recording(self._output_file)

    def _stop(self):
        if self._camera is not None:
            self._camera.stop_recording()
            self._camera.close()
            self._camera = None

    def _recording(self) -> bool:
        return (self._camera is not None) and (self._camera.recording)

    def get_framerate(self) -> int:
        if self._camera is not None:
            return int(self._camera.framerate)
        else:
            return 0
    
    def set_led_status(self, status: bool):
        if self._camera is not None:
            self._camera.led = status

    def capture_frame(self) -> str:
        if self._camera is not None:
            self._camera.capture('capture.jpg', use_video_port=True)

class RaspberryPiSystem(AbstractSystem):
    def get_cpu_temp(self) -> float:
        try:
            temp = int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1e3
            return temp
        except IOError:
            return 0

    def get_cpu_percent(self) -> int:
        return psutil.cpu_percent(interval=None)

    def get_disks_usage(self) -> dict:
        disk_usages = dict()
        for part in psutil.disk_partitions(all=False):
            mountpoint = part.mountpoint
            usage = psutil.disk_usage(mountpoint)
            disk_usages[mountpoint] = usage
        return disk_usages
    
    def get_ram_usage(self) -> int:
        return psutil.virtual_memory().percent

    def halt_system(self):
        subprocess.run(["shutdown", "-H", "now"])

    def enable_hotspot(self) -> bool:
        pass

    def disable_hotspot(self) -> bool:
        pass

    def get_hw_revision(self) -> str:
        hw_rev = "00000"
        try:
            f = open('/proc/cpuinfo','r')
            for line in f:
                if line[0:8]=='Revision':
                    hw_rev = line[10:]
            f.close()
        except:
            hw_rev = "00000"

        return hw_rev

    def get_serial(self) -> str:
        # Extract serial from cpuinfo file
        cpuserial = "0000000000000000"
        try:
            f = open('/proc/cpuinfo','r')
            for line in f:
                if line[0:6]=='Serial':
                    cpuserial = line[10:26]
            f.close()
        except:
            cpuserial = "ERROR000000000"

        return cpuserial

class RaspberryPiIO(AbstractIO):

    def __init__(self, camera: AbstractCamera, gpio_number: int):
        super().__init__(camera, gpio_number)
        self.button = Button(gpio_number)
    
    def start_monitoring(self):
        super().start_monitoring()
        self.button.when_pressed = self._camera.start_recording()
        self.button.when_released = self._camera.stop_recording()

        if self.button.is_pressed:
            self._camera.start_recording()

    def close(self):
        super().close()
        self.button.close()
        self.button = None