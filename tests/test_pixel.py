import unittest

from gen.pixel import rects, two_frames, validate


class PixelTest(unittest.TestCase):
    PAL = {"A": "#111111", "B": "#222222"}
    def test_rects_merges_runs(self):
        out = rects(["..AA.B"], self.PAL)
        self.assertEqual(out.count("<rect"), 2)
        self.assertIn('<rect x="2" y="0" width="2" height="1" fill="#111111"/>', out)
        self.assertIn('<rect x="5" y="0" width="1" height="1" fill="#222222"/>', out)
    def test_rects_applies_offset_and_scale(self):
        out = rects(["A"], self.PAL, x=10, y=20, scale=4)
        self.assertIn('<rect x="10" y="20" width="4" height="4" fill="#111111"/>', out)
    def test_validate_rejects_ragged_rows(self):
        with self.assertRaises(ValueError): validate(["AA", "A"], self.PAL)
    def test_validate_rejects_unknown_key(self):
        with self.assertRaises(ValueError): validate(["AZ"], self.PAL)
    def test_validate_rejects_empty(self):
        with self.assertRaises(ValueError): validate([], self.PAL)
    def test_two_frames_has_both_groups(self):
        out = two_frames(["A"], ["B"], self.PAL, 0, 0, 1)
        self.assertIn('class="f1"', out); self.assertIn('class="f2"', out)

if __name__ == "__main__":
    unittest.main()
