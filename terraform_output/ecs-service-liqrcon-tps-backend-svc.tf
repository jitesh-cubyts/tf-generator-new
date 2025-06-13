// # ECS Service and Task Definition: liqrcon-tps-backend-svc

module "ecs-task-liqrcon_tps_backend_svc" {
  source  = "terraform-ec2-01.terraform.prod-etss.aws.fanniemae.com/fanniemae-org/ecs-task-definition/aws"
  version = "~>1.0.23"

  appshortname = var.appshortname

  ecs_task_definition_string = templatefile(
    "./task_definitions/ecs_task_def_liqrcon_tps_backend_svc.json",
    merge(
      # Task-level variables
      {
        task_definition_family = var.liqrcon_tps_backend_svc_task_definition_family,
        task_role_arn         = var.liqrcon_tps_backend_svc_task_role_arn,
        execution_role_arn    = var.liqrcon_tps_backend_svc_execution_role_arn,
        network_mode          = var.liqrcon_tps_backend_svc_network_mode,
        launch_type           = var.liqrcon_tps_backend_svc_launch_type,
        task_cpu              = var.liqrcon_tps_backend_svc_task_cpu,
        task_memory           = var.liqrcon_tps_backend_svc_task_memory,
      },
      # Global environment variables
      {
        region                 = var.region,
        dt_log                 = var.dt_log,
        dt_tenant              = var.dt_tenant,
        dt_tenanttoken         = var.dt_tenanttoken,
        dt_connection_point    = var.dt_connection_point,
        dt_custom_prop         = var.dt_custom_prop,
        private_bucket         = var.private_bucket,
        spring_profiles_active = var.spring_profiles_active,
        app_name               = var.app_name,
        app_env                = var.app_env,
        app_region             = var.app_region,
        app_cluster_name       = var.app_cluster_name,
      },
      # Container-specific variables (populated by generator)
      {
        liqrcon_backend_svc_container_name = var.liqrcon_backend_svc_container_name,
        liqrcon_backend_svc_container_image = var.liqrcon_backend_svc_container_image,
        liqrcon_backend_svc_container_cpu = var.liqrcon_backend_svc_container_cpu,
        liqrcon_backend_svc_container_memory = var.liqrcon_backend_svc_container_memory,
        liqrcon_backend_svc_container_essential = var.liqrcon_backend_svc_container_essential,
        tw_container_name = var.tw_container_name,
        java_tool_options = var.java_tool_options,
        sm_ssl = var.sm_ssl,
        liqrcon_nginx_container_name = var.liqrcon_nginx_container_name,
        liqrcon_nginx_container_image = var.liqrcon_nginx_container_image,
        liqrcon_nginx_container_cpu = var.liqrcon_nginx_container_cpu,
        liqrcon_nginx_container_memory = var.liqrcon_nginx_container_memory,
        liqrcon_nginx_container_essential = var.liqrcon_nginx_container_essential,
        tw_container_name = var.tw_container_name,
        dt_loglevelcon = var.dt_loglevelcon,
        dt_cluster_id = var.dt_cluster_id,
        sm_ssl = var.sm_ssl
      }
    )
  )

  providers = {
    aws.local = aws.local
  }
}

module "ecs-service-liqrcon_tps_backend_svc" {
  source  = "terraform.fanniemae.com/fanniemae-org/ecs-service/aws"
  version = "1.0.19"

  providers = {
    aws.local = aws.local
  }

  appshortname                      = var.appshortname
  microservice_name                 = var.liqrcon_tps_backend_svc_service_name
  cluster_id                        = module.ecs-cluster-liqrcon-ecs-tf.ecs_cluster_arn
  task_definition_arn               = module.ecs-task-liqrcon_tps_backend_svc.ecs_task_definition_arn
  desired_count                     = var.liqrcon_tps_backend_svc_desired_count
  health_check_grace_period_seconds = var.liqrcon_tps_backend_svc_health_check_grace_period_seconds
  force_new_deployment              = true
  wait_for_steady_state             = false

  subnets = var.liqrcon_tps_backend_svc_subnets

  security_groups = var.liqrcon_tps_backend_svc_security_groups


  target_configuration = [
    {
      target_group_arn = var.liqrcon_tps_backend_svc_target_group_arn
      container_name   = var.liqrcon_tps_backend_svc_container_name
      container_port   = var.liqrcon_tps_backend_svc_container_port
    }
  ]

  ecs_autoscaling_configuration = {
    "max_capacity" = var.liqrcon_tps_backend_svc_max_capacity
    "min_capacity" = var.liqrcon_tps_backend_svc_min_capacity
  }
} 