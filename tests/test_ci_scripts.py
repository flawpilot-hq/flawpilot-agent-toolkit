"""Run the CI example scripts against a local mock of the FlawPilot REST API.
Skipped when curl or jq is missing. Run: python3 -m unittest discover -s tests"""
import json
import os
import shutil
import subprocess
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REFS = REPO / "plugins/flawpilot/skills/ci/references"
HAVE_TOOLS = all(shutil.which(t) for t in ("curl", "jq", "bash", "awk"))


class Mock(BaseHTTPRequestHandler):
    # Scenario state is set per test on the server object.
    def log_message(self, *a):
        pass

    def reply(self, code, body, headers=None):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        sc = self.server.scenario
        self.server.hits.append(("POST", self.path))
        if self.headers.get("Authorization") != "Bearer test-key":
            return self.reply(401, {"statusCode": 401, "message": "Unauthorized"})
        if sc.get("malformed_trigger") and self.path.endswith("/trigger"):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            return self.reply(200, [] if "code-scans" in self.path else {})
        if self.path == "/v1/scans/trigger":
            if sc.get("rate_limit_once") and not self.server.rate_limited:
                self.server.rate_limited = True
                return self.reply(429, {"error": "slow down"}, {"Retry-After": "1"})
            return self.reply(202, {"scanJobId": "scan-1", "status": "QUEUED"})
        if self.path == "/v1/code-scans/trigger":
            dims = json.loads(self.rfile.read(int(self.headers["Content-Length"])))["dimensions"]
            return self.reply(200, [{"id": f"job-{d}", "dimension": d, "status": "QUEUED", "branch": "main", "scanRunId": "run-1"} for d in dims])
        self.reply(404, {"statusCode": 404, "message": "nope"})

    def do_GET(self):
        sc = self.server.scenario
        self.server.hits.append(("GET", self.path))
        if self.headers.get("Authorization") != "Bearer test-key":
            return self.reply(401, {"statusCode": 401, "message": "Unauthorized"})
        if self.path == "/v1/scans/scan-1/status":
            return self.reply(200, sc["scan_status"])
        if self.path == "/v1/code-scans/runs/run-1":
            return self.reply(200, sc["run_status"])
        if self.path.startswith("/v1/code-scans/jobs/") and "severity=CRITICAL" in self.path:
            job = self.path.split("/")[4]
            return self.reply(200, {"items": [], "total": sc["critical"].get(job, 0), "page": 1, "limit": 1})
        self.reply(404, {"statusCode": 404, "message": "nope"})


def dims(*pairs):
    return {"scanRunId": "run-1", "dimensions": [
        {"dimension": d, "status": s, "score": None if s != "COMPLETED" else 80.0, "findingsCount": 12}
        for d, s in pairs]}


@unittest.skipUnless(HAVE_TOOLS, "needs curl, jq, bash, awk")
class CiScriptTests(unittest.TestCase):
    def serve(self, scenario):
        srv = HTTPServer(("127.0.0.1", 0), Mock)
        srv.scenario, srv.hits, srv.rate_limited = scenario, [], False
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.server_close)
        self.addCleanup(srv.shutdown)
        return srv

    def run_script(self, name, srv, **env):
        e = {**os.environ, "API": f"http://127.0.0.1:{srv.server_port}", "FLAWPILOT_API_KEY": "test-key",
             "POLL_SECONDS": "0", "MAX_POLLS": "3", **env}
        return subprocess.run(["bash", str(REFS / name)], env=e, capture_output=True, text=True, timeout=60)

    # quick-scan.sh
    def test_quick_scan_passes_above_threshold(self):
        srv = self.serve({"scan_status": {"status": "COMPLETE", "score_security": 82.5, "reportLink": "https://app.example/r"}})
        r = self.run_script("quick-scan.sh", srv, PROJECT_ID="PRJ-1", TARGET_URL="https://example.com")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("PASS", r.stdout)

    def test_quick_scan_fails_below_threshold_with_decimal_score(self):
        srv = self.serve({"scan_status": {"status": "COMPLETE", "score_security": 62.5}})
        r = self.run_script("quick-scan.sh", srv, PROJECT_ID="PRJ-1", TARGET_URL="https://example.com")
        self.assertEqual(r.returncode, 1)
        self.assertIn("below", r.stderr)

    def test_quick_scan_missing_score_is_failure_not_zero(self):
        srv = self.serve({"scan_status": {"status": "PARTIAL", "score_seo": 90}})
        r = self.run_script("quick-scan.sh", srv, PROJECT_ID="PRJ-1", TARGET_URL="https://example.com")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no score", r.stderr)

    def test_quick_scan_unscanned_pillar_reading_zero_is_not_a_score(self):
        # Live API returns 0 for pillars that were not scanned; only `categories` lists scanned ones.
        srv = self.serve({"scan_status": {"status": "COMPLETE", "score_security": 89.07, "score_seo": 0,
                                          "categories": [{"pillar": "SECURITY", "score": 89.07}]}})
        r = self.run_script("quick-scan.sh", srv, PROJECT_ID="PRJ-1", TARGET_URL="https://example.com", PILLAR="score_seo", MIN_SCORE="0")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no score", r.stderr)

    def test_quick_scan_reads_score_from_categories(self):
        srv = self.serve({"scan_status": {"status": "COMPLETE", "score_security": 89.07,
                                          "categories": [{"pillar": "SECURITY", "score": 89.07}]}})
        r = self.run_script("quick-scan.sh", srv, PROJECT_ID="PRJ-1", TARGET_URL="https://example.com")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_quick_scan_failed_status(self):
        srv = self.serve({"scan_status": {"status": "FAILED"}})
        r = self.run_script("quick-scan.sh", srv, PROJECT_ID="PRJ-1", TARGET_URL="https://example.com")
        self.assertEqual(r.returncode, 1)

    def test_quick_scan_timeout_is_failure(self):
        srv = self.serve({"scan_status": {"status": "RUNNING"}})
        r = self.run_script("quick-scan.sh", srv, PROJECT_ID="PRJ-1", TARGET_URL="https://example.com")
        self.assertEqual(r.returncode, 1)
        self.assertIn("timed out", r.stderr)

    def test_quick_scan_retries_after_429(self):
        srv = self.serve({"rate_limit_once": True, "scan_status": {"status": "COMPLETE", "score_security": 90}})
        r = self.run_script("quick-scan.sh", srv, PROJECT_ID="PRJ-1", TARGET_URL="https://example.com")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Rate limited", r.stderr)

    def test_bad_key_fails_without_retry(self):
        srv = self.serve({"scan_status": {"status": "COMPLETE"}})
        r = self.run_script("quick-scan.sh", srv, PROJECT_ID="PRJ-1", TARGET_URL="https://example.com", FLAWPILOT_API_KEY="wrong")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(len([h for h in srv.hits if h[0] == "POST"]), 1)
        self.assertNotIn("wrong", r.stdout + r.stderr)

    def test_quick_scan_rejects_unknown_pillar(self):
        srv = self.serve({"scan_status": {}})
        r = self.run_script("quick-scan.sh", srv, PROJECT_ID="PRJ-1", TARGET_URL="https://example.com", PILLAR="score_total")
        self.assertEqual(r.returncode, 2)

    def test_quick_scan_malformed_trigger_response_fails_fast(self):
        srv = self.serve({"malformed_trigger": True, "scan_status": {"status": "COMPLETE", "score_security": 99}})
        r = self.run_script("quick-scan.sh", srv, PROJECT_ID="PRJ-1", TARGET_URL="https://example.com")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no scanJobId", r.stderr)
        self.assertFalse([h for h in srv.hits if h[0] == "GET"], "must not poll /scans/null")

    def test_code_scan_malformed_trigger_response_is_not_a_pass(self):
        srv = self.serve({"malformed_trigger": True, "run_status": dims(("SAST", "COMPLETED")), "critical": {}})
        r = self.run_script("code-scan.sh", srv, REPO_ID="repo-1")
        self.assertEqual(r.returncode, 1)
        self.assertNotIn("PASS", r.stdout)

    # code-scan.sh
    def test_code_scan_passes_with_no_critical(self):
        srv = self.serve({"run_status": dims(("SAST", "COMPLETED"), ("SECRETS", "COMPLETED")), "critical": {}})
        r = self.run_script("code-scan.sh", srv, REPO_ID="repo-1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("PASS: 0", r.stdout)

    def test_code_scan_fails_on_critical_even_when_all_severity_count_is_low_noise(self):
        srv = self.serve({"run_status": dims(("SAST", "COMPLETED"), ("SCA", "COMPLETED")), "critical": {"job-SCA": 2}})
        r = self.run_script("code-scan.sh", srv, REPO_ID="repo-1", DIMENSIONS='["SAST","SCA"]')
        self.assertEqual(r.returncode, 1)
        self.assertIn("2 CRITICAL", r.stderr)

    def test_code_scan_threshold_allows_some_critical(self):
        srv = self.serve({"run_status": dims(("SAST", "COMPLETED")), "critical": {"job-SAST": 1}})
        r = self.run_script("code-scan.sh", srv, REPO_ID="repo-1", DIMENSIONS='["SAST"]', MAX_CRITICAL="1")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_code_scan_failed_dimension_fails(self):
        srv = self.serve({"run_status": dims(("SAST", "COMPLETED"), ("SECRETS", "FAILED")), "critical": {}})
        r = self.run_script("code-scan.sh", srv, REPO_ID="repo-1", DIMENSIONS='["SAST","SECRETS"]')
        self.assertEqual(r.returncode, 1)
        self.assertIn("SECRETS", r.stderr)

    def test_code_scan_timeout_fails(self):
        srv = self.serve({"run_status": dims(("SAST", "RUNNING")), "critical": {}})
        r = self.run_script("code-scan.sh", srv, REPO_ID="repo-1", DIMENSIONS='["SAST"]')
        self.assertEqual(r.returncode, 1)
        self.assertIn("timed out", r.stderr)

    def test_code_scan_null_score_prints_na_not_zero(self):
        srv = self.serve({"run_status": dims(("SAST", "FAILED")), "critical": {}})
        r = self.run_script("code-scan.sh", srv, REPO_ID="repo-1", DIMENSIONS='["SAST"]')
        self.assertIn("score=n/a", r.stdout)


if __name__ == "__main__":
    unittest.main()
