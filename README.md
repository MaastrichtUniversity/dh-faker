# dh-faker

# Dependencies
This faker application is tightly coupled to the DataHub iRODS infrastructure as described in [docker-dev](https://github.com/MaastrichtUniversity/docker-dev). 
 It relies on the specific business logic regarding project & collection structure and uses remote procedure calls defined
 in [irods-rule-wrapper](https://github.com/MaastrichtUniversity/irods-rule-wrapper).

# Before you start
Make sure that your runtime environment has:
* a running instance of the `irods` and `ires` container
* a value of `USE_SAMBA=false` in the irods.secrets.cfg file. This will ensure that both iRODS and dh-faker use the dropzones
 from the volume-bound `./docker-dev/staging-data` directory.

# Usage
1. Change the configuration settings on line 8-12
1. Start the container with 
    ``` 
    ./rit.sh up dh-faker
    ```
1. The stdout will now print on the names of the dropzones and the fake files that are being created.
1. The state that will be reached at exit of the dh-faker container is that _N_ amount of dropzones are being ingested by iRODS.
   
# TODO
* Use a config file instead of editing in the script.