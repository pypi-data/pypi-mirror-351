"""
Main entry point for the model serving application.
This serves as a wrapper around TorchServe for our fraud detection model.
"""

import argparse
import logging
import os
import signal
import subprocess
import sys
import time

from prometheus_client import Counter, Gauge, Summary, start_http_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Prometheus metrics
TORCHSERVE_UP = Gauge("torchserve_up", "Whether TorchServe is up and running")
MODEL_LOAD_TIME = Summary("model_load_seconds", "Time to load the model")
REQUESTS_TOTAL = Counter("requests_total", "Total number of requests processed")

# Environment variables for configurable edge types
ACTIVE_EDGES = os.getenv("ACTIVE_EDGES", "card_ip")
logger.info(f"Starting model server with active edge types: {ACTIVE_EDGES}")


def start_torchserve(model_store, models, port=8080, metrics_port=8081):
    """
    Start TorchServe process with the specified configuration.

    Args:
        model_store: Path to model store directory
        models: List of models to load
        port: Port for inference API
        metrics_port: Port for metrics API

    Returns:
        TorchServe process
    """
    start_time = time.time()

    # Build command for launching TorchServe
    cmd = [
        "torchserve",
        "--start",
        "--ncs",  # No config snapshot (use command line args)
        f"--model-store={model_store}",
        f"--models={models}",
        f"--inference-address=0.0.0.0:{port}",
        f"--management-address=0.0.0.0:{port + 1}",
        f"--metrics-address=0.0.0.0:{metrics_port}",
        "--foreground",  # Run in foreground
        "--log-config=",  # Empty log config to use default
        f"--ts-config={{'environment': {{'ACTIVE_EDGES': '{ACTIVE_EDGES}'}}}}",
    ]

    logger.info(f"Starting TorchServe with command: {' '.join(cmd)}")

    # Start TorchServe process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    )

    # Wait for model to load
    loaded = False
    while process.poll() is None:
        line = process.stdout.readline()
        print(line, end="")
        if 'Model "fraud_detection" loaded successfully' in line:
            loaded = True
            break

    # Update metrics
    if loaded:
        TORCHSERVE_UP.set(1)
        MODEL_LOAD_TIME.observe(time.time() - start_time)
        logger.info(
            f"TorchServe started successfully in {time.time() - start_time:.2f}s"
        )
    else:
        TORCHSERVE_UP.set(0)
        logger.error("Failed to start TorchServe")

    return process


def handle_sigterm(signum, _):
    """Handle SIGTERM gracefully."""
    logger.info("Received SIGTERM signal, initiating shutdown")
    if torchserve_process:
        logger.info("Stopping TorchServe...")
        torchserve_process.terminate()
        torchserve_process.wait(timeout=10)
    sys.exit(0)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Start the model serving application")
    parser.add_argument(
        "--model-store",
        default="/var/model-store",
        help="Path to model store directory",
    )
    parser.add_argument(
        "--models", default="fraud_detection=fraud_detection.mar", help="Models to load"
    )
    parser.add_argument("--port", type=int, default=8080, help="Port for inference API")
    parser.add_argument(
        "--metrics-port", type=int, default=8081, help="Port for metrics API"
    )
    parser.add_argument(
        "--prometheus-port", type=int, default=9090, help="Port for Prometheus metrics"
    )
    args = parser.parse_args()

    # Start Prometheus metrics server
    start_http_server(args.prometheus_port)
    logger.info(f"Started Prometheus metrics server on port {args.prometheus_port}")

    # Register signal handlers
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)

    # Start TorchServe
    global torchserve_process
    torchserve_process = start_torchserve(
        args.model_store, args.models, args.port, args.metrics_port
    )

    # Keep running until TorchServe exits
    while torchserve_process.poll() is None:
        line = torchserve_process.stdout.readline()
        if line:
            print(line, end="")

    # TorchServe exited
    exit_code = torchserve_process.returncode
    logger.info(f"TorchServe exited with code {exit_code}")
    TORCHSERVE_UP.set(0)

    return exit_code


if __name__ == "__main__":
    torchserve_process = None
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Unhandled exception in main: {e}", exc_info=True)
        sys.exit(1)
