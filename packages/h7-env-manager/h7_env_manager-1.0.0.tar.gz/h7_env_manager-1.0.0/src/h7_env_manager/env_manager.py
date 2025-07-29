import os
from h7_file_finder import find_env_file

# Track whether dotenv has been loaded
_dotenv_loaded = False


class EnvManager:
    """
    Manages environment variables for the application.
    Ensures .env file is loaded only once across the application.
    """

    @classmethod
    def _ensure_dotenv_loaded(cls):
        """Ensure .env file is loaded only once"""
        global _dotenv_loaded

        if not _dotenv_loaded:
            from dotenv.main import load_dotenv
            dotenv_path = find_env_file()
            load_dotenv(dotenv_path, override=True)
            _dotenv_loaded = True

    @classmethod
    def get_required_env_var(cls, key: str) -> str:
        """
        Get a required environment variable.
        
        Args:
            key: The name of the environment variable
            
        Returns:
            The value of the environment variable
            
        Raises:
            ValueError: If the environment variable is not found
        """
        cls._ensure_dotenv_loaded()
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Environment variable '{key}' not found")
        return value

    @classmethod
    def get_optional_env_var(cls, key: str, default: str = None) -> str:
        """
        Get an optional environment variable with a default value.
        
        Args:
            key: The name of the environment variable
            default: The default value to return if the variable is not found
            
        Returns:
            The value of the environment variable or the default value
        """
        cls._ensure_dotenv_loaded()
        return os.getenv(key, default)

    @classmethod
    def build_dataset_url(cls, dataset_id):
        """
        Build a dataset URL from a template and dataset ID.
        
        Args:
            dataset_id: The ID of the dataset
            
        Returns:
            The complete dataset URL
            
        Raises:
            ValueError: If dataset_id is None or empty
        """
        if not dataset_id:
            raise ValueError("dataset_id cannot be None or empty")
        url_template = cls.get_required_env_var('CMS_DATASET_URL_TEMPLATE')
        return url_template.format(DATASET=dataset_id)

    @classmethod
    def build_resource_url(cls, resource_id):
        """
        Build a resource URL from a template and resource ID.
        
        Args:
            resource_id: The ID of the resource
            
        Returns:
            The complete resource URL
            
        Raises:
            ValueError: If resource_id is None or empty
        """
        if not resource_id:
            raise ValueError("resource_id cannot be None or empty")
        url_template = cls.get_required_env_var('CMS_RESOURCE_URL_TEMPLATE')
        return url_template.format(RESOURCE_ID=resource_id)

    @classmethod
    def get_url_provider_info(cls):
        """Get the URL for provider information"""
        dataset_id = cls.get_required_env_var("DATASET_DOWNLOAD_URL_PROVIDER_INFO")
        return cls.build_dataset_url(dataset_id)

    @classmethod
    def get_url_resource_health_deficiency(cls):
        """Get the URL for health deficiency resource"""
        resource_id = cls.get_required_env_var("CMS_RESOURCE_HEALTH_DEFICIENCY")
        return cls.build_resource_url(resource_id)

    @classmethod
    def get_url_resource_fire_deficiency(cls):
        """Get the URL for fire deficiency resource"""
        resource_id = cls.get_required_env_var("CMS_RESOURCE_FIRE_DEFICIENCY")
        return cls.build_resource_url(resource_id)
