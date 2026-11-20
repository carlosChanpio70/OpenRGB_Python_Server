import datetime

from openrgb import OpenRGBClient
import time
from addons.color import Color
from addons.devices import Devices
from addons.volume import VolumeMonitor 

class NoDevicesFoundError(RuntimeError):
    """Raised when the OpenRGBClient reports no hardware devices."""
    pass

color_2_percentage = 0.2
gradient_min_steps = 4
gradient_max_steps = 6
names = ["Corsair Vengeance RGB Pro", "MSI MPG B550 GAMING PLUS (MS-7C56)"]

def startup():
    """
    Starts the OpenRGB Client
    :return: The client
    """
    while True:
        try:
            client = OpenRGBClient()
            
            devices = Devices()
            if not client.devices:                          # empty list is falsy
                # no hardware detected yet; raise a specific exception so
                # the outer loop can retry without swallowing unrelated
                # errors
                raise NoDevicesFoundError("no devices found")
            else:
                for device in client.devices:
                    device.set_mode(0)
                    color1 = colors[0].get_color()
                    color2 = colors[1].get_color()

                    devices.add_device(device, color1, color2, color_2_percentage)
                    if device.name == names[1]:
                        devices.set_color_correction(device,zone_name="JRAINBOW2",hue_correction=-10.0,color_index=2)
                    else:
                        devices.set_color_correction(device,zone_index=0)
                return client,devices
        except Exception as e:
            print(e)
            time.sleep(.1)

def update_effects(device, devices, volume_level) -> None:
    devices.set_gradient(device, gradient_min_steps, gradient_max_steps)

    if device.name == names[1]:
        devices.set_color_final(device, colors[0].get_color(), 0)
    if names[0].casefold() in device.name.casefold():
        devices.set_volume(device, volume_level)
    devices.apply_final_layer(device)

def main():
    client, devices = startup()

    fps = 24
    frame_time = 1.0 / fps

    while True:
        try:
            start = time.perf_counter()
            volume.update_volume()
            volume_level = volume.get_volume()

            for device in devices.get_device():
                update_effects(device, devices, volume_level)
            client.show()

            elapsed = time.perf_counter() - start
            sleep_time = frame_time - elapsed
            
            if sleep_time > 0:
                time.sleep(sleep_time)
        except Exception as e:
            print(e)
            client, devices = startup()

def color_selector():
    purple = Color()
    purple.set_hex("#5200b0")
    white = Color()
    white.set_hex("#ffffff")
    yellow = Color()
    yellow.set_hex("#ffff00")
    red = Color()
    red.set_hex("#ff0000")
    
    today = datetime.date.today()
    months = []
    for month in range(1, 13):
        months.append(datetime.date(month=month, day=today.day, year=today.year))
    
    global colors
    if today in months[10:12]:
        colors = [red, yellow]
    else:
        colors = [purple, white]

if __name__ == "__main__":
    volume = VolumeMonitor()
    volume.start()
    color_selector()
    main()