from irodsrulewrapper.rule import RuleManager
from faker_config import *
logger = logging.getLogger("Faker")


def create_project(configuration, fake):
    manager = RuleManager()
    project = manager.create_new_project("1-1-2018", "1-1-2018",
                                         "iresResource", "replRescUM01", 42, fake.catch_phrase(),
                                         configuration["user_name"],
                                         configuration["data_steward"], "XXXXXXXXX", "false", "false")
    manager.set_acl('default', 'own', configuration["data_steward"], project.project_path)
    manager.set_acl('default', 'own', configuration["user_name"], project.project_path)
    manager.set_acl('default', 'read', "datahub", project.project_path)
    return project


def create_contacts(amount, fake):
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


def create_collection(project_id, configuration, fake):
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
        "contacts": create_contacts(configuration["number_of_contacts"], fake)
    }
    token = RuleManager().create_drop_zone(data)
    logger.info(indent1+"Dropzone " + token + " was created")
    return token


def ingest_collection(configuration, token):
    RuleManager().start_ingest(configuration["user_name"], token)
    logger.info(indent1+"Ingest " + token + " was started")
