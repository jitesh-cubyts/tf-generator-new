#!/usr/bin/env python3
"""
ECS to Terraform Generator
Converts AWS ECS JSON configuration to Terraform files with proper variable extraction
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import re

class ECSToTerraformGenerator:
    def __init__(self, json_file_path: str, output_dir: str = "terraform_output"):
        self.json_file_path = json_file_path
        self.output_dir = output_dir
        self.ecs_data = {}
        self.services = {}
        self.task_definitions = {}
        self.container_definitions = {}
        self.cluster_name = ""
        self.all_variables = {}  # Central store for all variables
        
        # Create output directory
        Path(self.output_dir).mkdir(exist_ok=True)
        
        # Initialize mapping configuration
        self._init_mapping_config()
        
    def _init_mapping_config(self):
        """Initialize mapping configuration - simplified for direct extraction"""
        # This method is kept for compatibility but mappings are now done directly
        # in the extraction methods to avoid complexity and ensure correct source mapping
        
        # Keep only the old mappings for legacy compatibility
        self.aws_to_tf_mappings = {
            # === SERVICE LEVEL MAPPINGS ===
            'serviceName': {
                'tf_var': 'service_name',
                'type': 'string',
                'description': 'Name of the ECS service'
            },
            'desiredCount': {
                'tf_var': 'desired_count',
                'type': 'number',
                'default': 1,
                'description': 'Desired number of tasks'
            },
            'launchType': {
                'tf_var': 'launch_type',
                'type': 'string',
                'default': 'FARGATE',
                'description': 'Launch type for the service'
            },
            'platformVersion': {
                'tf_var': 'platform_version',
                'type': 'string',
                'default': 'LATEST',
                'description': 'Platform version'
            },
            'healthCheckGracePeriodSeconds': {
                'tf_var': 'health_check_grace_period_seconds',
                'type': 'number',
                'default': 0,
                'description': 'Health check grace period in seconds'
            },
            
            # === TASK DEFINITION MAPPINGS ===
            'task_definition.family': {
                'tf_var': 'task_family',
                'type': 'string',
                'description': 'Task definition family name'
            },
            'task_definition.cpu': {
                'tf_var': 'cpu',
                'type': 'string',
                'default': '256',
                'description': 'CPU allocation for task'
            },
            'task_definition.memory': {
                'tf_var': 'memory',
                'type': 'string',
                'default': '512',
                'description': 'Memory allocation for task'
            },
            'task_definition.taskRoleArn': {
                'tf_var': 'task_role_arn',
                'type': 'string',
                'description': 'Task role ARN'
            },
            'task_definition.executionRoleArn': {
                'tf_var': 'execution_role_arn',
                'type': 'string',
                'description': 'Execution role ARN'
            },
            
            # === DEPLOYMENT CONFIGURATION MAPPINGS ===
            'deploymentConfiguration.maximumPercent': {
                'tf_var': 'maximum_percent',
                'type': 'number',
                'default': 200,
                'description': 'Maximum percent for deployment'
            },
            'deploymentConfiguration.minimumHealthyPercent': {
                'tf_var': 'minimum_healthy_percent',
                'type': 'number',
                'default': 100,
                'description': 'Minimum healthy percent for deployment'
            },
            
            # === NETWORK CONFIGURATION MAPPINGS ===
            'networkConfiguration.awsvpcConfiguration.subnets': {
                'tf_var': 'subnets',
                'type': 'list(string)',
                'default': [],
                'description': 'List of subnet IDs'
            },
            'networkConfiguration.awsvpcConfiguration.securityGroups': {
                'tf_var': 'security_groups',
                'type': 'list(string)',
                'default': [],
                'description': 'List of security group IDs'
            },
            'networkConfiguration.awsvpcConfiguration.assignPublicIp': {
                'tf_var': 'assign_public_ip',
                'type': 'bool',
                'default': False,
                'description': 'Whether to assign public IP',
                'transform': lambda x: x == 'ENABLED'
            },
            
            # === LOAD BALANCER MAPPINGS ===
            'loadBalancers.0.targetGroupArn': {
                'tf_var': 'target_group_arn',
                'type': 'string',
                'description': 'Target group ARN for load balancer'
            },
            'loadBalancers.0.containerName': {
                'tf_var': 'container_name',
                'type': 'string',
                'description': 'Container name for load balancer'
            },
            'loadBalancers.0.containerPort': {
                'tf_var': 'container_port',
                'type': 'number',
                'default': 80,
                'description': 'Container port for load balancer'
            },
        }
        
        # === CLUSTER LEVEL MAPPINGS ===
        self.cluster_mappings = {
            'cluster_name': {
                'tf_var': 'cluster_name',
                'type': 'string',
                'description': 'ECS cluster name'
            },
            'appshortname': {
                'tf_var': 'appshortname',
                'type': 'string',
                'description': 'Application short name (derived from cluster)',
                'derive_func': self._derive_appshortname
            },
            'logical_identifier': {
                'tf_var': 'logical_identifier',
                'type': 'string',
                'description': 'Logical identifier for the cluster',
                'derive_func': lambda cluster_name: cluster_name
            },
            'aws_region_primary': {
                'tf_var': 'aws_region_primary',
                'type': 'string',
                'default': 'us-east-1',
                'description': 'Primary AWS region for ECS deployment',
                'derive_func': self._derive_region
            },
            'Environment': {
                'tf_var': 'Environment',
                'type': 'string',
                'default': 'devl',
                'description': 'Environment name (derived from cluster name)',
                'derive_func': self._derive_environment
            },
            'envSuffix': {
                'tf_var': 'envSuffix',
                'type': 'string',
                'default': '-devl',
                'description': 'Environment suffix (derived from environment)',
                'derive_func': self._derive_env_suffix
            },
            'life_cycle': {
                'tf_var': 'life_cycle',
                'type': 'string',
                'default': 'devl',
                'description': 'Life cycle stage (same as environment)',
                'derive_func': self._derive_environment
            },
        }
        
        # === CONTAINER ENVIRONMENT VARIABLE MAPPINGS ===
        self.container_env_mappings = {
            'DT_CONNECTION_POINT': {
                'tf_var': 'DT_CONNECTION_POINT',
                'type': 'string',
                'default': 'https://dynatrace-le.fanniemae.com:443/communication',
                'description': 'Dynatrace connection point'
            },
            'DT_TENANT': {
                'tf_var': 'DT_TENANT',
                'type': 'string',
                'description': 'Dynatrace tenant'
            },
            'DT_TENANTTOKEN': {
                'tf_var': 'DT_TENANTTOKEN',
                'type': 'string',
                'sensitive': True,
                'description': 'Dynatrace tenant token'
            },
            'DT_LOG': {
                'tf_var': 'DT_LOG',
                'type': 'string',
                'default': 'info',
                'description': 'Dynatrace log level'
            },
            'DT_LOGLEVELCON': {
                'tf_var': 'DT_LOGLEVELCON',
                'type': 'string',
                'default': 'info',
                'description': 'Dynatrace log level console'
            },
            'SPRING_PROFILES_ACTIVE': {
                'tf_var': 'SPRING_PROFILES_ACTIVE',
                'type': 'string',
                'description': 'Spring active profiles'
            },
            'spring.profiles.active': {
                'tf_var': 'SPRING_PROFILES_ACTIVE',
                'type': 'string',
                'description': 'Spring active profiles'
            },
            'JAVA_TOOL_OPTIONS': {
                'tf_var': 'JAVA_TOOL_OPTIONS',
                'type': 'string',
                'description': 'Java tool options'
            },
            'PRIVATE_BUCKET': {
                'tf_var': 'PRIVATE_BUCKET',
                'type': 'string',
                'description': 'Private S3 bucket name'
            },
        }
        
        # === DERIVED/CALCULATED MAPPINGS ===
        self.derived_mappings = {
            'DT_CUSTOM_PROP': {
                'tf_var': 'DT_CUSTOM_PROP',
                'type': 'string',
                'description': 'Dynatrace custom properties (generated)',
                'derive_func': self._derive_dt_custom_prop
            },
            'DT_CLUSTER_ID': {
                'tf_var': 'DT_CLUSTER_ID',
                'type': 'string',
                'description': 'Dynatrace cluster ID (generated)',
                'derive_func': self._derive_dt_cluster_id
            },
            'alb_unique_identifier': {
                'tf_var': 'alb_unique_identifier',
                'type': 'string',
                'description': 'ALB unique identifier (generated)',
                'derive_func': self._derive_alb_identifier
            },
            'max_capacity': {
                'tf_var': 'max_capacity',
                'type': 'number',
                'description': 'Maximum capacity for autoscaling (calculated)',
                'derive_func': self._derive_max_capacity
            },
            'min_capacity': {
                'tf_var': 'min_capacity',
                'type': 'number',
                'description': 'Minimum capacity for autoscaling (calculated)',
                'derive_func': self._derive_min_capacity
            }
        }

    def _derive_appshortname(self, cluster_name):
        """Extract application short name from cluster name"""
        return cluster_name.split('-')[0] if cluster_name else 'app'

    def _derive_region(self, cluster_name):
        """Extract region from cluster name or default to us-east-1"""
        # Try to extract from service ARNs first
        for service_config in self.services.values():
            cluster_arn = service_config.get('clusterArn', '')
            if 'arn:aws:' in cluster_arn:
                parts = cluster_arn.split(':')
                if len(parts) >= 4:
                    return parts[3]
        return 'us-east-1'

    def _derive_environment_from_app_env(self):
        """Derive environment from APP_ENV environment variable in container definitions"""
        # Look for APP_ENV in container environment variables
        for container_key, container_config in self.container_definitions.items():
            env_vars = container_config.get('environment', [])
            for env in env_vars:
                if env.get('name') == 'APP_ENV':
                    app_env_value = env.get('value', '').lower()
                    print(f"  Found APP_ENV = {app_env_value}")
                    
                    # Map APP_ENV values to standard environment names
                    if app_env_value in ['dev', 'development', 'devl']:
                        return 'devl'
                    elif app_env_value in ['test', 'testing', 'tst']:
                        return 'test'
                    elif app_env_value in ['stage', 'staging', 'stg']:
                        return 'stage'
                    elif app_env_value in ['prod', 'production']:
                        return 'prod'
                    else:
                        return app_env_value  # Use as-is if not mapped
        
        # Fallback to cluster name method if APP_ENV not found
        print("  APP_ENV not found, deriving from cluster name")
        return self._derive_environment(self.cluster_name)

    def _derive_environment(self, cluster_name):
        """Derive environment from cluster name (fallback method)"""
        cluster_lower = cluster_name.lower()
        if 'prod' in cluster_lower:
            return 'prod'
        elif 'test' in cluster_lower:
            return 'test'
        elif 'stage' in cluster_lower or 'staging' in cluster_lower:
            return 'stage'
        elif 'uat' in cluster_lower:
            return 'uat'
        else:
            return 'devl'

    def _derive_env_suffix(self, cluster_name):
        """Derive environment suffix from cluster name"""
        env = self._derive_environment(cluster_name)
        return f'-{env}'

    def _derive_dt_custom_prop(self, cluster_name):
        """Generate Dynatrace custom properties"""
        app = self._derive_appshortname(cluster_name)
        env = self._derive_environment(cluster_name)
        return f'App={app.upper()} LifeCycle={env} ServiceId={cluster_name}'

    def _derive_dt_cluster_id(self, cluster_name):
        """Generate Dynatrace cluster ID"""
        return self._derive_dt_custom_prop(cluster_name)

    def _derive_alb_identifier(self, cluster_name):
        """Generate ALB identifier"""
        app = self._derive_appshortname(cluster_name)
        env_suffix = self._derive_env_suffix(cluster_name)
        return f'{app}{env_suffix}-alb'

    def _derive_max_capacity(self, service_config):
        """Calculate maximum capacity based on desired count and service type"""
        desired_count = service_config.get('desiredCount', 1)
        has_load_balancer = bool(service_config.get('loadBalancers'))
        
        base_max = max(3, desired_count * 2)
        return max(base_max, desired_count * 3) if has_load_balancer else base_max

    def _derive_min_capacity(self, service_config):
        """Calculate minimum capacity based on desired count"""
        desired_count = service_config.get('desiredCount', 1)
        return max(1, desired_count)

    def _extract_family_from_arn(self, arn):
        """Extract family name from task definition ARN"""
        if arn and ':task-definition/' in arn:
            return arn.split(':task-definition/')[-1].split(':')[0]
        return "default-family"

    def _derive_primary_container_name(self, service_name):
        """Get primary container name for service"""
        for key, container in self.container_definitions.items():
            if service_name in key and container.get('essential', True):
                return container.get('name', f"{service_name}-container")
        return f"{service_name}-container"

    def _derive_primary_container_image(self, service_name):
        """Get primary container image for service"""
        for key, container in self.container_definitions.items():
            if service_name in key and container.get('essential', True):
                return container.get('image', 'nginx:latest')
        return 'nginx:latest'

    def _derive_primary_container_cpu(self, service_name):
        """Get primary container CPU for service"""
        for key, container in self.container_definitions.items():
            if service_name in key and container.get('essential', True):
                return container.get('cpu', 0)
        return 0

    def _derive_primary_container_memory(self, service_name):
        """Get primary container memory for service"""
        for key, container in self.container_definitions.items():
            if service_name in key and container.get('essential', True):
                return container.get('memory', 512)
        return 512

    def _derive_primary_container_port(self, service_name):
        """Get primary container port for service"""
        for key, container in self.container_definitions.items():
            if service_name in key and container.get('essential', True):
                port_mappings = container.get('portMappings', [])
                if port_mappings:
                    return port_mappings[0].get('containerPort', 80)
        return 80

    def _derive_primary_container_essential(self, service_name):
        """Get primary container essential flag for service"""
        for key, container in self.container_definitions.items():
            if service_name in key:
                return container.get('essential', True)
        return True

    def _derive_log_group(self, service_name):
        """Generate log group name for service"""
        for key, container in self.container_definitions.items():
            if service_name in key and container.get('essential', True):
                log_config = container.get('logConfiguration', {})
                options = log_config.get('options', {})
                if 'awslogs-group' in options:
                    return options['awslogs-group']
        
        # Generate default log group
        return f"/aws/ecs/{self.cluster_name}/{service_name}"

    def _derive_log_stream_prefix(self, service_name):
        """Generate log stream prefix for service"""
        for key, container in self.container_definitions.items():
            if service_name in key and container.get('essential', True):
                log_config = container.get('logConfiguration', {})
                options = log_config.get('options', {})
                if 'awslogs-stream-prefix' in options:
                    return options['awslogs-stream-prefix']
        
        # Generate default stream prefix
        return f"{service_name}-logs"

    def _build_container_definitions_json(self, service_name):
        """Build container definitions JSON for a service with all containers"""
        container_definitions = []
        
        for key, container_config in self.container_definitions.items():
            if service_name in key and 'container_definition' in key:
                # Build complete container definition with variables
                container_def = self._build_parameterized_container_definition(container_config, service_name)
                container_definitions.append(container_def)
        
        return json.dumps(container_definitions, indent=2)

    def _build_parameterized_container_definition(self, container_config: Dict, service_name: str) -> Dict:
        """Build parameterized container definition"""
        container_name = container_config.get('name', 'default-container')
        sanitized_container_name = self._sanitize_name(container_name)
        
        # Build environment variables with both hardcoded and dynamic values
        environment = []
        
        # Add original environment variables from AWS config
        original_env = container_config.get('environment', [])
        for env_var in original_env:
            env_name = env_var.get('name', '')
            # For common variables, use template variables, otherwise use actual values
            if env_name in ['DT_LOG', 'DT_TENANT', 'DT_TENANTTOKEN', 'DT_CONNECTION_POINT', 
                           'DT_CUSTOM_PROP', 'PRIVATE_BUCKET', 'APP_NAME', 
                           'APP_ENV', 'APP_REGION', 'APP_CLUSTER_NAME']:
                environment.append({
                    "name": env_name,
                    "value": "${" + env_name.lower().replace('.', '_') + "}"
                })
            elif env_name == 'REGION':
                environment.append({
                    "name": env_name,
                    "value": "${primary_region}"
                })
            elif env_name == 'spring.profiles.active':
                environment.append({
                    "name": env_name,
                    "value": "${spring_profiles_active}"
                })
            else:
                # Keep original value for service-specific variables
                environment.append(env_var)
        
        container_def = {
            "name": container_config.get("name", ""),
            "image": container_config.get("image", ""),
            "cpu": container_config.get("cpu", 0),
            "memory": container_config.get("memory", 512),
            "essential": container_config.get("essential", True),
            "entryPoint": container_config.get("entryPoint", []),
            "command": container_config.get("command", []),
            "environment": environment,
            "environmentFiles": container_config.get("environmentFiles", []),
            "mountPoints": container_config.get("mountPoints", []),
            "volumesFrom": container_config.get("volumesFrom", []),
            "linuxParameters": container_config.get("linuxParameters", {}),
            "secrets": container_config.get("secrets", []),
            "dependsOn": container_config.get("dependsOn", []),
            "dnsServers": container_config.get("dnsServers", []),
            "dnsSearchDomains": container_config.get("dnsSearchDomains", []),
            "extraHosts": container_config.get("extraHosts", []),
            "dockerSecurityOptions": container_config.get("dockerSecurityOptions", []),
            "dockerLabels": container_config.get("dockerLabels", {}),
            "ulimits": container_config.get("ulimits", []),
            "systemControls": container_config.get("systemControls", []),
            "resourceRequirements": container_config.get("resourceRequirements", []),
            "portMappings": container_config.get("portMappings", []),
            "logConfiguration": container_config.get("logConfiguration", {}),
            "healthCheck": container_config.get("healthCheck", {}),
            "repositoryCredentials": container_config.get("repositoryCredentials", {})
        }
        
        # Remove None and empty values to keep JSON clean
        container_def = {k: v for k, v in container_def.items() if v is not None and v != {}}
        
        return container_def

    def _get_nested_value(self, data, path, default=None):
        """Get nested value from dictionary using dot notation"""
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict):
                if key.isdigit():
                    # Handle array index like loadBalancers.0.targetGroupArn
                    parent_key = keys[keys.index(key) - 1]
                    if parent_key in current and isinstance(current[parent_key], list):
                        index = int(key)
                        if index < len(current[parent_key]):
                            current = current[parent_key][index]
                        else:
                            return default
                    else:
                        return default
                elif key in current:
                    current = current[key]
                else:
                    return default
            else:
                return default
        
        return current

    def load_json_data(self):
        """Load and parse JSON data"""
        try:
            with open(self.json_file_path, 'r') as file:
                data = json.load(file)
            self.ecs_data = data.get('ecs', {})
            self._parse_ecs_data()
        except Exception as e:
            print(f"Error loading JSON data: {e}")
            raise

    def _parse_ecs_data(self):
        """Parse ECS data and categorize into services, task definitions, and container definitions"""
        for key, value in self.ecs_data.items():
            if 'container_definition' in key:
                # Container definition
                self.container_definitions[key] = value
            elif 'task_definition' in key and not 'container_definition' in key:
                # Task definition
                service_name = key.split('/')[1] if '/' in key else key.replace('/task_definition', '')
                cluster_name = key.split('/')[0]
                if not self.cluster_name:
                    self.cluster_name = cluster_name
                self.task_definitions[service_name] = value
            else:
                # Service definition
                if '/' in key:
                    cluster_name, service_name = key.split('/', 1)
                    if not self.cluster_name:
                        self.cluster_name = cluster_name
                    self.services[service_name] = value

    def _extract_variables_from_service(self, service_name: str, service_config: Dict, task_def: Dict):
        """Extract all variables from service configuration using CORRECT AWS config locations"""
        base_name = self._sanitize_name(service_name)
        
        print(f"  Processing service: {service_name}")
        
        # === EXTRACT DIRECT SERVICE VALUES ===
        service_mappings = {
            'serviceName': {'tf_var': 'service_name', 'type': 'string'},
            'desiredCount': {'tf_var': 'desired_count', 'type': 'number'},
            'launchType': {'tf_var': 'launch_type', 'type': 'string'},
            'platformVersion': {'tf_var': 'platform_version', 'type': 'string'},
            'healthCheckGracePeriodSeconds': {'tf_var': 'health_check_grace_period_seconds', 'type': 'number'},
        }
        
        for aws_field, config in service_mappings.items():
            value = service_config.get(aws_field)
            if value is not None:
                var_name = f"{base_name}_{config['tf_var']}"
                self.all_variables[var_name] = {
                    'value': value,
                    'description': f"{config['tf_var'].replace('_', ' ').title()} for {service_name}",
                    'type': config['type'],
                    'source': f'Service:{aws_field}'
                }
                print(f"    ✓ {var_name} = {value} (from service.{aws_field})")
        
        # === EXTRACT TASK DEFINITION VALUES ===
        if task_def:
            task_mappings = {
                'family': {'tf_var': 'task_family', 'type': 'string'},
                'cpu': {'tf_var': 'cpu', 'type': 'string'},
                'memory': {'tf_var': 'memory', 'type': 'string'},
                'taskRoleArn': {'tf_var': 'task_role_arn', 'type': 'string'},
                'executionRoleArn': {'tf_var': 'execution_role_arn', 'type': 'string'},
            }
            
            for aws_field, config in task_mappings.items():
                value = task_def.get(aws_field)
                if value is not None:
                    var_name = f"{base_name}_{config['tf_var']}"
                    self.all_variables[var_name] = {
                        'value': value,
                        'description': f"{config['tf_var'].replace('_', ' ').title()} for {service_name}",
                        'type': config['type'],
                        'source': f'TaskDef:{aws_field}'
                    }
                    print(f"    ✓ {var_name} = {value} (from task_def.{aws_field})")
        
        # === EXTRACT DEPLOYMENT CONFIGURATION ===
        deployment_config = service_config.get('deploymentConfiguration', {})
        if deployment_config:
            deploy_mappings = {
                'maximumPercent': {'tf_var': 'maximum_percent', 'type': 'number'},
                'minimumHealthyPercent': {'tf_var': 'minimum_healthy_percent', 'type': 'number'},
            }
            
            for aws_field, config in deploy_mappings.items():
                value = deployment_config.get(aws_field)
                if value is not None:
                    var_name = f"{base_name}_{config['tf_var']}"
                    self.all_variables[var_name] = {
                        'value': value,
                        'description': f"{config['tf_var'].replace('_', ' ').title()} for {service_name}",
                        'type': config['type'],
                        'source': f'DeployConfig:{aws_field}'
                    }
                    print(f"    ✓ {var_name} = {value} (from deploymentConfiguration.{aws_field})")
        
        # === EXTRACT NETWORK CONFIGURATION ===
        network_config = service_config.get('networkConfiguration', {}).get('awsvpcConfiguration', {})
        if network_config:
            net_mappings = {
                'subnets': {'tf_var': 'subnets', 'type': 'list(string)'},
                'securityGroups': {'tf_var': 'security_groups', 'type': 'list(string)'},
                'assignPublicIp': {'tf_var': 'assign_public_ip', 'type': 'bool', 'transform': lambda x: x == 'ENABLED'},
            }
            
            for aws_field, config in net_mappings.items():
                value = network_config.get(aws_field)
                if value is not None:
                    if 'transform' in config:
                        value = config['transform'](value)
                    
                    var_name = f"{base_name}_{config['tf_var']}"
                    self.all_variables[var_name] = {
                        'value': value,
                        'description': f"{config['tf_var'].replace('_', ' ').title()} for {service_name}",
                        'type': config['type'],
                        'source': f'NetworkConfig:{aws_field}'
                    }
                    print(f"    ✓ {var_name} = {value} (from networkConfiguration.{aws_field})")
        
        # === EXTRACT LOAD BALANCER CONFIGURATION ===
        load_balancers = service_config.get('loadBalancers', [])
        if load_balancers:
            lb_config = load_balancers[0]  # Take first load balancer
            lb_mappings = {
                'targetGroupArn': {'tf_var': 'target_group_arn', 'type': 'string'},
                'containerName': {'tf_var': 'container_name', 'type': 'string'},
                'containerPort': {'tf_var': 'container_port', 'type': 'number'},
            }
            
            for aws_field, config in lb_mappings.items():
                value = lb_config.get(aws_field)
                if value is not None:
                    var_name = f"{base_name}_{config['tf_var']}"
                    self.all_variables[var_name] = {
                        'value': value,
                        'description': f"{config['tf_var'].replace('_', ' ').title()} for {service_name}",
                        'type': config['type'],
                        'source': f'LoadBalancer:{aws_field}'
                    }
                    print(f"    ✓ {var_name} = {value} (from loadBalancers[0].{aws_field})")
        
        # === EXTRACT CONTAINER ENVIRONMENT VARIABLES (DIRECTLY FROM CONTAINER DEFINITIONS) ===
        container_env_values = self._extract_container_env_values_direct(service_name)
        
        # Store all found environment variables
        for env_name, env_value in container_env_values.items():
            # Create terraform variable name from environment variable name
            tf_var_name = env_name.lower().replace('.', '_')
            
            self.all_variables[tf_var_name] = {
                'value': env_value,
                'description': f"Environment variable {env_name} (from container definition)",
                'type': 'string',
                'sensitive': 'TOKEN' in env_name.upper() or 'PASSWORD' in env_name.upper(),
                'source': f'ContainerEnv:{env_name}'
            }
            print(f"    ✓ {tf_var_name} = {env_value} (from container env {env_name})")
        
        # === CALCULATE INTELLIGENT AUTOSCALING ===
        desired_count = service_config.get('desiredCount', 1)
        has_load_balancer = bool(service_config.get('loadBalancers'))
        
        min_capacity = max(1, desired_count)
        max_capacity = max(3, desired_count * 2)
        if has_load_balancer:
            max_capacity = max(max_capacity, desired_count * 3)
        
        self.all_variables[f"{base_name}_min_capacity"] = {
            'value': min_capacity,
            'description': f"Minimum autoscaling capacity for {service_name} (based on desired: {desired_count})",
            'type': 'number',
            'source': f'Calculated:min_capacity'
        }
        
        self.all_variables[f"{base_name}_max_capacity"] = {
            'value': max_capacity,
            'description': f"Maximum autoscaling capacity for {service_name} (based on desired: {desired_count}, has_lb: {has_load_balancer})",
            'type': 'number',
            'source': f'Calculated:max_capacity'
        }
        
        print(f"    ✓ {base_name}_min_capacity = {min_capacity} (calculated)")
        print(f"    ✓ {base_name}_max_capacity = {max_capacity} (calculated)")

        # === EXTRACT TASK DEFINITION VARIABLES FOR TEMPLATE ===
        task_def_vars = {
            'task_definition_family': self._extract_family_from_arn(service_config.get('taskDefinitionArn', '')),
            'task_role_arn': task_def.get('taskRoleArn', ''),
            'execution_role_arn': task_def.get('executionRoleArn', ''),
            'network_mode': task_def.get('networkMode', 'awsvpc'),
            'task_cpu': task_def.get('cpu', '256'),
            'task_memory': task_def.get('memory', '512')
        }
        
        for var_name, value in task_def_vars.items():
            var_key = f"{base_name}_{var_name}"
            self.all_variables[var_key] = {
                'value': value,
                'description': f"{var_name.replace('_', ' ').title()} for {service_name}",
                'type': 'string' if isinstance(value, str) else ('number' if isinstance(value, int) else 'bool'),
                'source': f'TaskDef:{var_name}'
            }
            print(f"    ✓ {var_key} = {value} (for task definition template)")

        # === EXTRACT CONTAINER-SPECIFIC VARIABLES ===
        self._extract_container_variables(service_name)

    def _extract_container_variables(self, service_name: str):
        """Extract variables for each container in a service"""
        containers = self._get_containers_for_service(service_name)
        
        for container_config in containers:
            container_name = container_config.get('name', 'default-container')
            sanitized_container_name = self._sanitize_name(container_name)
            
            # Extract container-specific variables
            container_vars = {
                f'{sanitized_container_name}_name': container_config.get('name', ''),
                f'{sanitized_container_name}_image': container_config.get('image', ''),
                f'{sanitized_container_name}_cpu': container_config.get('cpu', 0),
                f'{sanitized_container_name}_memory': container_config.get('memory', 512),
                f'{sanitized_container_name}_essential': container_config.get('essential', True)
            }
            
            for var_name, value in container_vars.items():
                self.all_variables[var_name] = {
                    'value': value,
                    'description': f"Container {var_name.replace('_', ' ')} for {container_name}",
                    'type': 'string' if isinstance(value, str) else ('number' if isinstance(value, int) else 'bool'),
                    'source': f'Container:{container_name}'
                }
                print(f"    ✓ {var_name} = {value} (container variable)")
            
            # Extract container environment variables  
            container_env = container_config.get('environment', [])
            for env_var in container_env:
                env_name = env_var.get('name', '')
                env_value = env_var.get('value', '')
                
                # Skip common variables (already handled globally)
                if env_name in ['DT_LOG', 'DT_TENANT', 'DT_TENANTTOKEN', 'DT_CONNECTION_POINT', 
                               'DT_CUSTOM_PROP', 'PRIVATE_BUCKET', 'REGION', 'APP_NAME', 
                               'APP_ENV', 'APP_REGION', 'APP_CLUSTER_NAME', 'spring.profiles.active']:
                    continue  # Skip these as they are handled globally
                
                # Process other container-specific environment variables
                var_name = env_name.lower().replace('.', '_')
                if var_name not in self.all_variables:
                    self.all_variables[var_name] = {
                        'value': env_value,
                        'description': f"Environment variable {env_name} from container {container_name}",
                        'type': 'string',
                        'source': f'ContainerEnv:{container_name}:{env_name}'
                    }
                    print(f"    ✓ {var_name} = {env_value} (container env)")

    def _get_containers_for_service(self, service_name):
        """Get all containers for a service"""
        containers = []
        for key, container_config in self.container_definitions.items():
            if service_name in key and 'container_definition' in key:
                containers.append(container_config)
        return containers

    def _extract_container_env_values_direct(self, service_name: str) -> Dict[str, str]:
        """Extract environment variables DIRECTLY from container definitions in AWS config"""
        env_values = {}
        
        # Look for container definitions in the AWS config
        # Pattern: liqrcon-ecs-tf/liqrcon-backend-svc/service_1/task_definition/container_definition/liqrcon-backend-svc
        for key, value in self.ecs_data.items():
            if service_name in key and 'container_definition' in key:
                print(f"    Found container definition: {key}")
                container_env = value.get('environment', [])
                for env_var in container_env:
                    env_name = env_var.get('name')
                    env_value = env_var.get('value')
                    if env_name and env_value:
                        env_values[env_name] = env_value
                        print(f"      Found env var: {env_name} = {env_value}")
        
        return env_values
    
    def _extract_container_env_values(self, service_name: str) -> Dict[str, str]:
        """Extract environment variables from container definitions for a service (legacy method)"""
        # First try the direct method
        env_values = self._extract_container_env_values_direct(service_name)
        if env_values:
            return env_values
        
        # Fallback to old method
        for key, container_def in self.container_definitions.items():
            if service_name in key:
                environment = container_def.get('environment', [])
                for env_var in environment:
                    env_name = env_var.get('name', '')
                    env_value = env_var.get('value', '')
                    if env_name:
                        env_values[env_name] = env_value
                break
        
        return env_values

    def _extract_cluster_variables(self):
        """Extract cluster-level variables from ACTUAL AWS config"""
        print(f"Processing cluster: {self.cluster_name}")
        
        # === EXTRACT REGION FROM ACTUAL ARNs ===
        region = self._extract_region_from_arns()
        
        # === EXTRACT CLUSTER-LEVEL VALUES ===
        cluster_mappings = {
            'cluster_name': {'tf_var': 'cluster_name', 'type': 'string'},
            'primary_region': {'tf_var': 'primary_region', 'type': 'string'},
            'secondary_region': {'tf_var': 'secondary_region', 'type': 'string'},
            'environment': {'tf_var': 'environment', 'type': 'string'},
            'app_shortname': {'tf_var': 'app_shortname', 'type': 'string'},
        }
        
        for aws_field, config in cluster_mappings.items():
            if aws_field == 'cluster_name':
                value = self.cluster_name
            elif aws_field == 'primary_region':
                value = region
            elif aws_field == 'secondary_region':
                value = 'us-east-2'  # Default secondary region
            elif aws_field == 'environment':
                value = self._derive_environment_from_app_env()
            elif aws_field == 'app_shortname':
                value = self._derive_appshortname(self.cluster_name)
            else:
                value = None
            
            if value:
                self.all_variables[config['tf_var']] = {
                    'value': value,
                    'description': f"{config['tf_var'].replace('_', ' ').title()}",
                    'type': config['type'],
                    'source': f'Cluster:{aws_field}'
                }
                print(f"  ✓ {config['tf_var']} = {value} (from cluster)")
        
        # === EXTRACT GLOBAL ENVIRONMENT VARIABLES ===
        # Get all unique environment variables from all services
        all_env_vars = {}
        for service_name in self.services.keys():
            service_env = self._extract_container_env_values_direct(service_name)
            all_env_vars.update(service_env)
        
        # Store all found environment variables as global variables with proper categorization
        for env_name, env_value in all_env_vars.items():
            tf_var_name = env_name.lower().replace('.', '_')
            
            # Skip REGION since we handle it with primary_region
            if env_name == 'REGION':
                continue
            
            # Skip if already processed in service extraction
            if tf_var_name not in self.all_variables:
                # Determine the source category for better organization
                if env_name.startswith('DT_'):
                    source_category = 'ContainerEnv'
                    description = f"Environment variable {env_name} (from container definition)"
                elif env_name.startswith('APP_'):
                    source_category = 'ContainerEnv'
                    description = f"Environment variable {env_name} (from container definition)"
                elif env_name in ['PRIVATE_BUCKET', 'spring.profiles.active', 'JAVA_TOOL_OPTIONS', 'SM_SSL', 'TW_CONTAINER_NAME']:
                    source_category = 'ContainerEnv'
                    description = f"Environment variable {env_name} (from container definition)"
                else:
                    source_category = 'GlobalEnv'
                    description = f"Global environment variable {env_name}"
                
                self.all_variables[tf_var_name] = {
                    'value': env_value,
                    'description': description,
                    'type': 'string',
                    'sensitive': 'TOKEN' in env_name.upper() or 'PASSWORD' in env_name.upper(),
                    'source': f'{source_category}:{env_name}'
                }
                print(f"  ✓ {tf_var_name} = {env_value} (from global env {env_name})")
    
    def _extract_region_from_arns(self) -> str:
        """Extract AWS region from ARNs in the config"""
        # Look for any ARN in the config to extract region
        for service_name, service_config in self.services.items():
            cluster_arn = service_config.get('clusterArn', '')
            if cluster_arn and 'arn:aws:' in cluster_arn:
                # ARN format: arn:aws:ecs:us-east-1:123456789012:cluster/name
                parts = cluster_arn.split(':')
                if len(parts) >= 4:
                    region = parts[3]
                    print(f"  ✓ Extracted region '{region}' from ARN: {cluster_arn}")
                    return region
        
        # Fallback to default
        print("  ⚠ Could not extract region from ARNs, using default: us-east-1")
        return 'us-east-1'

    def _extract_dynatrace_values(self) -> Dict[str, str]:
        """Extract Dynatrace and other environment values from container definitions"""
        dt_values = {}
        
        for container_key, container_config in self.container_definitions.items():
            env_vars = container_config.get('environment', [])
            for env in env_vars:
                env_name = env.get('name', '')
                env_value = env.get('value', '')
                if env_name in ['DT_CONNECTION_POINT', 'DT_CUSTOM_PROP', 'DT_TENANT', 'DT_TENANTTOKEN',
                               'DT_LOG', 'DT_LOGLEVELCON', 'DT_CLUSTER_ID', 'PRIVATE_BUCKET',
                               'spring.profiles.active', 'JAVA_TOOL_OPTIONS']:
                    dt_values[env_name] = env_value
        
        return dt_values

    def _build_task_definition_from_config(self, service_name: str, task_def: Dict) -> Dict:
        """Build complete task definition from AWS config data"""
        print(f"  Building task definition for: {service_name}")
        
        # Start with base task definition structure
        task_definition = {
            "family": task_def.get("family", service_name),
            "taskRoleArn": task_def.get("taskRoleArn", ""),
            "executionRoleArn": task_def.get("executionRoleArn", ""),
            "networkMode": task_def.get("networkMode", "awsvpc"),
            "requiresCompatibilities": task_def.get("requiresCompatibilities", ["FARGATE"]),
            "cpu": task_def.get("cpu", "256"),
            "memory": task_def.get("memory", "512"),
            "volumes": task_def.get("volumes", []),
            "placementConstraints": task_def.get("placementConstraints", []),
            "requiresAttributes": task_def.get("requiresAttributes", []),
            "tags": task_def.get("tags", []),
            "containerDefinitions": []
        }
        
        # Add optional fields if they exist
        if "revision" in task_def:
            task_definition["revision"] = task_def["revision"]
        if "status" in task_def:
            task_definition["status"] = task_def["status"]
        if "registeredAt" in task_def:
            task_definition["registeredAt"] = task_def["registeredAt"]
        if "registeredBy" in task_def:
            task_definition["registeredBy"] = task_def["registeredBy"]
        if "compatibilities" in task_def:
            task_definition["compatibilities"] = task_def["compatibilities"]
        
        # Find and add container definitions for this service
        container_definitions = []
        for key, container_config in self.container_definitions.items():
            if service_name in key and 'container_definition' in key:
                container_def = self._build_container_definition(container_config)
                container_definitions.append(container_def)
                print(f"    Added container: {container_def.get('name', 'unnamed')}")
        
        task_definition["containerDefinitions"] = container_definitions
        
        return task_definition

    def _build_container_definition(self, container_config: Dict) -> Dict:
        """Build complete container definition from AWS config"""
        container_def = {
            "name": container_config.get("name", ""),
            "image": container_config.get("image", ""),
            "cpu": container_config.get("cpu", 0),
            "memory": container_config.get("memory", 512),
            "memoryReservation": container_config.get("memoryReservation"),
            "essential": container_config.get("essential", True),
            "entryPoint": container_config.get("entryPoint", []),
            "command": container_config.get("command", []),
            "environment": container_config.get("environment", []),
            "environmentFiles": container_config.get("environmentFiles", []),
            "mountPoints": container_config.get("mountPoints", []),
            "volumesFrom": container_config.get("volumesFrom", []),
            "linuxParameters": container_config.get("linuxParameters", {}),
            "secrets": container_config.get("secrets", []),
            "dependsOn": container_config.get("dependsOn", []),
            "startTimeout": container_config.get("startTimeout"),
            "stopTimeout": container_config.get("stopTimeout"),
            "hostname": container_config.get("hostname"),
            "user": container_config.get("user"),
            "workingDirectory": container_config.get("workingDirectory"),
            "disableNetworking": container_config.get("disableNetworking"),
            "privileged": container_config.get("privileged"),
            "readonlyRootFilesystem": container_config.get("readonlyRootFilesystem"),
            "dnsServers": container_config.get("dnsServers", []),
            "dnsSearchDomains": container_config.get("dnsSearchDomains", []),
            "extraHosts": container_config.get("extraHosts", []),
            "dockerSecurityOptions": container_config.get("dockerSecurityOptions", []),
            "interactive": container_config.get("interactive"),
            "pseudoTerminal": container_config.get("pseudoTerminal"),
            "dockerLabels": container_config.get("dockerLabels", {}),
            "ulimits": container_config.get("ulimits", []),
            "systemControls": container_config.get("systemControls", []),
            "resourceRequirements": container_config.get("resourceRequirements", []),
            "firelensConfiguration": container_config.get("firelensConfiguration"),
            "portMappings": container_config.get("portMappings", []),
            "logConfiguration": container_config.get("logConfiguration", {}),
            "healthCheck": container_config.get("healthCheck", {}),
            "repositoryCredentials": container_config.get("repositoryCredentials", {})
        }
        
        # Remove None values to keep the JSON clean
        container_def = {k: v for k, v in container_def.items() if v is not None}
        
        return container_def

    def _build_task_definition_template_from_config(self, service_name: str, task_def: Dict) -> str:
        """Build task definition template from AWS config with proper variables"""
        print(f"  Building task definition template for: {service_name}")
        
        # Get all containers for this service from AWS config
        containers = []
        for key, container_config in self.container_definitions.items():
            if service_name in key and 'container_definition' in key:
                container_template = self._build_container_template(container_config, service_name)
                containers.append(container_template)
                print(f"    Added container template: {container_config.get('name', 'unnamed')}")
        
        # Build complete task definition template
        task_definition = {
            "family": "${task_definition_family}",
            "taskRoleArn": "${task_role_arn}",
            "executionRoleArn": "${execution_role_arn}",
            "networkMode": "${network_mode}",
            "requiresCompatibilities": ["${launch_type}"],
            "cpu": "${task_cpu}",
            "memory": "${task_memory}",
            "volumes": task_def.get("volumes", []),
            "placementConstraints": task_def.get("placementConstraints", []),
            "requiresAttributes": task_def.get("requiresAttributes", []),
            "tags": task_def.get("tags", []),
            "containerDefinitions": containers
        }
        
        return json.dumps(task_definition, indent=2)

    def _build_container_template(self, container_config: Dict, service_name: str) -> Dict:
        """Build container template with proper variable references"""
        container_name = container_config.get('name', 'default-container')
        sanitized_container_name = self._sanitize_name(container_name)
        
        # Build environment variables with proper variable references
        environment = []
        original_env = container_config.get('environment', [])
        for env_var in original_env:
            env_name = env_var.get('name', '')
            env_value = env_var.get('value', '')
            
            # For common variables, use template variables
            if env_name in ['DT_LOG', 'DT_TENANT', 'DT_TENANTTOKEN', 'DT_CONNECTION_POINT', 
                           'DT_CUSTOM_PROP', 'PRIVATE_BUCKET', 'APP_NAME', 
                           'APP_ENV', 'APP_REGION', 'APP_CLUSTER_NAME']:
                var_name = env_name.lower().replace('.', '_')
                environment.append({
                    "name": env_name,
                    "value": f"${{{var_name}}}"
                })
            elif env_name == 'REGION':
                environment.append({
                    "name": env_name,
                    "value": "${primary_region}"
                })
            elif env_name == 'spring.profiles.active':
                environment.append({
                    "name": env_name,
                    "value": "${spring_profiles_active}"
                })
            else:
                # For service-specific variables, create a variable
                var_name = f"{env_name.lower().replace('.', '_')}"
                environment.append({
                    "name": env_name,
                    "value": f"${{{var_name}}}"
                })
        
        # Build container template with variables
        container_template = {
            "name": f"${{{sanitized_container_name}_name}}",
            "image": f"${{{sanitized_container_name}_image}}",
            "cpu": f"${{{sanitized_container_name}_cpu}}",
            "memory": f"${{{sanitized_container_name}_memory}}",
            "essential": f"${{{sanitized_container_name}_essential}}",
            "entryPoint": container_config.get("entryPoint", []),
            "command": container_config.get("command", []),
            "environment": environment,
            "environmentFiles": container_config.get("environmentFiles", []),
            "mountPoints": container_config.get("mountPoints", []),
            "volumesFrom": container_config.get("volumesFrom", []),
            "linuxParameters": container_config.get("linuxParameters", {}),
            "secrets": container_config.get("secrets", []),
            "dependsOn": container_config.get("dependsOn", []),
            "dnsServers": container_config.get("dnsServers", []),
            "dnsSearchDomains": container_config.get("dnsSearchDomains", []),
            "extraHosts": container_config.get("extraHosts", []),
            "dockerSecurityOptions": container_config.get("dockerSecurityOptions", []),
            "dockerLabels": container_config.get("dockerLabels", {}),
            "ulimits": container_config.get("ulimits", []),
            "systemControls": container_config.get("systemControls", []),
            "resourceRequirements": container_config.get("resourceRequirements", []),
            "portMappings": container_config.get("portMappings", []),
            "logConfiguration": container_config.get("logConfiguration", {}),
            "healthCheck": container_config.get("healthCheck", {}),
            "repositoryCredentials": container_config.get("repositoryCredentials", {})
        }
        
        # Remove empty values to keep template clean
        container_template = {k: v for k, v in container_template.items() if v not in [None, {}, []]}
        
        return container_template

    def _get_parameterized_task_definition_template(self) -> str:
        """Generate parameterized task definition template using variables"""
        template = {
            "family": "${task_definition_family}",
            "taskRoleArn": "${task_role_arn}",
            "executionRoleArn": "${execution_role_arn}",
            "networkMode": "${network_mode}",
            "requiresCompatibilities": ["${launch_type}"],
            "cpu": "${task_cpu}",
            "memory": "${task_memory}",
            "volumes": [],
            "placementConstraints": [],
            "requiresAttributes": [],
            "tags": [],
            "containerDefinitions": "${container_definitions_json}"
        }
        
        return json.dumps(template, indent=2)

    def _get_cluster_template(self) -> str:
        """Read generic cluster template from tf-template folder"""
        try:
            with open('tf-template/cluster_template.tf', 'r') as f:
                return f.read()
        except FileNotFoundError:
            print("Error: tf-template/cluster_template.tf not found!")
            raise

    def _get_service_template(self) -> str:
        """Read generic service template from tf-template folder"""
        try:
            with open('tf-template/service_template.tf', 'r') as f:
                return f.read()
        except FileNotFoundError:
            print("Error: tf-template/service_template.tf not found!")
            raise

    def generate_cluster_terraform(self):
        """Generate ECS cluster Terraform file using template"""
        template = self._get_cluster_template()
        cluster_content = template.format(
            cluster_name=self._sanitize_name(self.cluster_name).replace('_', '-')
        )
        
        filename = f"ecs-cluster-{self.cluster_name}.tf"
        with open(f"{self.output_dir}/{filename}", 'w') as f:
            f.write(cluster_content)
        print(f"Generated: {self.output_dir}/{filename}")

    def generate_service_terraform(self):
        """Generate ECS service Terraform files using template"""
        template = self._get_service_template()
        
        for service_name, service_config in self.services.items():
            sanitized_service_name = self._sanitize_name(service_name)
            
            # Prepare target configuration
            target_config = ""
            if service_config.get('loadBalancers'):
                target_config = f'''
  target_configuration = [
    {{
      target_group_arn = var.{sanitized_service_name}_config.target_group_arn
      container_name   = var.{sanitized_service_name}_config.container_name
      container_port   = var.{sanitized_service_name}_config.container_port
    }}
  ]'''
            
            # Build container variables for templatefile
            container_variables = self._build_container_variables_map(service_name)
            
            service_content = template.format(
                service_name=service_name,
                sanitized_service_name=sanitized_service_name,
                cluster_name=self._sanitize_name(self.cluster_name).replace('_', '-'),
                target_configuration=target_config,
                container_variables=container_variables
            )
            
            filename = f"ecs-service-{service_name}.tf"
            with open(f"{self.output_dir}/{filename}", 'w') as f:
                f.write(service_content)
            print(f"Generated: {self.output_dir}/{filename}")

    def _build_container_variables_map(self, service_name: str) -> str:
        """Build container variables map for templatefile function"""
        containers = self._get_containers_for_service(service_name)
        
        if not containers:
            return "var.container_config"
        
        # Use the container_config object instead of individual variables
        return "var.container_config"

    def generate_task_definition_json(self):
        """Generate task definition files per service based on AWS config"""
        # Create task_definitions subdirectory
        task_defs_dir = f"{self.output_dir}/task_definitions"
        Path(task_defs_dir).mkdir(exist_ok=True)
        
        # Generate task definition for each service based on AWS config
        for service_name, service_config in self.services.items():
            task_def = self.task_definitions.get(service_name, {})
            if not task_def:
                print(f"  ⚠ No task definition found for service: {service_name}")
                continue
            
            # Build task definition from AWS config with variables
            task_definition_template = self._build_task_definition_template_from_config(service_name, task_def)
            
            # Write to service-specific file
            sanitized_name = self._sanitize_name(service_name)
            filename = f"ecs_task_def_{sanitized_name}.json"
            
            with open(f"{task_defs_dir}/{filename}", 'w') as f:
                f.write(task_definition_template)
            print(f"Generated: {task_defs_dir}/{filename}")

    def generate_variables_tf(self):
        """Generate variables.tf file with object-structured variables"""
        print(f"Generating variables.tf with {len(self.all_variables)} variables...")
        
        content = "# Generated Variables File\n"
        content += "# Variables organized with object structure for services\n\n"
        
        # Categorize variables by usage type (same logic as generate_workspace_vars)
        infrastructure_vars = {}
        environment_vars = {}
        dynatrace_vars = {}
        service_vars = {}
        container_vars = {}
        
        for var_name, var_config in self.all_variables.items():
            source = var_config.get('source', '')
            
            # Skip region variable since we use primary_region instead
            if var_name == 'region':
                continue
            
            # Categorize variables by usage (same logic as workspace_vars)
            service_match = None
            for svc_name in self.services.keys():
                sanitized_svc = self._sanitize_name(svc_name)
                if var_name.startswith(f"{sanitized_svc}_"):
                    service_match = sanitized_svc
                    break
            
            if service_match:
                # This is a service-specific variable
                if service_match not in service_vars:
                    service_vars[service_match] = {}
                clean_var_name = var_name.replace(f"{service_match}_", "")
                service_vars[service_match][clean_var_name] = var_config
            elif source.startswith('Container:'):
                # This is a container variable
                container_vars[var_name] = var_config
            elif var_name.startswith('dt_') or 'dynatrace' in var_name.lower():
                # Dynatrace-related variables
                dynatrace_vars[var_name] = var_config
            elif var_name in ['cluster_name', 'primary_region', 'secondary_region', 'environment', 'app_shortname']:
                # Infrastructure variables
                infrastructure_vars[var_name] = var_config
            elif var_name.startswith('app_') or var_name in ['private_bucket', 'spring_profiles_active', 'java_tool_options', 'sm_ssl', 'tw_container_name']:
                # Application environment variables
                environment_vars[var_name] = var_config
            else:
                # Other infrastructure variables
                infrastructure_vars[var_name] = var_config
        
        # Generate infrastructure config object variable
        if infrastructure_vars:
            content += "# === INFRASTRUCTURE CONFIGURATION ===\n\n"
            content += 'variable "infrastructure_config" {\n'
            content += '  description = "Infrastructure configuration object"\n'
            content += '  type = object({\n'
            for var_name in sorted(infrastructure_vars.keys()):
                var_config = infrastructure_vars[var_name]
                var_type = var_config.get('type', 'string')
                content += f'    {var_name} = {var_type}\n'
            content += '  })\n'
            content += '}\n\n'
        
        # Generate dynatrace config object variable
        if dynatrace_vars:
            content += "# === DYNATRACE MONITORING CONFIGURATION ===\n\n"
            content += 'variable "dynatrace_config" {\n'
            content += '  description = "Dynatrace monitoring configuration object"\n'
            content += '  type = object({\n'
            for var_name in sorted(dynatrace_vars.keys()):
                var_config = dynatrace_vars[var_name]
                var_type = var_config.get('type', 'string')
                content += f'    {var_name} = {var_type}\n'
            content += '  })\n'
            content += '  sensitive = true\n'
            content += '}\n\n'
        
        # Generate application environment config object variable
        if environment_vars:
            content += "# === APPLICATION ENVIRONMENT CONFIGURATION ===\n\n"
            content += 'variable "application_config" {\n'
            content += '  description = "Application environment configuration object"\n'
            content += '  type = object({\n'
            for var_name in sorted(environment_vars.keys()):
                var_config = environment_vars[var_name]
                var_type = var_config.get('type', 'string')
                content += f'    {var_name} = {var_type}\n'
            content += '  })\n'
            content += '}\n\n'
        
        # Generate container config object variable
        if container_vars:
            content += "# === CONTAINER CONFIGURATIONS ===\n\n"
            content += 'variable "container_config" {\n'
            content += '  description = "Container configurations object"\n'
            content += '  type = object({\n'
            for var_name in sorted(container_vars.keys()):
                var_config = container_vars[var_name]
                var_type = var_config.get('type', 'string')
                content += f'    {var_name} = {var_type}\n'
            content += '  })\n'
            content += '}\n\n'
        
        # Generate service object variables
        for service_name in sorted(service_vars.keys()):
            # Find original service name for display
            original_service_name = service_name
            for orig_name in self.services.keys():
                if self._sanitize_name(orig_name) == service_name:
                    original_service_name = orig_name
                    break
            
            content += f"# === SERVICE: {original_service_name.upper()} ===\n\n"
            service_obj_name = f"{service_name}_config"
            
            # Build object type definition
            content += f'variable "{service_obj_name}" {{\n'
            content += f'  description = "Configuration object for {original_service_name} service"\n'
            content += f'  type = object({{\n'
            
            # Add all service variables to the object type
            for var_name in sorted(service_vars[service_name].keys()):
                var_config = service_vars[service_name][var_name]
                var_type = var_config.get('type', 'string')
                content += f'    {var_name} = {var_type}\n'
            
            content += f'  }})\n'
            content += f'}}\n\n'
        
        with open(f"{self.output_dir}/variables.tf", 'w') as f:
            f.write(content)
        print(f"Generated: {self.output_dir}/variables.tf")
        
        # Generate mapping report
        self._generate_mapping_report()

    def _generate_mapping_report(self):
        """Generate detailed mapping report showing source of each variable"""
        print("Generating mapping report...")
        
        report_content = "# AWS to Terraform Variable Mapping Report\n"
        report_content += f"# Generated on: {json.dumps(str(Path(self.json_file_path).name))}\n"
        report_content += f"# Cluster: {self.cluster_name}\n"
        report_content += f"# Services: {', '.join(self.services.keys())}\n\n"
        
        # Group by source type
        source_groups = {}
        for var_name, var_config in self.all_variables.items():
            source = var_config.get('source', 'Unknown')
            source_type = source.split(':')[0]
            if source_type not in source_groups:
                source_groups[source_type] = []
            source_groups[source_type].append((var_name, var_config))
        
        # Generate report sections
        for source_type in sorted(source_groups.keys()):
            report_content += f"## {source_type.upper()} MAPPINGS\n\n"
            
            # Sort variables within each group
            sorted_vars = sorted(source_groups[source_type])
            
            for var_name, var_config in sorted_vars:
                var_type = var_config.get('type', 'string')
                description = var_config.get('description', '')
                source = var_config.get('source', 'Unknown')
                value = var_config.get('value', '')
                
                report_content += f"- **{var_name}** ({var_type})\n"
                report_content += f"  - Source: {source}\n"
                report_content += f"  - Value: {value}\n"
                report_content += f"  - Description: {description}\n\n"
        
        with open(f"{self.output_dir}/MAPPING_REPORT.md", 'w') as f:
            f.write(report_content)
        print(f"Generated: {self.output_dir}/MAPPING_REPORT.md")

    def generate_workspace_vars(self):
        """Generate workspace_vars.tfvars file with organized object structure"""
        print(f"Generating workspace_vars.tfvars with {len(self.all_variables)} variables...")
        
        content = "# Generated Workspace Variables\n"
        content += "# Variables organized by service and global scope\n\n"
        
        # Categorize variables by usage type
        infrastructure_vars = {}
        environment_vars = {}
        dynatrace_vars = {}
        service_vars = {}
        container_vars = {}
        
        for var_name, var_config in self.all_variables.items():
            value = var_config.get('value')
            var_type = var_config.get('type', 'string')
            source = var_config.get('source', '')
            
            # Skip region variable since we use primary_region instead
            if var_name == 'region':
                continue
            
            # Format value based on type
            if value is not None:
                if var_type == 'string':
                    formatted_value = f'"{value}"'
                elif var_type == 'bool':
                    formatted_value = str(value).lower()
                elif var_type.startswith('list('):
                    if isinstance(value, list):
                        formatted_items = [f'"{item}"' for item in value]
                        formatted_value = f'[{", ".join(formatted_items)}]'
                    else:
                        formatted_value = f'"{value}"'
                else:
                    formatted_value = str(value)
                
                # Categorize variables by usage
                service_match = None
                for svc_name in self.services.keys():
                    sanitized_svc = self._sanitize_name(svc_name)
                    if var_name.startswith(f"{sanitized_svc}_"):
                        service_match = sanitized_svc
                        break
                
                if service_match:
                    # This is a service-specific variable
                    if service_match not in service_vars:
                        service_vars[service_match] = {}
                    clean_var_name = var_name.replace(f"{service_match}_", "")
                    service_vars[service_match][clean_var_name] = formatted_value
                elif source.startswith('Container:'):
                    # This is a container variable
                    container_vars[var_name] = formatted_value
                elif var_name.startswith('dt_') or 'dynatrace' in var_name.lower():
                    # Dynatrace-related variables
                    dynatrace_vars[var_name] = formatted_value
                elif var_name in ['cluster_name', 'primary_region', 'secondary_region', 'environment', 'app_shortname']:
                    # Infrastructure variables
                    infrastructure_vars[var_name] = formatted_value
                elif var_name.startswith('app_') or var_name in ['private_bucket', 'spring_profiles_active', 'java_tool_options', 'sm_ssl', 'tw_container_name']:
                    # Application environment variables
                    environment_vars[var_name] = formatted_value
                else:
                    # Other infrastructure variables
                    infrastructure_vars[var_name] = formatted_value
        
        # Generate infrastructure config object
        if infrastructure_vars:
            content += "# === INFRASTRUCTURE CONFIGURATION ===\n"
            content += "infrastructure_config = {\n"
            for var_name in sorted(infrastructure_vars.keys()):
                content += f'  {var_name} = {infrastructure_vars[var_name]}\n'
            content += "}\n\n"
        
        # Generate dynatrace config object
        if dynatrace_vars:
            content += "# === DYNATRACE MONITORING CONFIGURATION ===\n"
            content += "dynatrace_config = {\n"
            for var_name in sorted(dynatrace_vars.keys()):
                content += f'  {var_name} = {dynatrace_vars[var_name]}\n'
            content += "}\n\n"
        
        # Generate application environment config object
        if environment_vars:
            content += "# === APPLICATION ENVIRONMENT CONFIGURATION ===\n"
            content += "application_config = {\n"
            for var_name in sorted(environment_vars.keys()):
                content += f'  {var_name} = {environment_vars[var_name]}\n'
            content += "}\n\n"
        
        # Generate container configurations object
        if container_vars:
            content += "# === CONTAINER CONFIGURATIONS ===\n"
            content += "container_config = {\n"
            for var_name in sorted(container_vars.keys()):
                content += f'  {var_name} = {container_vars[var_name]}\n'
            content += "}\n\n"
        
        # Generate service object variables
        for service_name in sorted(service_vars.keys()):
            # Find original service name for display
            original_service_name = service_name
            for orig_name in self.services.keys():
                if self._sanitize_name(orig_name) == service_name:
                    original_service_name = orig_name
                    break
            
            content += f"# === SERVICE: {original_service_name.upper()} ===\n"
            service_obj_name = f"{service_name}_config"
            content += f'{service_obj_name} = {{\n'
            
            # Sort variables within service
            for var_name in sorted(service_vars[service_name].keys()):
                content += f'  {var_name} = {service_vars[service_name][var_name]}\n'
            
            content += '}\n\n'
        
        with open(f"{self.output_dir}/workspace_vars.tfvars", 'w') as f:
            f.write(content)
        print(f"Generated: {self.output_dir}/workspace_vars.tfvars")

    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for use in Terraform variables"""
        # Replace hyphens with underscores and remove invalid characters
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Ensure it starts with a letter or underscore
        if sanitized and sanitized[0].isdigit():
            sanitized = f'_{sanitized}'
        return sanitized

    def generate_all(self):
        """Generate all Terraform files"""
        print("Starting ECS to Terraform generation...")
        
        # Load and parse data
        self.load_json_data()
        
        if not self.cluster_name:
            print("Error: No cluster found in the JSON data")
            return
        
        print(f"Found cluster: {self.cluster_name}")
        print(f"Found services: {list(self.services.keys())}")
        
        # Extract variables
        self._extract_cluster_variables()
        for service_name, service_config in self.services.items():
            task_def = self.task_definitions.get(service_name, {})
            self._extract_variables_from_service(service_name, service_config, task_def)
        
        # Generate files
        self.generate_cluster_terraform()
        self.generate_service_terraform()
        self.generate_task_definition_json()
        self.generate_variables_tf()
        self.generate_workspace_vars()
        
        print(f"\n✅ Generation complete! Files created in '{self.output_dir}' directory")
        print(f"📊 Total variables extracted: {len(self.all_variables)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python ecs_to_terraform_generator.py <json_file_path>")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    
    if not Path(json_file_path).exists():
        print(f"Error: File '{json_file_path}' not found")
        sys.exit(1)
    
    generator = ECSToTerraformGenerator(json_file_path)
    generator.generate_all()

if __name__ == "__main__":
    main() 