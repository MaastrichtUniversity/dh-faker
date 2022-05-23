import random
import os

from faker_config import *

logger = logging.getLogger("Faker")


class BaseFolder:
    def __init__(self, configuration, fake):
        self.fake = fake
        self.number_of_folders = configuration["number_of_folders"]
        self.minimum_folder_depth = configuration["minimum_folder_depth"]
        self.maximum_folder_depth = configuration["maximum_folder_depth"]
        self.category = random.choice(configuration["categories"])
        self.number_of_files_per_folder = configuration["number_of_files_per_folder"]
        self.nb_sentences = random.randint(0, configuration["maximum_sentences_per_file"])

    def create_folder_structure(self, token):
        for y in range(self.number_of_folders):
            directory = self.create_dir(token, depth=self.get_folder_depth(), category=self.category)
            for x in range(self.number_of_files_per_folder):
                self.create_file(directory, category=self.category, nb_sentences=self.nb_sentences)

    def create_dir(self, token, depth=5, category="text"):
        ingest_zone = os.path.join("/mnt/ingest/zones/", token)
        full_path = self.fake.file_path(depth=depth, category=category)
        path, file = os.path.split(full_path)
        path = ingest_zone + path
        os.makedirs(path, exist_ok=True)
        logger.info(indent2 + path + " was created")
        return path

    def create_file(self, directory, category="text", nb_sentences=5):
        file_name = self.fake.file_name(category=category)
        f = open(directory + "/" + file_name, "w")
        f.write(self.fake.paragraph(nb_sentences=nb_sentences))
        f.close()
        logger.info(indent3 + directory + "/" + file_name + " was created")

    def get_folder_depth(self):
        return random.randint(self.minimum_folder_depth, self.maximum_folder_depth)
