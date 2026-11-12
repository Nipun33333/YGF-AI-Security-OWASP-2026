import unittest
from security_lab import all_cases,simulate_control,Sandbox

class SecurityLabTest(unittest.TestCase):
    def test_33_fixture_cases_have_vulnerable_and_hardened_outcomes(self):
        cases=list(all_cases())
        self.assertEqual(len(cases),33)
        for case in cases:
            with self.subTest(case=case['case_id']):
                self.assertTrue(simulate_control(case,False)['violated'])
                self.assertFalse(simulate_control(case,True)['violated'])
    def test_no_real_side_effects(self):
        sb=Sandbox()
        self.assertIn('FAKE OUTBOX',sb.send_email('a@example.invalid','toy',harden=False))
        self.assertFalse(sb.outbox[0]['sent'])
        self.assertFalse(sb.http_log)
    def test_mcp_boundary(self):
        sb=Sandbox()
        unsafe={'server_id':'rogue','tools':['send_email'],'scope':'read-write'}
        self.assertIn('BLOCKED',sb.mcp_connect(unsafe,harden=True))
        self.assertEqual(len(sb.tool_log),0)
    def test_private_file(self):
        sb=Sandbox()
        self.assertNotIn('SECRET-FLAG',sb.read_file('private.txt',harden=True))

if __name__=='__main__': unittest.main()
