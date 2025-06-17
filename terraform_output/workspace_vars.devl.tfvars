# Generated Workspace Variables
# Variables organized by service and global scope

# === INFRASTRUCTURE CONFIGURATION ===
infrastructure_config = {
  appshortname = "liqrcon"
  cluster_name = "liqrcon-ecs-tf"
  environment = "devl"
  logical_identifier = "tf"
  primary_region = "us-east-1"
  secondary_region = "us-east-2"
}

# === DYNATRACE MONITORING CONFIGURATION ===
dynatrace_config = {
  dt_cluster_id = "App=HCG-Liquidation-Reconciliation-Services LifeCycle=devl ServiceId=liqrcon-nginx-container CmdbCode=HCG AssetId=MSR13460 CMDBLongName=Liquidation Reconciliation Services"
  dt_connection_point = "https://dynatrace-le.fanniemae.com:443/communication"
  dt_custom_prop = "App=HCG-Liquidation-Reconciliation-Services LifeCycle=devl ServiceId=liqrcon-ecs-tf CmdbCode=HCG AssetId=MSR13460 CMDBLongName=Liquidation Reconciliation Services"
  dt_log = "info"
  dt_loglevelcon = "info"
  dt_tenant = "10ca672c-fb9c-4c47-a924-6aeb96202385"
  dt_tenanttoken = "ZtfXStulWhx32Om8"
}

# === APPLICATION ENVIRONMENT CONFIGURATION ===
application_config = {
  app_cluster_name = "liqrcon-ecs-tf"
  app_env = "DEV"
  app_name = "liqrcon"
  app_region = "us-east-1"
  java_tool_options = ""
  private_bucket = "liqrcon-devl-sfbu-us-east-1"
  sm_ssl = "True"
  spring_profiles_active = "DEVL"
  tw_container_name = "liqrcon-backend-svc-container"
}

# === CONTAINER CONFIGURATIONS ===
container_config = {
  liqrcon_backend_svc_container_cpu = 0
  liqrcon_backend_svc_container_essential = true
  liqrcon_backend_svc_container_image = "310306400902.dkr.ecr.us-east-1.amazonaws.com/liqrcon/liqrcon-tf:tps-backend-liqrcon-1.0.0-2721b090-2002758"
  liqrcon_backend_svc_container_memory = 30720
  liqrcon_backend_svc_container_name = "liqrcon-backend-svc-container"
  liqrcon_nginx_container_cpu = 0
  liqrcon_nginx_container_essential = false
  liqrcon_nginx_container_image = "920887439016.dkr.ecr.us-east-1.amazonaws.com/ssgecr/shared-images/mw/fm-mw-aws-nginx:6.5.0"
  liqrcon_nginx_container_memory = 2048
  liqrcon_nginx_container_name = "liqrcon-nginx-container"
}

# === SERVICE: LIQRCON-TPS-BACKEND-SVC ===
liqrcon_tps_backend_svc_config = {
  assign_public_ip = false
  container_name = "liqrcon-nginx-container"
  container_port = 443
  cpu = "4096"
  desired_count = 1
  execution_role_arn = "arn:aws:iam::310306400902:role/liqrcon-devl-sfbu-comp"
  health_check_grace_period_seconds = 0
  launch_type = "FARGATE"
  max_capacity = 3
  maximum_percent = 200
  memory = "30720"
  min_capacity = 1
  minimum_healthy_percent = 100
  network_mode = "awsvpc"
  platform_version = "1.3.0"
  security_groups = ["sg-002848e70774fa349", "sg-0c03858824f8e1556"]
  service_name = "liqrcon-tps-backend-svc"
  subnets = ["subnet-0dbc0c8a0d75b817b", "subnet-046c458e6b3cc57e2", "subnet-0f6324ddedfdfd72d", "subnet-02c679e33715abe3b"]
  target_group_arn = "arn:aws:elasticloadbalancing:us-east-1:310306400902:targetgroup/liqrcon-alb-ecs-tfbackend/c37c1dff4543a214"
  task_cpu = "4096"
  task_definition_family = "liqrcon-tps-backend-svc"
  task_family = "liqrcon-tps-backend-svc"
  task_memory = "30720"
  task_role_arn = "arn:aws:iam::310306400902:role/liqrcon-devl-sfbu-comp"
}

