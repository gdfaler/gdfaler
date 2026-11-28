import importlib.util
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('profile_showcase',ROOT/'scripts/profile_showcase.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
NS='{http://www.w3.org/2000/svg}'

class ShowcaseTests(unittest.TestCase):
    def test_reproduction_and_self_contained_xml(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp);p.generate(out)
            self.assertEqual(len(list(out.glob('*.svg'))),12)
            for f in out.glob('*.svg'):
                self.assertEqual(f.read_bytes(),(ROOT/'assets/showcase'/f.name).read_bytes(),f.name)
                root=ET.fromstring(f.read_text())
                self.assertEqual(root.attrib['role'],'img')
                self.assertIsNotNone(root.find(NS+'title'))
                self.assertNotIn('<script',f.read_text())
                self.assertNotIn('foreignObject',f.read_text())
                for image in root.iter(NS+'image'):
                    self.assertTrue(image.attrib['href'].startswith('data:image/png;base64,'))
    def test_scene_content_and_accessibility(self):
        for theme in ('dark','light'):
            for mobile in (False,True):
                source=p.render(theme,mobile);root=ET.fromstring(source)
                scenes=[x for x in root.findall(NS+'g') if 'scene' in x.attrib.get('class','').split()]
                self.assertEqual(len(scenes),4)
                self.assertIsNotNone(root.find(NS+'desc'))
                self.assertIn('prefers-reduced-motion:reduce',source)
                for label in ('DynamicIsland','HWMonitor','TorrentPlayer','BMSTU','EARLY MVP'):
                    self.assertIn(label,source)
                self.assertEqual(root.attrib['width'],'420' if mobile else '900')
    def test_corrupt_icon_preserves_last_good_output(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);icons=base/'icons';icons.mkdir();out=base/'out';out.mkdir()
            (out/'showcase-dark.svg').write_text('last good output')
            (icons/'dynamic-island.png').write_text('not a PNG')
            with self.assertRaises(ValueError):p.generate(out,icons)
            self.assertEqual((out/'showcase-dark.svg').read_text(),'last good output')
            self.assertEqual(len(list(out.iterdir())),1)
