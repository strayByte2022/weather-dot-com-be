#!/bin/bash

ls -l
pwd
sleep 12

set -e

KSQLDB_SERVER_URL="http://ksqldb:8088"
QUERY_FILE="init.sql"

# Wait until ksqldb-server is ready
echo "Waiting for ksqlDB server to be ready..."
until curl -s "${KSQLDB_SERVER_URL}/info" | grep '"KsqlServerInfo"' > /dev/null; do
  sleep 5
done

echo "ksqlDB server is ready. Submitting queries..."

# Submit the query
curl -X POST "${KSQLDB_SERVER_URL}/ksql" \
  -H "Content-Type: application/vnd.ksql.v1+json; charset=utf-8" \
  -d @"$QUERY_FILE"
