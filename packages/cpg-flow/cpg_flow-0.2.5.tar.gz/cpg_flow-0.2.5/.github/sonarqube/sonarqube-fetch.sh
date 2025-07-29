#!/bin/bash

# Variables
SONAR_HOST_URL=$1
SONAR_TOKEN=$2
PROJECT_KEY=$3
MAIN_PROJECT_KEY=$4

# Function to return the appropriate emoji based on Quality Gate status
get_quality_gate_emoji() {
  local status=$1
  local emoji

  if [[ "$status" == "OK" ]]; then
    emoji="✅"
  elif [[ "$status" == "ERROR" ]]; then
    emoji="❌"
  elif [[ "$status" == "WARN" ]]; then
    emoji="⚠️"
  else
    emoji="🔲"
  fi

  # Prepend the emoji to the status
  echo "$emoji $status"
}

# Fetch metrics for both overall and new code
METRICS="coverage bugs vulnerabilities code_smells security_hotspots"
METRICS_JOINED=$(echo "$METRICS" | tr ' ' ',')

# Fetching the project metrics for PR
RESPONSE_PR=$(curl -s -u "$SONAR_TOKEN:" "$SONAR_HOST_URL/api/measures/component?component=$PROJECT_KEY&metricKeys=$METRICS_JOINED")

# Fetching the project metrics for the main project
RESPONSE_MAIN=$(curl -s -u "$SONAR_TOKEN:" "$SONAR_HOST_URL/api/measures/component?component=$MAIN_PROJECT_KEY&metricKeys=$METRICS_JOINED")

# Fetch the Quality Gate statuses for PR and Main projects
QUALITY_GATE_PR=$(curl -s -u "$SONAR_TOKEN:" "$SONAR_HOST_URL/api/qualitygates/project_status?projectKey=$PROJECT_KEY" | jq -r '.projectStatus.status')
QUALITY_GATE_MAIN=$(curl -s -u "$SONAR_TOKEN:" "$SONAR_HOST_URL/api/qualitygates/project_status?projectKey=$MAIN_PROJECT_KEY" | jq -r '.projectStatus.status')

QUALITY_GATE_PR=$(get_quality_gate_emoji "$QUALITY_GATE_PR")
QUALITY_GATE_MAIN=$(get_quality_gate_emoji "$QUALITY_GATE_MAIN")

# Initialize an empty associative array for both main and PR project metrics
declare -A METRIC_VALUES_PR
declare -A METRIC_VALUES_MAIN

# Extract the overall metrics for PR
for metric in $METRICS; do
  VALUE_PR=$(echo "$RESPONSE_PR" | jq -r ".component.measures[] | select(.metric==\"$metric\") | .value // \"N/A\"" || echo "N/A")
  METRIC_VALUES_PR[$metric]=$VALUE_PR
done

# Extract the overall metrics for Main project
for metric in $METRICS; do
  VALUE_MAIN=$(echo "$RESPONSE_MAIN" | jq -r ".component.measures[] | select(.metric==\"$metric\") | .value // \"N/A\"" || echo "N/A")
  METRIC_VALUES_MAIN[$metric]=$VALUE_MAIN
done

# Load the template from the file (make sure you have a .github/sonarqube/sonarqube-template.md file)
TEMPLATE=$(cat .github/sonarqube/sonarqube-template.md)

# Replace the placeholders for PR metrics
for key in "${!METRIC_VALUES_PR[@]}"; do
  TEMPLATE=$(echo "$TEMPLATE" | sed "s|{{${key}_pr}}|${METRIC_VALUES_PR[$key]}|g")
done

# Replace the placeholders for Main project metrics
for key in "${!METRIC_VALUES_MAIN[@]}"; do
  TEMPLATE=$(echo "$TEMPLATE" | sed "s|{{${key}_main}}|${METRIC_VALUES_MAIN[$key]}|g")
done

# Add the Quality Gate values to the template
TEMPLATE=$(echo "$TEMPLATE" | sed "s|{{quality_gate_pr}}|$QUALITY_GATE_PR|g" | sed "s|{{quality_gate_main}}|$QUALITY_GATE_MAIN|g")

# Add the SONAR_HOST_URL, PROJECT_KEY and MAIN_PROJECT_KEY to the template
TEMPLATE=$(echo "$TEMPLATE" | sed "s|{{SONAR_HOST_URL}}|$SONAR_HOST_URL|g" | sed "s|{{PROJECT_KEY}}|$PROJECT_KEY|g" | sed "s|{{MAIN_PROJECT_KEY}}|$MAIN_PROJECT_KEY|g")

# Output the final comment to stdout
echo "$TEMPLATE"
