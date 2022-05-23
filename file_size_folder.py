from base_folder import *
import os

logger = logging.getLogger("Faker")


class FileSizeFolder(BaseFolder):
    def __init__(self, configuration, fake):
        super().__init__(configuration, fake)
        self.category = "text"
        self.include_large_files = configuration["include_large_files"]
        self.include_0byte_files = configuration["include_0byte_files"]
        self.number_of_folders = configuration["number_of_large_file_folders"]
        self.minimum_folder_depth = configuration["minimum_large_file_folder_depth"]
        self.maximum_folder_depth = configuration["maximum_large_file_folder_depth"]
        self.large_file_sizes = configuration["large_file_sizes"]
        self.large_file_names = configuration["large_file_names"]

    def create_folder_structure(self, token):
        for y in range(self.number_of_folders):
            directory = self.create_dir(token, depth=self.get_folder_depth(), category=self.category)
            self.create_file_size_files(directory)

    def create_file_size_files(self, directory):
        if self.include_large_files:
            self.write_large_files(directory)
        if self.include_0byte_files:
            self.write_0byte_files(directory)

    # region Large files
    def write_large_files(self, directory):
        for i in range(len(self.large_file_sizes)):
            file_size = str(int(int(self.large_file_sizes[i]) / 1024))
            file_name = self.large_file_names[i]
            file_path = f"{directory}/{file_name}"
            if self.drop_zone_type == "direct":
                self.write_large_direct_file(file_name, file_path, file_size)
            else:
                self.write_large_mounted_file(file_path, file_size)
            logger.info(f"{indent3}{file_path} was created")

    @staticmethod
    def write_large_mounted_file(file_path, file_size):
        cmd = "dd if=/dev/zero of=" + file_path + " count=" + file_size + " bs=1024"
        os.system(cmd)

    def write_large_direct_file(self, file_name, full_path, file_size):
        tmp_path = f"/tmp/{file_name}"
        self.write_large_mounted_file(tmp_path, file_size)

        rule_manager = RuleManager(self.username)
        rule_manager.session.data_objects.put(tmp_path, full_path)
        rule_manager.session.cleanup()
        os.remove(tmp_path)

    # endregion

    # region 0byte files

    def write_0byte_files(self, directory):
        file_name = "0b.bin"
        file_path = f"{directory}/{file_name}"
        if self.drop_zone_type == "direct":
            self.write_0byte_direct_file(file_path, file_name)
        else:
            self.write_0byte_mounted_file(file_path)

    @staticmethod
    def write_0byte_mounted_file(file_path):
        f = open(file_path, "w")
        f.close()
        logger.info(f"{indent3}{file_path} was created")

    def write_0byte_direct_file(self, file_path, file_name):
        tmp_path = f"/tmp/{file_name}"
        self.write_0byte_mounted_file(tmp_path)

        rule_manager = RuleManager(self.username)
        rule_manager.session.data_objects.put(tmp_path, file_path)
        rule_manager.session.cleanup()
        os.remove(tmp_path)
        logger.info(f"{indent3}{file_path} was created")

    # endregion
