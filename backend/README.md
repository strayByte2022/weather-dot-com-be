# Weather.com Backend

This README provides instructions for setting up and running the backend locally.

## Local Development Setup

### Setting up a Virtual Environment

First, create a virtual environment:

```bash
py -m venv venv
```

Then activate the virtual environment:

For Windows:

```cmd
venv\Scripts\activate
```

For POSIX (Linux/Mac):

```bash
source venv/bin/activate
```

### Installing Dependencies

Install the required packages:

```bash
pip install -e .
```

### Running the Backend

To start the backend API:

```bash
start-api
```

The backend will be running on http://localhost:8000

### Subscribe to WS

```bash
ws://0.0.0.0:8000/ws/weather/average
```

## Dockerization

_This section is a placeholder for future Docker setup instructions._
