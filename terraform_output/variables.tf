# Generated Variables File
# All variables extracted from AWS ECS configuration

# === CALCULATED VARIABLES ===

variable "liqrcon_tps_backend_svc_max_capacity" {
  description = "Maximum autoscaling capacity for liqrcon-tps-backend-svc (based on desired: 1, has_lb: True) (Source: Calculated:max_capacity)"
  type        = number
}

variable "liqrcon_tps_backend_svc_min_capacity" {
  description = "Minimum autoscaling capacity for liqrcon-tps-backend-svc (based on desired: 1) (Source: Calculated:min_capacity)"
  type        = number
}

# === CLUSTER VARIABLES ===

variable "app_shortname" {
  description = "App Shortname (Source: Cluster:app_shortname)"
  type        = string
}

variable "cluster_name" {
  description = "Cluster Name (Source: Cluster:cluster_name)"
  type        = string
}

variable "environment" {
  description = "Environment (Source: Cluster:environment)"
  type        = string
}

# === CONTAINER VARIABLES ===

variable "liqrcon_backend_svc_container_cpu" {
  description = "Container liqrcon backend svc container cpu for liqrcon-backend-svc-container (Source: Container:liqrcon-backend-svc-container)"
  type        = number
}

variable "liqrcon_backend_svc_container_essential" {
  description = "Container liqrcon backend svc container essential for liqrcon-backend-svc-container (Source: Container:liqrcon-backend-svc-container)"
  type        = number
}

variable "liqrcon_backend_svc_container_image" {
  description = "Container liqrcon backend svc container image for liqrcon-backend-svc-container (Source: Container:liqrcon-backend-svc-container)"
  type        = string
}

variable "liqrcon_backend_svc_container_memory" {
  description = "Container liqrcon backend svc container memory for liqrcon-backend-svc-container (Source: Container:liqrcon-backend-svc-container)"
  type        = number
}

variable "liqrcon_backend_svc_container_name" {
  description = "Container liqrcon backend svc container name for liqrcon-backend-svc-container (Source: Container:liqrcon-backend-svc-container)"
  type        = string
}

variable "liqrcon_nginx_container_cpu" {
  description = "Container liqrcon nginx container cpu for liqrcon-nginx-container (Source: Container:liqrcon-nginx-container)"
  type        = number
}

variable "liqrcon_nginx_container_essential" {
  description = "Container liqrcon nginx container essential for liqrcon-nginx-container (Source: Container:liqrcon-nginx-container)"
  type        = number
}

variable "liqrcon_nginx_container_image" {
  description = "Container liqrcon nginx container image for liqrcon-nginx-container (Source: Container:liqrcon-nginx-container)"
  type        = string
}

variable "liqrcon_nginx_container_memory" {
  description = "Container liqrcon nginx container memory for liqrcon-nginx-container (Source: Container:liqrcon-nginx-container)"
  type        = number
}

variable "liqrcon_nginx_container_name" {
  description = "Container liqrcon nginx container name for liqrcon-nginx-container (Source: Container:liqrcon-nginx-container)"
  type        = string
}

# === CONTAINERENV VARIABLES ===

variable "app_cluster_name" {
  description = "Environment variable APP_CLUSTER_NAME (from container definition) (Source: ContainerEnv:APP_CLUSTER_NAME)"
  type        = string
}

variable "app_env" {
  description = "Environment variable APP_ENV (from container definition) (Source: ContainerEnv:APP_ENV)"
  type        = string
}

variable "app_name" {
  description = "Environment variable APP_NAME (from container definition) (Source: ContainerEnv:APP_NAME)"
  type        = string
}

variable "app_region" {
  description = "Environment variable APP_REGION (from container definition) (Source: ContainerEnv:APP_REGION)"
  type        = string
}

variable "dt_cluster_id" {
  description = "Environment variable DT_CLUSTER_ID (from container definition) (Source: ContainerEnv:DT_CLUSTER_ID)"
  type        = string
}

variable "dt_connection_point" {
  description = "Environment variable DT_CONNECTION_POINT (from container definition) (Source: ContainerEnv:DT_CONNECTION_POINT)"
  type        = string
}

variable "dt_custom_prop" {
  description = "Environment variable DT_CUSTOM_PROP (from container definition) (Source: ContainerEnv:DT_CUSTOM_PROP)"
  type        = string
}

variable "dt_log" {
  description = "Environment variable DT_LOG (from container definition) (Source: ContainerEnv:DT_LOG)"
  type        = string
}

variable "dt_loglevelcon" {
  description = "Environment variable DT_LOGLEVELCON (from container definition) (Source: ContainerEnv:DT_LOGLEVELCON)"
  type        = string
}

variable "dt_tenant" {
  description = "Environment variable DT_TENANT (from container definition) (Source: ContainerEnv:DT_TENANT)"
  type        = string
}

variable "dt_tenanttoken" {
  description = "Environment variable DT_TENANTTOKEN (from container definition) (Source: ContainerEnv:DT_TENANTTOKEN)"
  type        = string
  sensitive   = true
}

variable "java_tool_options" {
  description = "Environment variable JAVA_TOOL_OPTIONS from container liqrcon-backend-svc-container (Source: ContainerEnv:liqrcon-backend-svc-container:JAVA_TOOL_OPTIONS)"
  type        = string
}

variable "private_bucket" {
  description = "Environment variable PRIVATE_BUCKET (from container definition) (Source: ContainerEnv:PRIVATE_BUCKET)"
  type        = string
}

variable "region" {
  description = "Environment variable REGION (from container definition) (Source: ContainerEnv:REGION)"
  type        = string
}

variable "sm_ssl" {
  description = "Environment variable SM_SSL (from container definition) (Source: ContainerEnv:SM_SSL)"
  type        = string
}

variable "spring_profiles_active" {
  description = "Environment variable spring.profiles.active (from container definition) (Source: ContainerEnv:spring.profiles.active)"
  type        = string
}

variable "tw_container_name" {
  description = "Environment variable TW_CONTAINER_NAME (from container definition) (Source: ContainerEnv:TW_CONTAINER_NAME)"
  type        = string
}

# === DEPLOYCONFIG VARIABLES ===

variable "liqrcon_tps_backend_svc_maximum_percent" {
  description = "Maximum Percent for liqrcon-tps-backend-svc (Source: DeployConfig:maximumPercent)"
  type        = number
}

variable "liqrcon_tps_backend_svc_minimum_healthy_percent" {
  description = "Minimum Healthy Percent for liqrcon-tps-backend-svc (Source: DeployConfig:minimumHealthyPercent)"
  type        = number
}

# === LOADBALANCER VARIABLES ===

variable "liqrcon_tps_backend_svc_container_name" {
  description = "Container Name for liqrcon-tps-backend-svc (Source: LoadBalancer:containerName)"
  type        = string
}

variable "liqrcon_tps_backend_svc_container_port" {
  description = "Container Port for liqrcon-tps-backend-svc (Source: LoadBalancer:containerPort)"
  type        = number
}

variable "liqrcon_tps_backend_svc_target_group_arn" {
  description = "Target Group Arn for liqrcon-tps-backend-svc (Source: LoadBalancer:targetGroupArn)"
  type        = string
}

# === NETWORKCONFIG VARIABLES ===

variable "liqrcon_tps_backend_svc_assign_public_ip" {
  description = "Assign Public Ip for liqrcon-tps-backend-svc (Source: NetworkConfig:assignPublicIp)"
  type        = bool
}

variable "liqrcon_tps_backend_svc_security_groups" {
  description = "Security Groups for liqrcon-tps-backend-svc (Source: NetworkConfig:securityGroups)"
  type        = list(string)
}

variable "liqrcon_tps_backend_svc_subnets" {
  description = "Subnets for liqrcon-tps-backend-svc (Source: NetworkConfig:subnets)"
  type        = list(string)
}

# === SERVICE VARIABLES ===

variable "liqrcon_tps_backend_svc_desired_count" {
  description = "Desired Count for liqrcon-tps-backend-svc (Source: Service:desiredCount)"
  type        = number
}

variable "liqrcon_tps_backend_svc_health_check_grace_period_seconds" {
  description = "Health Check Grace Period Seconds for liqrcon-tps-backend-svc (Source: Service:healthCheckGracePeriodSeconds)"
  type        = number
}

variable "liqrcon_tps_backend_svc_launch_type" {
  description = "Launch Type for liqrcon-tps-backend-svc (Source: Service:launchType)"
  type        = string
}

variable "liqrcon_tps_backend_svc_platform_version" {
  description = "Platform Version for liqrcon-tps-backend-svc (Source: Service:platformVersion)"
  type        = string
}

variable "liqrcon_tps_backend_svc_service_name" {
  description = "Service Name for liqrcon-tps-backend-svc (Source: Service:serviceName)"
  type        = string
}

# === TASKDEF VARIABLES ===

variable "liqrcon_tps_backend_svc_cpu" {
  description = "Cpu for liqrcon-tps-backend-svc (Source: TaskDef:cpu)"
  type        = string
}

variable "liqrcon_tps_backend_svc_execution_role_arn" {
  description = "Execution Role Arn for liqrcon-tps-backend-svc (Source: TaskDef:execution_role_arn)"
  type        = string
}

variable "liqrcon_tps_backend_svc_memory" {
  description = "Memory for liqrcon-tps-backend-svc (Source: TaskDef:memory)"
  type        = string
}

variable "liqrcon_tps_backend_svc_network_mode" {
  description = "Network Mode for liqrcon-tps-backend-svc (Source: TaskDef:network_mode)"
  type        = string
}

variable "liqrcon_tps_backend_svc_task_cpu" {
  description = "Task Cpu for liqrcon-tps-backend-svc (Source: TaskDef:task_cpu)"
  type        = string
}

variable "liqrcon_tps_backend_svc_task_definition_family" {
  description = "Task Definition Family for liqrcon-tps-backend-svc (Source: TaskDef:task_definition_family)"
  type        = string
}

variable "liqrcon_tps_backend_svc_task_family" {
  description = "Task Family for liqrcon-tps-backend-svc (Source: TaskDef:family)"
  type        = string
}

variable "liqrcon_tps_backend_svc_task_memory" {
  description = "Task Memory for liqrcon-tps-backend-svc (Source: TaskDef:task_memory)"
  type        = string
}

variable "liqrcon_tps_backend_svc_task_role_arn" {
  description = "Task Role Arn for liqrcon-tps-backend-svc (Source: TaskDef:task_role_arn)"
  type        = string
}

