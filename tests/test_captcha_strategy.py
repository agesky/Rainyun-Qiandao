import unittest

try:
    import cv2  # noqa: F401
    import numpy as np
except ModuleNotFoundError:
    cv2 = None
    np = None

if np is not None and cv2 is not None:
    from rainyun.main import StrategyCaptchaSolver, TemplateMatcher, split_sprite_image
else:
    StrategyCaptchaSolver = None
    TemplateMatcher = None
    split_sprite_image = None


class DummyMatcher:
    name = "dummy"

    def match(self, background, sprites, bboxes):
        return None


class CaptchaStrategyTests(unittest.TestCase):
    @unittest.skipIf(np is None or cv2 is None, "numpy/cv2 not installed")
    def test_template_matcher_positions(self):
        background = np.zeros((60, 60, 3), dtype=np.uint8)

        sprite1 = np.zeros((10, 10, 3), dtype=np.uint8)
        sprite1[2:8, 2:8] = 255
        sprite2 = np.zeros((10, 10, 3), dtype=np.uint8)
        sprite2[0:5, :] = 255
        sprite3 = np.zeros((10, 10, 3), dtype=np.uint8)
        sprite3[:, 0:3] = 255

        background[5:15, 5:15] = sprite1
        background[20:30, 30:40] = sprite2
        background[40:50, 10:20] = sprite3

        bboxes = [
            (5, 5, 15, 15),
            (20, 30, 30, 40),
            (40, 10, 50, 20),
        ]

        matcher = TemplateMatcher()
        result = matcher.match(background, [sprite1, sprite2, sprite3], bboxes)

        self.assertIsNotNone(result)
        self.assertEqual(result.positions, [(10, 10), (25, 35), (45, 15)])

    @unittest.skipIf(np is None or cv2 is None, "numpy/cv2 not installed")
    def test_solver_fallbacks_to_template(self):
        background = np.zeros((20, 20, 3), dtype=np.uint8)
        sprite = np.zeros((5, 5, 3), dtype=np.uint8)
        sprite[1:4, 1:4] = 255
        background[8:13, 8:13] = sprite

        bboxes = [(8, 8, 13, 13)]
        solver = StrategyCaptchaSolver([DummyMatcher(), TemplateMatcher()])
        result = solver.solve(background, [sprite, sprite, sprite], bboxes)

        self.assertIsNotNone(result)
        self.assertEqual(result.method, "template")

    @unittest.skipIf(np is None or cv2 is None, "numpy/cv2 not installed")
    def test_split_sprite_image(self):
        sprite = np.zeros((5, 10, 3), dtype=np.uint8)
        parts = split_sprite_image(sprite)
        self.assertEqual(len(parts), 3)
        self.assertEqual(parts[0].shape[1], 3)
        self.assertEqual(parts[1].shape[1], 3)
        self.assertEqual(parts[2].shape[1], 4)


if __name__ == "__main__":
    unittest.main()
