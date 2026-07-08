#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:3000}"

echo "Creating a ticket"
CREATE_RESPONSE="$(
  curl -s -X POST "$API_BASE_URL/tickets" \
    -H "Content-Type: application/json" \
    -d '{
      "customer_id": "demo-customer",
      "customer_email": "demo@example.com",
      "customer_name": "Demo Customer",
      "subject": "Critical password access issue",
      "description": "I cannot access my login after changing my password and this is blocking support work.",
      "metadata": {
        "source": "web_form",
        "browser": "Chrome",
        "device_type": "desktop"
      },
      "tags": ["demo", "login"]
    }'
)"
echo "$CREATE_RESPONSE"

TICKET_ID="$(
  python3 -c 'import json, sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE"
)"

echo
echo "Auto-classifying ticket $TICKET_ID"
curl -s -X POST "$API_BASE_URL/tickets/$TICKET_ID/auto-classify"

echo
echo
echo "Listing urgent tickets"
curl -s "$API_BASE_URL/tickets?priority=urgent"

echo
echo
echo "Updating ticket status"
curl -s -X PUT "$API_BASE_URL/tickets/$TICKET_ID" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress", "assigned_to": "agent-demo"}'

echo
echo
echo "Importing sample CSV with auto-classification"
curl -s -X POST "$API_BASE_URL/tickets/import?format=csv&auto_classify=true" \
  -F "file=@sample_data/valid/sample_tickets.csv"

echo
