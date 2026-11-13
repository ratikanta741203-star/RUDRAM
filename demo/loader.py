import os
import json
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

DEMO_DATASET_PATH = os.path.join(os.path.dirname(__file__), 'demo_dataset.json')

@lru_cache(maxsize=1)
def load_central_demo_dataset():
    """
    Loads and caches the centralized RUDRAM demo dataset from JSON.
    Returns python dictionary structure.
    """
    if os.path.exists(DEMO_DATASET_PATH):
        try:
            with open(DEMO_DATASET_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info("Successfully loaded RUDRAM Central Demo Dataset.")
                return data
        except Exception as e:
            logger.error(f"Error reading demo_dataset.json: {e}")
    else:
        logger.warning(f"Demo dataset file not found at {DEMO_DATASET_PATH}")
    return {}

def get_demo_data_by_key(key, default=None):
    """
    Retrieves a specific slice from the centralized demo dataset.
    """
    dataset = load_central_demo_dataset()
    return dataset.get(key, default if default is not None else {})

def is_global_demo_mode():
    """
    Checks if global DEMO_MODE is ON.
    """
    try:
        from apps.core.models import get_global_demo_mode
        return get_global_demo_mode()
    except Exception:
        from django.conf import settings
        return getattr(settings, 'DEMO_MODE', False)
