#!/usr/bin/env bash
# Post-deploy gate: run a Quick Scan on a deployed URL and fail the build if a
# pillar score is below a threshold, the scan failed, or it timed out.
# Needs curl, jq, awk. Env: FLAWPILOT_API_KEY, PROJECT_ID, TARGET_URL.
# Optional: PILLAR (default score_security), MIN_SCORE (70), POLL_SECONDS (10), MAX_POLLS (60).
set -euo pipefail

: "${FLAWPILOT_API_KEY:?set FLAWPILOT_API_KEY}"
: "${PROJECT_ID:?set PROJECT_ID}"
: "${TARGET_URL:?set TARGET_URL}"

API="${API:-https://api.flawpilot.com}"
PILLAR="${PILLAR:-score_security}"
MIN_SCORE="${MIN_SCORE:-70}"
POLL_SECONDS="${POLL_SECONDS:-10}"
MAX_POLLS="${MAX_POLLS:-60}"

HDR=$(mktemp)
trap 'rm -f "$HDR"' EXIT
# shellcheck source=fp-request.sh
source "$(dirname "$0")/fp-request.sh"

# Gate the pillar that matches the score you check.
case "$PILLAR" in
  score_security) pillars='["SECURITY"]' ;;
  score_performance) pillars='["PERFORMANCE"]' ;;
  score_infrastructure) pillars='["INFRASTRUCTURE"]' ;;
  score_seo) pillars='["SEO"]' ;;
  *) echo "PILLAR must be one of score_security, score_performance, score_infrastructure, score_seo" >&2; exit 2 ;;
esac

scan_id=$(fp_post "/v1/scans/trigger" \
  "$(jq -nc --arg p "$PROJECT_ID" --arg u "$TARGET_URL" --argjson pl "$pillars" \
      '{projectId:$p,url:$u,pillars:$pl}')" | jq -r '.scanJobId')
if [ -z "$scan_id" ] || [ "$scan_id" = "null" ]; then
  echo "FAIL: trigger response had no scanJobId" >&2
  exit 1
fi
echo "Scan $scan_id queued"

status=""
body=""
for _ in $(seq 1 "$MAX_POLLS"); do
  body=$(fp_get "/v1/scans/$scan_id/status")
  status=$(jq -r '.status' <<<"$body")
  case "$status" in COMPLETE | PARTIAL | FAILED) break ;; esac
  sleep "$POLL_SECONDS"
done

case "$status" in
  COMPLETE | PARTIAL) ;;
  FAILED) echo "FAIL: scan did not complete" >&2; exit 1 ;;
  *) echo "FAIL: timed out (last status: ${status:-unknown})" >&2; exit 1 ;;
esac

echo "Status: $status"
echo "Report: $(jq -r '.reportLink // "n/a"' <<<"$body")"

# Absent is not zero: never turn a missing score into 0.
# Unrequested pillars come back as 0, so read the score from `categories` (only
# scanned pillars appear there) and fall back to the flat field if it is absent.
PILLAR_NAME=$(tr '[:lower:]' '[:upper:]' <<<"${PILLAR#score_}")
score=$(jq -r --arg p "$PILLAR" --arg n "$PILLAR_NAME" '
  if has("categories") then ([.categories[] | select(.pillar == $n) | .score][0] // "")
  elif has($p) and .[$p] != null then .[$p] else "" end' <<<"$body")
if [ -z "$score" ]; then
  echo "FAIL: $PILLAR has no score in a $status scan" >&2
  exit 1
fi

echo "$PILLAR: $score (threshold $MIN_SCORE)"
# awk, because scores are decimals and [ -lt ] is integer-only.
if awk -v s="$score" -v m="$MIN_SCORE" 'BEGIN { exit !(s < m) }'; then
  echo "FAIL: $PILLAR $score is below $MIN_SCORE" >&2
  exit 1
fi
echo "PASS"
