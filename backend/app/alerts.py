"""Alert rules for Prometheus alerting."""

# Alert rules in YAML format
ALERT_RULES = """
groups:
  - name: engineeros
    interval: 30s
    
    rules:
      # Availability alerts
      - alert: HighErrorRate
        expr: rate(engineeros_errors_total[5m]) > 0.01
        for: 5m
        labels:
          severity: warning
          component: api
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 1%)"
      
      - alert: CriticalErrorRate
        expr: rate(engineeros_errors_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
          component: api
        annotations:
          summary: "Critical error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"
      
      # Latency alerts
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(engineeros_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
          component: api
        annotations:
          summary: "High API latency detected"
          description: "p95 latency is {{ $value | humanizeDuration }} (threshold: 500ms)"
      
      - alert: CriticalLatency
        expr: histogram_quantile(0.95, rate(engineeros_request_duration_seconds_bucket[5m])) > 2
        for: 2m
        labels:
          severity: critical
          component: api
        annotations:
          summary: "Critical API latency detected"
          description: "p95 latency is {{ $value | humanizeDuration }} (threshold: 2s)"
      
      # Database alerts
      - alert: DatabaseSlowQueries
        expr: histogram_quantile(0.95, rate(engineeros_db_query_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
          component: database
        annotations:
          summary: "Slow database queries detected"
          description: "p95 query time is {{ $value | humanizeDuration }} (threshold: 500ms)"
      
      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
          component: database
        annotations:
          summary: "Database is down"
          description: "PostgreSQL database is not responding"
      
      - alert: HighDatabasePoolUsage
        expr: engineeros_db_pool_size{pool_type="checked_out"} / engineeros_db_pool_size_total > 0.8
        for: 5m
        labels:
          severity: warning
          component: database
        annotations:
          summary: "High database pool usage"
          description: "{{ $value | humanizePercentage }} of connections in use (threshold: 80%)"
      
      # Authentication alerts
      - alert: HighAuthFailureRate
        expr: rate(engineeros_login_attempts_total{result="failure"}[5m]) / rate(engineeros_login_attempts_total[5m]) > 0.2
        for: 5m
        labels:
          severity: warning
          component: authentication
        annotations:
          summary: "High authentication failure rate"
          description: "{{ $value | humanizePercentage }} of login attempts failing (threshold: 20%)"
      
      # Uptime alerts
      - alert: ServiceDown
        expr: up{job="engineeros-api"} == 0
        for: 2m
        labels:
          severity: critical
          component: api
        annotations:
          summary: "Service is down"
          description: "EngineerOS API is not responding"
      
      # Memory alerts
      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / 1024 / 1024 > 500
        for: 5m
        labels:
          severity: warning
          component: api
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value | humanize }}MB (threshold: 500MB)"
      
      - alert: CriticalMemoryUsage
        expr: process_resident_memory_bytes / 1024 / 1024 > 800
        for: 2m
        labels:
          severity: critical
          component: api
        annotations:
          summary: "Critical memory usage"
          description: "Memory usage is {{ $value | humanize }}MB (threshold: 800MB)"
      
      # CPU alerts
      - alert: HighCPUUsage
        expr: rate(process_cpu_seconds_total[5m]) * 100 > 80
        for: 5m
        labels:
          severity: warning
          component: api
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value | humanize }}% (threshold: 80%)"
      
      # SLO breach alerts
      - alert: SLOBreach_Availability
        expr: engineeros_availability_percent < 99.9
        for: 15m
        labels:
          severity: critical
          slo: availability
        annotations:
          summary: "Availability SLO breach"
          description: "Availability is {{ $value | humanizePercentage }} (target: 99.9%)"
      
      - alert: SLOBreach_ResponseTime
        expr: histogram_quantile(0.95, rate(engineeros_request_duration_seconds_bucket[1h])) > 0.2
        for: 15m
        labels:
          severity: warning
          slo: latency
        annotations:
          summary: "Response time SLO breach"
          description: "p95 response time is {{ $value | humanizeDuration }} (target: 200ms)"
      
      - alert: SLOBreach_ErrorRate
        expr: rate(engineeros_errors_total[1h]) > 0.001
        for: 15m
        labels:
          severity: warning
          slo: error_rate
        annotations:
          summary: "Error rate SLO breach"
          description: "Error rate is {{ $value | humanizePercentage }} (target: 0.1%)"
"""

# Alert routing rules
ALERT_ROUTING = """
global:
  resolve_timeout: 5m

route:
  receiver: default
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  
  routes:
    # Critical alerts to PagerDuty
    - match:
        severity: critical
      receiver: pagerduty
      continue: true
    
    # Warnings to Slack
    - match:
        severity: warning
      receiver: slack
    
    # SLO breaches to team
    - match_re:
        alertname: "SLOBreach.*"
      receiver: team
      group_wait: 0s

receivers:
  - name: 'default'
  
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '${PAGERDUTY_SERVICE_KEY}'
  
  - name: 'slack'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
  
  - name: 'team'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#engineering'
        title: 'SLO Alert: {{ .GroupLabels.alertname }}'
"""
