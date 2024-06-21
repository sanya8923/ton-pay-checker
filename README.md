# TON Pay Service

TON Pay Service is a service for processing payments in the TON network. This project is now packaged in Docker for simplified deployment and management.

## Installation and Running

1. Install Docker on your machine. Instructions for installing Docker can be found on the [official Docker website](https://docs.docker.com/get-docker/).

2. Clone the project repository:

```bash
git clone https://github.com/yourusername/ton-pay-service.git
```

3. Navigate to the project directory:

```bash
cd ton-pay-service
```

4. Build the Docker image:

```bash
docker build -t ton-pay-service .
```

5. Run the Docker container:

```bash
docker run -p 5002:5002 ton-pay-service
```

The application is now accessible at `localhost:5002`.

## Configuration

For service configuration, use the `.env` file. An example configuration can be found in the `.env.example` file.

## Working with the Service

The service provides the following HTTP endpoints:

- `GET /transactions`: Get transaction information.
- `POST /create_order`: Create a new order.
