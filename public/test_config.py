"""Run in the existing Hub image: no network, Docker socket or user volumes."""
import asyncio
import os
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch
from traitlets.config import Config
from tornado.web import HTTPError

BASE = {
    'JAVA_LAB_HOST': 'java.school.test', 'MOODLE_ORIGIN': 'https://moodle.school.test',
    'JAVA_SINGLEUSER_IMAGE': 'registry.school.test/java@sha256:' + 'a' * 64,
    'JAVA_ACTIVE_SERVER_LIMIT': '2', 'LTI_CLIENT_ID': 'registered-client',
    'LTI_DEPLOYMENT_IDS': 'deployment-1',
}


def load(overrides=None):
    with patch.dict(os.environ, dict(BASE, **(overrides or {})), clear=True):
        return runpy.run_path(str(Path(__file__).with_name('jupyterhub_config.py')),
                              init_globals={'get_config': Config})


class PublicConfigTests(unittest.TestCase):
    def test_https_and_storage_isolation(self):
        c = load()['c']
        self.assertEqual(c.LTI13Authenticator.uri_scheme, 'https')
        self.assertEqual(c.LTI13Authenticator.jwks_endpoint, 'https://moodle.school.test/mod/lti/certs.php')
        self.assertEqual(c.DockerSpawner.network_name, 'java-lab-public-learners')
        self.assertEqual(c.DockerSpawner.volumes, {'java-lab-public-user-{username}': '/home/jovyan/work'})
        self.assertEqual(c.JupyterHub.active_server_limit, 2)

    def test_unsafe_settings_rejected(self):
        cases = [('MOODLE_ORIGIN', 'http://moodle.school.test'),
                 ('MOODLE_ORIGIN', 'https://user:password@moodle.school.test'),
                 ('MOODLE_ORIGIN', 'https://moodle.school.test/'),
                 ('JAVA_LAB_HOST', 'localhost'),
                 ('JAVA_LAB_HOST', 'java.example.org'),
                 ('JAVA_SINGLEUSER_IMAGE', 'java:latest'),
                 ('JAVA_ACTIVE_SERVER_LIMIT', '0'), ('LTI_DEPLOYMENT_IDS', ',')]
        for key, value in cases:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                load({key: value})

    def test_registered_learner_allowed(self):
        hook = load()['restrict_deployment']
        auth = {'auth_state': {
            'https://purl.imsglobal.org/spec/lti/claim/deployment_id': 'deployment-1',
            'https://purl.imsglobal.org/spec/lti/claim/roles': ['http://purl.imsglobal.org/vocab/lis/v2/membership#Learner']}}
        self.assertIs(asyncio.run(hook(None, None, auth)), auth)

    def test_guest_and_other_deployment_rejected(self):
        hook = load()['restrict_deployment']
        for deployment, roles in [('other', ['http://purl.imsglobal.org/vocab/lis/v2/membership#Learner']), ('deployment-1', []), ('deployment-1', ['Guest'])]:
            with self.subTest(deployment=deployment, roles=roles), self.assertRaises(HTTPError):
                asyncio.run(hook(None, None, {'auth_state': {
                    'https://purl.imsglobal.org/spec/lti/claim/deployment_id': deployment,
                    'https://purl.imsglobal.org/spec/lti/claim/roles': roles}}))


if __name__ == '__main__':
    unittest.main()
