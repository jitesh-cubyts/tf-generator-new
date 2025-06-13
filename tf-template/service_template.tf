// # ECS Service and Task Definition: {service_name}

module "ecs-task-{sanitized_service_name}" {{
  source  = "terraform-ec2-01.terraform.prod-etss.aws.fanniemae.com/fanniemae-org/ecs-task-definition/aws"
  version = "~>1.0.23"

  appshortname = var.appshortname

  ecs_task_definition_string = templatefile(
    "./task_definitions/ecs_task_def_{sanitized_service_name}.json",
    merge(
      # Task-level variables
      {{
        task_definition_family = var.{sanitized_service_name}_task_definition_family,
        task_role_arn         = var.{sanitized_service_name}_task_role_arn,
        execution_role_arn    = var.{sanitized_service_name}_execution_role_arn,
        network_mode          = var.{sanitized_service_name}_network_mode,
        launch_type           = var.{sanitized_service_name}_launch_type,
        task_cpu              = var.{sanitized_service_name}_task_cpu,
        task_memory           = var.{sanitized_service_name}_task_memory,
      }},
      # Global environment variables
      {{
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
      }},
      # Container-specific variables (populated by generator)
      {container_variables}
    )
  )

  providers = {{
    aws.local = aws.local
  }}
}}

module "ecs-service-{sanitized_service_name}" {{
  source  = "terraform.fanniemae.com/fanniemae-org/ecs-service/aws"
  version = "1.0.19"

  providers = {{
    aws.local = aws.local
  }}

  appshortname                      = var.appshortname
  microservice_name                 = var.{sanitized_service_name}_service_name
  cluster_id                        = module.ecs-cluster-{cluster_name}.ecs_cluster_arn
  task_definition_arn               = module.ecs-task-{sanitized_service_name}.ecs_task_definition_arn
  desired_count                     = var.{sanitized_service_name}_desired_count
  health_check_grace_period_seconds = var.{sanitized_service_name}_health_check_grace_period_seconds
  force_new_deployment              = true
  wait_for_steady_state             = false

  subnets = var.{sanitized_service_name}_subnets

  security_groups = var.{sanitized_service_name}_security_groups

{target_configuration}

  ecs_autoscaling_configuration = {{
    "max_capacity" = var.{sanitized_service_name}_max_capacity
    "min_capacity" = var.{sanitized_service_name}_min_capacity
  }}
}} 