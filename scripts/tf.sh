#!/usr/bin/env bash
# Wrapper for `terraform` that exports AWS creds and the pg-backend conn string.
# Invoked via `mise run tf <env> <terraform args>`.
set -euo pipefail

env="$1"
shift

eval "$(aws configure export-credentials --format env)"

# Fetch PG_CONN_STR for the pg backend. Only "secret not found" is tolerated
# (bootstrap case); other errors must surface, otherwise an empty PG_CONN_STR
# silently degrades to "localhost:5432 connection refused".
sm_out="$(aws secretsmanager get-secret-value \
  --secret-id infusethink/terraform-state-conn-str \
  --query SecretString --output text 2>&1)" && sm_rc=0 || sm_rc=$?

if [ "$sm_rc" -eq 0 ]; then
  export PG_CONN_STR="$sm_out"
elif printf '%s' "$sm_out" | grep -q ResourceNotFoundException; then
  export PG_CONN_STR=""
else
  printf '%s\n' "$sm_out" >&2
  echo "Failed to load PG_CONN_STR; only a missing secret is allowed (during bootstrap)." >&2
  exit 1
fi

cd "environments/$env"
exec terraform "$@"
