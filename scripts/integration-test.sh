#!/usr/bin/env bash
# End-to-end smoke test against a running stack (compose: http://localhost:8080,
# Kind: http://localhost:8081). Usage: scripts/integration-test.sh [base-url]
set -euo pipefail

BASE_URL="${1:-http://localhost:8080}"
USER_NAME="it-$(date +%s)"

fail() { echo "FAIL: $*" >&2; exit 1; }
json_id() { sed -E 's/^\{"id":([0-9]+).*/\1/'; }

echo "Waiting for $BASE_URL ..."
for _ in $(seq 1 60); do
  curl -sf "$BASE_URL/api/health/ready" >/dev/null && break
  sleep 2
done
curl -sf "$BASE_URL/api/health/ready" >/dev/null || fail "backend never became ready"

echo "Frontend is served"
curl -sf "$BASE_URL/" | grep -q '<div id="root">' || fail "SPA index not served"

echo "Create user"
user_id=$(curl -sf -X POST "$BASE_URL/api/users" -H 'Content-Type: application/json' \
  -d "{\"name\":\"$USER_NAME\"}" | json_id)
auth="X-User-Id: $user_id"

echo "Create task"
task_id=$(curl -sf -X POST "$BASE_URL/api/tasks" -H "$auth" -H 'Content-Type: application/json' \
  -d '{"title":"integration task"}' | json_id)

echo "Update task"
curl -sf -X PATCH "$BASE_URL/api/tasks/$task_id" -H "$auth" -H 'Content-Type: application/json' \
  -d '{"status":"done"}' | grep -q '"status":"done"' || fail "status not updated"

echo "List tasks"
curl -sf "$BASE_URL/api/tasks?status=done" -H "$auth" | grep -q "integration task" \
  || fail "task missing from filtered list"

echo "Ownership is enforced"
other_id=$(curl -sf -X POST "$BASE_URL/api/users" -H 'Content-Type: application/json' \
  -d "{\"name\":\"$USER_NAME-other\"}" | json_id)
code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/api/tasks/$task_id" -H "X-User-Id: $other_id")
[ "$code" = "404" ] || fail "expected 404 for another user's task, got $code"

echo "Delete task"
code=$(curl -s -o /dev/null -w '%{http_code}' -X DELETE "$BASE_URL/api/tasks/$task_id" -H "$auth")
[ "$code" = "204" ] || fail "expected 204 on delete, got $code"

echo "PASS"
