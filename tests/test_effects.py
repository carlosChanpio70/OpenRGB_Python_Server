import unittest
from types import SimpleNamespace

from openrgb.utils import RGBColor

from addons.effects import set_volume


class SetVolumeTests(unittest.TestCase):
    def test_volume_bar_uses_second_color_and_preserves_opacity(self):
        leds = [SimpleNamespace(id=index) for index in range(5)]
        device = SimpleNamespace(leds=leds, zones=[SimpleNamespace(leds=leds)])
        color1 = RGBColor(255, 0, 0)
        color2 = RGBColor(255, 255, 0)
        color1.alpha = 0.2
        color2.alpha = 0.8

        colors = set_volume(device, color1, color2, 0.5)

        self.assertEqual((colors[1].red, colors[1].green, colors[1].blue), (255, 255, 0))
        self.assertEqual(colors[1].alpha, 0.2)
        self.assertEqual((colors[2].red, colors[2].green, colors[2].blue), (255, 255, 0))
        self.assertEqual(colors[2].alpha, 0.5)
        self.assertIsNone(colors[3])


if __name__ == "__main__":
    unittest.main()
