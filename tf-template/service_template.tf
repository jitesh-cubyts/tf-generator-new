// # ECS Service and Task Definition: {service_name}

module "ecs-task-{sanitized_service_name}" {{
  source  = "terraform-ec2-01.terraform.prod-etss.aws.fanniemae.com/fanniemae-org/ecs-task-definition/aws"
  version = "~>1.0.23"

  appshortname = var.appshortname

  ecs_task_definition_string = templatefile(
    "./task_definitions/ecs_task_def_{sanitized_service_name}.json",
    merge(
      # Infrastructure variables
      var.infrastructure_config,
      # Dynatrace monitoring variables
      var.dynatrace_config,
      # Application environment variables
      var.application_config,
      # Container configurations
      var.container_config,
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
  microservice_name                 = var.{sanitized_service_name}_config.service_name
  cluster_id                        = module.ecs-cluster-{cluster_name}.ecs_cluster_arn
  task_definition_arn               = module.ecs-task-{sanitized_service_name}.ecs_task_definition_arn
  desired_count                     = var.{sanitized_service_name}_config.desired_count
  health_check_grace_period_seconds = var.{sanitized_service_name}_config.health_check_grace_period_seconds
  force_new_deployment              = true
  wait_for_steady_state             = false

  subnets = var.{sanitized_service_name}_config.subnets

  security_groups = var.{sanitized_service_name}_config.security_groups

{target_configuration}

  ecs_autoscaling_configuration = {{
    "max_capacity" = var.{sanitized_service_name}_config.max_capacity
    "min_capacity" = var.{sanitized_service_name}_config.min_capacity
  }}
}} 