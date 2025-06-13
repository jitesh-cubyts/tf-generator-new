// # ECS Cluster Configuration

module "ecs-cluster-{cluster_name}" {{
  source  = "terraform-ec2-01.terraform.prod-etss.aws.fanniemae.com/fanniemae-org/ecs-cluster/aws"
  version = ">=1.0.10"

  appshortname      = var.appshortname
  unique_identifier = var.logical_identifier

  providers = {{
    aws.local = aws.local
  }}
}} 