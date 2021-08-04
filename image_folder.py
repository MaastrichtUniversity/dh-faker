from base_folder import *
logger = logging.getLogger("Faker")


class ImageFolder(BaseFolder):
    def __init__(self, configuration, fake):
        self.fake = fake
        self.number_of_folders = configuration["number_of_image_folders"]
        self.minimum_folder_depth = configuration["minimum_image_folder_depth"]
        self.maximum_folder_depth = configuration["maximum_image_folder_depth"]
        self.category = "image"
        self.number_of_files_per_folder = configuration["number_of_images_per_folder"]
        self.nb_sentences = random.randint(0, configuration["maximum_sentences_per_file"])
        self.extension = random.choice(configuration["image_format"])
        self.size = (configuration["image_height"], configuration["image_width"])
        self.hue = random.choice(configuration["image_hue"])

    def create_folder_structure(self, token):
        for y in range(self.number_of_folders):
            directory = self.create_dir(token, depth=self.get_folder_depth(), category=self.category)
            for x in range(self.number_of_files_per_folder):
                self.create_image(directory)

    def create_image(self, directory):
        file_name = self.fake.file_name(category="image", extension=self.extension)
        image = self.fake.image(size=self.size, hue=self.hue, luminosity='random', image_format=self.extension)
        f = open(directory + "/" + file_name, "wb")
        f.write(image)
        f.close()
        logger.info(indent3+directory + "/" + file_name + " was created")
