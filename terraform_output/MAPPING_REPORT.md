# AWS to Terraform Variable Mapping Report
# Generated from: aws-liqrcon-ecs.json
# Cluster: liqrcon-ecs-tf
# Services: liqrcon-tps-backend-svc

## CALCULATED MAPPINGS

- **liqrcon_tps_backend_svc_max_capacity** (number)
  - Source: Calculated:max_capacity
  - Value: 3
  - Description: Max Capacity for liqrcon-tps-backend-svc (calculated)

- **liqrcon_tps_backend_svc_min_capacity** (number)
  - Source: Calculated:min_capacity
  - Value: 1
  - Description: Min Capacity for liqrcon-tps-backend-svc (calculated)

## CLUSTER MAPPINGS

- **app_shortname** (string)
  - Source: Cluster:app_shortname
  - Value: liqrcon
  - Description: App Shortname

- **cluster_name** (string)
  - Source: Cluster:cluster_name
  - Value: liqrcon-ecs-tf
  - Description: Cluster Name

- **environment** (string)
  - Source: Cluster:environment
  - Value: devl
  - Description: Environment

- **primary_region** (string)
  - Source: Cluster:primary_region
  - Value: us-east-1
  - Description: Primary Region

- **secondary_region** (string)
  - Source: Cluster:secondary_region
  - Value: us-east-2
  - Description: Secondary Region

## CONTAINER MAPPINGS

- **liqrcon_backend_svc_container_cpu** (number)
  - Source: Container:liqrcon-backend-svc-container
  - Value: 0
  - Description: Container liqrcon backend svc container cpu for liqrcon-backend-svc-container

- **liqrcon_backend_svc_container_essential** (number)
  - Source: Container:liqrcon-backend-svc-container
  - Value: True
  - Description: Container liqrcon backend svc container essential for liqrcon-backend-svc-container

- **liqrcon_backend_svc_container_image** (string)
  - Source: Container:liqrcon-backend-svc-container
  - Value: 310306400902.dkr.ecr.us-east-1.amazonaws.com/liqrcon/liqrcon-tf:tps-backend-liqrcon-1.0.0-2721b090-2002758
  - Description: Container liqrcon backend svc container image for liqrcon-backend-svc-container

- **liqrcon_backend_svc_container_memory** (number)
  - Source: Container:liqrcon-backend-svc-container
  - Value: 30720
  - Description: Container liqrcon backend svc container memory for liqrcon-backend-svc-container

- **liqrcon_backend_svc_container_name** (string)
  - Source: Container:liqrcon-backend-svc-container
  - Value: liqrcon-backend-svc-container
  - Description: Container liqrcon backend svc container name for liqrcon-backend-svc-container

- **liqrcon_nginx_container_cpu** (number)
  - Source: Container:liqrcon-nginx-container
  - Value: 0
  - Description: Container liqrcon nginx container cpu for liqrcon-nginx-container

- **liqrcon_nginx_container_essential** (number)
  - Source: Container:liqrcon-nginx-container
  - Value: False
  - Description: Container liqrcon nginx container essential for liqrcon-nginx-container

- **liqrcon_nginx_container_image** (string)
  - Source: Container:liqrcon-nginx-container
  - Value: 920887439016.dkr.ecr.us-east-1.amazonaws.com/ssgecr/shared-images/mw/fm-mw-aws-nginx:6.5.0
  - Description: Container liqrcon nginx container image for liqrcon-nginx-container

- **liqrcon_nginx_container_memory** (number)
  - Source: Container:liqrcon-nginx-container
  - Value: 2048
  - Description: Container liqrcon nginx container memory for liqrcon-nginx-container

- **liqrcon_nginx_container_name** (string)
  - Source: Container:liqrcon-nginx-container
  - Value: liqrcon-nginx-container
  - Description: Container liqrcon nginx container name for liqrcon-nginx-container

## CONTAINERENV MAPPINGS

- **app_cluster_name** (string)
  - Source: ContainerEnv:APP_CLUSTER_NAME
  - Value: liqrcon-ecs-tf
  - Description: Environment variable APP_CLUSTER_NAME (from container definition)

- **app_env** (string)
  - Source: ContainerEnv:APP_ENV
  - Value: DEV
  - Description: Environment variable APP_ENV (from container definition)

- **app_name** (string)
  - Source: ContainerEnv:APP_NAME
  - Value: liqrcon
  - Description: Environment variable APP_NAME (from container definition)

- **app_region** (string)
  - Source: ContainerEnv:APP_REGION
  - Value: us-east-1
  - Description: Environment variable APP_REGION (from container definition)

- **dt_cluster_id** (string)
  - Source: ContainerEnv:DT_CLUSTER_ID
  - Value: App=HCG-Liquidation-Reconciliation-Services LifeCycle=devl ServiceId=liqrcon-nginx-container CmdbCode=HCG AssetId=MSR13460 CMDBLongName=Liquidation Reconciliation Services
  - Description: Environment variable DT_CLUSTER_ID (from container definition)

- **dt_connection_point** (string)
  - Source: ContainerEnv:DT_CONNECTION_POINT
  - Value: https://dynatrace-le.fanniemae.com:443/communication
  - Description: Environment variable DT_CONNECTION_POINT (from container definition)

- **dt_custom_prop** (string)
  - Source: ContainerEnv:DT_CUSTOM_PROP
  - Value: App=HCG-Liquidation-Reconciliation-Services LifeCycle=devl ServiceId=liqrcon-ecs-tf CmdbCode=HCG AssetId=MSR13460 CMDBLongName=Liquidation Reconciliation Services
  - Description: Environment variable DT_CUSTOM_PROP (from container definition)

- **dt_log** (string)
  - Source: ContainerEnv:DT_LOG
  - Value: info
  - Description: Environment variable DT_LOG (from container definition)

- **dt_loglevelcon** (string)
  - Source: ContainerEnv:DT_LOGLEVELCON
  - Value: info
  - Description: Environment variable DT_LOGLEVELCON (from container definition)

- **dt_tenant** (string)
  - Source: ContainerEnv:DT_TENANT
  - Value: 10ca672c-fb9c-4c47-a924-6aeb96202385
  - Description: Environment variable DT_TENANT (from container definition)

- **dt_tenanttoken** (string)
  - Source: ContainerEnv:DT_TENANTTOKEN
  - Value: ZtfXStulWhx32Om8
  - Description: Environment variable DT_TENANTTOKEN (from container definition)

- **java_tool_options** (string)
  - Source: ContainerEnv:liqrcon-backend-svc-container:JAVA_TOOL_OPTIONS
  - Value: 
  - Description: Environment variable JAVA_TOOL_OPTIONS from container liqrcon-backend-svc-container

- **private_bucket** (string)
  - Source: ContainerEnv:PRIVATE_BUCKET
  - Value: liqrcon-devl-sfbu-us-east-1
  - Description: Environment variable PRIVATE_BUCKET (from container definition)

- **region** (string)
  - Source: ContainerEnv:REGION
  - Value: us-east-1
  - Description: Environment variable REGION (from container definition)

- **sm_ssl** (string)
  - Source: ContainerEnv:SM_SSL
  - Value: True
  - Description: Environment variable SM_SSL (from container definition)

- **spring_profiles_active** (string)
  - Source: ContainerEnv:spring.profiles.active
  - Value: DEVL
  - Description: Environment variable spring.profiles.active (from container definition)

- **tw_container_name** (string)
  - Source: ContainerEnv:TW_CONTAINER_NAME
  - Value: liqrcon-backend-svc-container
  - Description: Environment variable TW_CONTAINER_NAME (from container definition)

## DEPLOYCONFIG MAPPINGS

- **liqrcon_tps_backend_svc_maximum_percent** (number)
  - Source: DeployConfig:maximumPercent
  - Value: 200
  - Description: Maximum Percent for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_minimum_healthy_percent** (number)
  - Source: DeployConfig:minimumHealthyPercent
  - Value: 100
  - Description: Minimum Healthy Percent for liqrcon-tps-backend-svc

## LOADBALANCER MAPPINGS

- **liqrcon_tps_backend_svc_container_name** (string)
  - Source: LoadBalancer:containerName
  - Value: liqrcon-nginx-container
  - Description: Container Name for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_container_port** (number)
  - Source: LoadBalancer:containerPort
  - Value: 443
  - Description: Container Port for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_target_group_arn** (string)
  - Source: LoadBalancer:targetGroupArn
  - Value: arn:aws:elasticloadbalancing:us-east-1:310306400902:targetgroup/liqrcon-alb-ecs-tfbackend/c37c1dff4543a214
  - Description: Target Group Arn for liqrcon-tps-backend-svc

## NETWORKCONFIG MAPPINGS

- **liqrcon_tps_backend_svc_assign_public_ip** (bool)
  - Source: NetworkConfig:assignPublicIp
  - Value: False
  - Description: Assign Public Ip for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_security_groups** (list(string))
  - Source: NetworkConfig:securityGroups
  - Value: ['sg-002848e70774fa349', 'sg-0c03858824f8e1556']
  - Description: Security Groups for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_subnets** (list(string))
  - Source: NetworkConfig:subnets
  - Value: ['subnet-0dbc0c8a0d75b817b', 'subnet-046c458e6b3cc57e2', 'subnet-0f6324ddedfdfd72d', 'subnet-02c679e33715abe3b']
  - Description: Subnets for liqrcon-tps-backend-svc

## SERVICE MAPPINGS

- **liqrcon_tps_backend_svc_desired_count** (number)
  - Source: Service:desiredCount
  - Value: 1
  - Description: Desired Count for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_health_check_grace_period_seconds** (number)
  - Source: Service:healthCheckGracePeriodSeconds
  - Value: 0
  - Description: Health Check Grace Period Seconds for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_launch_type** (string)
  - Source: Service:launchType
  - Value: FARGATE
  - Description: Launch Type for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_platform_version** (string)
  - Source: Service:platformVersion
  - Value: 1.3.0
  - Description: Platform Version for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_service_name** (string)
  - Source: Service:serviceName
  - Value: liqrcon-tps-backend-svc
  - Description: Service Name for liqrcon-tps-backend-svc

## TASKDEF MAPPINGS

- **liqrcon_tps_backend_svc_cpu** (string)
  - Source: TaskDef:cpu
  - Value: 4096
  - Description: Cpu for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_execution_role_arn** (string)
  - Source: TaskDef:execution_role_arn
  - Value: arn:aws:iam::310306400902:role/liqrcon-devl-sfbu-comp
  - Description: Execution Role Arn for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_memory** (string)
  - Source: TaskDef:memory
  - Value: 30720
  - Description: Memory for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_network_mode** (string)
  - Source: TaskDef:network_mode
  - Value: awsvpc
  - Description: Network Mode for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_task_cpu** (string)
  - Source: TaskDef:task_cpu
  - Value: 4096
  - Description: Task Cpu for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_task_definition_family** (string)
  - Source: TaskDef:task_definition_family
  - Value: default-family
  - Description: Task Definition Family for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_task_family** (string)
  - Source: TaskDef:family
  - Value: liqrcon-tps-backend-svc
  - Description: Task Family for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_task_memory** (string)
  - Source: TaskDef:task_memory
  - Value: 30720
  - Description: Task Memory for liqrcon-tps-backend-svc

- **liqrcon_tps_backend_svc_task_role_arn** (string)
  - Source: TaskDef:task_role_arn
  - Value: arn:aws:iam::310306400902:role/liqrcon-devl-sfbu-comp
  - Description: Task Role Arn for liqrcon-tps-backend-svc

