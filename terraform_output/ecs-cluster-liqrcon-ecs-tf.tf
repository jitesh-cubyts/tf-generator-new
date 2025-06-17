// # ECS Cluster Configuration

module "ecs-cluster-liqrcon-ecs-tf" {
  source  = "terraform-ec2-01.terraform.prod-etss.aws.fanniemae.com/fanniemae-org/ecs-cluster/aws"
  version = ">=1.0.10"

  appshortname      = var.infrastructure_config.appshortname
  unique_identifier = var.infrastructure_config.logical_identifier

  providers = {
    aws.local = aws.local
  }
} 