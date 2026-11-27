import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('profile_generator',ROOT/'scripts/profile.py')
p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
SNAPSHOT=json.loads((ROOT/'assets/profile/snapshot.json').read_text())

class ProfileTests(unittest.TestCase):
    def test_offline_outputs_reproduce_and_are_safe_xml(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp); p.generate(SNAPSHOT,out)
            self.assertEqual(sorted(x.name for x in out.iterdir()),sorted(x.name for x in (ROOT/'assets/profile').iterdir()))
            for f in out.iterdir():
                self.assertEqual(f.read_bytes(),(ROOT/'assets/profile'/f.name).read_bytes(),f.name)
                if f.suffix=='.svg':
                    root=ET.fromstring(f.read_text())
                    self.assertIsNotNone(root.find('{http://www.w3.org/2000/svg}title'))
                    self.assertIsNotNone(root.find('{http://www.w3.org/2000/svg}desc'))
                    self.assertNotIn('<script',f.read_text())
                    self.assertNotIn('foreignObject',f.read_text())
                    for el in root.iter():
                        self.assertFalse(any(k.lower().startswith('on') for k in el.attrib))

    def test_missing_data_is_not_fabricated_and_external_text_is_escaped(self):
        data=copy.deepcopy(SNAPSHOT)
        data['latest_commit']=None;data['latest_release']=None
        self.assertIn('No public commits',p.island(data,'dark'))
        self.assertIn('No stable releases',p.island(data,'light',True))
        data['latest_commit']=copy.deepcopy(SNAPSHOT['latest_commit'])
        data['latest_commit']['message']='<script>&"'
        svg=p.island(data,'dark');ET.fromstring(svg)
        self.assertIn('&lt;script&gt;',svg);self.assertNotIn('<script>',svg)

    def test_rejects_invalid_data_without_changing_previous_output(self):
        for mutate in (lambda d:d['activity'].pop(),lambda d:d['activity'][0].update(commits=-1),lambda d:d['repos'][0].update(downloads=None)):
            data=copy.deepcopy(SNAPSHOT);mutate(data)
            with tempfile.TemporaryDirectory() as temp:
                out=Path(temp); (out/'sentinel').write_text('last good')
                with self.assertRaises(ValueError):p.generate(data,out)
                self.assertEqual([x.name for x in out.iterdir()],['sentinel'])

    def test_pagination_and_failures(self):
        with patch.object(p,'api',side_effect=[list(range(100)),[100]]) as call:
            self.assertEqual(len(p.pages('/test?x=1')),101)
            self.assertIn('&per_page=100&page=2',call.call_args.args[0])
        with patch.object(p,'api',side_effect=ValueError('network failed')):
            with self.assertRaises(ValueError):p.collect()

    def test_weekly_and_language_denominator(self):
        text=p.island(SNAPSHOT,'dark')
        total=sum(d['commits'] for d in SNAPSHOT['activity'][-7:])
        self.assertIn(f'{total} authored commits',text)
        counts=p.Counter(r['language'] or 'Unclassified' for r in SNAPSHOT['repos'])
        for name,n in counts.items():self.assertIn(f'{name} {n}/{len(SNAPSHOT["repos"])}',p.monitor(SNAPSHOT,'light'))

class ProfilePublishTests(unittest.TestCase):
    def test_fixed_output_branch_protected_sources_noop_and_update(self):
        script=(ROOT/'scripts/publish_profile.sh').read_text()
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);repo=base/'repo';repo.mkdir();remote=base/'remote.git';runner=base/'runner'
            (runner/'profile').mkdir(parents=True)
            def git(*args):return subprocess.check_output(['git',*args],cwd=repo,stderr=subprocess.STDOUT,text=True).strip()
            git('init','--bare',str(remote));git('init','-b','main')
            git('config','user.name','Test');git('config','user.email','test@example.invalid')
            (repo/'README.md').write_text('unchanged');git('add','.');git('commit','-m','Initial')
            original=git('rev-parse','HEAD');git('remote','add','origin',str(remote))
            for branch in ('main','contribution-world','feat/profile-under-the-hood'):git('push','origin',f'HEAD:refs/heads/{branch}')
            for name in ('island-dark.svg','snapshot.json','snapshot.md'):(runner/'profile'/name).write_text('fixture')
            env=dict(os.environ,RUNNER_TEMP=str(runner),PROFILE_SOURCE_REF='feat/profile-under-the-hood',PROFILE_DEFAULT_REF='main')
            def publish(ok=True):
                result=subprocess.run(['bash','-c',script],cwd=repo,env=env,capture_output=True,text=True)
                self.assertEqual(result.returncode==0,ok,result.stderr)
            publish(False)
            env['PROFILE_SOURCE_REF']='main';publish();first=git('rev-parse','HEAD');publish();self.assertEqual(git('rev-parse','HEAD'),first)
            self.assertEqual(git('ls-tree','--name-only','HEAD'), 'assets')
            (runner/'profile/snapshot.json').write_text('updated');publish();self.assertNotEqual(git('rev-parse','HEAD'),first)
            for branch in ('main','contribution-world','feat/profile-under-the-hood'):
                self.assertEqual(git('ls-remote','origin',f'refs/heads/{branch}').split()[0],original)
