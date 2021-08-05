import json
import configparser
import logging
import os


# Note: A Linux file name cannot contain /
# Note: A Windows file name cannot contain \ / : * ? " < > |
# Note: A MacOS file name cannot contain / :
specialchar_elements = (
' ', '`', '~', '!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '+', '=', '{', '}', '[', ']', ';', '\'', ',', '.',
'€')
diacritic_elements = (
' ', 'Á', 'á', 'À', 'à', 'Â', 'â', 'Ã', 'ã', 'Ä', 'ä', 'Å', 'å', 'Æ', 'æ', 'Ç', 'ç', 'Œ', 'œ', 'Ø', 'ø')

indent0 = "* "
indent1 = "-\t"
indent2 = "--\t\t"
indent3 = "---\t\t\t"


class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class FakerConfig(metaclass=SingletonMeta):
    configuration = {}

    def set_config(self, file):
        config = configparser.ConfigParser()
        config.read(file)
        if len(config.sections()) == 0:
            raise ValueError("Failed to open config file")

        self.configuration["locales"] = json.loads(config.get('GENERAL', 'Locales', fallback='["nl_NL"]'))
        self.configuration["sleep_between_ingests"] = config.getint('GENERAL', 'SleepBetweenIngests', fallback=5)
        self.configuration["number_of_contacts"] = config.getint('GENERAL', 'NumberOfContacts', fallback=3)
        self.configuration["verbose"] = config.get('GENERAL', 'Verbose', fallback="low")
        self.configuration["resource"] = config.get('GENERAL', 'Resource', fallback="replRescUM01")

        self.configuration["user_name"] = config.get('USER', 'UserName', fallback="jmelius")
        self.configuration["user_email"] = config.get('USER', 'UserEmail',
                                                       fallback="fake-email@maastrichtuniversity.nl")
        self.configuration["data_steward"] = config.get('USER', 'DataSteward', fallback="opalmen")

        self.configuration["existing_project_id"] = config.get('PROJECT', 'ExistingProjectId', fallback="")
        self.configuration["number_of_projects"] = config.getint('PROJECT', 'NumberOfProjects', fallback=1)
        self.configuration["number_of_collections_per_project"] = config.getint('PROJECT',
                                                                                 'NumberOfCollectionsPerProject',
                                                                                 fallback=5)

        self.configuration["categories"] = json.loads(config.get('FOLDER', 'Categories', fallback='["text"]'))
        self.configuration["number_of_folders"] = config.getint('FOLDER', 'NumberOfFolders', fallback=3)
        self.configuration["minimum_folder_depth"] = config.getint('FOLDER', 'MinimumFolderDepth', fallback=0)
        self.configuration["maximum_folder_depth"] = config.getint('FOLDER', 'MaximumFolderDepth', fallback=5)
        self.configuration["number_of_files_per_folder"] = config.getint('FOLDER', 'NumberOfFilesPerFolder',
                                                                          fallback=2)
        self.configuration["maximum_sentences_per_file"] = config.getint('FOLDER', 'MaximumSentencesPerFile',
                                                                          fallback=100)

        self.configuration["include_images"] = config.getboolean('IMAGES', 'IncludeImages', fallback=False)
        self.configuration["number_of_image_folders"] = config.getint('IMAGES', 'NumberOfImageFolders', fallback=3)
        self.configuration["minimum_image_folder_depth"] = config.getint('IMAGES', 'MinimumImageFolderDepth',
                                                                          fallback=0)
        self.configuration["maximum_image_folder_depth"] = config.getint('IMAGES', 'MaximumImageFolderDepth',
                                                                          fallback=5)
        self.configuration["number_of_images_per_folder"] = config.getint('IMAGES', 'NumberOfImagesPerFolder',
                                                                           fallback=2)
        self.configuration["image_height"] = config.getint('IMAGES', 'ImageHeight', fallback=256)
        self.configuration["image_width"] = config.getint('IMAGES', 'ImageWidth', fallback=256)
        self.configuration["image_hue"] = json.loads(config.get('IMAGES', 'ImageHue', fallback='["red"]'))
        self.configuration["image_format"] = json.loads(config.get('IMAGES', 'ImageFormat', fallback='["png"]'))

        self.configuration["use_diacritics"] = config.getboolean('SPECIALFOLDERS', 'UseDiacritics', fallback=False)
        self.configuration["use_specialchars"] = config.getboolean('SPECIALFOLDERS', 'UseSpecialchars', fallback=False)
        self.configuration["number_of_special_folders"] = config.getint('SPECIALFOLDERS', 'NumberOfSpecialFolders',
                                                                         fallback=3)
        self.configuration["minimum_special_folder_depth"] = config.getint('SPECIALFOLDERS',
                                                                            'MinimumSpecialFolderDepth',
                                                                            fallback=0)
        self.configuration["maximum_special_folder_depth"] = config.getint('SPECIALFOLDERS',
                                                                            'MaximumSpecialFolderDepth',
                                                                            fallback=5)
        self.configuration["number_of_special_files_per_folder"] = config.getint('SPECIALFOLDERS',
                                                                                  'NumberOfSpecialFilesPerFolder',
                                                                                  fallback=2)
        self.configuration["maximum_sentences_per_special_file"] = config.getint('SPECIALFOLDERS',
                                                                                  'MaximumSentencesPerSpecialFile',
                                                                                  fallback=100)

        self.configuration["include_large_files"] = config.getboolean('FILESIZES', 'IncludeLargeFiles', fallback=False)
        self.configuration["include_0byte_files"] = config.getboolean('FILESIZES', 'Include0ByteFiles', fallback=False)
        self.configuration["number_of_large_file_folders"] = config.getint('FILESIZES', 'NumberOfFileSizeFolders',
                                                                        fallback=1)
        self.configuration["minimum_large_file_folder_depth"] = config.getint('FILESIZES',
                                                                           'MinimumFileSizeFolderDepth',
                                                                           fallback=0)
        self.configuration["maximum_large_file_folder_depth"] = config.getint('FILESIZES',
                                                                           'MaximumFileSizeFolderDepth',
                                                                           fallback=5)
        self.configuration["large_file_sizes"] = json.loads(config.get('FILESIZES', 'LargeFileSizes', fallback='["10240", "1048576"]'))
        self.configuration["large_file_names"] = json.loads(config.get('FILESIZES', 'LargeFileNames', fallback='["10Kb.bin", "1Mb.bin"]'))

        # self.configuration = local_configuration
        #
        # for key, value in local_configuration.items():
        #     self.__dict__.update({key: value})

    def get_config(self):
        return self.configuration
