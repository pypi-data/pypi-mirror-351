# Hidalgo2 Data Transfer Lib
This repository contains the implementation of the Hidalgo2 data transfer library. It uses [Apache NIFI](https://nifi.apache.org/) to transfer data from different data sources to specified targets

## Features
This library is planning to support the following features:
- transfer datasets from Cloud Providers to HDFS
- transfer datasets from Cloud Providers to CKAN
- transfer datasets from/to Hadoop HDFS to/from HPC
- transfer datasets from/to Hadoop HDFS to/from CKAN
- transfer datasets from/to a CKAN to/from HPC
- transfer datasets from/to local filesystem to/from HPC
- transfer datasets from/to local filesystem to/from CKAN

## Prototype
Current prototype of the library supports the following features:
- transfer datasets from/to Hadoop HDFS to/from HPC
- transfer datasets from/to Hadoop HDFS to/from CKAN
- transfer datasets from/to a CKAN to/from HPC
- transfer datasets from/to local filesystem to/from CKAN


## Implementation
This is a Python library that offers specialized API methods to transfer data from data sources to targets. 
Each API method launches a NIFI pipeline, by instantiating a NIFI process group out of its workflow definition registered in the NIFI registry. 
It uses the parameters given within the library method invocation to populate a NIFI parameter context that is asociated to the process group. 
Then, processors in the process group are executed once (or until the incomining processor's flowfile queue gets empty), one after another, following the group sequence flow, until the flow is completed. 
A processor is executed after the previous one has terminated. To check the status of the transfer command, the library offers another check-status command. 
Upon termination, the NIFI environment is cleaned up, by removing the created entities (i.e. the process group and its paramenter context). 
The Data Transfer Library sends requests to NIFI through its REST API. 

## Requirements
To use the Data Transfer library, it is required the following requirements:
 - **Python3** execution environment
 - **Poetry** python package management tool (optional)
 - **NIFI** instance, and either an NIFI or KEYCLOAK user's account and a NIFI server ssh account
 - **HDFS** instance
 - **CKAN** instance, with an user APIKey

 Python3 should be installed in the computer where Data Transfer CLI will be used.
 To install Poetry, follows [this instructions](https://python-poetry.org/docs/#installing-with-the-official-installer)

## Data Transfer lib configuration
### Configuration file
Before using the Data Transfer library, you should configure it to point at the target NIFI. The configuration file is located, by default, at the *data_transfer_cli/conf/hid_dt.cfg* file. Otherwise, its location can be specified in the environement variable *HID_DT_CONFIG_FILE*

```
[Nifi]
nifi_endpoint=https://nifi.hidalgo2.eu:9443
nifi_upload_folder=/opt/nifi/data/upload
nifi_download_folder=/opt/nifi/data/download
nifi_secure_connection=True

[Keycloak]
keycloak_endpoint=https://idm.hidalgo2.eu
keycloak_client_id=nifi
keycloak_client_secret=<keycloak_nifi_client_secret>

[Network]
check_status_sleep_lapse=5
```
Under the NIFI section, 
- We define the url of the NIFI service (*nifi_endpoint*), 
- We also specify a folder (*nifi_upload_folder*) in NIFI server where to upload files 
- And another folder (*nifi_download_folder*) where from to download files. These folder must be accessible by the NIFI service (ask NIFI administrator for details). 
- Additionally, you cat set if NIFI servers listens on a secure HTTPS connection (*nifi_secure_connection*=True) or on a non-secure HTTP (*nifi_secure_connection*=False)

Under the Keycloak section, you can configure the Keycloak integrated with NIFI, specifying:
- The Keycloak service endpoint (*keycloak_endpoint*)
- The NIFI client in Keycloak (*keycloak_client*)
- The NIFI secret in Keycloak (*keycloak_client_secret*)

Under the Network section, you can configure the lapse time (in seconds) each processor in the NIFI pipeline is checked for complation. Most of users should leave the default value.

HiDALGO2 developers can contact the Keycloak administrator for the *keycloak_client_secret*

### User's accounts in environment variables

You must also specify a user account (username, private_key) that grants to upload/download files to the NIFI server (as requested to upload temporary HPC keys or to support local file transfer). This user's account is provided by Hidalgo2 infrastructure provider and it is user's or service's specific. This account is set up in the following environment variables
- NIFI_SERVER_USERNAME: `export NIFI_SERVER_USERNAME=<nifi_server_username>`
- NIFI_SERVER_PRIVATE_KEY: `export NIFI_SERVER_PRIVATE_KEY=<path_to_private_key>`

Additionally, a user account granted with access to the NIFI service must be specified, either a

#### A) NIFI User Account
The NIFI account must be configured in the following environment variables:
- NIFI_LOGIN: `export NIFI_LOGIN=<nifi_login>`
- NIFI_PASSWORD: `export NIFI_PASSWORD=<nifi_password>`

This NIFI account is provided by the NIFI administrator. 

#### B) Keycloak Account with access to NIFI
The Keycloak account must be configured in the following environment variables:
- KEYCLOAK_LOGIN: `export KEYCLOAK_LOGIN=<keycloak_login>`
- KEYCLOAK_PASSWORD: `export KEYCLOAK_PASSWORD=<keycloak_password>`

For HiDALGO2 developers, NIFI (Service, Server) and Keycloak accounts are provided by the HiDALGO2 administrator.


## Usage
The data transfer library can be invoked following this procedure:

- Provide NIFI server and Keycloak accounts in environment variables
```
NIFI_SERVER_USERNAME=<nifi_server_username>
NIFI_SERVER_PRIVATE_KEY=<path_to_nifi_server_user_private_key>
KEYCLOAK_LOGIN=<keycloak_username>
KEYCLOAK_PASSWORD=<keycloak_password>
```
- Customized above hid_dt.cfg and specify its path in the envirorment variable
`HID_DT_CONFIG_FILE=<path_to_data_transfer_configuration_file`

- In your python code, instantiate a HIDDataTransferConfiguration object and an HIDDataTranfer object
  The HDIDataTransfer object can be created, by default, using the Keycloak account provided in the environment variables,
  or by providing a dictionary with the Keycloak token, the refresh token, and the expiration time

```
from hid_data_transfer_lib.hid_dt_lib import HIDDataTransfer
from hid_data_transfer_lib.conf.hid_dt_configuration import (
    HidDataTransferConfiguration
)

config = HidDataTransferConfiguration()
# Create a HIDDataTransfer object that uses the Keycloak account provided in the environment variables
dt_client = HIDDataTransfer(conf=config, secure=True)

# OR

# Create a HIDDataTransfer object that uses the provided Keycloak token dictionary
keycloak_token = {
  "username": <keycloak_username>,
  "token": <keycloak_token>,
  "expires_in": <keycloak_token_expires_in>,
  "refresh_token": <keycloak_refresh_token>
}
dt_client = HIDDataTransfer(
  conf=config,
  secure=True,
  keycloak_token=keycloak_token
)
```
- Invoke any data transfer library method using the created object to tranfer data
```
dt_client.ckan2hpc(
  ckan_host=<ckan_endpoint>,
  ckan_api_key=<ckan_apikey>,
  ckan_organization=<ckan_organization>,
  ckan_dataset=<ckan_dataset>,
  ckan_resource=<ckan_resource>,
  hpc_host=<hpc_endpoint>,
  hpc_username=<hpc_username>,
  hpc_secret_key_path=<hpc_secret_key>,
  data_target=<hpc_target_folder>,
)
```

## Support for HPC clusters that require a 2FA token
This library includes methods (suffixed as _2fa) to transfer data to/from HPC clusters that require a 2FA token. These methods offer an optional parameter *callback_2fa* that points to a method that should return (as str) the 2FA token when invoked by the library. If not set by the method caller, these methods call a default implementation that prompts the user (in the standard input) for the token. 

## Data transfer process with NIFI
The following UML Sequence Diagram describes the data transfer process for each command, for instance *ckan2hpc*, leveraging the associated NIFI pipeline.
The Data Transfer (DT) Consumer (a client of this library) invokes a *ckan2hpc* command by following these steps:
- Creates an instance of HidDataTransferConfiguration, which reads the file and environment configuration (see [Installation Instructions](#data-transfer-lib-configuration)).
- Creates an instance of HIDDataTransfer with that configuration object, with secure mode activated, and by passing a dictionary with Keycloak token details. A renewable Keycloak token is required to invoke the remote NIFI REST APIs.

This HIDDataTransfer instance acts as the proxy to trigger one or more data transfer requests, by selecting the correspoding data transfer method. In the following, we explain the internal process to trigger a data transfer from CKAN to HPC, but the common internal process is identical to any other data transfer command.

- The DT consumer invokes the HIDDataTransfer *ckan2hpc* command, passing the required information to identify the CKAN resource to transfer and the destination HPC, including the HPC user's account and data destination path.
- The HIDDataTransfer proxy leverages the NIFIClient class to run the NIFI pipeline for *ckan2hpc*. In turn, this NIFIClient:
  - Instantiates the ckan2hpc pipeline in the NIFI service, taking it from the NIFI registry.
  - Uploads the user's HPC keys (if provided) into the NIFI server, for future HPC ssh access. This keys are safekeeping in a temporary folder accessible only by the user and the NIFI service.
  - Starts the pipeline in the NIFI service. This concrete pipeline retrieves the source resource from CKAN, keeps it in the NIFI queue and transfers it to the target HPC location using SFTP
  - Eventually, if during the data transfer process the keycloak token expires, and additional requests to the REST API of the NIFI service are required, the NIFI Client proxy requests Keycloak to renew the token.
  - Once the data transfer process terminates (or in case of failure), the pipeline is cleaned up in the NIFI service, and the keys uploaded to the NIFI server deleted.

![Data Transfer process with NIFI](images/hid_data_transfer_lib.png)
