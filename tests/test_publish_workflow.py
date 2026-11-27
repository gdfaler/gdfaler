"""Exercise the actual publishing shell against a local remote, without GitHub."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


class PublishTests(unittest.TestCase):
    def test_publish_leaves_main_unchanged_and_skips_identical_data(self):
        workflow=(ROOT/'.github/workflows/contribution-world.yml').read_text()
        shell=workflow.rsplit('        run: |\n',1)[1]
        shell='\n'.join(line[10:] for line in shell.splitlines())
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp); remote=base/'remote.git'; repo=base/'repo'; runner=base/'runner'
            repo.mkdir(); (runner/'world').mkdir(parents=True)
            def git(*args,cwd=repo):
                return subprocess.check_output(['git',*args],cwd=cwd,stderr=subprocess.STDOUT,text=True).strip()
            git('init','--bare',str(remote))
            git('init','-b','main')
            git('config','user.email','test@example.invalid'); git('config','user.name','Test')
            (repo/'README.md').write_text('Keep my profile unchanged\n')
            git('add','.'); git('commit','-m','Initial profile')
            original=git('rev-parse','HEAD')
            git('remote','add','origin',str(remote)); git('push','-u','origin','main')
            for name in ('world-dark.svg','world-light.svg','calendar.json'):
                (runner/'world'/name).write_text('fixture '+name)
            env=dict(os.environ,RUNNER_TEMP=str(runner),GIT_CONFIG_NOSYSTEM='1')
            def publish():
                subprocess.run(['bash','-c',shell],cwd=repo,env=env,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            publish()
            first=git('rev-parse','HEAD')
            self.assertNotEqual(first,original)
            self.assertEqual(git('ls-tree','--name-only','HEAD').splitlines(), ['calendar.json','world-dark.svg','world-light.svg'])
            publish()
            self.assertEqual(git('rev-parse','HEAD'),first)
            self.assertEqual(git('ls-remote','origin','refs/heads/main').split()[0],original)
            (runner/'world'/'calendar.json').write_text('new day')
            publish()
            self.assertNotEqual(git('rev-parse','HEAD'),first)
            self.assertEqual(git('ls-remote','origin','refs/heads/main').split()[0],original)
