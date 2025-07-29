import os
from pathlib import Path

from t_bug_catcher import attach_file_to_exception, report_error
from PIL import ImageGrab

from t_desktop.config import CONFIG
from t_desktop.utils.logger import logger


def capture_screenshot(file_name: str, output: str = CONFIG.DIRECTORIES.SCREENSHOTS) -> str | None:
    """Take a screenshot and save it to the specified directory.

    Args:
        file_name (str): The name of the screenshot file.
        output (str): The directory where the screenshot will be saved.
    """
    Path(output).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(output, file_name)

    try:
        # Try to capture the screenshot
        screenshot = ImageGrab.grab()
        screenshot.save(file_path)
        logger.info(f"Screenshot saved to {file_path}")
        return file_path
    except Exception as error:
        try:
            from RPA.Desktop import Desktop as RpaDesktop

            logger.warning(f"Failed to capture screenshot using ImageGrab. Cause: {error}")
            desktop = RpaDesktop()
            desktop.take_screenshot(file_path)
            logger.info(f"Screenshot saved to {file_path}")
            attach_file_to_exception(error, file_path)
            return file_path
        except ImportError as e:
            logger.warning("rpaframework not installed")
            report_error(e)
        report_error(error)
