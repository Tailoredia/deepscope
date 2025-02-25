# Configuration

The `config` directory contains configuration files and settings for the application.

## constants.py

The `constants.py` file defines various constants and configuration settings used throughout the application. It includes:
- `DATA_HOME`: The base directory for data files, defaulting to `"./data"` if not set in the environment variables.
- `BASE_DIR`: The base directory of the application, determined using the `__file__` magic variable.
- Constants for different directories and their corresponding URL prefixes, such as `OUTPUT`, `STATIC`, `JSONS`, `FIGS`, `DEEPSCOPE`, etc.
- `DIRECTORY_CONFIG`: A dictionary mapping directory names to their configuration settings, including paths, URL prefixes, authentication requirements, descriptions, and mount names.

These constants provide a centralized place to define and manage the application's directory structure, URL prefixes, and related configurations. They are used in various parts of the application to ensure consistent paths and URLs.

## loggers.py

The `loggers.py` file contains utility functions for configuring and retrieving loggers. It includes:
- `get_and_set_logger`: A function that retrieves or creates a logger with the specified name and log level. It sets up the basic logging configuration and returns the logger instance.

This file provides a convenient way to obtain pre-configured loggers for different modules in the application. It ensures consistent logging setup and allows for easy customization of log levels and formatting.

### Usage

The configuration files in this directory are used to centralize and manage various settings and constants used throughout the application. Here are some examples of how they are used:

- The `constants.py` file is imported in various modules to access the defined constants for directory paths, URL prefixes, and configuration settings. For example, `output_paths.py` uses the `OUTPUT_DIR`, `OUTPUT_FIGS`, and `OUTPUT_JSONS` constants to construct file paths for saving output files.

- The `main.py` file in the `web` directory uses the `DIRECTORY_CONFIG` constant to mount static directories and configure URL prefixes based on the defined settings.

- The `loggers.py` file is imported in different modules to obtain pre-configured logger instances using the `get_and_set_logger` function. This ensures consistent logging setup across the application.

To customize the application's configuration, you can modify the values in the `constants.py` file. For example, you can change the `DATA_HOME` constant to specify a different base directory for data files, or update the `DIRECTORY_CONFIG` to add new directories or modify their settings.

When adding new features or modules to the application, you may need to define new constants or configuration settings in the `constants.py` file to maintain a centralized configuration management.

Remember to keep sensitive information, such as database credentials or API keys, out of the configuration files and instead use environment variables or separate configuration files that are not version-controlled.

Overall, the configuration files in this directory provide a clean and organized way to manage the application's settings, making it easier to configure and maintain the codebase.