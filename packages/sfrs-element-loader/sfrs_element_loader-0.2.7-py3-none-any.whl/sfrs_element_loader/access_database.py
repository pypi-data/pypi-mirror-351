import os
from dotenv import load_dotenv
from tabulate import tabulate
import inspect
import numpy as np

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .model import (
    Element, Dipole, Quadrupole, Sextupole, Octupole, Steerer, Drift,
    ExperimentalChamber, EmptyDetector, BeamStopper, ProfileGrid,
    HorizontalSlit, PlasticScintillator, RotaryWedgeDegrader,
    SlidableWedgeDegrader, LadderSystemDegrader
)

class ElementLoader:
    def __init__(self, env_path: str = '.env'):
        self._load_env(env_path)
        self._setup_database()
        
    def _load_env(self, env_path: str):
        load_dotenv(env_path)
        self.database_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
        if not self.database_uri:
            raise ValueError("Database URI not found in environment variables")

    def _setup_database(self):
        engine = create_engine(self.database_uri)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def load_element_data(self, element_name: str) -> dict:
        element = self.session.query(Element).filter(Element.element_name == element_name).first()
        if not element:
            raise ValueError(f"Element '{element_name}' not found in the database")

        # Dynamically collect fields for the specific subclass of the element
        model_class = type(element)
        columns = model_class.__mapper__.column_attrs
        data = {col.key: getattr(element, col.key) for col in columns}

        # Optional: Add related objects dynamically (like experimental_chamber)
        # You can inspect relationships using `__mapper__.relationships`
        for rel in model_class.__mapper__.relationships:
            related_obj = getattr(element, rel.key)
            if related_obj:
                data[rel.key] = {
                    col.key: getattr(related_obj, col.key)
                    for col in type(related_obj).__mapper__.column_attrs
                }

        return data
    
    def list_all_optical_elements(self):
        elements = self.session.query(Element).all()
        return [element.element_name for element in elements]

    def list_all_multipletts(self, pprint = False):
        elements = self.session.query(Element).all()
        multiplett_names = [
            element.multiplett_company_name 
            for element in elements 
            if hasattr(element, 'multiplett_company_name') and element.multiplett_company_name is not None
        ]
        multiplett_list = np.unique(multiplett_names)

        if pprint:
            print(multiplett_list)
        return multiplett_list

    def list_magnets_in_multiplett(self, multiplett_name):
        magnets_in_multipletts = []
        positions_in_multiplett = []

        for model_class in [Quadrupole, Sextupole, Octupole, Steerer]:
            magnets = (
                self.session.query(model_class)
                .join(model_class.multiplett)  # join with the multiplett relationship
                .filter(model_class.multiplett.has(plm_comp_manufact_serial=multiplett_name))
                .all()
            )
            for magnet in magnets:
                magnets_in_multipletts.append(magnet)
                positions_in_multiplett.append(magnet.position_in_multiplett)


        sorted_magnets_in_multipletts = [magnets_in_multipletts[i] for i in sorted(range(len(positions_in_multiplett)), key=lambda k: positions_in_multiplett[k])]
        return sorted_magnets_in_multipletts

if __name__ == "__main__":                                                                                                                                                                                                                                                                                                                                                                                              
    loader = ElementLoader(env_path = '../../.env')
    element_name = 'FTF1QT21'  # adjust as needed
    data = loader.list_magnets_in_multiplett('LM20')
    print(data)
    #loader.help()

