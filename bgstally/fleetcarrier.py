import json
from os.path import join
from typing import List

from bgstally.constants import MaterialsCategory
from bgstally.debug import Debug
from config import config

FILENAME_FCMATERIALS = "FCMaterials.json"

class FleetCarrier:
    def __init__(self, bgstally):
        self.bgstally = bgstally
        self.name:str = None
        self.id:str = None
        self.buying:List = []
        self.selling:List = []

        #self._parse_materials()


    def available(self):
        """
        Return true if there is data available on a Fleet Carrier
        """
        return self.name is not None


    def _parse_materials(self):
        """
        Load and parse the 'FCMaterials.json' file from the player journal folder
        """
        journal_dir = config.get_str('journaldir') or config.default_journal_dir
        if not journal_dir: return

        try:
            with open(join(journal_dir, FILENAME_FCMATERIALS), 'rb') as file:
                data = file.read().strip()
                if not data: return

                json_data = json.loads(data)
                self.name = json_data['CarrierName']
                self.id = json_data['CarrierID']
                materials = json_data['Items']
                materials = sorted(materials, key=lambda d: d['Name_Localised'])
                for material in materials:
                    if material['Stock'] > 0:
                        self.selling.append(material)
                    elif material['Demand'] > 0:
                        self.buying.append(material)


        except Exception as e:
            Debug.logger.info(f"Unable to load FCMaterials.json from the player journal folder (No Fleet Carrier?)")


    def _get_materials(self, category: MaterialsCategory):
        """
        Get the materials being either bought or sold
        """
        match category:
            case MaterialsCategory.SELLING: return self.selling
            case MaterialsCategory.BUYING: return self.buying


    def get_materials_plaintext(self, category: MaterialsCategory = None):
        """
        Return a list of formatted materials for posting to Discord
        """
        result:str = ""
        materials:List = []

        if category == MaterialsCategory.SELLING:
            materials = self.selling
            key = 'Stock'
        elif category == MaterialsCategory.BUYING:
            materials = self.buying
            key = 'Demand'

        for material in materials:
            if material[key] > 0: result += f"{material['Name_Localised']} x {material[key]} @ {material['Price']}\n"

        return result
