import os


def get_default_exchange_name():
    return f"{os.getenv('RABBIT_SERIES_PREFIX') or 'fast'}.{os.getenv('RABBIT_APP_PREFIX') or os.getenv('APP_CODE') or 'default'}"


def get_default_routing_key(task_type: str):
    if not task_type:
        raise ValueError(f'task_type must not none: task_type={task_type}')

    return f"{os.getenv('RABBIT_SERIES_PREFIX') or 'fast'}.{os.getenv('RABBIT_APP_PREFIX') or os.getenv('APP_CODE') or 'default'}.{task_type}"


def get_default_queue_name(task_type: str):
    if not task_type:
        raise ValueError(f'task_type must not none: task_type={task_type}')

    return f"{os.getenv('RABBIT_SERIES_PREFIX') or 'fast'}.{os.getenv('RABBIT_APP_PREFIX') or os.getenv('APP_CODE') or 'default'}.{task_type}"
