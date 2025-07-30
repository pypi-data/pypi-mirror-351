from swarm.extensions.blueprint.blueprint_discovery import discover_blueprints
from swarm.extensions.config.config_loader import load_env_config, validate_env_vars
import argparse

def validate_envvars(blueprint_name=None):
    """
    Validate environment variables for blueprints.

    Args:
        blueprint_name (str, optional): The name of the blueprint to validate.
                                         Validates all blueprints if None.
    """
    # Discover blueprints
    blueprints = discover_blueprints(["blueprints"])

    if blueprint_name:
        blueprint = blueprints.get(blueprint_name)
        if not blueprint:
            print(f"Blueprint '{blueprint_name}' not found.")
            return
        required_vars = blueprint.get("env_vars", [])
        env_vars = load_env_config()
        validation = validate_env_vars(env_vars, required_vars)
        print(f"Validation for '{blueprint_name}': {validation}")
    else:
        # Global validation
        env_vars = load_env_config()
        print("Global Environment Validation:")
        for blueprint_name, blueprint_data in blueprints.items():
            required_vars = blueprint_data.get("env_vars", [])
            validation = validate_env_vars(env_vars, required_vars)
            print(f"Validation for '{blueprint_name}': {validation}")

def main():
    parser = argparse.ArgumentParser(description="Validate environment variables.")
    parser.add_argument("--blueprint", help="Specify a blueprint to validate")
    args = parser.parse_args()

    validate_envvars(blueprint_name=args.blueprint)
