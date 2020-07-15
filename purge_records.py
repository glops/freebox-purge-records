import argparse
from argparse import RawTextHelpFormatter
import logging
from logging.handlers import RotatingFileHandler
from PurgeRecords import PurgeRecords
from pathlib import Path
import os


if __name__ == "__main__":
    scriptPath = Path(os.path.dirname(os.path.realpath(__file__)))

    logPath = scriptPath / "log"

    logPath.mkdir(exist_ok=True)
    logging.basicConfig(
        handlers=[
            RotatingFileHandler(logPath / "purgeRecords.log", maxBytes=1000000, backupCount=10),
            logging.StreamHandler(),
        ],
        level=logging.DEBUG,
        # format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # Set logging level for urllib3 to warning
    loggerUrllib3 = logging.getLogger("urllib3")
    loggerUrllib3.setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.description = (
        ""
        "Script pour automatiser la suppression des enregistrements sur la Freebox.\n"
        "1/ Ajouter un nom secondaire à l'enregistrement de la forme : 'suppression : n jours|semaines|mois'\n"
        "   Le nom secondaire peut-être ajouter dans le générateur, ou directement sur l'enregistrement\n"
        "2/ Exécuter ce script. La 1ère fois, appuyer sur le bouton OK sur l'écran de la Freebox\n"
        "   pour autoriser l'application."
    )
    parser.add_argument(
        "--simulation", help="Mode simulation, ne supprime pas les fichiers", action="store_true",
    )
    args = parser.parse_args()
    if args.simulation:
        logging.info(f"Simulation mode")
    purgeRecords = PurgeRecords(args.simulation, scriptPath)
    purgeRecords.getRecords()
