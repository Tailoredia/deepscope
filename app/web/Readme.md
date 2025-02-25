
# Web Module

The Web module provides the necessary components for building the web-based user interface and handling user interactions for the data visualization application. It includes the main application entry point, URL routing configuration, and view templates.

## main.py

The `main.py` file serves as the main entry point for the web application. It sets up the FastAPI application, configures static file serving, and defines the root URL handler. It also includes the necessary URL routers for different parts of the application.

## viz.py

The `viz.py` file contains the route handlers and logic for the visualization pages. It defines the endpoints for rendering the t-SNE visualizations based on the provided data file paths. It uses Jinja2 templates to render the HTML pages with the necessary data and configuration.

## browser.py

The `browser.py` file implements the file browsing functionality for the application. It defines the route handlers for browsing and navigating through directories, displaying file and directory listings, and handling file uploads. It integrates with the authentication system to ensure proper access control.

## templates/

The `templates/` directory contains the Jinja2 HTML templates used for rendering the web pages. It includes templates for the visualization pages, file browser, and other common UI components. The templates are populated with data from the backend and provide the structure and layout for the user interface.

### Use Cases

- Building a web-based data exploration and visualization platform
- Creating interactive dashboards for monitoring key metrics and trends
- Developing a visual analytics tool for business intelligence
- Providing a user-friendly interface for non-technical users to explore and analyze data
- Integrating visualizations into existing web applications or frameworks

The Web module forms the foundation of the user-facing portion of the data visualization application. It leverages the power of FastAPI and Jinja2 templating to create dynamic and interactive web pages that allow users to explore and gain insights from their data. By providing a intuitive and visually appealing interface, the Web module enables users to effectively communicate their findings and make data-driven decisions.
