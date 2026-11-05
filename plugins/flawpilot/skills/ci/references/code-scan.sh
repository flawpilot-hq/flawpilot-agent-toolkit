#!/usr/bin/env bash
# Post-merge or nightly gate: run a Code Scan on the branch assigned in
# FlawPilot Integrations and fail on a failed dimension, a timeout, or too many
# CRITICAL findings. Needs curl and jq. Env: FLAWPILOT_API_KEY, REPO_ID.
# Optional: DIMENSIONS (JSON array), MAX_CRITICAL (0), POLL_SECONDS (15), MAX_POLLS (120).
set -euo pipefail

: "${FLAWPILOT_API_KEY:?set FLAWPILOT_API_KEY}"
: "${REPO_ID:?set REPO_ID (integrationRepoId from GET /v1/integration-repos)}"

API="${API:-https://api.flawpilot.com}"
DIMENSIONS="${DIMENSIONS:-[\"SAST\",\"SECRETS\",\"SCA\",\"CODE_QUALITY\"]}"
MAX_CRITICAL="${MAX_CRITICAL:-0}"
POLL_SECONDS="${POLL_SECONDS:-15}"
MAX_POLLS="${MAX_POLLS:-120}"

HDR=$(mktemp)
trap 'rm -f "$HDR"' EXIT
# shellcheck source=fp-request.sh
source "$(dirname "$0")/fp-request.sh"

run=$(fp_post "/v1/code-scans/trigger" \
  "$(jq -nc --arg r "$REPO_ID" --argjson d "$DIMENSIONS" '{integrationRepoId:$r,dimensions:$d}')")
run_id=$(jq -r '.[0].scanRunId' <<<"$run")
job_ids=$(jq -r '.[].id' <<<"$run") # the run status does not return job ids
if [ -z "$run_id" ] || [ "$run_id" = "null" ] || [ -z "$job_ids" ]; then
  echo "FAIL: trigger response had no scanRunId or no jobs; nothing was checked" >&2
  exit 1
fi
echo "Scan run: $run_id (branch: $(jq -r '.[0].branch' <<<"$run"))"

status=""
pending=1
for _ in $(seq 1 "$MAX_POLLS"); do
  status=$(fp_get "/v1/code-scans/runs/$run_id")
  pending=$(jq '[.dimensions[] | select(.status == "QUEUED" or .status == "RUNNING")] | length' <<<"$status")
  [ "$pending" -eq 0 ] && break
  sleep "$POLL_SECONDS"
done

if [ "$pending" -ne 0 ]; then
  echo "FAIL: timed out with $pending dimension(s) still running" >&2
  exit 1
fi

# null score means no result: print n/a, never 0.
jq -r '.dimensions[] | " \(.dimension): \(.status) all-severity findings=\(.findingsCount) score=\(if .score == null then "n/a" else .score end)"' <<<"$status"

failed=$(jq -r '[.dimensions[] | select(.status == "FAILED") | .dimension] | join(", ")' <<<"$status")
if [ -n "$failed" ]; then
  echo "FAIL: dimension(s) did not complete: $failed (a dimension that never ran is not clean)" >&2
  exit 1
fi

# findingsCount covers every severity, so ask each job for CRITICAL only.
critical=0
for job_id in $job_ids; do
  n=$(fp_get "/v1/code-scans/jobs/$job_id/findings?severity=CRITICAL&limit=1" | jq -r '.total // 0')
  critical=$((critical + n))
done

if [ "$critical" -gt "$MAX_CRITICAL" ]; then
  echo "FAIL: $critical CRITICAL finding(s), threshold is $MAX_CRITICAL" >&2
  exit 1
fi
echo "PASS: $critical CRITICAL finding(s), within threshold $MAX_CRITICAL"
