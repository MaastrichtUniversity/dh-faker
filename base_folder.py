import random

from faker_config import *
from irodsrulewrapper.rule import RuleManager

logger = logging.getLogger("Faker")


class BaseFolder:
    def __init__(self, configuration, fake):
        self.fake = fake
        self.number_of_folders = configuration["number_of_folders"]
        self.minimum_folder_depth = configuration["minimum_folder_depth"]
        self.maximum_folder_depth = configuration["maximum_folder_depth"]
        self.number_of_files_per_folder = configuration["number_of_files_per_folder"]
        self.drop_zone_type = configuration["drop_zone_type_chosen"]
        self.username = configuration["user_name"]

        self.category = random.choice(configuration["categories"])
        self.nb_sentences = random.randint(0, configuration["maximum_sentences_per_file"])

    def create_folder_structure(self, token):
        for y in range(self.number_of_folders):
            directory = self.create_dir(token, depth=self.get_folder_depth(), category=self.category)
            for x in range(self.number_of_files_per_folder):
                self.create_file(directory, category=self.category, nb_sentences=self.nb_sentences)

    def create_dir(self, token, depth=5, category="text"):
        full_path = self.fake.file_path(depth=depth, category=category)
        if self.drop_zone_type == "direct":
            path = self.make_direct_dir(token, full_path)
        else:
            path = self.make_mounted_dir(token, full_path)

        logger.info(f"{indent2}{path} was created")
        return path

    def make_mounted_dir(self, token, full_path):
        base_path = "/mnt/ingest/zones/"
        path = self.format_dropzone_dir_path(base_path, token, full_path)
        os.makedirs(path, exist_ok=True)
        return path

    def make_direct_dir(self, token, full_path):
        base_path = "/nlmumc/ingest/direct"
        if os.path.split(full_path)[0] == "/":
            # logger.info(indent2 + full_path + "; root path; folder creation skipped")
            return os.path.join(base_path, token)

        path = self.format_dropzone_dir_path(base_path, token, full_path)
        rule_manager = RuleManager(self.username)
        rule_manager.session.collections.create(path)
        rule_manager.session.cleanup()
        return path

    @staticmethod
    def format_dropzone_dir_path(base_path, token, full_path):
        ingest_zone = os.path.join(base_path, token)
        path, file = os.path.split(full_path)
        path = ingest_zone + path
        return path

    def create_file(self, directory, category="text", nb_sentences=5):
        file_name = self.fake.file_name(category=category)
        fake_file = self.fake.paragraph(nb_sentences=nb_sentences)

        if self.drop_zone_type == "direct":
            self.write_direct_file(directory, file_name, fake_file)
        else:
            self.write_mounted_file(directory, file_name, fake_file)

        logger.info(f"{indent3}{directory}/{file_name} was created")

    @staticmethod
    def write_mounted_file(directory, file_name, fake_file, write_mode="w"):
        f = open(f"{directory}/{file_name}", write_mode)
        f.write(fake_file)
        f.close()

    def write_direct_file(self, directory, file_name, fake_file, write_mode="w"):
        tmp_path = f"/tmp/{file_name}"
        tmp_file = open(tmp_path, write_mode)
        tmp_file.write(fake_file)
        tmp_file.close()

        full_path = f"{directory}/{file_name}"

        rule_manager = RuleManager(self.username)
        rule_manager.session.data_objects.put(tmp_path, full_path)
        rule_manager.session.cleanup()
        os.remove(tmp_path)

    def get_folder_depth(self):
        return random.randint(self.minimum_folder_depth, self.maximum_folder_depth)
