import logging
from logging.handlers import RotatingFileHandler
import os
import sys


class WindowsConsoleHandler(logging.StreamHandler):
    """Handler personnalisé pour la console Windows"""

    def __init__(self):
        if sys.platform == "win32":
            # Force l'utilisation de utf-8 sur Windows
            import ctypes

            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        super().__init__(sys.stdout)

    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            # Remplacer les caractères problématiques
            msg = msg.replace("≠", "!=")
            stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


def setup_logger(name: str) -> logging.Logger:
    """Configure et retourne un logger avec support UTF-8"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Éviter les logs en double
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formateur avec correction de 'levelname'
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler pour la console avec support Windows
    console_handler = WindowsConsoleHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler pour le fichier avec encodage UTF-8
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    file_handler = RotatingFileHandler(
        f"{log_dir}/lorcana_price.log",
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
