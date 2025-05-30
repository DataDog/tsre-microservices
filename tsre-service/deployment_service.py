import os
import click
import subprocess
import time
import sys
from datetime import datetime, timezone
import yaml

from logger import getJSONLogger

logger = getJSONLogger('deployment-service')

FAILURE_WAIT_TIME = 120

@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = False
    logger.info(f"{os.path.basename(__file__)} started")

def get_version_from_compose(filename):
    try:
        with open(filename, 'r') as file:
            compose_data = yaml.safe_load(file)
            if 'services' in compose_data and 'paymentservice' in compose_data['services']:
                # Get DD_VERSION from environment variables
                env_vars = compose_data['services']['paymentservice'].get('environment', [])
                for env_var in env_vars:
                    if env_var.startswith('DD_VERSION='):
                        return env_var.split('=')[1]
    except (yaml.YAMLError, FileNotFoundError) as e:
        logger.error(f"Error loading docker-compose file: {e}")
    return None

def deploy_service(file_path, service_name):
    # Start only the specified service with the new compose file
    command = ["docker", "compose", "-f", file_path, "up", "-d", service_name]
    start_time = datetime.now(timezone.utc)
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logger.info(f"Started {service_name} from {file_path}: {result.stdout}")
        time.sleep(5)  # Give service time to start
        
        # Check if the service is running
        command = ["docker", "compose", "-f", file_path, "ps", service_name]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        
        if "Up" in result.stdout:
            logger.info(f"{service_name} is running...")
            end_time = datetime.now(timezone.utc)
            return start_time, end_time, True
        else:
            logger.warning(f"Service not running: {result.stdout}")
            end_time = datetime.now(timezone.utc)
            return start_time, end_time, False
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start {service_name} from {file_path}: {e}")
        return None, None, False

@cli.command(name='start_service')
@click.option('--debug/--no-debug', default=False)
@click.option('--service-name', '-s', type=click.STRING, required=True, help="Service Name (eg. paymentservice)")
@click.option('--version-a', '-a', type=click.Path(exists=True), help="PATH to Version A docker-compose file")
@click.option('--version-b', '-b', type=click.Path(exists=True), help="PATH to Version B docker-compose file")
@click.option('--version-a-interval', type=click.INT, default=420, help="Time to wait after deploying version A (in seconds)", show_default=True)
@click.option('--version-b-interval', type=click.INT, default=540, help="Time to wait after deploying version B (in seconds)", show_default=True)
@click.option('--retry-limit', '-r', type=click.INT, default=5, help="Number of deployment retry attempts before exiting", show_default=True)
@click.pass_context
def start_service(ctx, debug, service_name, version_a, version_b, version_a_interval, version_b_interval, retry_limit):
    logger.info(f"Starting deployment service with versions A and B...")
    
    # Get versions from docker-compose files
    version_a_tag = get_version_from_compose(version_a)
    version_b_tag = get_version_from_compose(version_b)
    logger.info(f"Version A: {version_a_tag}, Version B: {version_b_tag}")
    
    # Check current running version
    try:
        command = ["docker", "compose", "ps", service_name]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logger.info(f"Current running version: {result.stdout}")
    except subprocess.CalledProcessError:
        logger.info("No services currently running")
    
    nbr_version_a_try, nbr_version_b_try = 0, 0
    
    while True:
        # Deploy version A
        logger.info(f"Deploying version A ({version_a_tag})...")
        _, _, deployed = deploy_service(version_a, service_name)
        if deployed:
            nbr_version_a_try = 0
            logger.info(f"Version A ({version_a_tag}) deployed. Running for {version_a_interval} seconds...")
            time.sleep(version_a_interval)
        else:
            nbr_version_a_try += 1
            logger.error(f"Failed to deploy version A ({version_a_tag}) - Attempt {nbr_version_a_try}")
            if nbr_version_a_try >= retry_limit:
                logger.error(f"Failed to deploy version A {retry_limit} times. Exiting...")
                break
            time.sleep(FAILURE_WAIT_TIME)
            continue

        # Deploy version B
        logger.info(f"Deploying version B ({version_b_tag})...")
        _, _, deployed = deploy_service(version_b, service_name)
        if deployed:
            nbr_version_b_try = 0
            logger.info(f"Version B ({version_b_tag}) deployed. Running for {version_b_interval} seconds...")
            time.sleep(version_b_interval)
        else:
            nbr_version_b_try += 1
            logger.error(f"Failed to deploy version B ({version_b_tag}) - Attempt {nbr_version_b_try}")
            if nbr_version_b_try >= retry_limit:
                logger.error(f"Failed to deploy version B {retry_limit} times. Exiting...")
                break
            time.sleep(FAILURE_WAIT_TIME)
            continue

if __name__ == "__main__":
    cli(obj={})