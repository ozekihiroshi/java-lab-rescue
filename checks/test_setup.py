import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import setup

CONNECTION={'schema_version':1,'kind':'java','platform':{
    'issuer':'http://localhost:8083','authorize_url':'http://localhost:8083/mod/lti/auth.php',
    'jwks_url':'http://localhost:8083/mod/lti/certs.php','client_id':'example-client','deployment_id':'2'},
    'tool':{'base_url':'http://localhost:8087','login_url':'http://localhost:8087/hub/lti13/oauth_login',
            'callback_url':'http://localhost:8087/hub/lti13/oauth_callback','target_url':'http://localhost:8087/hub/user-redirect/ide/'}}

class SetupTest(unittest.TestCase):
    def test_reject_cross_lab_and_bad_endpoints(self):
        for key,value in [('kind','python'),('schema_version',2)]:
            with self.assertRaises(ValueError): setup.validate(dict(CONNECTION,**{key:value}))
        wrong=copy.deepcopy(CONNECTION); wrong['platform']['jwks_url']='http://elsewhere/key'
        with self.assertRaises(ValueError): setup.validate(wrong)

    def test_idempotent_import_preserves_storage(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(setup,'ROOT',Path(directory)):
            root=Path(directory); env=root/'.env'
            env.write_text('LTI_CLIENT_ID=example-client\nJAVA_USER_VOLUME_PREFIX=existing-user\n')
            manifest=root/'connection.json'; manifest.write_text(json.dumps(CONNECTION))
            setup.connect(manifest); before=env.read_bytes(); setup.connect(manifest)
            self.assertEqual(before,env.read_bytes())
            self.assertIn('JAVA_USER_VOLUME_PREFIX=existing-user',env.read_text())
            changed=copy.deepcopy(CONNECTION); changed['platform']['client_id']='another-client'
            manifest.write_text(json.dumps(changed))
            with self.assertRaises(ValueError): setup.connect(manifest)
            self.assertEqual(before,env.read_bytes())

if __name__=='__main__': unittest.main()
