# Generated Variables File
# Variables organized with object structure for services

# === INFRASTRUCTURE CONFIGURATION ===

variable "infrastructure_config" {
  description = "Infrastructure configuration object"
  type = object({
    app_shortname = string
    cluster_name = string
    environment = string
    primary_region = string
    secondary_region = string
  })
}

# === DYNATRACE MONITORING CONFIGURATION ===

variable "dynatrace_config" {
  description = "Dynatrace monitoring configuration object"
  type = object({
    dt_cluster_id = string
    dt_connection_point = string
    dt_custom_prop = string
    dt_log = string
    dt_loglevelcon = string
    dt_tenant = string
    dt_tenanttoken = string
  })
  sensitive = true
}

# === APPLICATION ENVIRONMENT CONFIGURATION ===

variable "application_config" {
  description = "Application environment configuration object"
  type = object({
    app_cluster_name = string
    app_env = string
    app_name = string
    app_region = string
    java_tool_options = string
    private_bucket = string
    sm_ssl = string
    spring_profiles_active = string
    tw_container_name = string
  })
}

# === CONTAINER CONFIGURATIONS ===

variable "container_config" {
  description = "Container configurations object"
  type = object({
    liqrcon_backend_svc_container_cpu = number
    liqrcon_backend_svc_container_essential = number
    liqrcon_backend_svc_container_image = string
    liqrcon_backend_svc_container_memory = number
    liqrcon_backend_svc_container_name = string
    liqrcon_nginx_container_cpu = number
    liqrcon_nginx_container_essential = number
    liqrcon_nginx_container_image = string
    liqrcon_nginx_container_memory = number
    liqrcon_nginx_container_name = string
  })
}

# === SERVICE: LIQRCON-TPS-BACKEND-SVC ===

variable "liqrcon_tps_backend_svc_config" {
  description = "Configuration object for liqrcon-tps-backend-svc service"
  type = object({
    assign_public_ip = bool
    container_name = string
    container_port = number
    cpu = string
    desired_count = number
    execution_role_arn = string
    health_check_grace_period_seconds = number
    launch_type = string
    max_capacity = number
    maximum_percent = number
    memory = string
    min_capacity = number
    minimum_healthy_percent = number
    network_mode = string
    platform_version = string
    security_groups = list(string)
    service_name = string
    subnets = list(string)
    target_group_arn = string
    task_cpu = string
    task_definition_family = string
    task_family = string
    task_memory = string
    task_role_arn = string
  })
}

