class ScraperError(Exception):
    """Base class for scraper errors"""

class ConfigError(ScraperError):
    """Configuration loading errors"""

class FetchError(ScraperError):
    """HTTP fetch failed"""

class EngineError(ScraperError):
    """Unexpected error in engine"""
