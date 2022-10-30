import json
from os.path import join

from config import config

from bgstally.debug import Debug


class FleetCarrier:
    def __init__(self, bgstally):
        self.bgstally = bgstally
        self.name = ""
        self.id = ""
        self.materials = {}

        self._parse_materials()


    def _parse_materials(self):
        """
        Load and parse the 'FCMaterials.json' file from the player journal folder
        """
        journal_dir = config.get_str('journaldir') or config.default_journal_dir
        if not journal_dir: return

        try:
            with open(join(journal_dir, 'FCMaterials.json'), 'rb') as file:
                data = file.read().strip()
                if not data: return

                json_data = json.loads(data)
                self.name = json_data['CarrierName']
                self.id = json_data['CarrierID']
                self.materials = json_data['Items']
                self.materials = sorted(self.materials, key=lambda d: d['Name_Localised'])

        except Exception as e:
            Debug.logger.error(f"Unable to load FCMaterials.json from the player journal folder", exc_info=e)


    def get_materials_plaintext(self):
        """
        Return a list of formatted materials for posting to Discord
        """
        selling = ""
        buying = ""

        for material in self.materials:
            if material["Stock"] > 0:
                selling += f" {material['Name_Localised']} x {material['Stock']} @ {material['Price']}\n"
            else:
                buying += f" {material['Name_Localised']} x {material['Demand']} @ {material['Price']}\n"

        return f"```css\nSelling:\n{selling}\nBuying\n{buying}```"
