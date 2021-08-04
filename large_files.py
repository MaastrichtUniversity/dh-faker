from base_folder import *
logger = logging.getLogger("Faker")


class LargeFilesFolder(BaseFolder):
    def __init__(self, configuration, fake):
        self.fake = fake
        self.category = "text"
        self.number_of_folders = configuration["number_of_large_file_folders"]
        self.minimum_folder_depth = configuration["minimum_large_file_folder_depth"]
        self.maximum_folder_depth = configuration["maximum_large_file_folder_depth"]
        self.large_file_sizes = configuration["large_file_sizes"]
        self.large_file_names = configuration["large_file_names"]

    def create_folder_structure(self, token):
        for y in range(self.number_of_folders):
            directory = self.create_dir(token, depth=self.get_folder_depth(), category=self.category)
            self.create_large_files(directory)


    def create_large_files(self, directory):
        for i in range(len(self.large_file_sizes)):
            file_size = int(self.large_file_sizes[i])
            file_name = self.large_file_names[i]
            file_content = self.fake.binary(length=file_size)
            f = open(directory + "/" + file_name, "wb")
            f.write(file_content)
            f.close()
            logger.info(indent3 + directory + "/" + file_name + " was created")

