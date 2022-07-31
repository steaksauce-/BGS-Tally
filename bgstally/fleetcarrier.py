import json
from os.path import join
import logging

from config import config


class FleetCarrier:
    def __init__(self, logger):
        self.name = ""
        self.id = ""
        self.materials = {}
        self.logger = logger

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

        except Exception as e:
            self.logger.error(f"Unable to fetch latest tick from elitebgs.app", exc_info=e)


    def get_formatted_materials(self):
        result = f"```css\nMaterials List for Carrier {self.name}\n\n"
        selling = ""
        buying = ""
        for material in self.materials:
            if material["Stock"] > 0:
                selling += f" {material['Name_Localised']} x {material['Stock']} @ {material['Price']}\n"
            else:
                buying += f" {material['Name_Localised']} x {material['Demand']} @ {material['Price']}\n"

        result += f"Selling:\n{selling}\nBuying\n{buying}```"
        return result
