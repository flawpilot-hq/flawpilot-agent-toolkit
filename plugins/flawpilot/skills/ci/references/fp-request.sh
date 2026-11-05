# Sourced by quick-scan.sh and code-scan.sh. Needs curl.
# Expects API and FLAWPILOT_API_KEY to be set by the caller.
#
# Rules: 2xx returns the body. 429 waits Retry-After seconds (default 30) and
# retries. 5xx retries with backoff. Any other 4xx fails at once and prints the
# body, which carries the error code. The key is never echoed.

MAX_ATTEMPTS="${MAX_ATTEMPTS:-5}"
HDR="${HDR:-$(mktemp)}"

# fp_request METHOD PATH [JSON_BODY] -> body on stdout, non-zero on failure
fp_request() {
  local method="$1" path="$2" body="${3:-}" attempt=1 delay raw code payload
  while :; do
    local args=(-sS -X "$method" "$API$path"
      -H "Authorization: Bearer $FLAWPILOT_API_KEY"
      -D "$HDR" -w '\n%{http_code}')
    [ -n "$body" ] && args+=(-H "Content-Type: application/json" -d "$body")

    raw=$(curl "${args[@]}") || { echo "network error" >&2; return 1; }
    code=$(printf '%s' "$raw" | tail -n1)
    payload=$(printf '%s' "$raw" | sed '$d')

    case "$code" in
      2*) printf '%s' "$payload"; return 0 ;;
      429)
        delay=$(grep -i '^retry-after:' "$HDR" | tr -d '\r' | awk '{print $2}')
        delay="${delay:-30}"
        echo "Rate limited; retrying in ${delay}s (attempt $attempt/$MAX_ATTEMPTS)" >&2 ;;
      5*)
        delay=$((attempt * 5))
        echo "Server error $code; retrying in ${delay}s (attempt $attempt/$MAX_ATTEMPTS)" >&2 ;;
      *)
        echo "Request failed: HTTP $code" >&2
        echo "$payload" >&2
        return 1 ;;
    esac

    attempt=$((attempt + 1))
    if [ "$attempt" -gt "$MAX_ATTEMPTS" ]; then
      echo "Giving up after $MAX_ATTEMPTS attempts" >&2
      return 1
    fi
    sleep "$delay"
  done
}

fp_get() { fp_request GET "$1"; }
fp_post() { fp_request POST "$1" "$2"; }
