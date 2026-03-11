# This file is part of the research_and_analyst package.
# It serves as the initializer for the logger module, allowing for easy imports of logging functionalities across
from .custom_logger import CustomLogger

# Initialize a global logger instance for the entire project
GLOBAL_LOGGER = CustomLogger().get_logger("research_and_analyst")