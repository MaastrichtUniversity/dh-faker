import time
import sys

from faker import Faker
from faker_config import *
from base_folder import BaseFolder
from image_folder import ImageFolder
from special_folder import SpecialFolder
from project_collection import create_project, create_drop_zone, ingest_collection
from file_size_folder import FileSizeFolder

log_level = os.environ["LOG_LEVEL"]
logging.basicConfig(level=logging.getLevelName(log_level), format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("Faker")


def filter_verbose(record):
    configuration = FakerConfig().get_config()
    if "verbose" not in configuration:
        return True
    if configuration["verbose"] == "low" and (record.msg.startswith(indent3) or record.msg.startswith(indent2)):
        return False
    elif configuration["verbose"] == "medium" and record.msg.startswith(indent3):
        return False
    return True


logger.addFilter(filter_verbose)


def create_folder_structure(configuration, fake, token):
    BaseFolder(configuration, fake).create_folder_structure(token)
    if configuration["include_images"]:
        ImageFolder(configuration, fake).create_folder_structure(token)
    if configuration["use_diacritics"] or configuration["use_specialchars"]:
        SpecialFolder(configuration, fake).create_folder_structure(token)
    if configuration["include_large_files"] or configuration["include_0byte_files"]:
        FileSizeFolder(configuration, fake).create_folder_structure(token)


def create_collections(configuration, fake, project_id):
    for y in range(configuration["number_of_collections_per_project"]):
        token = create_drop_zone(project_id, configuration, fake)
        create_folder_structure(configuration, fake, token)
        ingest_collection(configuration, token)
        logger.info(f"Sleeping for {configuration['sleep_between_ingests']} seconds")
        time.sleep(configuration["sleep_between_ingests"])


def main():
    # Parse command line arguments
    arguments = FakerConfig().parse_arguments()
    FakerConfig().set_config(arguments)
    configuration = FakerConfig().get_config()
    fake = Faker(configuration["locales"])

    if configuration["existing_project_id"] == "":
        for x in range(configuration["number_of_projects"]):
            project = create_project(configuration, fake)
            logger.info(f"{indent0} Creating new project : {project.project_id}")
            create_collections(configuration, fake, project.project_id)
    else:
        logger.info(f"{indent0} Existing project : {configuration['existing_project_id']}")
        create_collections(configuration, fake, configuration["existing_project_id"])


if __name__ == "__main__":
    main()
