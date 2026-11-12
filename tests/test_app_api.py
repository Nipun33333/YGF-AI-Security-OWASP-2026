"""End-to-end localhost API smoke tests; no API keys or external network used."""
import json, threading, unittest
from urllib.request import urlopen, Request
from http.server import ThreadingHTTPServer
from app import Handler

class AppAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.host=f'http://127.0.0.1:{cls.server.server_port}'
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join(5)
    def test_scenario_listing(self):
        with urlopen(self.host+'/api/cases') as response:
            cases=json.load(response)
        self.assertEqual(len(cases),33)
    def test_hardened_example(self):
        payload=json.dumps({'case_id':'LLM02-01','provider':'claude','mode':'fixture','hardened':True}).encode()
        request=Request(self.host+'/api/run',data=payload,headers={'Content-Type':'application/json'})
        with urlopen(request) as response:
            result=json.load(response)
        self.assertEqual(result['result'],'NO_MARKER')
        self.assertEqual(result['evidence_type'],'FIXTURE_ONLY_NO_LLM_CALL')
        self.assertNotIn('SECRET-FLAG-123',result['response'])
if __name__=='__main__':unittest.main()
