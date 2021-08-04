from base_folder import *
logger = logging.getLogger("Faker")


class SpecialFolder(BaseFolder):
    def __init__(self, configuration, fake):
        self.fake = fake
        self.number_of_folders = configuration["number_of_special_folders"]
        self.use_diacritics = configuration["use_diacritics"]
        self.use_specialchars = configuration["use_specialchars"]
        self.minimum_folder_depth = configuration["minimum_special_folder_depth"]
        self.maximum_folder_depth = configuration["maximum_special_folder_depth"]
        self.category = random.choice(configuration["categories"])
        self.number_of_files_per_folder = configuration["number_of_special_files_per_folder"]
        self.nb_sentences = random.randint(0, configuration["maximum_sentences_per_special_file"])

    def create_folder_structure(self, token):
        for y in range(self.number_of_folders):
            if self.use_diacritics:
                self.create_special_folders(token, diacritic_elements)
            if self.use_specialchars:
                self.create_special_folders(token, specialchar_elements)

    def create_special_folders(self, token, elements):
        directory = self.create_special_dir(token, depth=self.get_folder_depth(), elements=elements)
        for x in range(self.number_of_files_per_folder):
            self.create_special_file(directory, nb_sentences=self.nb_sentences, elements=elements)

    def create_special_dir(self, token, depth=5, elements=("A", "B", "C")):
        ingest_zone = os.path.join("/mnt/ingest/zones/", token)
        full_path = ""
        for i in range(depth + 1):
            full_path = full_path + "/" + "".join(self.fake.random_elements(elements=elements, length=5, unique=True))
        path, file = os.path.split(full_path)
        path = ingest_zone + path
        os.makedirs(path, exist_ok=True)
        logger.info(indent2 + path + " was created")

        return path

    def create_special_file(self, directory, nb_sentences=5, elements=("A", "B", "C")):
        file_name = "".join(self.fake.random_elements(elements=elements, length=20, unique=True)) + ".txt"
        f = open(directory + "/" + file_name, "w")
        f.write(self.fake.paragraph(nb_sentences=nb_sentences))
        f.close()
        logger.info(indent3 + directory + "/" + file_name + " was created")

