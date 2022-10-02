import plug

from bgstally.debug import Debug

try:
    from EDMCOverlay import edmcoverlay
except ImportError:
    edmcoverlay = None


class Overlay:
    """
    Handles the game overlay. Provides purpose-agnostic functions to display information and data in frames on screen.
    """
    def __init__(self):
        self.edmcoverlay = None
        self._check_overlay()


    def display_message(self, frame_name: str, message: str):
        if self.edmcoverlay == None: return
        fi = self._get_frame_info(frame_name)
        self.edmcoverlay.send_shape(f"bgstally-frame-{frame_name}", "rect", fi["border_colour"], fi["fill_colour"], fi["x"], fi["y"], fi["w"], fi["h"], ttl=fi["ttl"])
        self.edmcoverlay.send_message(f"bgstally-msg-{frame_name}", message, fi["text_colour"], fi["x"] + 10, fi["y"] + 5, ttl=fi["ttl"])


    def _check_overlay(self):
        """
        Ensure overlay is running and available
        """
        if edmcoverlay:
            try:
                self.edmcoverlay = edmcoverlay.Overlay()
                self.display_message("info", "BGSTally Ready")
            except Exception as e:
                self.edmcoverlay = None
                Debug.logger.warning(f"EDMCOverlay is not running, disabling overlay features")
                plug.show_error(f"BGS-Tally: EDMCOverlay is not running, disabling overlay features")
                return False
            else:
                Debug.logger.info(f"EDMCOverlay is running, enabling overlay features")
                return True
        else:
            # Couldn't load edmcoverlay python lib, the plugin probably isn't installed
            Debug.logger.error(f"EDMCOverlay plugin is not installed")
            plug.show_error(f"BGS-Tally: EDMCOverlay plugin is not installed")
            return False


    def _get_frame_info(self, frame: str):
        if frame == "info":
            return {"border_colour": "red", "fill_colour": "blue", "text_colour": "yellow", "x": 20, "y": 180, "w": 100, "h": 25, "ttl": 30}
        elif frame == "tick":
            return {"border_colour": "#ffffff", "fill_colour": "#ffffff", "text_colour": "#010101", "x": 1000, "y": 180, "w": 200, "h": 25, "ttl": 30}
        elif frame == "tickwarn":
            return {"border_colour": "yellow", "fill_colour": "red", "text_colour": "#ffffff", "x": 1000, "y": 180, "w": 200, "h": 25, "ttl": 30}
