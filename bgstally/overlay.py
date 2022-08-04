import plug

try:
    from EDMCOverlay import edmcoverlay
except ImportError:
    edmcoverlay = None


class Overlay:
    def __init__(self, logger):
        self.edmcoverlay = None
        self.logger = logger


    def check_overlay(self):
        """
        Ensure overlay is running and available
        """
        if edmcoverlay:
            try:
                self.edmcoverlay = edmcoverlay.Overlay()
                self.display_message("", "BGSTally Ready")
            except Exception as e:
                self.edmcoverlay = None
                self.logger.error(f"EDMCOverlay is not running", exc_info=e)
                plug.show_error(f"BGS-Tally: EDMCOverlay is not running")
                return False
            else:
                self.logger.info(f"EDMCOverlay is running")
                return True
        else:
            # Couldn't load edmcoverlay python lib, the plugin probably isn't installed
            self.logger.error(f"EDMCOverlay plugin is not installed")
            plug.show_error(f"BGS-Tally: EDMCOverlay plugin is not installed")
            return False


    def display_message(self, position, message):
        if self.edmcoverlay == None: return
        self.edmcoverlay.send_shape("bgstallyrect", "rect", "red", "blue", 20, 180, 100, 25, ttl=10)
        self.edmcoverlay.send_message("bgstallystart", message, "yellow", 30, 185, ttl=10)