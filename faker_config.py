import argparse
import json
import configparser
import logging
import os

logger = logging.getLogger("Faker")

# Note: A Linux file name cannot contain /
# Note: A Windows file name cannot contain \ / : * ? " < > |
# Note: A MacOS file name cannot contain / :
specialchar_elements = (
    " ",
    "`",
    "~",
    "!",
    "@",
    "#",
    "$",
    "%",
    "^",
    "&",
    "(",
    ")",
    "-",
    "_",
    "+",
    "=",
    "{",
    "}",
    "[",
    "]",
    ";",
    "'",
    ",",
    ".",
    "€",
)
diacritic_elements = (
    " ",
    "Á",
    "á",
    "À",
    "à",
    "Â",
    "â",
    "Ã",
    "ã",
    "Ä",
    "ä",
    "Å",
    "å",
    "Æ",
    "æ",
    "Ç",
    "ç",
    "Œ",
    "œ",
    "Ø",
    "ø",
)

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

    def parse_arguments(self):
        # Parse any conf_file specification
        # We make this parser with add_help=False so that
        # it doesn't parse -h and print help.
        conf_parser = argparse.ArgumentParser(
            # Turn off help, so we print all options in response to -h
            add_help=False
        )
        conf_parser.add_argument("-c", "--config", help="Specify other config file ", metavar="FILE")
        args, remaining_argv = conf_parser.parse_known_args()

        default_conf_file = 'config.ini'

        conf_file = None
        if not args.config and os.path.exists(default_conf_file):
            conf_file = default_conf_file
        elif args.config and os.path.exists(args.config):
            conf_file = args.config
        elif args.config and os.path.exists(args.config):
            raise Exception('Config file %s does not exist' % args.config)

        # Parse config file
        config = configparser.ConfigParser()
        config.read(conf_file)

        # Parse rest of arguments
        # Don't suppress add_help here so it will handle -h
        parser = argparse.ArgumentParser(
            # Inherit options from config_parser
            parents=[conf_parser],
            formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=35, width=100)
        )

        # User arguments
        user_group = parser.add_argument_group('user arguments')
        user_group.add_argument("--username", metavar='NAME', help="Override config file iRODS username")

        # Project arguments
        project_group = parser.add_argument_group('project arguments')
        project_group.add_argument("--existing_project_id", metavar='P000000001', help="Override config file Existing project ID")

        # TODO: Setting these overrides can be done prettier
        overrides = parser.parse_args(remaining_argv)
        if overrides.username is not None:
            config.set('USER', 'UserName', overrides.username)

        if overrides.existing_project_id is not None:
            config.set('PROJECT', 'ExistingProjectId', overrides.existing_project_id)

        logger.info("Running dh-faker with configuration file: " + conf_file)

        return config

    def set_config(self, config):

        self.configuration["locales"] = json.loads(config.get("GENERAL", "Locales", fallback='["nl_NL"]'))
        self.configuration["sleep_between_ingests"] = config.getint("GENERAL", "SleepBetweenIngests", fallback=5)
        self.configuration["number_of_contributors"] = config.getint("GENERAL", "NumberOfContributors", fallback=3)
        self.configuration["number_of_subjects"] = config.getint("GENERAL", "NumberOfSubjects", fallback=3)
        self.configuration["verbose"] = config.get("GENERAL", "Verbose", fallback="low")
        self.configuration["resource"] = config.get("GENERAL", "Resource", fallback="replRescUM01")
        self.configuration["collection_metadata"] = config.get("GENERAL", "CollectionMetadata", fallback="minimal")
        self.configuration["drop_zone_type"] = json.loads(config.get("GENERAL", "DropZoneType", fallback="direct"))

        self.configuration["user_name"] = config.get("USER", "UserName", fallback="jmelius")
        self.configuration["user_email"] = config.get(
            "USER", "UserEmail", fallback="fake-email@maastrichtuniversity.nl"
        )
        self.configuration["data_steward"] = config.get("USER", "DataSteward", fallback="opalmen")

        self.configuration["existing_project_id"] = config.get("PROJECT", "ExistingProjectId", fallback="")
        self.configuration["number_of_projects"] = config.getint("PROJECT", "NumberOfProjects", fallback=1)
        self.configuration["number_of_collections_per_project"] = config.getint(
            "PROJECT", "NumberOfCollectionsPerProject", fallback=5
        )

        self.configuration["categories"] = json.loads(config.get("FOLDER", "Categories", fallback='["text"]'))
        self.configuration["number_of_folders"] = config.getint("FOLDER", "NumberOfFolders", fallback=3)
        self.configuration["minimum_folder_depth"] = config.getint("FOLDER", "MinimumFolderDepth", fallback=0)
        self.configuration["maximum_folder_depth"] = config.getint("FOLDER", "MaximumFolderDepth", fallback=5)
        self.configuration["number_of_files_per_folder"] = config.getint("FOLDER", "NumberOfFilesPerFolder", fallback=2)
        self.configuration["maximum_sentences_per_file"] = config.getint(
            "FOLDER", "MaximumSentencesPerFile", fallback=100
        )

        self.configuration["include_images"] = config.getboolean("IMAGES", "IncludeImages", fallback=False)
        self.configuration["number_of_image_folders"] = config.getint("IMAGES", "NumberOfImageFolders", fallback=3)
        self.configuration["minimum_image_folder_depth"] = config.getint(
            "IMAGES", "MinimumImageFolderDepth", fallback=0
        )
        self.configuration["maximum_image_folder_depth"] = config.getint(
            "IMAGES", "MaximumImageFolderDepth", fallback=5
        )
        self.configuration["number_of_images_per_folder"] = config.getint(
            "IMAGES", "NumberOfImagesPerFolder", fallback=2
        )
        self.configuration["image_height"] = config.getint("IMAGES", "ImageHeight", fallback=256)
        self.configuration["image_width"] = config.getint("IMAGES", "ImageWidth", fallback=256)
        self.configuration["image_hue"] = json.loads(config.get("IMAGES", "ImageHue", fallback='["red"]'))
        self.configuration["image_format"] = json.loads(config.get("IMAGES", "ImageFormat", fallback='["png"]'))

        self.configuration["use_diacritics"] = config.getboolean("SPECIALFOLDERS", "UseDiacritics", fallback=False)
        self.configuration["use_specialchars"] = config.getboolean("SPECIALFOLDERS", "UseSpecialchars", fallback=False)
        self.configuration["number_of_special_folders"] = config.getint(
            "SPECIALFOLDERS", "NumberOfSpecialFolders", fallback=3
        )
        self.configuration["minimum_special_folder_depth"] = config.getint(
            "SPECIALFOLDERS", "MinimumSpecialFolderDepth", fallback=0
        )
        self.configuration["maximum_special_folder_depth"] = config.getint(
            "SPECIALFOLDERS", "MaximumSpecialFolderDepth", fallback=5
        )
        self.configuration["number_of_special_files_per_folder"] = config.getint(
            "SPECIALFOLDERS", "NumberOfSpecialFilesPerFolder", fallback=2
        )
        self.configuration["maximum_sentences_per_special_file"] = config.getint(
            "SPECIALFOLDERS", "MaximumSentencesPerSpecialFile", fallback=100
        )

        self.configuration["include_large_files"] = config.getboolean("FILESIZES", "IncludeLargeFiles", fallback=False)
        self.configuration["include_0byte_files"] = config.getboolean("FILESIZES", "Include0ByteFiles", fallback=False)
        self.configuration["number_of_large_file_folders"] = config.getint(
            "FILESIZES", "NumberOfFileSizeFolders", fallback=1
        )
        self.configuration["minimum_large_file_folder_depth"] = config.getint(
            "FILESIZES", "MinimumFileSizeFolderDepth", fallback=0
        )
        self.configuration["maximum_large_file_folder_depth"] = config.getint(
            "FILESIZES", "MaximumFileSizeFolderDepth", fallback=5
        )
        self.configuration["large_file_sizes"] = json.loads(
            config.get("FILESIZES", "LargeFileSizes", fallback='["10240", "1048576"]')
        )
        self.configuration["large_file_names"] = json.loads(
            config.get("FILESIZES", "LargeFileNames", fallback='["10Kb.bin", "1Mb.bin"]')
        )

        # self.configuration = local_configuration
        #
        # for key, value in local_configuration.items():
        #     self.__dict__.update({key: value})

    def get_config(self):
        return self.configuration
