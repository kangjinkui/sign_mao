import logging


logger = logging.getLogger("sign_map.audit")


def log_radius_check(address: str, count: int) -> None:
    logger.info("radius_check address=%s count=%s", address, count)
