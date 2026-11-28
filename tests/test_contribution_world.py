import copy
import datetime as dt
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location('world', Path(__file__).resolve().parents[1]/'scripts/contribution_world.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


class WorldTests(unittest.TestCase):
    def test_calendar_and_leap_bounds(self):
        self.assertEqual(w.bounds(dt.date(2024,2,29)), (dt.date(2023,3,1),dt.date(2024,2,29)))
        self.assertEqual(w.bounds(dt.date(2025,2,28))[0],dt.date(2024,2,29))
        self.assertEqual(len(w.validate(w.demo())),365)

    def test_real_count_controls_height(self):
        values=[w.height(n) for n in (0,1,2,10,100,10000)]
        self.assertEqual(values,sorted(set(values)))

    def test_svg_data_integrity_and_themes(self):
        data=w.demo(); days=w.validate(data)
        for theme in ('dark','light'):
            svg=w.render(data,theme); root=ET.fromstring(svg)
            tiles=[e for e in root.iter() if 'data-date' in e.attrib]
            self.assertEqual(len(tiles),len(days))
            self.assertEqual(sum(int(t.attrib['data-count']) for t in tiles), data['calendar']['totalContributions'])
            self.assertEqual([t.attrib['data-date'] for t in sorted(tiles,key=lambda t:t.attrib['data-date'])], [d['date'] for d in days])
            self.assertIn('SYNTHETIC DEMO',svg)
            self.assertIn('prefers-reduced-motion',svg)
            self.assertNotIn('<script',svg)
            self.assertEqual(svg,w.render(data,theme))
        self.assertNotEqual(w.render(data,'dark'),w.render(data,'light'))

    def test_column_chart_has_real_bars_and_flat_zero_days(self):
        data=w.demo()
        for theme in ('dark','light'):
            root=ET.fromstring(w.render(data,theme))
            ns='{http://www.w3.org/2000/svg}'
            bars=[e for e in root.iter() if 'data-date' in e.attrib]
            heights={}
            for bar in bars:
                count=int(bar.attrib['data-count'])
                z=float(bar.attrib['data-height'])
                self.assertEqual(len(bar.findall(ns+'polygon')),3 if count else 1)
                self.assertEqual(z==0,count==0)
                if count in heights:self.assertEqual(z,heights[count])
                heights[count]=z
            self.assertEqual([heights[n] for n in sorted(heights)],sorted(set(heights.values())))
            labels=' '.join(e.text or '' for e in root.iter(ns+'text'))
            self.assertIn('ONE COLUMN / ONE DAY',labels)
            self.assertNotIn('decorative trees',labels)

    def test_month_panels_preserve_every_date_and_count(self):
        data=w.demo();days=w.validate(data)
        root=ET.fromstring(w.render(data,'dark'))
        ns='{http://www.w3.org/2000/svg}'
        panels=[e for e in root.iter() if e.attrib.get('class')=='month-panel']
        self.assertLessEqual(len(panels),12)
        observed=[]
        expected={d['date']:d['contributionCount'] for d in days}
        for panel in panels:
            bars=[e for e in panel if 'data-date' in e.attrib]
            dates=[e.attrib['data-date'] for e in bars]
            self.assertEqual(panel.attrib['data-start'],dates[0])
            self.assertEqual(panel.attrib['data-end'],dates[-1])
            self.assertEqual(dates,sorted(dates))
            self.assertEqual([int(e.attrib['data-day-index']) for e in bars],list(range(len(bars))))
            total=sum(expected[date] for date in dates)
            labels=[e.text for e in panel.findall(ns+'text')]
            self.assertIn(f'{total} contributions',labels)
            observed.extend(dates)
        self.assertEqual(observed,[d['date'] for d in days])

    def test_zero_and_sparse_calendars(self):
        data=w.demo()
        for week in data['calendar']['weeks']:
            for day in week['contributionDays']:
                day.update(contributionCount=0,contributionLevel='NONE')
        data['calendar']['totalContributions']=0
        ET.fromstring(w.render(data,'light'))
        data['calendar']['weeks']=[{'contributionDays': data['calendar']['weeks'][0]['contributionDays'][:1]}]
        ET.fromstring(w.render(data,'dark'))

    def test_reject_bad_data(self):
        for mutation in ('negative','duplicate','gap','weekday','total','level','source'):
            data=copy.deepcopy(w.demo()); days=data['calendar']['weeks'][0]['contributionDays']
            if mutation=='negative': days[0]['contributionCount']=-1
            if mutation=='duplicate': days[1]=days[0]
            if mutation=='gap': days.pop(1)
            if mutation=='weekday': days[0]['weekday']=99
            if mutation=='total': data['calendar']['totalContributions']+=1
            if mutation=='level': days[0]['contributionLevel']='BOGUS'
            if mutation=='source': data['source']='unknown'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): w.validate(data)

    def test_graphql_request_and_real_label(self):
        calendar=w.demo()['calendar']
        payload={'data':{'user':{'login':'gdfaler','contributionsCollection':{'contributionCalendar':calendar}}}}
        with patch.object(w.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps(payload).encode())) as call:
            data=w.fetch('gdfaler',dt.date(2026,11,27),'test-only')
        request=call.call_args.args[0]; body=json.loads(request.data)
        self.assertIn('contributionCalendar',body['query'])
        self.assertEqual(body['variables']['from'],'2025-11-28T00:00:00Z')
        self.assertIn('GITHUB GRAPHQL · SNAPSHOT',w.render(data,'dark'))
        self.assertNotIn('SYNTHETIC DEMO',w.render(data,'dark'))

    def test_api_errors_and_retry(self):
        for payload in ({'errors':[{'message':'denied'}]}, {'data':{'user':None}}):
            with patch.object(w.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps(payload).encode())):
                with self.assertRaises(ValueError): w.fetch('gdfaler',dt.date.today(),'test-only')
        for code,attempts in ((401,1),(403,1),(502,3)):
            with patch.object(w.urllib.request,'urlopen',side_effect=urllib.error.HTTPError('url',code,'error',{},None)) as call, patch.object(w.time,'sleep'):
                with self.assertRaises(ValueError): w.fetch('gdfaler',dt.date.today(),'test-only')
                self.assertEqual(call.call_count,attempts)

    def test_failure_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'world-dark.svg'; target.write_text('existing')
            with patch.dict(w.os.environ,{},clear=True):
                self.assertEqual(w.main(['--output-dir',temp]),1)
            self.assertEqual(target.read_text(),'existing')
            self.assertEqual(list(Path(temp).iterdir()),[target])

    def test_cli_roundtrip_and_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(w.main(['--demo','--output-dir',temp]),0)
            datafile=Path(temp)/'calendar.json'
            self.assertEqual(w.main(['--input',str(datafile),'--output-dir',temp]),0)
            self.assertEqual(w.main(['--input',str(datafile),'--login','someone-else','--output-dir',temp]),1)


if __name__=='__main__': unittest.main()
