"""Check a fresh learner image, including IDE Maven settings and cached dependencies."""
import json
from pathlib import Path
import subprocess

subprocess.run(['python','/usr/local/bin/java-materials.py'],check=True)
work = Path.home()/'work'
settings = json.loads((work/'.ide/Machine/settings.json').read_text())
assert settings['java.configuration.maven.userSettings'] == '/opt/java-course/maven-settings.xml'
assert settings['java.jdt.ls.vmargs'] == '-Xms128m -Xmx1024m'
assert settings['java.transport'] == 'stdio'
source = Path('/opt/java-course/materials/java-intro/course-v2')
files = [p for p in source.rglob('*') if p.is_file()]
for file in files:
    assert file.read_bytes() == (work/'java-intro/course-v2'/file.relative_to(source)).read_bytes()
result = subprocess.run(['mvn','-B','-o','-s',settings['java.configuration.maven.userSettings'],
    '-f',str(work/'java-intro/course-v2/lesson-7-3/pom.xml'),'test'],capture_output=True,text=True,timeout=120)
if result.returncode: raise RuntimeError(result.stdout+'\n'+result.stderr)
assert 'Tests run: 5, Failures: 0, Errors: 0' in result.stdout
print(f'PASS: fresh image, {len(files)} files, IDE Maven settings, 5 final-project tests offline')
