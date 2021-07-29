from irodsrulewrapper.rule import RuleManager
from faker import Faker
import os
import json
import time
import configparser
import random
import sys
import logging

log_level = os.environ['LOG_LEVEL']
logging.basicConfig(level=logging.getLevelName(log_level), format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("Faker")

indent0 = "* "
indent1 = "-\t"
indent2 = "--\t\t"
indent3 = "---\t\t\t"

configuration = {}
fake = Faker()

# Note: A Linux file name cannot contain /
# Note: A Windows file name cannot contain \ / : * ? " < > |
# Note: A MacOS file name cannot contain / :
specialchar_elements = (
' ', '`', '~', '!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '+', '=', '{', '}', '[', ']', ';', '\'', ',', '.',
'€')
diacritic_elements = (
' ', 'Á', 'á', 'À', 'à', 'Â', 'â', 'Ã', 'ã', 'Ä', 'ä', 'Å', 'å', 'Æ', 'æ', 'Ç', 'ç', 'Œ', 'œ', 'Ø', 'ø')


def filter_verbose(record):
    if "verbose" not in configuration:
        return True
    if configuration["verbose"] == 'low' and (record.msg.startswith(indent3) or record.msg.startswith(indent2)):
        return False
    elif configuration["verbose"] == 'medium' and record.msg.startswith(indent3):
        return False
    return True


logging.getLogger('Faker').addFilter(filter_verbose)


def read_config_file(file):
    local_configuration = {}
    config = configparser.ConfigParser()
    config.read(file)
    if len(config.sections()) == 0:
        raise ValueError("Failed to open config file")

    local_configuration["locales"] = json.loads(config.get('GENERAL', 'Locales', fallback='["nl_NL"]'))
    local_configuration["sleep_between_ingests"] = config.getint('GENERAL', 'SleepBetweenIngests', fallback=5)
    local_configuration["number_of_contacts"] = config.getint('GENERAL', 'NumberOfContacts', fallback=3)
    local_configuration["verbose"] = config.get('GENERAL', 'Verbose', fallback="low")

    local_configuration["user_name"] = config.get('USER', 'UserName', fallback="jmelius")
    local_configuration["user_email"] = config.get('USER', 'UserEmail', fallback="fake-email@maastrichtuniversity.nl")
    local_configuration["data_steward"] = config.get('USER', 'DataSteward', fallback="opalmen")

    local_configuration["existing_project_id"] = config.get('PROJECT', 'ExistingProjectId', fallback="")
    local_configuration["number_of_projects"] = config.getint('PROJECT', 'NumberOfProjects', fallback=1)
    local_configuration["number_of_collections_per_project"] = config.getint('PROJECT', 'NumberOfCollectionsPerProject',
                                                                             fallback=5)

    local_configuration["categories"] = json.loads(config.get('FOLDER', 'Categories', fallback='["text"]'))
    local_configuration["number_of_folders"] = config.getint('FOLDER', 'NumberOfFolders', fallback=3)
    local_configuration["minimum_folder_depth"] = config.getint('FOLDER', 'MinimumFolderDepth', fallback=0)
    local_configuration["maximum_folder_depth"] = config.getint('FOLDER', 'MaximumFolderDepth', fallback=5)
    local_configuration["number_of_files_per_folder"] = config.getint('FOLDER', 'NumberOfFilesPerFolder', fallback=2)
    local_configuration["maximum_sentences_per_file"] = config.getint('FOLDER', 'MaximumSentencesPerFile', fallback=100)

    local_configuration["include_images"] = config.getboolean('IMAGES', 'IncludeImages', fallback=False)
    local_configuration["number_of_image_folders"] = config.getint('IMAGES', 'NumberOfImageFolders', fallback=3)
    local_configuration["minimum_image_folder_depth"] = config.getint('IMAGES', 'MinimumImageFolderDepth', fallback=0)
    local_configuration["maximum_image_folder_depth"] = config.getint('IMAGES', 'MaximumImageFolderDepth', fallback=5)
    local_configuration["number_of_images_per_folder"] = config.getint('IMAGES', 'NumberOfImagesPerFolder', fallback=2)
    local_configuration["image_height"] = config.getint('IMAGES', 'ImageHeight', fallback=256)
    local_configuration["image_width"] = config.getint('IMAGES', 'ImageWidth', fallback=256)
    local_configuration["image_hue"] = json.loads(config.get('IMAGES', 'ImageHue', fallback='["red"]'))
    local_configuration["image_format"] = json.loads(config.get('IMAGES', 'ImageFormat', fallback='["png"]'))

    local_configuration["use_diacritics"] = config.getboolean('SPECIALFOLDERS', 'UseDiacritics', fallback=False)
    local_configuration["use_specialchars"] = config.getboolean('SPECIALFOLDERS', 'UseSpecialchars', fallback=False)
    local_configuration["number_of_special_folders"] = config.getint('SPECIALFOLDERS', 'NumberOfSpecialFolders',
                                                                     fallback=3)
    local_configuration["minimum_special_folder_depth"] = config.getint('SPECIALFOLDERS', 'MinimumSpecialFolderDepth',
                                                                        fallback=0)
    local_configuration["maximum_special_folder_depth"] = config.getint('SPECIALFOLDERS', 'MaximumSpecialFolderDepth',
                                                                        fallback=5)
    local_configuration["number_of_special_files_per_folder"] = config.getint('SPECIALFOLDERS',
                                                                              'NumberOfSpecialFilesPerFolder',
                                                                              fallback=2)
    local_configuration["maximum_sentences_per_special_file"] = config.getint('SPECIALFOLDERS',
                                                                              'MaximumSentencesPerSpecialFile',
                                                                              fallback=100)

    return local_configuration


def create_file(directory, category='text', nb_sentences=5):
    file_name = fake.file_name(category=category)
    f = open(directory + "/" + file_name, "w")
    f.write(fake.paragraph(nb_sentences=nb_sentences))
    f.close()
    logger.info(indent3+directory + "/" + file_name + " was created")


def create_image(directory):
    extension = random.choice(configuration["image_format"])
    file_name = fake.file_name(category="image", extension=extension)
    image = fake.image(size=(configuration["image_height"], configuration["image_width"]),
                       hue=random.choice(configuration["image_hue"]), luminosity='random', image_format=extension)
    f = open(directory + "/" + file_name, "wb")
    f.write(image)
    f.close()
    logger.info(indent3+directory + "/" + file_name + " was created")


def create_dir(token, depth=5, category='text'):
    ingest_zone = os.path.join("/mnt/ingest/zones/", token)
    full_path = fake.file_path(depth=depth, category=category)
    path, file = os.path.split(full_path)
    path = ingest_zone + path
    os.makedirs(path, exist_ok=True)
    logger.info(indent2+path + " was created")
    return path


def create_project():
    manager = RuleManager()
    project = manager.create_new_project("1-1-2018", "1-1-2018",
                                         "iresResource", "replRescUM01", 42, fake.catch_phrase(),
                                         configuration["user_name"],
                                         configuration["data_steward"], "XXXXXXXXX", "false", "false")
    manager.set_acl('default', 'own', configuration["data_steward"], project.project_path)
    manager.set_acl('default', 'own', configuration["user_name"], project.project_path)
    manager.set_acl('default', 'read', "datahub", project.project_path)
    return project


def create_contacts(amount):
    users = []
    for counter in range(amount):
        user = {}
        user['FirstName'] = fake.first_name()
        user['LastName'] = fake.last_name()
        user['MidInitials'] = ""
        user['Email'] = fake.ascii_company_email()
        user['Phone'] = fake.phone_number()
        user['Address'] = fake.address().replace("\n", " ")
        user['Affiliation'] = fake.company()
        user['Role'] = fake.job()
        users.append(user)

    return json.dumps(users)


def create_collection(project_id):
    data = {
        "user": configuration["user_name"],
        "creator": configuration["user_email"],
        "project": project_id,
        "title": fake.catch_phrase(),
        "description": fake.sentence(),
        "date": fake.date(),
        "articles": '10.1016/j.cell.2021.02.021,10.1126/science.abc4346',
        "organism_id": "ncbitaxon:http://purl.obolibrary.org/obo/NCBITaxon_9606",
        "organism_label": "Homo sapiens",
        "tissue_id": "efo:http://www.ebi.ac.uk/efo/EFO_0000803",
        "tissue_label": "renal system",
        "technology_id": "ero:http://purl.obolibrary.org/obo/ERO_0000570",
        "technology_label": "heart perfusion",
        "factors": [fake.word(), fake.word(), fake.word(), fake.word()],
        "contacts": create_contacts(configuration["number_of_contacts"])
    }
    token = RuleManager().create_drop_zone(data)
    logger.info(indent1+"Dropzone " + token + " was created")
    return token


def ingest_collection(token):
    RuleManager().start_ingest(configuration["user_name"], token)
    logger.info(indent1+"Ingest " + token + " was started")


def create_folder_structure(token):
    for y in range(configuration["number_of_folders"]):
        directory = create_dir(token, depth=random.randint(configuration["minimum_folder_depth"],
                                                           configuration["maximum_folder_depth"]),
                               category=random.choice(configuration["categories"]))
        for x in range(configuration["number_of_files_per_folder"]):
            create_file(directory, category=random.choice(configuration["categories"]),
                        nb_sentences=random.randint(0, configuration["maximum_sentences_per_file"]))
    if configuration["include_images"]:
        create_image_folder_structure(token)
    if configuration["use_diacritics"] or configuration["use_specialchars"]:
        create_special_folderstructure(token)


def create_special_dir(token, depth=5, elements=("A", "B", "C")):
    ingest_zone = os.path.join("/mnt/ingest/zones/", token)
    full_path = ""
    for i in range(depth + 1):
        full_path = full_path + "/" + "".join(fake.random_elements(elements=elements, length=5, unique=True))
    path, file = os.path.split(full_path)
    path = ingest_zone + path
    os.makedirs(path, exist_ok=True)
    logger.info(indent2+path + " was created")

    return path


def create_special_file(directory, nb_sentences=5, elements=("A", "B", "C")):
    file_name = "".join(fake.random_elements(elements=elements, length=20, unique=True)) + ".txt"
    f = open(directory + "/" + file_name, "w")
    f.write(fake.paragraph(nb_sentences=nb_sentences))
    f.close()
    logger.info(indent3+directory + "/" + file_name + " was created")


def create_special_folderstructure(token):
    for y in range(configuration["number_of_special_folders"]):
        if configuration["use_diacritics"]:
            directory = create_special_dir(token, depth=random.randint(
                configuration["minimum_special_folder_depth"], configuration["maximum_special_folder_depth"]),
                                                       elements=diacritic_elements)
            for x in range(configuration["number_of_special_files_per_folder"]):
                create_special_file(directory,
                                    nb_sentences=random.randint(0, configuration["maximum_sentences_per_special_file"]),
                                    elements=diacritic_elements)
        if configuration["use_specialchars"]:
            directory = create_special_dir(token, depth=random.randint(
                configuration["minimum_special_folder_depth"], configuration["maximum_special_folder_depth"]),
                                                       elements=specialchar_elements)
            for x in range(configuration["number_of_special_files_per_folder"]):
                create_special_file(directory,
                                    nb_sentences=random.randint(0, configuration["maximum_sentences_per_special_file"]),
                                    elements=specialchar_elements)


def create_image_folder_structure(token):
    for y in range(configuration["number_of_image_folders"]):
        directory = create_dir(token, depth=random.randint(configuration["minimum_image_folder_depth"],
                                                           configuration["maximum_image_folder_depth"]),
                               category="image")
        for x in range(configuration["number_of_images_per_folder"]):
            create_image(directory)


def main():
    global configuration
    global fake

    # Parse command line arguments
    configuration_file = "config.ini"
    if len(sys.argv) > 1:
        configuration_file = sys.argv[1]

    logger.info("Running dh-faker with configuration file: " + configuration_file)
    configuration = read_config_file(configuration_file)
    fake = Faker(configuration["locales"])

    if configuration["existing_project_id"] == "":
        for x in range(configuration["number_of_projects"]):
            project = create_project()
            logger.info(indent0+"Creating new project : " + project.project_id)
            for y in range(configuration["number_of_collections_per_project"]):
                token = create_collection(project.project_id)
                create_folder_structure(token)
                ingest_collection(token)
                time.sleep(configuration["sleep_between_ingests"])
    else:
        logger.info(indent0+"Existing project : " + configuration["existing_project_id"])
        for y in range(configuration["number_of_collections_per_project"]):
            token = create_collection(configuration["existing_project_id"])
            create_folder_structure(token)
            ingest_collection(token)
            time.sleep(configuration["sleep_between_ingests"])


if __name__ == "__main__":
    main()
