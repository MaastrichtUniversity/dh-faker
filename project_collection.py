import random

from irodsrulewrapper.rule import RuleManager
from faker_config import *

logger = logging.getLogger("Faker")


def create_project(configuration, fake):
    manager = RuleManager(admin_mode=True)
    project = manager.create_new_project(
        "ires-hnas-umResource",
        configuration["resource"],
        fake.catch_phrase(),
        configuration["user_name"],
        configuration["data_steward"],
        "XXXXXXXXX",
        {
            "authorizationPeriodEndDate": "1-1-2018",
            "dataRetentionPeriodEndDate": "1-1-2018",
            "storageQuotaGb": 42,
            "enableArchive": "false",
            "enableUnarchive": "false",
            "enableDropzoneSharing": "false",
            "collectionMetadataSchemas":  "DataHub_general_schema",
        },
    )
    manager.set_acl("default", "own", configuration["data_steward"], project.project_path)
    manager.set_acl("default", "own", configuration["user_name"], project.project_path)
    manager.set_acl("default", "read", "datahub", project.project_path)
    manager.session.cleanup()
    return project


def create_drop_zone(project_id, configuration, fake):
    title = fake.catch_phrase()
    user_name = configuration["user_name"]
    configuration["drop_zone_type_chosen"] = random.choice(configuration["drop_zone_type"])
    data = {
        "user": user_name,
        "project": project_id,
        "title": title,
        "dropzone_type": configuration["drop_zone_type_chosen"],
    }

    if configuration["drop_zone_type_chosen"] == "direct":
        rule_manager = RuleManager(user_name)
    else:
        rule_manager = RuleManager(admin_mode=True)
    token = rule_manager.create_drop_zone(
        data, "/opt/assets/schema.json", get_metadata(configuration, fake, title), "DataHub_General_schema", "1.0.0"
    )
    rule_manager.session.cleanup()
    logger.info(f"{indent1} Dropzone {token} ({configuration['drop_zone_type_chosen']}) was created")
    return token


def ingest_collection(configuration, token):
    user_name = configuration["user_name"]
    rule_manager = RuleManager(user_name)
    rule_manager.ingest(user_name, token, configuration["drop_zone_type_chosen"])
    rule_manager.session.cleanup()
    logger.info(f"{indent1} Ingest {token} was started")


def get_metadata(configuration, fake, title):
    user_name = configuration["user_name"]
    rule_manager = RuleManager(user_name)
    display_name = rule_manager.get_user_attribute_value(user_name, "displayName", "false").value
    rule_manager.session.cleanup()
    split_display_name = display_name.split(" ", 1)

    json_file = open(
        "/opt/assets/instance.json",
    )
    tree_validation = json.load(json_file)
    tree_validation["pav:createdBy"] = f"https://mdr.datahubmaastricht.nl/user/{user_name}"
    tree_validation["oslc:modifiedBy"] = f"https://mdr.datahubmaastricht.nl/user/{user_name}"
    tree_validation["2_Creator"]["creatorGivenName"]["@value"] = split_display_name[0]
    tree_validation["2_Creator"]["creatorFamilyName"]["@value"] = split_display_name[1]
    tree_validation["2_Creator"]["creatorFullName"]["@value"] = display_name
    tree_validation["3_Title"]["title"]["@value"] = title
    tree_validation["8_Date"]["datasetDate"]["@value"] = fake.date()
    tree_validation["17_Description"]["Description"]["@value"] = fake.sentence()

    if configuration["collection_metadata"] == "full":
        tree_validation["7_Contributor"] = create_contributors(configuration, fake)
        tree_validation["12_RelatedIdentifier"][0]["relatedResourceIdentifier"]["@value"] = (
            "https://doi.org/" + fake.word()
        )
        tree_validation["6_Subject"] = create_subjects(configuration, fake)

    if configuration["collection_metadata"] == "wrong":
        # Date is missing and therefore validation should fail
        tree_validation["8_Date"]["datasetDate"]["@value"] = None

    return tree_validation


def create_subjects(configuration, fake):
    subjects = []
    for counter in range(configuration["number_of_subjects"]):
        value = fake.word()
        subject = {
            "Subject": {"@value": value},
            "subjectSchemeIRI": {"@value": "http://www.orpha.net/ORDO"},
            "valueURI": {"@id": "http://www.orpha.net/ORDO/Orphanet_fake_" + str(counter), "rdfs:label": value},
            "@id": "https://repo.metadatacenter.org/template-elements/fc4e957d-637c-4a00-b371-d9e981ce3af4",
            "@context": {
                "subjectSchemeIRI": "http://vocab.fairdatacollective.org/gdmt/hasSubjectSchemeIRI",
                "valueURI": "https://schema.metadatacenter.org/properties/af9c45ec-d971-4056-a6c2-5ce930b9b181",
                "Subject": "https://schema.metadatacenter.org/properties/71f1a80c-d59e-4d92-a084-4f22f219cb6e",
            },
        }
        subjects.append(subject)
    return subjects


def create_contributors(configuration, fake):
    contributors = []
    for counter in range(configuration["number_of_contributors"]):
        first_name = fake.first_name()
        last_name = fake.last_name()
        contributor = {
            "contributorType": {"@id": "http://purl.org/zonmw/generic/10088", "rdfs:label": "work package leader"},
            "contributorFullName": {"@value": f"{first_name} {last_name}"},
            "contributorGivenName": {"@value": first_name},
            "contributorFamilyName": {"@value": last_name},
            "contributorEmail": {"@value": fake.ascii_company_email()},
            "contributorAffiliation": {},
            "contributorIdentifier": {"@value": "1234-5678-9012-3456"},
            "contributorIdentifierScheme": {"@id": "https://orcid.org/", "rdfs:label": "ORCiD"},
            "@id": "https://repo.metadatacenter.org/template-elements/1d979a88-1028-421d-a124-11b5011f278a",
            "@context": {
                "contributorType": "https://schema.metadatacenter.org/properties/4d0bd488-6d4a-4388-bfa9-3cbb1d941afb",
                "contributorFullName": "https://schema.metadatacenter.org/properties/272d6c5e-467c-4c01-a513-23b8df92585d",
                "contributorGivenName": "https://schema.metadatacenter.org/properties/1b2e719d-c7cc-4db0-b6f8-22ccdf43a387",
                "contributorFamilyName": "https://schema.metadatacenter.org/properties/510d9317-3658-429b-b773-8f9c0d288668",
                "contributorEmail": "https://schema.metadatacenter.org/properties/72eb0553-76b7-4ef2-898f-694aa015cdd4",
                "contributorAffiliation": "https://schema.metadatacenter.org/properties/73214405-3002-4fde-8f6c-b012faf907ec",
                "contributorIdentifier": "https://schema.metadatacenter.org/properties/4636604a-6a42-4257-8a34-b8c68627cf32",
                "contributorIdentifierScheme": "https://schema.metadatacenter.org/properties/264bff35-9c7e-4a84-a722-712217dfa232",
            },
        }
        contributors.append(contributor)
    return contributors
