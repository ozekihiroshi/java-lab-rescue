import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import prepare
import capacity

DOCUMENT = {'schema_version': 1, 'kind': 'java', 'platform': {
    'issuer': 'https://moodle.school.test', 'authorize_url': 'https://moodle.school.test/mod/lti/auth.php',
    'jwks_url': 'https://moodle.school.test/mod/lti/certs.php', 'client_id': 'client-test', 'deployment_id': '2'},
    'tool': {'base_url': 'https://java.school.test', 'login_url': 'https://java.school.test/hub/lti13/oauth_login',
             'callback_url': 'https://java.school.test/hub/lti13/oauth_callback',
             'target_url': 'https://java.school.test/hub/user-redirect/ide/'}}


class PrepareTests(unittest.TestCase):
    def test_repeat_preserves_unrelated_settings_and_backup(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); source = p / 'connection.json'; source.write_text(json.dumps(DOCUMENT))
            target = p / '.env.production'
            with patch.object(prepare, 'ROOT', Path(__file__).resolve().parent):
                prepare.prepare(source, target)
                self.assertIn('JAVA_ACTIVE_SERVER_LIMIT=1', target.read_text())
                text = target.read_text().replace('JAVA_ACTIVE_SERVER_LIMIT=1', 'JAVA_ACTIVE_SERVER_LIMIT=3') + 'CUSTOM_STORAGE=keep-me\n'
                target.write_text(text)
                prepare.prepare(source, target)
                prepare.prepare(source, target)
            self.assertEqual(target.read_text(), text)
            self.assertEqual((p / '.env.production.before-connect').read_text(), text)

    def test_rebind_rejected_without_writes(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); source = p / 'connection.json'; source.write_text(json.dumps(DOCUMENT))
            target = p / '.env.production'; target.write_text('LTI_CLIENT_ID=other-client\n')
            with self.assertRaises(ValueError):
                prepare.prepare(source, target)
            self.assertEqual(target.read_text(), 'LTI_CLIENT_ID=other-client\n')
            self.assertFalse((p / '.env.production.before-connect').exists())

    def test_wrong_origin_kind_and_target_rejected(self):
        for group, key, value in [('platform', 'issuer', 'http://moodle.school.test'),
                                  ('tool', 'target_url', 'https://java.school.test/hub/user-redirect/lab/'),
                                  ('platform', 'client_id', 'id\nINJECT=x')]:
            doc = copy.deepcopy(DOCUMENT); doc[group][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                prepare.validate(doc)
        doc = copy.deepcopy(DOCUMENT); doc['kind'] = 'python'
        with self.assertRaises(ValueError): prepare.validate(doc)

    def test_duplicate_keys_rejected(self):
        with self.assertRaises(ValueError):
            prepare.merge('LTI_CLIENT_ID=client-test\nexport LTI_CLIENT_ID=client-test\n', {'LTI_CLIENT_ID': 'client-test'})

    def test_small_host_budget_fails_even_without_other_workloads(self):
        self.assertFalse(capacity.assess({'MemAvailable': 2 * capacity.GIB}, 1)['memory_budget_pass'])
        self.assertTrue(capacity.assess({'MemAvailable': 5 * capacity.GIB}, 1)['memory_budget_pass'])
        self.assertFalse(capacity.assess({'MemAvailable': 5 * capacity.GIB}, 2)['memory_budget_pass'])


if __name__ == '__main__': unittest.main()
