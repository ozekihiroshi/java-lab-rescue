import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from lab import selected

class SelectionTest(unittest.TestCase):
    def test_inherited_compose_labels(self):
        config = {'name':'lab', 'services':{'jupyterhub':{'environment':{
            'JAVA_LEARNER_NETWORK':'lab-learners','JAVA_USER_VOLUME_PREFIX':'lab-user'}}}}
        learner = {'Config':{'Labels':{'com.docker.compose.project':'lab','com.docker.compose.service':'singleuser-image'}},
            'NetworkSettings':{'Networks':{'lab-learners':{}}},
            'Mounts':[{'Name':'lab-user-10','Destination':'/home/jovyan/work'}]}
        hub = {'Config':{'Labels':{'com.docker.compose.project':'lab','com.docker.compose.service':'jupyterhub'}},
            'NetworkSettings':{'Networks':{'lab-learners':{}}},'Mounts':[]}
        self.assertEqual(selected(config,[learner,hub]),([hub],[learner]))
        foreign=dict(learner,Mounts=[{'Name':'another-user-10','Destination':'/home/jovyan/work'}])
        self.assertEqual(selected(config,[foreign]),([],[]))

if __name__ == '__main__': unittest.main()
