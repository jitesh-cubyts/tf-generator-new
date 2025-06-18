// # ECS Cluster Configuration

module "ecs-cluster-liqrcon-ecs-giza-tfe" {
  source  = "terraform.fanniemae.com/fanniemae-org/ecs-cluster/aws"
  version = "~>1.0.12"

  appshortname      = var.appshortname
  unique_identifier = var.logical_identifier

  providers = {
    aws.local = aws.local
  }
} 