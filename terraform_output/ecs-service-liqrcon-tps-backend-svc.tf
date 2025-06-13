// # ECS Service and Task Definition: liqrcon-tps-backend-svc

module "ecs-task-liqrcon_tps_backend_svc" {
  source  = "terraform-ec2-01.terraform.prod-etss.aws.fanniemae.com/fanniemae-org/ecs-task-definition/aws"
  version = "~>1.0.23"

  appshortname = var.appshortname

  ecs_task_definition_string = templatefile(
    "./task_definitions/ecs_task_def_liqrcon_tps_backend_svc.json",
    merge(
      # Task-level variables from service config object
      {
        task_definition_family = var.liqrcon_tps_backend_svc_config.task_definition_family,
        task_role_arn         = var.liqrcon_tps_backend_svc_config.task_role_arn,
        execution_role_arn    = var.liqrcon_tps_backend_svc_config.execution_role_arn,
        network_mode          = var.liqrcon_tps_backend_svc_config.network_mode,
        launch_type           = var.liqrcon_tps_backend_svc_config.launch_type,
        task_cpu              = var.liqrcon_tps_backend_svc_config.task_cpu,
        task_memory           = var.liqrcon_tps_backend_svc_config.task_memory,
      },
      # Infrastructure variables
      var.infrastructure_config,
      # Dynatrace monitoring variables
      var.dynatrace_config,
      # Application environment variables
      var.application_config,
      # Container configurations
      var.container_config
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
  microservice_name                 = var.liqrcon_tps_backend_svc_config.service_name
  cluster_id                        = module.ecs-cluster-liqrcon-ecs-tf.ecs_cluster_arn
  task_definition_arn               = module.ecs-task-liqrcon_tps_backend_svc.ecs_task_definition_arn
  desired_count                     = var.liqrcon_tps_backend_svc_config.desired_count
  health_check_grace_period_seconds = var.liqrcon_tps_backend_svc_config.health_check_grace_period_seconds
  force_new_deployment              = true
  wait_for_steady_state             = false

  subnets = var.liqrcon_tps_backend_svc_config.subnets

  security_groups = var.liqrcon_tps_backend_svc_config.security_groups


  target_configuration = [
    {
      target_group_arn = var.liqrcon_tps_backend_svc_config.target_group_arn
      container_name   = var.liqrcon_tps_backend_svc_config.container_name
      container_port   = var.liqrcon_tps_backend_svc_config.container_port
    }
  ]

  ecs_autoscaling_configuration = {
    "max_capacity" = var.liqrcon_tps_backend_svc_config.max_capacity
    "min_capacity" = var.liqrcon_tps_backend_svc_config.min_capacity
  }
} 