from irodsrulewrapper.rule import RuleManager
from faker import Faker
import os
import json

# region CONFIG
# General options
user = "jmelius"
user_email = "fake-email@maastrichtuniversity.nl"
data_steward = "opalmen"
number_of_projects = 1
number_of_collections_per_project = 5

# Options for locale
locale = True                       # False: only en_US active, True: multiple locales active

# Options for file names
filename_diacritics = True           # If special accents should occur in folder- and file names
filename_specialchars = True        # If special characters should occur in folder- and file names
# endregion

if locale:
    fake = Faker(["nl_NL", "de_DE", "zh_CN"])
else:
    fake = Faker("en_US")

# Note: A Linux file name cannot contain /
# Note: A Windows file name cannot contain \ / : * ? " < > |
# Note: A MacOS file name cannot contain / :
specialchar_elements = (' ', '`', '~', '!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '+', '=', '{', '}', '[', ']', ';', '\'', ',', '.', '€')
diacritic_elements = (' ', 'Á', 'á', 'À', 'à', 'Â', 'â', 'Ã', 'ã', 'Ä', 'ä', 'Å', 'å', 'Æ', 'æ', 'Ç', 'ç', 'Œ', 'œ', 'Ø', 'ø')

def create_file(directory, category='text', nb_sentences=5, filename_diacritics=False, diacr_elem=diacritic_elements, filename_specialchars=False, specchar_elem=specialchar_elements):
    if filename_diacritics:
        file_name = "".join(fake.random_elements(elements=diacr_elem, length=20, unique=True)) + ".txt"
    elif filename_specialchars:
        file_name = "".join(fake.random_elements(elements=specchar_elem, length=20, unique=True)) + ".txt"
    else:
        file_name = fake.file_name(category=category)
    f = open(directory + "/" + file_name, "a")
    f.write(fake.paragraph(nb_sentences=nb_sentences))
    f.close()
    print(file_name)


def create_dir(token, depth=5, category='text', filename_diacritics=False, diacr_elem=diacritic_elements, filename_specialchars=False, specchar_elem=specialchar_elements):
    ingest_zone = os.path.join("/mnt/ingest/zones/", token)
    full_path = ""
    if filename_diacritics:
        for i in range(depth+1):
            full_path = full_path + "/" + "".join(fake.random_elements(elements=diacr_elem, length=5, unique=True))
    elif filename_specialchars:
        for i in range(depth+1):
            full_path = full_path + "/" + "".join(fake.random_elements(elements=specchar_elem, length=5, unique=True))
    else:
        full_path = fake.file_path(depth=depth, category=category)
    path, file = os.path.split(full_path)
    path = ingest_zone + path
    os.makedirs(path, exist_ok=True)
    print(path)
    return path


def create_project():
    manager = RuleManager()
    project = manager.create_new_project("1-1-2018", "1-1-2018",
                                         "iresResource", "replRescUM01", 42, fake.catch_phrase(), user,
                                         data_steward, "XXXXXXXXX", "false", "false")
    manager.set_acl('default', 'own', data_steward, project.project_path)
    manager.set_acl('default', 'own', user, project.project_path)
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
        "user": user,
        "creator": user_email,
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
        "contacts": create_contacts(3)
    }
    token = RuleManager().create_drop_zone(data)
    print(token)
    return token


def ingest_collection(token):
    RuleManager().start_ingest(user, token)


def main():
    for x in range(number_of_projects):
        project = create_project()
        print(project.project_id)
        for y in range(number_of_collections_per_project):
            token = create_collection(project.project_id)
            directory = create_dir(token)   # all options to default
            create_file(directory)          # all options to default
            directory = create_dir(token, depth=3, category='video', filename_diacritics=filename_diacritics)
            create_file(directory, category='video', nb_sentences=100, filename_diacritics=filename_diacritics)
            directory = create_dir(token, depth=1, category='office', filename_specialchars=filename_specialchars)
            create_file(directory, category='office', nb_sentences=250, filename_specialchars=filename_specialchars)
            ingest_collection(token)


if __name__ == "__main__":
    main()
