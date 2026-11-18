import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openrgb.utils import RGBColor

from addons.color import ColorCorrection
from addons.devices import Devices


class ApplyCorrectionTests(unittest.TestCase):
    def create_gradient_device(self):
        led = SimpleNamespace(id=0)
        device = SimpleNamespace(
            id=1,
            leds=[led],
            zones=[SimpleNamespace(leds=[led])],
        )
        first_color = RGBColor(255, 0, 0)
        second_color = RGBColor(0, 0, 255)
        devices = Devices()
        devices.add_device(device, first_color, second_color, 0.0)
        layers = devices.devices_layers[device.id]
        layers[devices.layer_names[0]] = [first_color]
        layers[devices.layer_names[1]] = [second_color]
        layers[devices.layer_names[2]] = [3]
        layers[devices.layer_names[3]] = [4]
        return devices, device

    def test_hue_correction_rotates_hue_and_wraps(self):
        red = RGBColor(255, 0, 0)

        shifted_forward = ColorCorrection(hue_correction=120.0).apply(red)
        shifted_backward = ColorCorrection(hue_correction=-120.0).apply(red)
        full_rotation = ColorCorrection(hue_correction=360.0).apply(red)
        shifted_purple = ColorCorrection(hue_correction=-80.0).apply(RGBColor(82, 0, 176))

        self.assertEqual(
            (shifted_forward.red, shifted_forward.green, shifted_forward.blue),
            (0, 255, 0),
        )
        self.assertEqual(
            (shifted_backward.red, shifted_backward.green, shifted_backward.blue),
            (0, 0, 255),
        )
        self.assertEqual(
            (full_rotation.red, full_rotation.green, full_rotation.blue),
            (255, 0, 0),
        )
        self.assertEqual(
            (shifted_purple.red, shifted_purple.green, shifted_purple.blue),
            (0, 153, 176),
        )

    def test_color_index_correction_applies_before_blending(self):
        devices, device = self.create_gradient_device()
        devices.set_color_correction(
            device, zone_index=0, hue_correction=120.0, color_index=1
        )

        devices.set_gradient(device, 1, 4)

        color = devices.get_layer(device, devices.layer_names[4])[0]
        self.assertEqual((color.red, color.green, color.blue), (0, 127, 127))

        devices, device = self.create_gradient_device()
        devices.set_color_correction(
            device, zone_index=0, hue_correction=120.0, color_index=2
        )

        devices.set_gradient(device, 1, 4)

        color = devices.get_layer(device, devices.layer_names[4])[0]
        self.assertEqual((color.red, color.green, color.blue), (255, 0, 0))

    def test_zero_or_none_disables_correction_and_omission_keeps_legacy_scope(self):
        for color_index in (0, None):
            with self.subTest(color_index=color_index):
                devices, device = self.create_gradient_device()
                devices.set_color_correction(
                    device, zone_index=0, hue_correction=120.0, color_index=color_index
                )

                devices.set_gradient(device, 1, 4)

                color = devices.get_layer(device, devices.layer_names[4])[0]
                self.assertEqual((color.red, color.green, color.blue), (127, 0, 127))

        devices, device = self.create_gradient_device()
        devices.set_color_correction(device, zone_index=0, hue_correction=120.0)

        devices.set_gradient(device, 1, 4)

        color = devices.get_layer(device, devices.layer_names[4])[0]
        self.assertEqual((color.red, color.green, color.blue), (127, 127, 0))


if __name__ == "__main__":
    unittest.main()
