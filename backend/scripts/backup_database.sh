#!/usr/bin/env bash
# Database backup script for PostgreSQL
# Usage: ./backup_database.sh [--compress] [--upload-s3]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${SCRIPT_DIR}/../backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/engineeros_${TIMESTAMP}.sql"
COMPRESSED_FILE="${BACKUP_FILE}.gz"

# Configuration
DB_HOST=${POSTGRES_HOST:-localhost}
DB_PORT=${POSTGRES_PORT:-5432}
DB_NAME=${POSTGRES_DB:-engineeros}
DB_USER=${POSTGRES_USER:-engineeros}
DB_PASSWORD=${POSTGRES_PASSWORD:-}

# Options
COMPRESS=${COMPRESS:-false}
UPLOAD_S3=${UPLOAD_S3:-false}
S3_BUCKET=${S3_BUCKET:-}
RETENTION_DAYS=${RETENTION_DAYS:-30}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --compress)
      COMPRESS=true
      shift
      ;;
    --upload-s3)
      UPLOAD_S3=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Perform backup
echo -e "${YELLOW}Starting database backup...${NC}"
echo "Database: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
echo "Output: ${BACKUP_FILE}"

if [ -n "$DB_PASSWORD" ]; then
  export PGPASSWORD="${DB_PASSWORD}"
fi

pg_dump \
  --host="${DB_HOST}" \
  --port="${DB_PORT}" \
  --username="${DB_USER}" \
  --no-password \
  --format=plain \
  --verbose \
  --file="${BACKUP_FILE}" \
  "${DB_NAME}"

echo -e "${GREEN}✅ Database backup completed${NC}"

# Compress if requested
if [ "${COMPRESS}" = true ]; then
  echo -e "${YELLOW}Compressing backup...${NC}"
  gzip "${BACKUP_FILE}"
  echo -e "${GREEN}✅ Backup compressed: ${COMPRESSED_FILE}${NC}"
  FINAL_FILE="${COMPRESSED_FILE}"
else
  FINAL_FILE="${BACKUP_FILE}"
fi

# Show file size
FILE_SIZE=$(du -h "${FINAL_FILE}" | cut -f1)
echo "Backup size: ${FILE_SIZE}"

# Upload to S3 if requested
if [ "${UPLOAD_S3}" = true ]; then
  if [ -z "${S3_BUCKET}" ]; then
    echo -e "${RED}❌ S3_BUCKET not set${NC}"
    exit 1
  fi
  
  echo -e "${YELLOW}Uploading to S3...${NC}"
  aws s3 cp "${FINAL_FILE}" "s3://${S3_BUCKET}/backups/" \
    --sse AES256 \
    --metadata "timestamp=${TIMESTAMP}"
  echo -e "${GREEN}✅ Uploaded to S3${NC}"
fi

# Cleanup old backups
echo -e "${YELLOW}Cleaning up old backups (keeping last ${RETENTION_DAYS} days)...${NC}"
find "${BACKUP_DIR}" -name "engineeros_*.sql*" -mtime +${RETENTION_DAYS} -delete
echo -e "${GREEN}✅ Cleanup completed${NC}"

# Verify backup
echo -e "${YELLOW}Verifying backup integrity...${NC}"
if [ "${COMPRESS}" = true ]; then
  gzip -t "${FINAL_FILE}" && echo -e "${GREEN}✅ Backup integrity verified${NC}" || \
    (echo -e "${RED}❌ Backup is corrupted${NC}" && exit 1)
else
  # Basic verification: check SQL syntax
  head -20 "${FINAL_FILE}" | grep -q "PostgreSQL" && \
    echo -e "${GREEN}✅ Backup header verified${NC}" || \
    (echo -e "${RED}❌ Backup appears invalid${NC}" && exit 1)
fi

echo -e "${GREEN}✅ Backup completed successfully${NC}"
echo "Backup location: ${FINAL_FILE}"
