import logging


def get_logger(name):
    """
    Create and return a logger with the given name

    Args:
        name: Name for the logger

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure handlers if they haven't been added yet
    if not logger.handlers:
        # Configure logging level
        logger.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)

        # Prevent propagation to root logger to avoid duplicate logs
        logger.propagate = False

    return logger
