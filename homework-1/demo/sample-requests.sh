#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:3000}"
API_KEY="${BANKING_API_KEY:-homework-api-key}"

curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{"fromAccount":null,"toAccount":"ACC-12345","amount":250.00,"currency":"USD","type":"deposit"}'
printf "\n"

curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d '{"fromAccount":"ACC-12345","toAccount":"ACC-67890","amount":100.50,"currency":"USD","type":"transfer"}'
printf "\n"

curl -s "$BASE_URL/transactions" -H "X-API-Key: $API_KEY"
printf "\n"

curl -s "$BASE_URL/transactions?accountId=ACC-12345&type=transfer" -H "X-API-Key: $API_KEY"
printf "\n"

curl -s "$BASE_URL/accounts/ACC-12345/balance" -H "X-API-Key: $API_KEY"
printf "\n"

curl -s "$BASE_URL/accounts/ACC-12345/summary" -H "X-API-Key: $API_KEY"
printf "\n"
