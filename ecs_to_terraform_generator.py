#!/usr/bin/env python3
"""
ECS to Terraform Generator
Converts AWS ECS JSON configuration to Terraform files with proper variable extraction.
This script generates clean, object-structured Terraform configurations from AWS ECS exports.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
import os


class ECSToTerraformGenerator:
    """
    Main class for converting AWS ECS JSON configuration to Terraform files.
    
    Features:
    - Extracts variables from AWS config with proper categorization
    - Generates object-structured Terraform variables
    - Creates service-specific task definitions with template variables
    - Supports multi-container services
    - Derives environment from APP_ENV container variable
    """
    
    def __init__(self, json_file_path: str, output_dir: str = "terraform_output"):
        self.json_file_path = json_file_path
        self.output_dir = output_dir
        self.ecs_data = {}
        self.services = {}
        self.task_definitions = {}
        self.container_definitions = {}
        self.cluster_name = ""
        self.all_variables = {}
        
        # Create output directory
        Path(self.output_dir).mkdir(exist_ok=True)
        
        # Common environment variables that should use template variables
        self.common_env_vars = {
            'DT_LOG': 'dt_log',
            'DT_TENANT': 'dt_tenant', 
            'DT_TENANTTOKEN': 'dt_tenanttoken',
            'DT_CONNECTION_POINT': 'dt_connection_point',
            'DT_CUSTOM_PROP': 'dt_custom_prop',
            'PRIVATE_BUCKET': 'private_bucket',
            'APP_NAME': 'app_name',
            'APP_ENV': 'app_env',
            'APP_REGION': 'app_region',
            'APP_CLUSTER_NAME': 'app_cluster_name',
            'REGION': 'primary_region',
            'spring.profiles.active': 'spring_profiles_active'
        }

    # ==================== UTILITY METHODS ====================
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for use in Terraform variables"""
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        if sanitized and sanitized[0].isdigit():
            sanitized = f'_{sanitized}'
        return sanitized

    def _derive_appshortname(self, cluster_name: str) -> str:
        """Extract application short name from cluster name"""
        return cluster_name.split('-')[0] if cluster_name else 'app'

    def _derive_environment_from_app_env(self) -> str:
        """Derive environment from APP_ENV environment variable in container definitions"""
        for container_config in self.container_definitions.values():
            env_vars = container_config.get('environment', [])
            for env in env_vars:
                if env.get('name') == 'APP_ENV':
                    app_env_value = env.get('value', '').lower()
                    print(f"  Found APP_ENV = {app_env_value}")
                    
                    env_mapping = {
                        'dev': 'devl', 'development': 'devl', 'devl': 'devl',
                        'test': 'test', 'testing': 'test', 'tst': 'test',
                        'stage': 'stage', 'staging': 'stage', 'stg': 'stage',
                        'prod': 'prod', 'production': 'prod'
                    }
                    return env_mapping.get(app_env_value, app_env_value)
        
        print("  APP_ENV not found, deriving from cluster name")
        return self._derive_environment_from_cluster(self.cluster_name)

    def _derive_environment_from_cluster(self, cluster_name: str) -> str:
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
        return 'devl'

    def _extract_family_from_arn(self, arn: str) -> str:
        """Extract family name from task definition ARN"""
        if arn and ':task-definition/' in arn:
            return arn.split(':task-definition/')[-1].split(':')[0]
        return "default-family"

    def _extract_region_from_arns(self) -> str:
        """Extract AWS region from ARNs in the config"""
        for service_config in self.services.values():
            cluster_arn = service_config.get('clusterArn', '')
            if cluster_arn and 'arn:aws:' in cluster_arn:
                parts = cluster_arn.split(':')
                if len(parts) >= 4:
                    region = parts[3]
                    print(f"  ✓ Extracted region '{region}' from ARN: {cluster_arn}")
                    return region
        
        print("  ⚠ Could not extract region from ARNs, using default: us-east-1")
        return 'us-east-1'

    # ==================== DATA LOADING AND PARSING ====================
    
    def load_json_data(self) -> None:
        """Load and parse JSON data"""
        try:
            with open(self.json_file_path, 'r') as file:
                data = json.load(file)
            self.ecs_data = data.get('ecs', {})
            self._parse_ecs_data()
        except FileNotFoundError:
            print(f"Error: File '{self.json_file_path}' not found")
            raise
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in file '{self.json_file_path}': {e}")
            raise
        except Exception as e:
            print(f"Error loading JSON data: {e}")
            raise

    def _parse_ecs_data(self) -> None:
        """Parse ECS data and categorize into services, task definitions, and container definitions"""
        for key, value in self.ecs_data.items():
            if 'container_definition' in key:
                self.container_definitions[key] = value
            elif 'task_definition' in key and 'container_definition' not in key:
                service_name = key.split('/')[1] if '/' in key else key.replace('/task_definition', '')
                cluster_name = key.split('/')[0]
                if not self.cluster_name:
                    self.cluster_name = cluster_name
                self.task_definitions[service_name] = value
            else:
                if '/' in key:
                    cluster_name, service_name = key.split('/', 1)
                    if not self.cluster_name:
                        self.cluster_name = cluster_name
                    self.services[service_name] = value

    # ==================== VARIABLE EXTRACTION ====================
    
    def _extract_cluster_variables(self) -> None:
        """Extract cluster-level variables from AWS config"""
        print(f"Processing cluster: {self.cluster_name}")
        
        region = self._extract_region_from_arns()
        
        cluster_vars = {
            'cluster_name': self.cluster_name,
            'primary_region': region,
            'secondary_region': 'us-east-2',  # Default secondary region
            'environment': self._derive_environment_from_app_env(),
            'app_shortname': self._derive_appshortname(self.cluster_name)
        }
        
        for var_name, value in cluster_vars.items():
            self.all_variables[var_name] = {
                'value': value,
                'description': f"{var_name.replace('_', ' ').title()}",
                'type': 'string',
                'source': f'Cluster:{var_name}'
            }
            print(f"  ✓ {var_name} = {value} (from cluster)")
        
        # Extract global environment variables
        self._extract_global_env_variables()

    def _extract_global_env_variables(self) -> None:
        """Extract global environment variables from all services"""
        all_env_vars = {}
        for service_name in self.services.keys():
            service_env = self._extract_container_env_values_direct(service_name)
            all_env_vars.update(service_env)
        
        for env_name, env_value in all_env_vars.items():
            tf_var_name = env_name.lower().replace('.', '_')
            
            # Skip REGION since we handle it with primary_region
            if env_name == 'REGION':
                continue
            
            if tf_var_name not in self.all_variables:
                self.all_variables[tf_var_name] = {
                    'value': env_value,
                    'description': f"Environment variable {env_name} (from container definition)",
                    'type': 'string',
                    'sensitive': 'TOKEN' in env_name.upper() or 'PASSWORD' in env_name.upper(),
                    'source': f'ContainerEnv:{env_name}'
                }
                print(f"  ✓ {tf_var_name} = {env_value} (from global env {env_name})")

    def _extract_variables_from_service(self, service_name: str, service_config: Dict, task_def: Dict) -> None:
        """Extract all variables from service configuration"""
        base_name = self._sanitize_name(service_name)
        print(f"  Processing service: {service_name}")
        
        # Service-level mappings
        service_mappings = {
            'serviceName': {'tf_var': 'service_name', 'type': 'string'},
            'desiredCount': {'tf_var': 'desired_count', 'type': 'number'},
            'launchType': {'tf_var': 'launch_type', 'type': 'string'},
            'platformVersion': {'tf_var': 'platform_version', 'type': 'string'},
            'healthCheckGracePeriodSeconds': {'tf_var': 'health_check_grace_period_seconds', 'type': 'number'},
        }
        
        # Extract service variables
        self._extract_config_variables(service_config, service_mappings, base_name, service_name, 'Service')
        
        # Extract task definition variables
        if task_def:
            task_mappings = {
                'family': {'tf_var': 'task_family', 'type': 'string'},
                'cpu': {'tf_var': 'cpu', 'type': 'string'},
                'memory': {'tf_var': 'memory', 'type': 'string'},
                'taskRoleArn': {'tf_var': 'task_role_arn', 'type': 'string'},
                'executionRoleArn': {'tf_var': 'execution_role_arn', 'type': 'string'},
            }
            self._extract_config_variables(task_def, task_mappings, base_name, service_name, 'TaskDef')
        
        # Extract deployment configuration
        deployment_config = service_config.get('deploymentConfiguration', {})
        if deployment_config:
            deploy_mappings = {
                'maximumPercent': {'tf_var': 'maximum_percent', 'type': 'number'},
                'minimumHealthyPercent': {'tf_var': 'minimum_healthy_percent', 'type': 'number'},
            }
            self._extract_config_variables(deployment_config, deploy_mappings, base_name, service_name, 'DeployConfig')
        
        # Extract network configuration
        network_config = service_config.get('networkConfiguration', {}).get('awsvpcConfiguration', {})
        if network_config:
            net_mappings = {
                'subnets': {'tf_var': 'subnets', 'type': 'list(string)'},
                'securityGroups': {'tf_var': 'security_groups', 'type': 'list(string)'},
                'assignPublicIp': {'tf_var': 'assign_public_ip', 'type': 'bool', 'transform': lambda x: x == 'ENABLED'},
            }
            self._extract_config_variables(network_config, net_mappings, base_name, service_name, 'NetworkConfig')
        
        # Extract load balancer configuration
        load_balancers = service_config.get('loadBalancers', [])
        if load_balancers:
            lb_mappings = {
                'targetGroupArn': {'tf_var': 'target_group_arn', 'type': 'string'},
                'containerName': {'tf_var': 'container_name', 'type': 'string'},
                'containerPort': {'tf_var': 'container_port', 'type': 'number'},
            }
            self._extract_config_variables(load_balancers[0], lb_mappings, base_name, service_name, 'LoadBalancer')
        
        # Extract container environment variables
        self._extract_container_env_variables(service_name)
        
        # Calculate autoscaling capacities
        self._calculate_autoscaling_capacities(service_config, base_name, service_name)
        
        # Extract task definition template variables
        self._extract_task_def_template_variables(service_config, task_def, base_name, service_name)
        
        # Extract container-specific variables
        self._extract_container_variables(service_name)

    def _extract_config_variables(self, config: Dict, mappings: Dict, base_name: str, service_name: str, source_prefix: str) -> None:
        """Extract variables from a configuration object using mappings"""
        for aws_field, mapping in mappings.items():
            value = config.get(aws_field)
            if value is not None:
                if 'transform' in mapping:
                    value = mapping['transform'](value)
                
                var_name = f"{base_name}_{mapping['tf_var']}"
                self.all_variables[var_name] = {
                    'value': value,
                    'description': f"{mapping['tf_var'].replace('_', ' ').title()} for {service_name}",
                    'type': mapping['type'],
                    'source': f'{source_prefix}:{aws_field}'
                }
                print(f"    ✓ {var_name} = {value} (from {source_prefix.lower()}.{aws_field})")

    def _extract_container_env_variables(self, service_name: str) -> None:
        """Extract container environment variables"""
        container_env_values = self._extract_container_env_values_direct(service_name)
        
        for env_name, env_value in container_env_values.items():
            tf_var_name = env_name.lower().replace('.', '_')
            self.all_variables[tf_var_name] = {
                'value': env_value,
                'description': f"Environment variable {env_name} (from container definition)",
                'type': 'string',
                'sensitive': 'TOKEN' in env_name.upper() or 'PASSWORD' in env_name.upper(),
                'source': f'ContainerEnv:{env_name}'
            }
            print(f"    ✓ {tf_var_name} = {env_value} (from container env {env_name})")

    def _calculate_autoscaling_capacities(self, service_config: Dict, base_name: str, service_name: str) -> None:
        """Calculate intelligent autoscaling capacities"""
        desired_count = service_config.get('desiredCount', 1)
        has_load_balancer = bool(service_config.get('loadBalancers'))
        
        min_capacity = max(1, desired_count)
        max_capacity = max(3, desired_count * 2)
        if has_load_balancer:
            max_capacity = max(max_capacity, desired_count * 3)
        
        capacities = {
            'min_capacity': min_capacity,
            'max_capacity': max_capacity
        }
        
        for capacity_type, value in capacities.items():
            var_name = f"{base_name}_{capacity_type}"
            self.all_variables[var_name] = {
                'value': value,
                'description': f"{capacity_type.replace('_', ' ').title()} for {service_name} (calculated)",
                'type': 'number',
                'source': f'Calculated:{capacity_type}'
            }
            print(f"    ✓ {var_name} = {value} (calculated)")

    def _extract_task_def_template_variables(self, service_config: Dict, task_def: Dict, base_name: str, service_name: str) -> None:
        """Extract task definition variables for template"""
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

    def _extract_container_variables(self, service_name: str) -> None:
        """Extract variables for each container in a service"""
        containers = self._get_containers_for_service(service_name)
        
        for container_config in containers:
            container_name = container_config.get('name', 'default-container')
            sanitized_container_name = self._sanitize_name(container_name)
            
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
            
            # Extract container-specific environment variables
            container_env = container_config.get('environment', [])
            for env_var in container_env:
                env_name = env_var.get('name', '')
                env_value = env_var.get('value', '')
                
                # Skip common variables (already handled globally)
                if env_name in self.common_env_vars:
                    continue
                
                var_name = env_name.lower().replace('.', '_')
                if var_name not in self.all_variables:
                    self.all_variables[var_name] = {
                        'value': env_value,
                        'description': f"Environment variable {env_name} from container {container_name}",
                        'type': 'string',
                        'source': f'ContainerEnv:{container_name}:{env_name}'
                    }
                    print(f"    ✓ {var_name} = {env_value} (container env)")

    def _get_containers_for_service(self, service_name: str) -> List[Dict]:
        """Get all containers for a service"""
        containers = []
        for key, container_config in self.container_definitions.items():
            if service_name in key and 'container_definition' in key:
                containers.append(container_config)
        return containers

    def _extract_container_env_values_direct(self, service_name: str) -> Dict[str, str]:
        """Extract environment variables directly from container definitions in AWS config"""
        env_values = {}
        
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

    # ==================== CONTAINER TEMPLATE BUILDING ====================
    




    # ==================== TERRAFORM FILE GENERATION ====================
    
    def _get_cluster_template(self) -> str:
        """Read cluster template from tf-template folder"""
        try:
            with open('tf-template/cluster_template.tf', 'r') as f:
                return f.read()
        except FileNotFoundError:
            print("Error: tf-template/cluster_template.tf not found!")
            raise

    def _get_service_template(self) -> str:
        """Read service template from tf-template folder"""
        try:
            with open('tf-template/service_template.tf', 'r') as f:
                return f.read()
        except FileNotFoundError:
            print("Error: tf-template/service_template.tf not found!")
            raise
    
    def generate_cluster_terraform(self) -> None:
        """Generate ECS cluster Terraform file using template"""
        template = self._get_cluster_template()
        cluster_content = template.format(
            cluster_name=self._sanitize_name(self.cluster_name).replace('_', '-')
        )
        
        filename = f"ecs-cluster-{self.cluster_name}.tf"
        with open(f"{self.output_dir}/{filename}", 'w') as f:
            f.write(cluster_content)
        print(f"Generated: {self.output_dir}/{filename}")

    def generate_service_terraform(self) -> None:
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
            
            # Build container variables for templatefile - map to template variable names
            container_variables = f'''
      # Template variable mappings for task definition
      {{
        task_def_family     = var.{sanitized_service_name}_config.task_definition_family,
        taskrolearn         = var.{sanitized_service_name}_config.task_role_arn,
        executionrolearn    = var.{sanitized_service_name}_config.execution_role_arn,
        taskcpu             = var.{sanitized_service_name}_config.task_cpu,
        taskmemory          = var.{sanitized_service_name}_config.task_memory,
        appcontainername    = var.{sanitized_service_name}_config.container_name,
        cluster_name        = var.infrastructure_config.cluster_name,
        awsregion           = var.infrastructure_config.primary_region,
      }}'''
            
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

    def generate_task_definition_json(self) -> None:
        """Generate task definition files per service using original data structure with template variables"""
        for service_name in self.services.keys():
            sanitized_service_name = self._sanitize_name(service_name)
            
            # Find the task definition for this service
            task_def = self.task_definitions.get(service_name)
            if not task_def:
                print(f"Warning: No task definition found for service {service_name}")
                continue
            
            # Get container definitions for this service
            containers = self._get_containers_for_service(service_name)
            
            # Build the task definition preserving ALL original properties
            task_definition = {
                "family": "${task_def_family}",
                "taskRoleArn": "${taskrolearn}",
                "executionRoleArn": "${executionrolearn}",
                "networkMode": task_def.get("networkMode", "awsvpc"),
                "requiresCompatibilities": task_def.get("requiresCompatibilities", ["FARGATE"]),
                "cpu": "${taskcpu}",
                "memory": "${taskmemory}",
                "containerDefinitions": []
            }
            
            # Add volumes if present
            if "volumes" in task_def:
                task_definition["volumes"] = task_def["volumes"]
            
            # Add placement constraints if present
            if "placementConstraints" in task_def:
                task_definition["placementConstraints"] = task_def["placementConstraints"]
            
            # Add requires attributes if present
            if "requiresAttributes" in task_def:
                task_definition["requiresAttributes"] = task_def["requiresAttributes"]
            
            # Add compatibilities if present
            if "compatibilities" in task_def:
                task_definition["compatibilities"] = task_def["compatibilities"]
            
            # Process each container definition
            for container in containers:
                container_def = {
                    "name": "${appcontainername}" if container.get("essential", False) else container.get("name", "container"),
                    "image": container.get("image", "REPLACE_WITH_YOUR_IMAGE_URI"),
                    "cpu": container.get("cpu", 0),
                    "memory": container.get("memory", 512),
                    "essential": container.get("essential", True),
                    "portMappings": container.get("portMappings", []),
                    "environment": [],
                    "logConfiguration": container.get("logConfiguration", {})
                }
                
                # Add entryPoint if it exists
                if container.get("entryPoint"):
                    container_def["entryPoint"] = container["entryPoint"]
                
                # Add command if it exists
                if container.get("command"):
                    container_def["command"] = container["command"]
                
                # Add mountPoints if present
                if "mountPoints" in container:
                    container_def["mountPoints"] = container["mountPoints"]
                
                # Add volumesFrom if present
                if "volumesFrom" in container:
                    container_def["volumesFrom"] = container["volumesFrom"]
                
                # Add linuxParameters if present
                if "linuxParameters" in container:
                    container_def["linuxParameters"] = container["linuxParameters"]
                
                # Add systemControls if present
                if "systemControls" in container:
                    container_def["systemControls"] = container["systemControls"]
                
                # Process environment variables with template substitution
                for env in container.get("environment", []):
                    env_name = env.get("name", "")
                    env_value = env.get("value", "")
                    
                    # Map common environment variables to template variables using correct names
                    if env_name == "DT_LOG":
                        container_def["environment"].append({
                            "name": env_name,
                            "value": "${dt_log}"
                        })
                    elif env_name == "DT_TENANT":
                        container_def["environment"].append({
                            "name": env_name,
                            "value": "${dt_tenant}"
                        })
                    elif env_name == "DT_TENANTTOKEN":
                        container_def["environment"].append({
                            "name": env_name,
                            "value": "${dt_tenanttoken}"
                        })
                    elif env_name == "DT_CONNECTION_POINT":
                        container_def["environment"].append({
                            "name": env_name,
                            "value": "${dt_connection_point}"
                        })
                    elif env_name == "DT_CUSTOM_PROP":
                        container_def["environment"].append({
                            "name": env_name,
                            "value": "${dt_custom_prop}"
                        })
                    elif env_name == "PRIVATE_BUCKET":
                        container_def["environment"].append({
                            "name": env_name,
                            "value": "${private_bucket}"
                        })
                    elif env_name == "spring.profiles.active":
                        container_def["environment"].append({
                            "name": env_name,
                            "value": "${spring_profiles_active}"
                        })
                    elif env_name == "APP_NAME":
                        container_def["environment"].append({
                            "name": env_name,
                            "value": "${app_name}"
                        })
                    elif env_name == "APP_ENV":
                        container_def["environment"].append({
                            "name": env_name,
                            "value": "${app_env}"
                        })
                    elif env_name == "APP_REGION":
                        container_def["environment"].append({
                            "name": env_name,
                            "value": "${app_region}"
                        })
                    elif env_name == "APP_CLUSTER_NAME":
                        container_def["environment"].append({
                            "name": env_name,
                            "value": "${app_cluster_name}"
                        })
                    elif env_name == "TW_CONTAINER_NAME":
                        container_def["environment"].append({
                            "name": env_name,
                            "value": "${appcontainername}"
                        })
                    elif env_name == "REGION":
                        container_def["environment"].append({
                            "name": env_name,
                            "value": "${awsregion}"
                        })
                    elif env_name == "JAVA_TOOL_OPTIONS":
                        container_def["environment"].append({
                            "name": env_name,
                            "value": "${java_tool_options}"
                        })
                    else:
                        # Keep original value for other variables
                        container_def["environment"].append({
                            "name": env_name,
                            "value": env_value
                        })
                
                # Update log configuration with template variables
                if "logConfiguration" in container_def and container_def["logConfiguration"]:
                    log_config = container_def["logConfiguration"]
                    if "options" in log_config:
                        options = log_config["options"]
                        if "awslogs-group" in options:
                            # Use template variables for log group
                            options["awslogs-group"] = "/aws/ecs/${cluster_name}/${appcontainername}"
                        if "awslogs-region" in options:
                            options["awslogs-region"] = "${awsregion}"
                        if "awslogs-stream-prefix" in options:
                            options["awslogs-stream-prefix"] = "${appcontainername}"
                
                task_definition["containerDefinitions"].append(container_def)
            
            # Write the task definition file
            filename = f"ecs_task_def_{sanitized_service_name}.json"
            filepath = f"{self.output_dir}/task_definitions/{filename}"
            
            os.makedirs(f"{self.output_dir}/task_definitions", exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(task_definition, f, indent=2)
            
            print(f"Generated: {filepath}")

    def generate_variables_tf(self) -> None:
        """Generate variables.tf file with object-structured variables"""
        print(f"Generating variables.tf with {len(self.all_variables)} variables...")
        
        # Categorize variables
        infrastructure_vars, dynatrace_vars, environment_vars, container_vars, service_vars = self._categorize_variables()
        
        content = "# Generated Variables File\n"
        content += "# Variables organized with object structure for services\n\n"
        
        # Generate infrastructure config
        if infrastructure_vars:
            content += self._generate_variable_object("infrastructure_config", "Infrastructure configuration object", infrastructure_vars)
        
        # Generate dynatrace config
        if dynatrace_vars:
            content += self._generate_variable_object("dynatrace_config", "Dynatrace monitoring configuration object", dynatrace_vars, sensitive=True)
        
        # Generate application config
        if environment_vars:
            content += self._generate_variable_object("application_config", "Application environment configuration object", environment_vars)
        
        # Generate container config
        if container_vars:
            content += self._generate_variable_object("container_config", "Container configurations object", container_vars)
        
        # Generate service objects
        for service_name in sorted(service_vars.keys()):
            original_service_name = self._get_original_service_name(service_name)
            content += f"# === SERVICE: {original_service_name.upper()} ===\n\n"
            content += self._generate_variable_object(f"{service_name}_config", f"Configuration object for {original_service_name} service", service_vars[service_name])
        
        with open(f"{self.output_dir}/variables.tf", 'w') as f:
            f.write(content)
        print(f"Generated: {self.output_dir}/variables.tf")

    def generate_workspace_vars(self) -> None:
        """Generate workspace_vars.tfvars file with organized object structure"""
        print(f"Generating workspace_vars.tfvars with {len(self.all_variables)} variables...")
        
        # Categorize variables
        infrastructure_vars, dynatrace_vars, environment_vars, container_vars, service_vars = self._categorize_variables()
        
        content = "# Generated Workspace Variables\n"
        content += "# Variables organized by service and global scope\n\n"
        
        # Generate config objects
        if infrastructure_vars:
            content += self._generate_tfvars_object("infrastructure_config", infrastructure_vars)
        
        if dynatrace_vars:
            content += self._generate_tfvars_object("dynatrace_config", dynatrace_vars)
        
        if environment_vars:
            content += self._generate_tfvars_object("application_config", environment_vars)
        
        if container_vars:
            content += self._generate_tfvars_object("container_config", container_vars)
        
        # Generate service objects
        for service_name in sorted(service_vars.keys()):
            original_service_name = self._get_original_service_name(service_name)
            content += f"# === SERVICE: {original_service_name.upper()} ===\n"
            content += self._generate_tfvars_object(f"{service_name}_config", service_vars[service_name])
        
        with open(f"{self.output_dir}/workspace_vars.tfvars", 'w') as f:
            f.write(content)
        print(f"Generated: {self.output_dir}/workspace_vars.tfvars")

    def _categorize_variables(self) -> tuple:
        """Categorize variables by usage type"""
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
            
            # Categorize variables
            service_match = None
            for svc_name in self.services.keys():
                sanitized_svc = self._sanitize_name(svc_name)
                if var_name.startswith(f"{sanitized_svc}_"):
                    service_match = sanitized_svc
                    break
            
            if service_match:
                if service_match not in service_vars:
                    service_vars[service_match] = {}
                clean_var_name = var_name.replace(f"{service_match}_", "")
                service_vars[service_match][clean_var_name] = var_config
            elif source.startswith('Container:'):
                container_vars[var_name] = var_config
            elif var_name.startswith('dt_') or 'dynatrace' in var_name.lower():
                dynatrace_vars[var_name] = var_config
            elif var_name in ['cluster_name', 'primary_region', 'secondary_region', 'environment', 'app_shortname']:
                infrastructure_vars[var_name] = var_config
            elif var_name.startswith('app_') or var_name in ['private_bucket', 'spring_profiles_active', 'java_tool_options', 'sm_ssl', 'tw_container_name']:
                environment_vars[var_name] = var_config
            else:
                infrastructure_vars[var_name] = var_config
        
        return infrastructure_vars, dynatrace_vars, environment_vars, container_vars, service_vars

    def _generate_variable_object(self, var_name: str, description: str, variables: Dict, sensitive: bool = False) -> str:
        """Generate a variable object definition"""
        content = f'variable "{var_name}" {{\n'
        content += f'  description = "{description}"\n'
        content += f'  type = object({{\n'
        
        for name in sorted(variables.keys()):
            var_config = variables[name]
            var_type = var_config.get('type', 'string')
            content += f'    {name} = {var_type}\n'
        
        content += f'  }})\n'
        if sensitive:
            content += f'  sensitive = true\n'
        content += f'}}\n\n'
        
        return content

    def _generate_tfvars_object(self, obj_name: str, variables: Dict) -> str:
        """Generate a tfvars object"""
        content = f'{obj_name} = {{\n'
        
        for var_name in sorted(variables.keys()):
            var_config = variables[var_name]
            value = var_config.get('value')
            var_type = var_config.get('type', 'string')
            
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
                
                content += f'  {var_name} = {formatted_value}\n'
        
        content += '}\n\n'
        return content

    def _get_original_service_name(self, sanitized_name: str) -> str:
        """Get original service name from sanitized name"""
        for orig_name in self.services.keys():
            if self._sanitize_name(orig_name) == sanitized_name:
                return orig_name
        return sanitized_name

    def _generate_mapping_report(self) -> None:
        """Generate detailed mapping report showing source of each variable"""
        print("Generating mapping report...")
        
        report_content = "# AWS to Terraform Variable Mapping Report\n"
        report_content += f"# Generated from: {Path(self.json_file_path).name}\n"
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
            
            for var_name, var_config in sorted(source_groups[source_type]):
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

    # ==================== MAIN GENERATION METHOD ====================
    
    def generate_all(self) -> None:
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
        self._generate_mapping_report()
        
        print(f"\n✅ Generation complete! Files created in '{self.output_dir}' directory")
        print(f"📊 Total variables extracted: {len(self.all_variables)}")


def main():
    """Main entry point"""
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