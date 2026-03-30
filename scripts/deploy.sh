#!/usr/bin/env bash
set -euo pipefail

# deploy.sh - Extract a single service from porter.yaml and deploy it.
# Usage: ./deploy.sh <service-name>

if [ $# -lt 1 ]; then
  echo "Error: No service name provided."
  echo "Usage: ./deploy.sh <service-name>"
  echo "       ./deploy.sh buildpack"
  exit 1
fi

if [ "$1" = "buildpack" ]; then
  BUILDPACKS_FILE="buildpacks.porter.yaml"
  if [ ! -f "$BUILDPACKS_FILE" ]; then
    echo "Error: ${BUILDPACKS_FILE} not found in the current directory."
    exit 1
  fi
  echo "Running: porter apply -f ${BUILDPACKS_FILE}"
  porter apply -f "$BUILDPACKS_FILE"
  exit 0
fi

SERVICE_NAME="$1"
PORTER_FILE="porter.yaml"
OUTPUT_DIR="tmp/bin"
OUTPUT_FILE="${OUTPUT_DIR}/${SERVICE_NAME}.yaml"

# Verify porter.yaml exists
if [ ! -f "$PORTER_FILE" ]; then
  echo "Error: ${PORTER_FILE} not found in the current directory."
  exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Extract the header (everything before the "services:" line) and the specific
# service block from porter.yaml.
#
# The porter.yaml structure is:
#   version: ...
#   name: ...
#   build: ...
#   services:
#     - name: hello-world
#       ...
#     - name: hello-crash
#       ...
#
# Strategy:
#   1. Capture all lines from the start up to and including "services:".
#   2. Find the service block that starts with "  - name: <SERVICE_NAME>" and
#      capture every subsequent line that is indented deeper than the list-item
#      marker (i.e., continuation lines for that item), stopping when we hit
#      the next list item ("  - name:") or a line that is not indented enough
#      (end of services section / end of file).

awk -v svc="$SERVICE_NAME" '
BEGIN {
  in_target = 0
  service_found = 0
  header_done = 0
  target_line = "  - name: " svc
}

!header_done {
  print
  if ($0 ~ /^services:/) {
    header_done = 1
  }
  next
}

/^  - name:/ {
  if (in_target) {
    exit
  }
  if ($0 == target_line) {
    in_target = 1
    service_found = 1
    print
    next
  }
}

in_target {
  if ($0 ~ /^    / || $0 ~ /^$/) {
    print
  } else {
    exit
  }
}

END {
  if (!service_found) {
    printf "ERROR: Service \"%s\" not found in porter.yaml\n", svc > "/dev/stderr"
    exit 1
  }
}
' "$PORTER_FILE" > "$OUTPUT_FILE" || {
  rm -f "$OUTPUT_FILE"
  exit 1
}

# Verify the output file is not empty / was actually written
if [ ! -s "$OUTPUT_FILE" ]; then
  echo "Error: Failed to extract service '${SERVICE_NAME}' -- output file is empty."
  rm -f "$OUTPUT_FILE"
  exit 1
fi

echo "Extracted service '${SERVICE_NAME}' to ${OUTPUT_FILE}"
echo "Running: porter apply -f ${OUTPUT_FILE}"
porter apply -f "$OUTPUT_FILE"
