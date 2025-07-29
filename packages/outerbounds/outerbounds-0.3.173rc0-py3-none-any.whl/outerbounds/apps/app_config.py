import json
import os
from outerbounds._vendor import yaml
from typing import Dict, Any

CODE_PACKAGE_PREFIX = "mf.obp-apps"

CAPSULE_DEBUG = os.environ.get("OUTERBOUNDS_CAPSULE_DEBUG", False)


def build_config_from_options(options):
    """Build an app configuration from CLI options."""
    config = {}

    # Set basic fields
    for key in ["name", "port", "image", "compute_pools"]:
        if options.get(key):
            config[key] = options[key]

    # Handle list fields
    if options.get("tags"):
        config["tags"] = list(options["tags"])
    if options.get("secrets"):
        config["secrets"] = list(options["secrets"])

    # Build env dict from key-value pairs
    if options.get("envs"):
        env_dict = {}
        for env_item in options["envs"]:
            env_dict.update(env_item)
        config["environment"] = env_dict

    # Handle dependencies (only one type allowed)
    deps = {}
    if options.get("dep_from_task"):
        deps["from_task"] = options["dep_from_task"]
    elif options.get("dep_from_run"):
        deps["from_run"] = options["dep_from_run"]
    elif options.get("dep_from_requirements"):
        deps["from_requirements_file"] = options["dep_from_requirements"]
    elif options.get("dep_from_pyproject"):
        deps["from_pyproject_toml"] = options["dep_from_pyproject"]

    # TODO: [FIX ME]: Get better CLI abstraction for pypi/conda dependencies

    if deps:
        config["dependencies"] = deps

    # Handle resources
    resources = {}
    for key in ["cpu", "memory", "gpu", "storage"]:
        if options.get(key):
            resources[key] = options[key]

    if resources:
        config["resources"] = resources

    # Handle health check options
    health_check = {}
    if options.get("health_check_enabled") is not None:
        health_check["enabled"] = options["health_check_enabled"]
    if options.get("health_check_path"):
        health_check["path"] = options["health_check_path"]
    if options.get("health_check_initial_delay") is not None:
        health_check["initial_delay_seconds"] = options["health_check_initial_delay"]
    if options.get("health_check_period") is not None:
        health_check["period_seconds"] = options["health_check_period"]

    if health_check:
        config["health_check"] = health_check

    # Handle package options
    if options.get("package_src_path") or options.get("package_suffixes"):
        config["package"] = {}
        if options.get("package_src_path"):
            config["package"]["src_path"] = options["package_src_path"]
        if options.get("package_suffixes"):
            config["package"]["suffixes"] = options["package_suffixes"]

    # Handle auth options
    if options.get("auth_type") or options.get("auth_public"):
        config["auth"] = {}
        if options.get("auth_type"):
            config["auth"]["type"] = options["auth_type"]
        if options.get("auth_public"):
            config["auth"]["public"] = options["auth_public"]

    return config


class AppConfigError(Exception):
    """Exception raised when app configuration is invalid."""

    pass


class AppConfig:
    """Class representing an Outerbounds App configuration."""

    def __init__(self, config_dict: Dict[str, Any]):
        """Initialize configuration from a dictionary."""
        self.config = config_dict or {}
        self.schema = self._load_schema()
        self._final_state = {}

    def set_state(self, key, value):
        self._final_state[key] = value
        return self

    def get_state(self, key, default=None):
        return self._final_state.get(key, self.config.get(key, default))

    def dump_state(self):
        x = {k: v for k, v in self.config.items()}
        for k, v in self._final_state.items():
            x[k] = v
        return x

    @staticmethod
    def _load_schema():
        """Load the configuration schema from the YAML file."""
        schema_path = os.path.join(os.path.dirname(__file__), "config_schema.yaml")
        with open(schema_path, "r") as f:
            return yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        return self.config.get(key, default)

    def validate(self) -> None:
        """Validate the configuration against the schema."""
        self._validate_required_fields()
        self._validate_field_types()
        self._validate_field_constraints()

    def set_deploy_defaults(self, packaging_directory: str) -> None:
        """Set default values for fields that are not provided."""
        if not self.config.get("auth"):
            self.config["auth"] = {}
        if not self.config["auth"].get("public"):
            self.config["auth"]["public"] = True
        if not self.config["auth"].get("type"):
            self.config["auth"]["type"] = "SSO"

        if not self.config.get("health_check"):
            self.config["health_check"] = {}
        if not self.config["health_check"].get("enabled"):
            self.config["health_check"]["enabled"] = False

        if not self.config.get("resources"):
            self.config["resources"] = {}
        if not self.config["resources"].get("cpu"):
            self.config["resources"]["cpu"] = 1
        if not self.config["resources"].get("memory"):
            self.config["resources"]["memory"] = "4096Mi"
        if not self.config["resources"].get("disk"):
            self.config["resources"]["disk"] = "20Gi"

    def _validate_required_fields(self) -> None:
        """Validate that all required fields are present."""
        required_fields = self.schema.get("required", [])
        for field in required_fields:
            if field not in self.config:
                raise AppConfigError(
                    f"Required field '{field}' is missing from the configuration."
                )

    def _validate_field_types(self) -> None:
        """Validate that fields have correct types."""
        properties = self.schema.get("properties", {})

        for field, value in self.config.items():
            if field not in properties:
                raise AppConfigError(f"Unknown field '{field}' in configuration.")

            field_schema = properties[field]
            field_type = field_schema.get("type")

            if field_type == "string" and not isinstance(value, str):
                raise AppConfigError(f"Field '{field}' must be a string.")

            elif field_type == "integer" and not isinstance(value, int):
                raise AppConfigError(f"Field '{field}' must be an integer.")

            elif field_type == "boolean" and not isinstance(value, bool):
                raise AppConfigError(f"Field '{field}' must be a boolean.")

            elif field_type == "array" and not isinstance(value, list):
                raise AppConfigError(f"Field '{field}' must be an array.")

            elif field_type == "object" and not isinstance(value, dict):
                raise AppConfigError(f"Field '{field}' must be an object.")

    def _validate_field_constraints(self) -> None:
        """Validate field-specific constraints."""
        properties = self.schema.get("properties", {})

        # Validate name
        if "name" in self.config:
            name = self.config["name"]
            max_length = properties["name"].get("maxLength", 20)
            if len(name) > max_length:
                raise AppConfigError(
                    f"App name '{name}' exceeds maximum length of {max_length} characters."
                )

        # Validate port
        if "port" in self.config:
            port = self.config["port"]
            min_port = properties["port"].get("minimum", 1)
            max_port = properties["port"].get("maximum", 65535)
            if port < min_port or port > max_port:
                raise AppConfigError(
                    f"Port number {port} is outside valid range ({min_port}-{max_port})."
                )

        # Validate dependencies (only one type allowed)
        if "dependencies" in self.config:
            deps = self.config["dependencies"]
            if not isinstance(deps, dict):
                raise AppConfigError("Dependencies must be an object.")

            valid_dep_types = [
                "from_requirements_file",
                "from_pyproject_toml",
            ]

            found_types = [dep_type for dep_type in valid_dep_types if dep_type in deps]

            if len(found_types) > 1:
                raise AppConfigError(
                    f"You can only specify one mode of specifying dependencies. You have specified : {found_types} . Please only set one."
                )

    def to_dict(self) -> Dict[str, Any]:
        """Return the configuration as a dictionary."""
        return self.config

    def to_yaml(self) -> str:
        """Return the configuration as a YAML string."""
        return yaml.dump(self.config, default_flow_style=False)

    def to_json(self) -> str:
        """Return the configuration as a JSON string."""
        return json.dumps(self.config, indent=2)

    @classmethod
    def from_file(cls, file_path: str) -> "AppConfig":
        """Create a configuration from a file."""
        if not os.path.exists(file_path):
            raise AppConfigError(f"Configuration file '{file_path}' does not exist.")

        with open(file_path, "r") as f:
            try:
                config_dict = yaml.safe_load(f)
            except Exception as e:
                raise AppConfigError(f"Failed to parse configuration file: {e}")

        return cls(config_dict)

    def update_from_cli_options(self, options):
        """
        Update configuration from CLI options using the same logic as build_config_from_options.
        This ensures consistent handling of CLI options whether they come from a config file
        or direct CLI input.
        """
        cli_config = build_config_from_options(options)

        # Process each field using allow_union property
        for key, value in cli_config.items():
            if key in self.schema.get("properties", {}):
                self._update_field(key, value)

        return self

    def _update_field(self, field_name, new_value):
        """Update a field based on its allow_union property."""
        properties = self.schema.get("properties", {})

        # Skip if field doesn't exist in schema
        if field_name not in properties:
            return

        field_schema = properties[field_name]
        allow_union = field_schema.get("allow_union", False)

        # If field doesn't exist in config, just set it
        if field_name not in self.config:
            self.config[field_name] = new_value
            return

        # If allow_union is True, merge values based on type
        if allow_union:
            current_value = self.config[field_name]

            if isinstance(current_value, list) and isinstance(new_value, list):
                # For lists, append new items
                self.config[field_name].extend(new_value)
            elif isinstance(current_value, dict) and isinstance(new_value, dict):
                # For dicts, update with new values
                self.config[field_name].update(new_value)
            else:
                # For other types, replace with new value
                self.config[field_name] = new_value
        else:
            raise AppConfigError(
                f"Field '{field_name}' does not allow union. Current value: {self.config[field_name]}, new value: {new_value}"
            )
