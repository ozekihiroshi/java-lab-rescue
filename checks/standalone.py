"""Local-only acceptance: login, IDE, Java execution, stop/restart persistence."""
from pathlib import Path
import http.cookiejar
import re
import subprocess
import time
import urllib.parse
import urllib.request
import uuid

ROOT=Path(__file__).resolve().parents[1]
settings=dict(line.split('=',1) for line in (ROOT/'.env.standalone').read_text().splitlines() if '=' in line)
base='http://127.0.0.1:'+settings.get('JAVA_STANDALONE_PORT','8088')


def login():
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    page=opener.open(base+'/hub/login',timeout=15).read().decode()
    token=re.search(r'name="_xsrf" value="([^"]+)"',page)[1]
    response=opener.open(base+'/hub/login',data=urllib.parse.urlencode({'username':'learner','password':settings['JAVA_LOCAL_PASSWORD'],'_xsrf':token}).encode(),timeout=180)
    for _ in range(60):
        path=urllib.parse.urlsplit(response.url).path
        if path.startswith('/user/learner/'):
            assert response.status==200; return
        assert '/hub/login' not in path, 'Login failed'
        time.sleep(3)
        response=opener.open(base+'/hub/user-redirect/ide/',timeout=180)
    raise RuntimeError('IDE launch timed out')


login()
print('PASS: Moodle-free login and IDE HTTP 200',flush=True)
marker='.standalone-check-'+uuid.uuid4().hex
code="from pathlib import Path; import tempfile,subprocess; p=Path('/home/jovyan/work')/"+repr(marker)+"; p.write_text('saved'); d=Path(tempfile.mkdtemp()); (d/'Main.java').write_text('public class Main { public static void main(String[] a) { System.out.println(42); }}'); subprocess.run(['javac',str(d/'Main.java')],check=True); assert subprocess.check_output(['java','-cp',str(d),'Main'],text=True).strip()=='42'"
subprocess.run(['docker','exec','-u','1000','java-lab-standalone-learner','python','-c',code],check=True)
subprocess.run(['python3',str(ROOT/'scripts/lab.py'),'--standalone','stop'],check=True)
assert 'java-lab-standalone-learner' not in subprocess.check_output(['docker','ps','--format','{{.Names}}'],text=True).split()
subprocess.run(['python3',str(ROOT/'scripts/lab.py'),'--standalone','start'],check=True)
login()
subprocess.run(['docker','exec','-u','1000','java-lab-standalone-learner','python','-c',
                "from pathlib import Path; p=Path('/home/jovyan/work')/"+repr(marker)+"; assert p.read_text()=='saved'; p.unlink()"],check=True)
print('PASS: Java compile/run and persistent workspace after standalone stop/start',flush=True)
