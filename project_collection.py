from irodsrulewrapper.rule import RuleManager
from faker_config import *
logger = logging.getLogger("Faker")


def create_project(configuration, fake):
    manager = RuleManager(admin_mode=True)
    project = manager.create_new_project("1-1-2018", "1-1-2018",
                                         "iresResource", configuration["resource"], 42, fake.catch_phrase(),
                                         configuration["user_name"],
                                         configuration["data_steward"], "XXXXXXXXX", "false", "false", "false", "DataHub_general_schema")
    manager.set_acl('default', 'own', configuration["data_steward"], project.project_path)
    manager.set_acl('default', 'own', configuration["user_name"], project.project_path)
    manager.set_acl('default', 'read', "datahub", project.project_path)
    return project

def create_collection(project_id, configuration, fake):
    title = fake.catch_phrase()
    data = {
        'user': configuration["user_name"],
        'project': project_id,
        'title': title
    }
    token = RuleManager(admin_mode=True).create_drop_zone(data, "/opt/assets/schema.json", get_metadata(configuration, fake, title))
    logger.info(indent1 + "Dropzone " + token + " was created")
    return token


def ingest_collection(configuration, token):
    RuleManager(admin_mode=True).ingest(configuration["user_name"], token)
    logger.info(indent1 + "Ingest " + token + " was started")


def get_metadata(configuration, fake, title):
    json_file = open('/opt/assets/instance.json', )
    tree_validation = json.load(json_file)
    tree_validation["pav:createdBy"] = f"https://mdr.datahubmaastricht.nl/user/{configuration['user_name']}"
    tree_validation["oslc:modifiedBy"] = f"https://mdr.datahubmaastricht.nl/user/{configuration['user_name']}"
    tree_validation["2_Creator"]["creatorName"]["@value"] = configuration["user_name"]
    tree_validation["3_Title"]["title"]["@value"] = title
    tree_validation["8_Date"][0]["datasetDate"]["@value"] = fake.date()
    tree_validation["17_Description"]["Description"]["@value"] = fake.sentence()

    if configuration["collection_metadata"] == "full":
        tree_validation["7_Contributor"] = create_contributors(configuration, fake)
        tree_validation["12_RelatedIdentifier"][0]["relatedResourceIdentifier"]["@value"] = "https://doi.org/"+fake.word()
        tree_validation["6_Subject"] = create_subjects(configuration, fake)

    if configuration["collection_metadata"] == "wrong":
        # Date is missing and therefore validation should fail
        tree_validation["8_Date"][0]["datasetDate"]["@value"] = None

    return tree_validation

def create_subjects(configuration, fake):
    subjects = []
    for counter in range(configuration["number_of_subjects"]):
        subject = {
            "Subject": {
                "@id": "http://www.orpha.net/ORDO/Orphanet_fake_" + str(counter),
                "rdfs:label": fake.word()
            },
            "subjectSchemeIRI": {
                "@value": fake.word()
            },
            "subjectIRI": {
                "@value": fake.word()
            },
            "@id": "https://repo.metadatacenter.org/template-elements/fc4e957d-637c-4a00-b371-d9e981ce3af4",
            "@context": {
                "Subject": "https://schema.metadatacenter.org/properties/71f1a80c-d59e-4d92-a084-4f22f219cb6e",
                "subjectSchemeIRI": "http://vocab.fairdatacollective.org/gdmt/hasSubjectSchemeIRI",
                "subjectIRI": "http://vocab.fairdatacollective.org/gdmt/hasSubjectIRI"
            }
        }
        subjects.append(subject)
    return subjects

def create_contributors(configuration, fake):
    contributors = []
    for counter in range(configuration["number_of_contributors"]):
        first_name = fake.first_name()
        last_name = fake.last_name()
        contributor =  {
            "contributorType": {
                "@id": "http://purl.org/zonmw/generic/10088",
                "rdfs:label": "work package leader"
            },
            "contributorName1": {
                "@value": f"{first_name} {last_name}"
            },
            "givenName": {
                "@value": first_name
            },
            "familyName": {
                "@value": last_name
            },
            "contributorContact": {
                "@value": fake.ascii_company_email()
            },
            "contributorIdentifier": {
                "@value": "1234-5678-9012-3456"
            },
            "contributorIdentifierScheme": {
                "@id": "https://orcid.org/",
                "rdfs:label": "ORCiD"
            },
            "@id": "https://repo.metadatacenter.org/template-elements/1d979a88-1028-421d-a124-11b5011f278a",
            "@context": {
                "contributorType": "https://schema.metadatacenter.org/properties/4d0bd488-6d4a-4388-bfa9-3cbb1d941afb",
                "contributorName1": "https://schema.metadatacenter.org/properties/f98681e6-2367-4e5b-8b38-0536056a2f59",
                "givenName": "https://schema.metadatacenter.org/properties/1b2e719d-c7cc-4db0-b6f8-22ccdf43a387",
                "familyName": "https://schema.metadatacenter.org/properties/510d9317-3658-429b-b773-8f9c0d288668",
                "contributorContact": "https://schema.metadatacenter.org/properties/72eb0553-76b7-4ef2-898f-694aa015cdd4",
                "contributorIdentifier": "https://schema.metadatacenter.org/properties/4636604a-6a42-4257-8a34-b8c68627cf32",
                "contributorIdentifierScheme": "https://schema.metadatacenter.org/properties/264bff35-9c7e-4a84-a722-712217dfa232"
            }
        }
        contributors.append(contributor)
    return contributors