# Local verification — 2026-09-22

WSL Ubuntu-24.04 Docker Engine, existing local Moodle at port 8083, Java Lab at port 8087. AWS was not accessed or modified for deployment.

- Built Hub and learner images from this independent repository. Existing Docker build cache was used; this was not a cold dependency-download test.
- Recreated Hub/JWKS from the independent Compose while retaining the existing project, Hub data and learner volumes.
- Both existing Moodle learners completed signed LTI login, learner spawn and IDE HTTP 200.
- Java compiled and printed the expected result in both learner containers.
- Distinct saved markers survived stop/start and LTI relaunch; existing Java/CSV source hashes in all three retained learner volumes matched the pre-migration record.
- A stopped Hub backup was taken before migration. No Moodle course, submission or learner source file was replaced.
- The lifecycle selector has a regression test for Compose image labels inherited by learner containers; learners are identified by both network and workspace volume.
- Public configuration tests passed (four test methods plus invalid topology checks and real Hub config load). This is configuration testing, not public TLS/LTI acceptance.

Repeatable checks: `python3 checks/local.py`, `python3 checks/test_lifecycle.py`, `python3 public/test_local.py`. The migration LTI checks use private local test credentials and are kept outside this public repository. Logs and credentials are not published.

Not claimed: a newly installed Moodle end-to-end test, a cold image build, public AWS deployment, capacity guarantee, or disaster-recovery acceptance. The initial services-network allocation failed because this host exhausted Docker's default pools; the prior explicit subnet was restored and startup then passed.
