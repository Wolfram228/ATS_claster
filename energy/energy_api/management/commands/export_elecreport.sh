#!/bin/bash
DB_NAME="energy_db"
DB_USER="energy_user"
DB_HOST="localhost"
OUTPUT_DIR="/home/energy_user/ATS_project/exports"
DATE_FROM="${1:-2023-02-13}"
DATE_TO="${2:-$(date +%Y-%m-%d)}"
REGION="${3:-}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILENAME="elecreport_${DATE_FROM}_${DATE_TO}_${TIMESTAMP}.csv"
FULL_PATH="${OUTPUT_DIR}/${FILENAME}"
mkdir -p "$OUTPUT_DIR"

WHERE_CONDITIONS="timestamp >= '$DATE_FROM'::date AND timestamp <= '$DATE_TO'::date"
if [ ! -z "$REGION" ]; then
    WHERE_CONDITIONS="$WHERE_CONDITIONS AND region = '$REGION'"
fi

export PGPASSWORD='energy~ATS%istu'
export PGCLIENTENCODING=UTF8

psql -d "$DB_NAME" -U "$DB_USER" -h "$DB_HOST" -c "\copy (
    SELECT 
        timestamp,
        region,
        hour,
        ROUND(\"plan_GES\"::numeric, 2), ROUND(\"plan_AES\"::numeric, 2), ROUND(\"plan_TES\"::numeric, 2), ROUND(\"plan_SES\"::numeric, 2), ROUND(\"plan_VES\"::numeric, 2), ROUND(plan_other::numeric, 2),
        ROUND(\"techmin_GES\"::numeric, 2), ROUND(\"techmin_AES\"::numeric, 2), ROUND(\"techmin_TES\"::numeric, 2), ROUND(\"techmin_SES\"::numeric, 2), ROUND(\"techmin_VES\"::numeric, 2), ROUND(techmin_other::numeric, 2),
        ROUND(\"technomin_GES\"::numeric, 2), ROUND(\"technomin_AES\"::numeric, 2), ROUND(\"technomin_TES\"::numeric, 2), ROUND(\"technomin_SES\"::numeric, 2), ROUND(\"technomin_VES\"::numeric, 2), ROUND(technomin_other::numeric, 2),
        ROUND(\"techmax_GES\"::numeric, 2), ROUND(\"techmax_AES\"::numeric, 2), ROUND(\"techmax_TES\"::numeric, 2), ROUND(\"techmax_SES\"::numeric, 2), ROUND(\"techmax_VES\"::numeric, 2), ROUND(techmax_other::numeric, 2),
        ROUND(plan_consumption::numeric, 2), ROUND(plan_export::numeric, 2), ROUND(plan_import::numeric, 2),
        ROUND(price_buy::numeric, 2), ROUND(price_sell::numeric, 2), ROUND(full_plan::numeric, 2)
    FROM public.elec_reports
    WHERE $WHERE_CONDITIONS
    ORDER BY timestamp, region, hour
) TO '$FULL_PATH' WITH CSV HEADER DELIMITER ';' ENCODING 'UTF8';"

if [ -f "$FULL_PATH" ]; then
    ROW_COUNT=$(($(wc -l < "$FULL_PATH") - 1))
else
    ROW_COUNT=0
fi

echo "{\"file\":\"$FILENAME\",\"path\":\"$FULL_PATH\",\"records\":$ROW_COUNT,\"date_from\":\"$DATE_FROM\",\"date_to\":\"$DATE_TO\"}"
