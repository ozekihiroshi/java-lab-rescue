import os
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch
from traitlets.config import Config

def config(env):
    with patch.dict(os.environ,env,clear=True):
        return runpy.run_path(str(Path(__file__).resolve().parents[1]/'hub/jupyterhub_config.py'),init_globals={'get_config':Config})['c']

class AuthTest(unittest.TestCase):
    def test_standalone_requires_opt_in(self):
        with self.assertRaises(RuntimeError): config({'JAVA_AUTH_MODE':'standalone','JAVA_LOCAL_PASSWORD':'a'*32})
        with self.assertRaises(RuntimeError): config({'JAVA_AUTH_MODE':'standalone','JAVA_LOCAL_DEVELOPMENT':'true','JAVA_LOCAL_PASSWORD':'short'})

    def test_standalone_has_no_lti_requirement_or_admin(self):
        c=config({'JAVA_AUTH_MODE':'standalone','JAVA_LOCAL_DEVELOPMENT':'true','JAVA_LOCAL_PASSWORD':'a'*32})
        self.assertEqual(c.Authenticator.allowed_users, {'learner'})
        self.assertFalse(c.Authenticator.allow_all)
        self.assertEqual(c.JupyterHub.authenticator_class,'jupyterhub.auth.DummyAuthenticator')

    def test_lti_is_default_and_requires_registration(self):
        with self.assertRaises(RuntimeError): config({})
        c=config({'LTI_CLIENT_ID':'sample'})
        self.assertEqual(c.LTI13Authenticator.client_id,['sample'])
        self.assertEqual(c.LTI13Authenticator.username_key,'sub')

if __name__=='__main__': unittest.main()
