import unittest

from gen.content import INVENTORY
from gen.pixel import validate
from gen.sprites import misc
from gen.sprites.avatar import AVATAR_A, AVATAR_B, AVATAR_BLINK, PALETTE
from gen.sprites.items import ITEMS
from gen.sprites.misc import ICONS, MUG, PAC, ghost
from gen.sprites.people import PEOPLE

MISC_STATIC = ("CAT", "TROPHY", "HEART_ON", "HEART_OFF", "STAR", "ARROW", "DOWN", "DOT",
               "ENVELOPE", "LINKEDIN_IN", "DOWNLOAD", "GLOBE", "PLANT")


def all_static_sprites():
    """Recorre todos los sprites de los módulos como pares (filas, paleta)."""
    for name in MISC_STATIC:
        yield name, getattr(misc, name)
    for name, spr in ICONS.items():
        yield f"ICONS[{name}]", spr
    for name, spr in ITEMS.items():
        yield f"ITEMS[{name}]", spr
    yield "ghost", ghost("#f85149")
    for name, (a, b, pal) in (("MUG", MUG), ("PAC", PAC)):
        yield f"{name}.a", (a, pal)
        yield f"{name}.b", (b, pal)
    for i, (a, b, pal) in enumerate(PEOPLE):
        yield f"PEOPLE[{i}].a", (a, pal)
        yield f"PEOPLE[{i}].b", (b, pal)
    for name, rows in (("AVATAR_A", AVATAR_A), ("AVATAR_B", AVATAR_B), ("AVATAR_BLINK", AVATAR_BLINK)):
        yield name, (rows, PALETTE)


class SpritesTest(unittest.TestCase):
    def test_every_sprite_validates(self):
        for name, (rows, pal) in all_static_sprites():
            with self.subTest(name):
                validate(rows, pal)

    def test_two_frame_sprites_same_size(self):
        for a, b, pal in PEOPLE + [(AVATAR_A, AVATAR_B, PALETTE), MUG, PAC]:
            self.assertEqual((len(a), len(a[0])), (len(b), len(b[0])))

    def test_avatar_size_and_traits(self):
        for fr in (AVATAR_A, AVATAR_B, AVATAR_BLINK):
            self.assertEqual((len(fr[0]), len(fr)), (24, 30))
            joined = "".join(fr)
            for key in "HSGWB":
                self.assertIn(key, joined)      # pelo, piel, sudadera, reloj, pulsera visibles
        self.assertEqual(PALETTE["B"], "#c0c7d0"); self.assertEqual(PALETTE["H"], "#6b4423")
        self.assertEqual(PALETTE["S"], "#e8b48a"); self.assertEqual(PALETTE["b"], "#eef2f6")

    def test_bracelet_and_watch_two_rows_tall(self):
        # con una sola fila apenas se veían a 830 px
        for fr in (AVATAR_A, AVATAR_B):
            self.assertEqual(sum("B" in r for r in fr), 2)     # pulsera
            self.assertEqual(sum("w" in r for r in fr), 2)     # esfera del reloj

    def test_avatar_frames_alternate_hands(self):
        def row(key, frame): return min(i for i, r in enumerate(frame) if key in r)
        self.assertLess(row("B", AVATAR_A), row("B", AVATAR_B))       # A: sube la mano de la pulsera
        self.assertGreater(row("W", AVATAR_A), row("W", AVATAR_B))    # B: sube la del reloj
        self.assertEqual(AVATAR_A[:14], AVATAR_B[:14])                # la cabeza no se mueve al teclear

    def test_blink_only_closes_eyes(self):
        self.assertNotIn("K", "".join(AVATAR_BLINK))
        diff_rows = {r for r, (a, c) in enumerate(zip(AVATAR_A, AVATAR_BLINK)) if a != c}
        eye_rows = {r for r, row in enumerate(AVATAR_A) if "K" in row}
        self.assertTrue(diff_rows)
        self.assertLessEqual(diff_rows, eye_rows | {r + 1 for r in eye_rows})

    def test_inventory_has_all_items(self):
        self.assertEqual(set(ITEMS), set(INVENTORY))

    def test_quest_icons(self):
        self.assertEqual(set(ICONS), {"camera", "document", "crab", "city"})

    def test_four_people_distinct(self):
        self.assertEqual(len({tuple(a) + tuple(sorted(p.items())) for a, _, p in PEOPLE}), 4)

    def test_people_size_and_walk(self):
        for a, b, _ in PEOPLE:
            self.assertEqual((len(a[0]), len(a)), (10, 16))
            self.assertNotEqual(a, b)

    def test_ghost_takes_color(self):
        rows, pal = ghost("#56d4dd")
        self.assertIn("#56d4dd", pal.values())


if __name__ == "__main__":
    unittest.main()
