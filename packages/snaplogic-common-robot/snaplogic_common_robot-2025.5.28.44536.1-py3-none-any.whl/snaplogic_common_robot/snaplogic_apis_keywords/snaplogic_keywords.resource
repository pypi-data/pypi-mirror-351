*** Settings ***
Documentation       Common Used Keywords for API Testing
...                 This resource file contains high-level keywords that build upon the API keywords.
...                 Keywords cover project setup, account management, file operations, and task execution.

Library             Collections
Library             DateTime
Library             OperatingSystem
Library             JSONLibrary
Library             RequestsLibrary
Library             ../libraries/utils.py
Resource            snaplogic_apis.resource


*** Variables ***
${ORG_SNODE_ID}                     ${EMPTY}
${ACCOUNTS_DETAIL}                  ${NONE}
${GLOBAL_SHARED}                    shared
${project_space_setup}              ${FALSE}    # Default value for project space setup
${TRIGGERED_TASK_PAYLOAD_FILE}      ${CURDIR}/../test_data/triggered_task.json
${SNAPLEX_FILE_PATH}                ${CURDIR}/../test_data/slim_groundplex.json


*** Keywords ***
Set Up Data
    [Documentation]    Sets up the test environment with necessary project structure and data.
    ...
    ...    This keyword performs a complete setup of the SnapLogic test environment by:
    ...    - Authenticating with the provided credentials using Login Api
    ...    - Retrieving and setting the organization's snode ID as global and environment variables
    ...    - Conditionally deleting existing project space based on the ``project_space_setup`` variable
    ...    - Creating new project space and project when ``project_space_setup`` is enabled
    ...    - Setting up the foundation for subsequent API testing operations
    ...
    ...    The keyword will skip organization and project setup if ``org_name`` is set to ``${NONE}``,
    ...    returning ``${NONE}`` immediately after authentication. Project space operations (delete, create space,
    ...    create project) are only performed when the global variable ``${project_space_setup}``
    ...    is set to ``'True'``. When ``${project_space_setup}`` is ``${FALSE}`` (default), the keyword
    ...    expects that the project space and project already exist and will skip all project setup operations.
    ...    Note that ``${project_space_setup}`` is not a parameter of this keyword
    ...    but a global variable that must be set separately before calling this keyword.
    ...    The ``env_file_path`` parameter is accepted but not currently processed
    ...    by this keyword - it may be used by other keywords in the test flow.
    ...
    ...    *Global Variables Set:*
    ...    - Sets global variable ``${ORG_SNODE_ID}`` with the organization's snode ID
    ...    - Sets environment variable ``ORG_SNODE_ID`` with the same value
    ...    - Logs project space information to console
    ...
    ...    *Global Variable Dependencies:*
    ...    - ``${project_space_setup}``: Controls project setup behavior
    ...    - When ``'True'``: Deletes existing project space and creates new project space/project
    ...    - When ``${FALSE}`` (default): Assumes project space and project already exist, skips setup
    ...    - This variable must be explicitly set to ``'True'`` if project creation is needed
    ...
    ...    *Arguments:*
    ...    - ``url``: Base URL for the SnapLogic API endpoint
    ...    - ``username``: Username for API authentication
    ...    - ``password``: Password for API authentication
    ...    - ``org_name``: Name of the target organization
    ...    - ``project_space``: Name of the project space to manage
    ...    - ``project_name``: Name of the project to create within the space
    ...    - ``env_file_path``: Path to environment configuration file (optional, default: ``${None}`` - parameter accepted but not processed by this keyword)
    ...
    ...    *Returns:*
    ...    The organization's snode ID as a string, or ``${NONE}`` if ``org_name`` is ``${NONE}``
    ...
    ...    *Examples:*
    ...    | # Basic setup as used in test suites |
    ...    | ${org_id} = | Set Up Data | ${URL} | ${ORG_ADMIN_USER} | ${ORG_ADMIN_PASSWORD} | ${ORG_NAME} | ${PROJECT_SPACE} | ${PROJECT_NAME} | ${ENV_FILE_PATH} |
    ...    |
    ...    | # Setup with minimal required parameters |
    ...    | ${org_id} = | Set Up Data | https://api.snaplogic.com | User | Password | MyOrg | ProjectSpace | Project |
    ...    |
    ...    | # Setup without environment file |
    ...    | ${org_id} = | Set Up Data | https://api.snaplogic.com | User | Password | MyOrg | ProjectSpace | TestProject | ${None} |
    ...    |
    ...    | # Skip organization and project setup (only authenticate) |
    ...    | Set Up Data | https://api.snaplogic.com | myuser | mypass | ${NONE} | TestSpace | TestProject |
    ...    |
    ...    | # Setup when project_space_setup is disabled (expects existing project space/project) |
    ...    | Set Variable | ${project_space_setup} | False |
    ...    | ${org_id} = | Set Up Data | https://api.snaplogic.com | myuser | mypass | MyOrg | TestSpace | TestProject |
    ...    |
    ...    | # Setup with project creation enabled |
    ...    | Set Variable | ${project_space_setup} | True |
    ...    | ${org_id} = | Set Up Data | https://api.snaplogic.com | myuser | mypass | MyOrg | NewSpace | NewProject |
    ...    *Prerequisites:*
    ...    - Valid SnapLogic API credentials
    ...    - Network connectivity to the SnapLogic platform
    ...    - Proper permissions for organization and project operations
    ...
    ...    *See also:* `Login Api`, `Get Org Snode ID`, `Delete ProjectSpace`, `Create Project Space`, `Create Project`
    [Arguments]
    ...    ${url}
    ...    ${username}
    ...    ${password}
    ...    ${org_name}
    ...    ${project_space}
    ...    ${project_name}
    ...    ${env_file_path}=${None}
    ${auth}    Create List    ${username}    ${password}
    Login Api    ${auth}
    IF    $org_name == $NONE    RETURN
    ${org_snode_id}    Get Org Snode ID    ${org_name}
    Set Global Variable    ${ORG_SNODE_ID}    ${org_snode_id}
    Set Environment Variable    ORG_SNODE_ID    ${org_snode_id}
    Log    Project space is: ${project_space}    level=CONSOLE
    IF    '${project_space_setup}' == 'True'
        Delete ProjectSpace    ${org_name}    ${project_space}
    END
    IF    '${project_space_setup}'=='True'
        Create Project Space    ${org_name}    ${project_space}
    END
    IF    '${project_space_setup}'=='True'
        Create Project    ${org_name}    ${project_space}    ${project_name}
    END
    RETURN    ${org_snode_id}

Get Project List
    [Documentation]    Retrieves the list of projects in a project space.
    ...
    ...    This keyword calls the SnapLogic API to get all projects within a specified
    ...    project space and returns the entries for further processing. It's commonly
    ...    used to check if projects exist before creating new ones or to list all
    ...    available projects in a space.
    ...
    ...    *Arguments:*
    ...    - ``org_name``: Name of the organization
    ...    - ``project_space``: Name of the project space to query
    ...
    ...    *Returns:*
    ...    A list of project entry dictionaries, each containing project metadata such as
    ...    name, asset_type, creation date, and other project properties
    ...
    ...    *Examples:*
    ...    | ${projects} = | Get Project List | my_organization | my_project_space |
    ...    | Log | Found ${len(${projects})} projects |
    ...    |
    ...    | # Check if specific project exists |
    ...    | ${projects} = | Get Project List | ${ORG_NAME} | ${PROJECT_SPACE} |
    ...    | ${exists} = | Evaluate | any(p['name'] == 'MyProject' for p in $projects) |
    ...
    ...    *See also:* `Create Project`, `Get Org List`
    [Arguments]    ${org_name}    ${project_space}
    Log    Project Space [${project_space}] is used"    level=CONSOLE
    ${resp}    Get Project List Api    ${org_name}    ${project_space}
    RETURN    ${resp.json()['response_map']['entries']}

Create Project
    [Documentation]    Creates a new project if it doesn't already exist.
    ...
    ...    This keyword first checks if a project with the specified name already exists
    ...    in the project space. If the project exists, it logs a message and skips creation.
    ...    If the project doesn't exist, it creates a new directory-type project with the
    ...    specified name and default metadata settings.
    ...
    ...    *Arguments:*
    ...    - ``org_name``: Name of the organization
    ...    - ``project_space``: Name of the project space where the project will be created
    ...    - ``project_name``: Name of the project to create
    ...
    ...    *Returns:*
    ...    None (logs creation status to console)
    ...
    ...    *Examples:*
    ...    | Create Project | my_organization | my_project_space | my_project |
    ...    |
    ...    | # Create project with variables |
    ...    | Create Project | ${ORG_NAME} | ${PROJECT_SPACE} | ${PROJECT_NAME} |
    ...
    ...    *See also:* `Get Project List`, `Create Project Space`
    [Arguments]    ${org_name}    ${project_space}    ${project_name}
    @{objects}    Get Project List    ${org_name}    ${project_space}
    ${exists}    Evaluate    any('${project_name}' == obj["name"] for obj in $objects)
    IF    ${exists}
        Log    Project Name [${project_name}] exists"    level=CONSOLE
    ELSE
        ${metadata}    Create Dictionary    pattern=false    validation=null
        ${request_payload}    Create Dictionary    asset_type=Dir    metadata=${metadata}    name=${project_name}
        ${resp}    Create Project Api    ${org_name}    ${project_space}    ${project_name}    ${request_payload}
    END

Get Org List
    [Documentation]    Retrieves the list of assets in an organization.
    ...    *Arguments:*
    ...    - ``org_name``: Name of the organization
    ...    *Returns:*
    ...    - List of organization entries
    ...    *Example:*
    ...    | ${org_entries} | Get Org List | my_organization |
    [Arguments]    ${org_name}
    ${resp}    Get Org List Api    ${org_name}
    RETURN    ${resp.json()['response_map']['entries']}

Create Project Space
    [Documentation]    Creates a new project space if it doesn't already exist.
    ...
    ...    This keyword checks if a project space with the specified name already exists
    ...    in the organization. If it exists, it logs a message and skips creation.
    ...    If it doesn't exist, it creates a new directory-type project space with the
    ...    specified name. Project spaces are containers for organizing multiple projects
    ...    within an organization.
    ...
    ...    *Arguments:*
    ...    - ``org_name``: Name of the organization
    ...    - ``project_space``: Name of the project space to create
    ...
    ...    *Returns:*
    ...    None (logs creation status to console)
    ...
    ...    *Examples:*
    ...    | Create Project Space | my_organization | my_project_space |
    ...    |
    ...    | # Create project space with variables |
    ...    | Create Project Space | ${ORG_NAME} | ${PROJECT_SPACE} |
    ...
    ...    *See also:* `Get Org List`, `Delete ProjectSpace`, `Create Project`
    [Arguments]    ${org_name}    ${project_space}
    @{objects}    Get Org List    ${org_name}
    ${exists}    Evaluate    any('${project_space}' == obj["name"] for obj in $objects)
    IF    ${exists}
        Log    Project Space [${project_space}] exists"    level=CONSOLE
    ELSE
        ${request_payload}    Create Dictionary    asset_type=Dir    name=${project_space}
        Log    Project Space [${project_space}] before creating"    level=CONSOLE
        ${resp}    Create Project Space Api    ${org_name}    ${project_space}    ${request_payload}
        Log    Project Space [${project_space}] created"    level=CONSOLE
    END

Delete ProjectSpace
    [Documentation]    Deletes a project space if it exists.
    ...
    ...    *Arguments:*
    ...    - ``org_name``: Name of the organization
    ...    - ``project_space``: Name of the project space to delete
    ...
    ...    *Example:*
    ...    | Delete ProjectSpace | my_organization | my_project_space |
    [Arguments]    ${org_name}    ${project_space}
    @{org_list}    Get Org List    ${org_name}
    ${org_list_exists}    Evaluate    any('${project_space}' == obj["name"] for obj in $org_list)
    IF    ${org_list_exists}
        ${resp}    Delete ProjectSpace Api    ${org_name}    ${project_space}
        Log    ProjectSpace Name [${project_space}] was deleted"    level=CONSOLE
    ELSE
        Log    ProjectSpace Name [${project_space}] do not exist"    level=CONSOLE
    END

Get Org Snode ID
    [Documentation]    Retrieves the snode ID for an organization.
    ...
    ...    *Arguments:*
    ...    - ``org_name``: Name of the organization
    ...
    ...    *Returns:*
    ...    - The organization's snode ID
    ...
    ...    *Example:*
    ...    | ${snode_id} | Get Org Snode ID | my_organization |
    [Arguments]    ${org_name}
    ${resp}    Get Org List Api    ${org_name}
    RETURN    ${resp.json()['response_map']['entries'][0]['parent_snode_id']}

Create All Accounts
    [Documentation]    Creates all accounts defined in the environment file.
    ...
    ...    This keyword loads environment variables from the specified file, renders
    ...    account templates with those variables, and creates all defined accounts
    ...    in the SnapLogic platform. It skips creating accounts that already exist
    ...    and updates account class FQIDs to use the latest versions.
    ...
    ...    *Global Variable Dependencies:*
    ...    - ``${ACCOUNT_PAYLOAD_PATH}``: Path to account template files directory
    ...    - ``${ACCOUNT_LOCATION_PATH}``: Target location path for account creation
    ...    - ``${org_name}``: Organization name (must be set globally)
    ...
    ...    *Arguments:*
    ...    - ``env_file_path``: Path to the environment file containing account variable definitions
    ...
    ...    *Returns:*
    ...    None (logs account creation status for each account)
    ...
    ...    *Examples:*
    ...    | Create All Accounts | /path/to/env_file.json |
    ...    |
    ...    | # Create accounts using variables |
    ...    | Create All Accounts | ${ENV_FILE_PATH} |
    ...
    ...    *See also:* `Create Account`, `Get Account Version By Class Fqid`
    [Arguments]    ${env_file_path}
    Log    env_file_path is:${env_file_path}    level=CONSOLE
    ${env_variables}    Load Env Variables    ${env_file_path}
    Log    Accounts_path is:${ACCOUNT_PAYLOAD_PATH}    level=CONSOLE
    ${acc_payloads}    Render Env Variables for JSON File    ${ACCOUNT_PAYLOAD_PATH}    ${env_variables}

    # Check if account payloads were found
    IF    $acc_payloads == [] or $acc_payloads == None
        Fail    No account templates found in path: ${ACCOUNT_PAYLOAD_PATH}
    END

    Log    org Name is:${org_name}    level=CONSOLE
    ${entries}    Get Project List    ${org_name}    ${ACCOUNT_LOCATION_PATH}
    ${accounts_entries}    Evaluate    [x for x in $entries if x['asset_type'] == 'Account']
    FOR    ${payload}    IN    @{acc_payloads}
        ${acc_name}    Set Variable    ${payload}[account][property_map][info][label][value]
        ${account_exist}    Evaluate    any(x for x in $accounts_entries if x['name'] == '${acc_name}')
        IF    ${account_exist}
            Log    Account [${acc_name}] exists, skip creation    level=CONSOLE
        ELSE
            ${class_fqid}    Set Variable    ${payload}[account][class_fqid]
            ${class_fqid}    Get Account Version By Class Fqid    ${class_fqid}
            ${payload}[account][class_fqid]    Set Variable    ${class_fqid}
            Log    Account payoad is: ${payload}    level=CONSOLE
            ${resp}    Create Account API    ${org_name}/${ACCOUNT_LOCATION_PATH}    ${acc_name}    ${payload}
            Log    Account [${acc_name}] created at location ${org_name}/${ACCOUNT_LOCATION_PATH}    level=CONSOLE
        END
    END

Create Account
    [Documentation]    Creates a single account from a JSON file that includes Jinja-style template placeholders.
    ...
    ...    *Arguments:*
    ...    - ``account_file_path``: Path to the account JSON file with placeholders.
    ...    - ``env_file_path``: Path to the environment file providing variable values.
    ...
    ...    *Example:*
    ...    | Create Account From File | /path/to/account.json | /path/to/env_file.json |
    [Arguments]    ${account_file_path}    ${env_file_path}

    Log    📄 Loading environment variables from: ${env_file_path}    level=CONSOLE
    ${env_variables}    Load Env Variables    ${env_file_path}

    Log    🧩 Rendering account JSON with env variables    level=CONSOLE
    ${payloads}    Render Env Variables for JSON File    ${account_file_path}    ${env_variables}
    ${payload}    Get From List    ${payloads}    0

    ${acc_name}    Set Variable    ${payload}[account][property_map][info][label][value]
    Log    🔍 Account Name: ${acc_name}, Org: ${org_name}    level=CONSOLE

    ${entries}    Get Project List    ${org_name}    ${ACCOUNT_LOCATION_PATH}
    ${accounts_entries}    Evaluate    [x for x in $entries if x['asset_type'] == 'Account']
    ${account_exist}    Evaluate    any(x for x in $accounts_entries if x['name'] == '${acc_name}')

    IF    ${account_exist}
        Log    ✅ Account [${acc_name}] already exists. Skipping creation.    level=CONSOLE
    ELSE
        ${class_fqid}    Set Variable    ${payload}[account][class_fqid]
        ${class_fqid}    Get Account Version By Class Fqid    ${class_fqid}
        ${payload}[account][class_fqid]    Set Variable    ${class_fqid}

        Log    🚀 Creating account with payload: ${payload}    level=CONSOLE
        ${resp}    Create Account API    ${org_name}/${ACCOUNT_LOCATION_PATH}    ${acc_name}    ${payload}
        Log    🎉 Account [${acc_name}] created at ${org_name}/${ACCOUNT_LOCATION_PATH}    level=CONSOLE
    END

Get Account Version By Class Fqid
    [Documentation]    Retrieves the account version by class FQID.
    ...
    ...    *Arguments:*
    ...    - ``class_fqid``: The class FQID to get the version for
    ...
    ...    *Returns:*
    ...    - The account class FQID with version
    ...
    ...    *Example:*
    ...    | ${account_fqid} | Get Account Version By Class Fqid | my_class_fqid |
    [Arguments]    ${class_fqid}
    IF    ${ACCOUNTS_DETAIL} == None
        ${accounts_detail}    GET Accounts Detail
        ${ACCOUNTS_DETAIL}    Set Variable    ${accounts_detail}
    END

    ${class_fqid_match}    Evaluate    re.search(r"(.+?)_", $class_fqid)
    ${class_id}    Set Variable    ${class_fqid_match.group(1)}
    ${account_detail}    Set Variable    ${ACCOUNTS_DETAIL}[${class_id}]
    ${account_class_fqid}    Set Variable    ${account_detail}[class_fqid]
    RETURN    ${account_class_fqid}

Get Accounts Detail
    [Documentation]    Retrieves detailed information about all accounts.
    ...
    ...    *Returns:*
    ...    - A dictionary containing the response map with account details
    ...
    ...    *Example:*
    ...    | ${accounts} | Get Accounts Detail |
    ${resp}    Get Accounts Detail Api
    RETURN    ${resp.json()['response_map']}

Import Pipeline
    [Documentation]    Imports a pipeline from a JSON file to a specified path.
    ...
    ...    This keyword loads a pipeline definition from a JSON file, wraps it in the
    ...    required import payload structure, sets the pipeline name, and imports it
    ...    to the specified SnapLogic path. The imported pipeline can then be used
    ...    to create triggered tasks or execute directly.
    ...
    ...    *Arguments:*
    ...    - ``pipeline_file_path``: Path to the pipeline JSON file (.slp file)
    ...    - ``pipeline_name``: Name to assign to the imported pipeline in SnapLogic
    ...    - ``path``: Target path where the pipeline will be imported (e.g., /${org}/${project_space}/${project})
    ...
    ...    *Returns:*
    ...    Dictionary containing the response map with information about the imported pipeline,
    ...    including the pipeline's snode_id for future reference
    ...
    ...    *Examples:*
    ...    | ${pipeline_info} = | Import Pipeline | ${PIPELINE_DIR}/my_pipeline.slp | My Pipeline | /${ORG_NAME}/${PROJECT_SPACE}/${PROJECT_NAME} |
    ...    | ${snode_id} = | Set Variable | ${pipeline_info}[snode_id] |
    ...    |
    ...    | # Import pipeline with variables |
    ...    | ${pipeline_info} = | Import Pipeline | ${CURDIR}/pipelines/data_processing.slp | Data Processing Pipeline | ${project_path} |
    ...
    ...    *See also:* `Create Triggered Task`, `Import Pipelines From Template`
    [Arguments]    ${pipeline_file_path}    ${pipeline_name}    ${path}
    ${pipeline}    Load Json From File    ${pipeline_file_path}
    ${pipeline_new}    Create Dictionary    pipe=EMPTY
    ${pipeline_new}    Set To Dictionary    ${pipeline_new}    pipe=${pipeline}
    ${import_pipeline_payload}    Set Variable    ${pipeline_new}

    # The value of the fields within ${import_pipeline_payload} are modified
    ${import_pipeline_payload}[pipe][property_map][info][label][value]    Set Variable    ${pipeline_name}
    Log    Payload created for Creating Pipeline is: ${import_pipeline_payload}
    ${response}    Import Pipeline Api    ${path}    ${import_pipeline_payload}
    Log    ...Import Pipeline URL is: ${response.url}    level=CONSOLE
    Log    ...pipeline_name is....:${pipeline_name}    level=CONSOLE
    Log    ...pipeline_filePath is....:${pipeline_file_path}    level=CONSOLE
    Log    ...pipeline:(${pipeline_name})_imported to projectpath...:${path}    level=CONSOLE
    log    ...pipeline_snodeID....:${response.json()['response_map']}
    RETURN    ${response.json()['response_map']}

GET Runtime Path Id
    [Documentation]    Retrieves the runtime path ID for a specified organization and plex.
    ...
    ...    *Arguments:*
    ...    - ``org_name``: Organization name (default: ${org_name})
    ...    - ``default_plex``: Plex name to find (default: ${default_plex})
    ...
    ...    *Returns:*
    ...    - The runtime path ID corresponding to the specified plex
    ...
    ...    *Example:*
    ...    | ${runtime_id} | GET Runtime Path Id | my_org | my_plex |
    [Arguments]    ${org_name}=${org_name}    ${default_plex}=${default_plex}
    ${response}    GET Runtime Path Id Api    ${org_name}
    @{snaplex_list}    Set Variable    ${response.json()['response_map']}
    FOR    ${line}    IN    @{snaplex_list}
        IF    $line['label'] == $default_plex
            RETURN    ${line['runtime_path_id']}
        END
    END

Create Triggered Task
    [Documentation]    Creates a task with the specified parameters.
    ...
    ...    *Arguments:*
    ...    - ``task_name``: Name for the new task
    ...    - ``pipeline_snodeid``: The pipeline snode ID
    ...    - ``plex_name``: Name of the plex to use
    ...    - ``path``: Path where the task will be created
    ...    - ``pipeline_params``: Dictionary of pipeline parameters to add/update (optional)
    ...    - ``execution_timeout``: Value for execution timeout (optional)
    ...    - ``notification``: Dictionary with notification settings (optional)
    ...    - ``num_instances``: Number of instances (optional)
    ...    - ``debug_next_runs``: Number of debug next runs (optional)
    ...
    ...    *Returns:*
    ...    - A tuple containing the task payload and the snode ID of the created task
    ...
    ...    *Examples:*
    ...    | # Basic usage with required arguments only |
    ...    | ${task_payload}    ${task_snode_id} | Create Task | My Task | ${pipeline_id} | default_plex | /org/project | task_template.json |
    ...    |
    ...    | # With execution timeout and pipeline parameters |
    ...    | ${pipeline_params}= | Create Dictionary | param1=value1 | param2=value2 |
    ...    | ${task_payload}    ${task_snode_id} | Create Task | My Task | ${pipeline_id} | default_plex | /org/project | task_template.json | pipeline_params=${pipeline_params} | execution_timeout=3600 |
    ...    |
    ...    | # With notification settings |
    ...    | ${notification}= | Create Dictionary | email=${TRUE} | recipients=user@example.com |
    ...    | ${task_payload}    ${task_snode_id} | Create Task | Task With Notifications | ${pipeline_id} | default_plex | /org/project | task_template.json | notification=${notification} |
    ...    |
    ...    | # With multiple optional parameters |
    ...    | ${pipeline_params}= | Create Dictionary | env=production | debug=${FALSE} |
    ...    | ${notification}= | Create Dictionary | email=${TRUE} | slack=${TRUE} |
    ...    | ${task_payload}    ${task_snode_id} | Create Task | Complex Task | ${pipeline_id} | default_plex | /org/project | task_template.json | pipeline_params=${pipeline_params} | execution_timeout=7200 | notification=${notification} | num_instances=3 | debug_next_runs=2 |
    [Arguments]    ${task_name}    ${pipeline_snodeid}    ${plex_name}    ${path}
    ...    ${pipeline_params}=${None}    ${execution_timeout}=${None}    ${notification}=${None}
    ...    ${num_instances}=${None}    ${debug_next_runs}=${None}

    Log    Current directory: ${CURDIR}    level=CONSOLE
    ${payload}    Set Variable    ${TRIGGERED_TASK_PAYLOAD_FILE}
    ${task_payload}    Load Json From File    ${payload}
    Log    payload is: ${payload}    level=CONSOLE
    ${task_payload}    Load Json From File    ${payload}
    ${runtime_path_id}    GET Runtime Path Id    ${org_name}    ${plex_name}
    Log    Plex_name is: ${plex_name}    level=CONSOLE
    Log    runtime_path_id is: ${runtime_path_id}    level=CONSOLE

    # Only update these basic fields
    Set To Dictionary    ${task_payload}    path_id=${path}
    Set To Dictionary    ${task_payload}    job_name=${task_name}
    Set To Dictionary    ${task_payload}    name=${task_name}
    Set To Dictionary    ${task_payload}    org_path=/${org_name}

    ${parameters_value}    Get From Dictionary    ${task_payload}    parameters

    # Always update these required fields
    Set To Dictionary    ${parameters_value}    runtime_path_id=${runtime_path_id}
    Set To Dictionary    ${parameters_value}    pipeline_snode_id=${pipeline_snodeid}

    # Only update pipeline_parameters if provided
    IF    ${pipeline_params} is not ${None}
        IF    'pipeline_parameters' not in $parameters_value
            Set To Dictionary    ${parameters_value}    pipeline_parameters=&{EMPTY}
        END
        Set To Dictionary    ${parameters_value}[pipeline_parameters]    &{pipeline_params}
    END

    # Only update execution_timeout if provided
    IF    ${execution_timeout} is not ${None}
        Set To Dictionary    ${parameters_value}    execution_timeout=${execution_timeout}
    END

    # Only update notification if provided
    IF    ${notification} is not ${None}
        Set To Dictionary    ${parameters_value}    notification=${notification}
    END

    # Only update num_instances if provided
    IF    ${num_instances} is not ${None}
        Set To Dictionary    ${parameters_value}    num_instances=${num_instances}
    END

    # Only update debug_next_runs if provided
    IF    ${debug_next_runs} is not ${None}
        Set To Dictionary    ${parameters_value}    debug_next_runs=${debug_next_runs}
    END

    Log    Payload created for Creating Task: ${task_payload}    level=CONSOLE
    ${response}    Create Task Api    ${task_payload}
    Should Be Equal As Strings    ${response.status_code}    201
    RETURN    ${task_payload}    ${response.json()['response_map']['snode_id']}

Get Unique Id
    [Documentation]    Generates a unique ID using the current timestamp.
    ...
    ...    *Returns:*
    ...    - A string containing a unique ID based on the current date and time
    ...
    ...    *Example:*
    ...    | ${unique_id} | Get Unique Id |
    ${UNIQUE_ID}    Get Current Date    result_format=%Y%m%d%H%M%S%f
    RETURN    ${UNIQUE_ID}

Run Triggered Task
    [Documentation]    Runs a triggered task with optional parameters and retries on failure.
    ...
    ...    *Arguments:*
    ...    - ``path``: Path where the task is located
    ...    - ``task_name``: Name of the task to run
    ...    - ``params``: Optional parameters for the task (default: ${EMPTY})
    ...
    ...    *Returns:*
    ...    - The response from the task execution
    ...
    ...    *Example:*
    ...    | ${task_response} | Run Triggered Task | /org/project | My Task | param1=value1&param2=value2 |
    [Arguments]    ${path}    ${task_name}    ${params}=${EMPTY}
    ${response}    Wait Until Keyword Succeeds
    ...    30 sec
    ...    5 sec
    ...    Run Triggered Task Api
    ...    ${path}
    ...    ${task_name}
    ...    ${params}
    RETURN    ${response}

Create Snaplex
    [Documentation]    Creates a new snaplex using configuration from files.
    ...
    ...    *Arguments:*
    ...    - ``env_file_path``: Path to the environment variables file
    ...    - ``GROUNDPLEX_NAME``: Name of the groundplex (optional, overrides env file)
    ...    - ``GROUNDPLEX_ENV``: Environment of the groundplex (optional, overrides env file)
    ...    - ``ORG_NAME``: Organization name (optional, overrides env file)
    ...    - ``RELEASE_BUILD_VERSION``: Release build version (optional, overrides env file)
    ...    - ``SNAP_PLEX_LOCATION``: Custom container path for the snaplex (optional, overrides env file)
    ...
    ...    *Returns:*
    ...    - A dictionary with the creation status and message
    ...
    ...    *Example:*
    ...    | ${result} | Create Snaplex | ${CONFIG_DIR}/snaplex.json | ${CONFIG_DIR}/env.json | slim-groundplex | slimgroundplexdev | my-org | main-30028 | /custom/container/path |
    [Arguments]
    ...    ${env_file_path}
    ...    ${GROUNDPLEX_NAME}=${EMPTY}
    ...    ${GROUNDPLEX_ENV}=${EMPTY}
    ...    ${ORG_NAME}=${EMPTY}
    ...    ${RELEASE_BUILD_VERSION}=${EMPTY}
    ...    ${SNAP_PLEX_LOCATION}=${EMPTY}

    Log    snaplex_file_path is: ${snaplex_file_path}    level=CONSOLE
    Log    env_file_path is: ${env_file_path}    level=CONSOLE

    # Log all input parameters to help with debugging
    Log    Input GROUNDPLEX_NAME: ${GROUNDPLEX_NAME}    level=CONSOLE
    Log    Input GROUNDPLEX_ENV: ${GROUNDPLEX_ENV}    level=CONSOLE
    Log    Input ORG_NAME: ${ORG_NAME}    level=CONSOLE
    Log    Input RELEASE_BUILD_VERSION: ${RELEASE_BUILD_VERSION}    level=CONSOLE
    Log    Input SNAP_PLEX_LOCATION: ${SNAP_PLEX_LOCATION}    level=CONSOLE

    # Load environment variables
    ${env_variables}    Load Env Variables    ${env_file_path}

    # Set a default SNAP_PLEX_LOCATION if not in env variables
    ${has_container_path}    Run Keyword And Return Status
    ...    Dictionary Should Contain Key
    ...    ${env_variables}
    ...    SNAP_PLEX_LOCATION
    IF    not ${has_container_path}
        ${org_name}    Get From Dictionary    ${env_variables}    ORG_NAME
        Set To Dictionary    ${env_variables}    SNAP_PLEX_LOCATION=/${org_name}/shared
        Log    Setting default SNAP_PLEX_LOCATION to "/${org_name}/shared"    level=CONSOLE
    END

    # Store original values for logging
    ${original_groundplex_name}    Get From Dictionary    ${env_variables}    GROUNDPLEX_NAME    default=Not Found
    ${original_groundplex_env}    Get From Dictionary    ${env_variables}    GROUNDPLEX_ENV    default=Not Found
    ${original_org_name}    Get From Dictionary    ${env_variables}    ORG_NAME    default=Not Found
    ${original_release_build}    Get From Dictionary    ${env_variables}    RELEASE_BUILD_VERSION    default=Not Found
    ${original_snap_plex_path}    Get From Dictionary    ${env_variables}    SNAP_PLEX_LOCATION    default=Not Found

    # Override environment variables with provided arguments if not empty or ${None}
    IF    '${GROUNDPLEX_NAME}' != '${EMPTY}' and '${GROUNDPLEX_NAME}' != '${None}'
        Set To Dictionary    ${env_variables}    GROUNDPLEX_NAME=${GROUNDPLEX_NAME}
        Log    Updated GROUNDPLEX_NAME from "${original_groundplex_name}" to "${GROUNDPLEX_NAME}"    level=CONSOLE
    END

    IF    '${GROUNDPLEX_ENV}' != '${EMPTY}' and '${GROUNDPLEX_ENV}' != '${None}'
        Set To Dictionary    ${env_variables}    GROUNDPLEX_ENV=${GROUNDPLEX_ENV}
        Log    Updated GROUNDPLEX_ENV from "${original_groundplex_env}" to "${GROUNDPLEX_ENV}"    level=CONSOLE
    END

    IF    '${ORG_NAME}' != '${EMPTY}' and '${ORG_NAME}' != '${None}'
        Set To Dictionary    ${env_variables}    ORG_NAME=${ORG_NAME}
        Log    Updated ORG_NAME from "${original_org_name}" to "${ORG_NAME}"    level=CONSOLE
    END

    IF    '${RELEASE_BUILD_VERSION}' != '${EMPTY}' and '${RELEASE_BUILD_VERSION}' != '${None}'
        Set To Dictionary    ${env_variables}    RELEASE_BUILD_VERSION=${RELEASE_BUILD_VERSION}
        Log
        ...    Updated RELEASE_BUILD_VERSION from "${original_release_build}" to "${RELEASE_BUILD_VERSION}"
        ...    level=CONSOLE
    END

    # Update SNAP_PLEX_LOCATION in env variables if provided
    IF    '${SNAP_PLEX_LOCATION}' != '${EMPTY}' and '${SNAP_PLEX_LOCATION}' != '${None}'
        Set To Dictionary    ${env_variables}    SNAP_PLEX_LOCATION=/${org_name}/${SNAP_PLEX_LOCATION}/
        Log
        ...    Updated SNAP_PLEX_LOCATION from "${original_snap_plex_path}" to "${SNAP_PLEX_LOCATION}"
        ...    level=CONSOLE
    END

    # Add special mapping for CONTAINER_PATH (for template compatibility)
    ${snap_plex_location}    Get From Dictionary    ${env_variables}    SNAP_PLEX_LOCATION
    Set To Dictionary    ${env_variables}    CONTAINER_PATH=${snap_plex_location}
    Log    Set CONTAINER_PATH to match SNAP_PLEX_LOCATION: ${snap_plex_location}    level=CONSOLE

    ${snaplex_file_path}    Set Variable    ${CURDIR}/../test_data/slim_groundplex.json
    ${snaplex_payloads}    Render Env Variables for JSON File    ${snaplex_file_path}    ${env_variables}

    # Assuming your function returns a list, take the first item or iterate as needed
    ${payload}    Set Variable    ${snaplex_payloads}[0]

    # Check if container_path is correctly rendered in the payload
    ${container_path_in_payload}    Get From Dictionary    ${payload}    container_path
    Log    container_path in rendered payload: ${container_path_in_payload}    level=CONSOLE

    # Ensure the container_path in the payload matches our location value
    ${snap_plex_location}    Get From Dictionary    ${env_variables}    SNAP_PLEX_LOCATION
    Set To Dictionary    ${payload}    container_path=${snap_plex_location}
    Log    Ensuring container_path in payload is set to: ${snap_plex_location}    level=CONSOLE

    Log    Final snaplex configuration: ${payload}    level=CONSOLE

    # Now send the fully rendered payload to the API
    # Try to create snaplex
    ${status}    ${response}    Run Keyword And Ignore Error    Create Snaplex Api    ${payload}

    # Success case: 201 Created
    ${is_success}    Run Keyword And Return Status
    ...    Run Keywords
    ...    Should Be Equal    ${status}    PASS    AND
    ...    Should Be Equal As Strings    ${response.status_code}    201

    # Conflict case: 409 Conflict
    ${is_conflict}    Run Keyword And Return Status
    ...    Run Keywords
    ...    Should Be Equal    ${status}    FAIL    AND
    ...    Should Contain    ${response}    409

    # Handle 409 conflict case
    IF    ${is_conflict}
        ${result}    Log    ***Resource already exists (409 Conflict). Skipping creation****.    level=CONSOLE
        ${result}    Evaluate    {"status": "success", "message": "Resource already exists"}
    ELSE
        ${result}    Set Variable    ${None}
    END

    # Handle 201 success case
    IF    ${is_success}
        ${result}    Evaluate    {"status": "success", "message": "Resource created"}
    ELSE IF    ${is_conflict}
        ${result}    Set Variable    ${result}
    ELSE
        ${result}    Set Variable    ${None}
    END

    # Fail if neither condition is met
    IF    not ${is_success} and not ${is_conflict}
        Fail    Status is neither 409 nor 201. Error: ${response}
    END
    RETURN    ${result}

Create Directory If Not Exists
    [Documentation]    Creates a directory if it doesn't already exist.
    ...
    ...    *Arguments:*
    ...    - ``directory``: Path of the directory to check/create
    ...
    ...    *Example:*
    ...    | Create Directory If Not Exists | ${CONFIG_DIR}/logs |
    [Arguments]    ${directory}
    ${dir_exists}    Run Keyword And Return Status    Directory Should Exist    ${directory}
    IF    not ${dir_exists}    Create Directory    ${directory}
    Log    Directory check completed for: ${directory}

Download And Save Config File
    [Documentation]    Downloads a configuration file from a URL and saves it to the specified location.
    ...
    ...    *Arguments:*
    ...    - ``url``: URL from which to download the file
    ...    - ``CONFIG_DIR``: Directory where the file should be saved
    ...    - ``SLPROPZ_FILE_NAME``: Filename to use when saving
    ...
    ...    *Example:*
    ...    | Download And Save Config File | https://example.com/config | ${CONFIG_DIR} | config.slpropz |
    [Arguments]    ${url}    ${CONFIG_DIR}    ${PROJECT_LOCATION}    ${SLPROPZ_FILE_NAME}
    Create Directory If Not Exists    ${CONFIG_DIR}
    ${response}    Download slpropz file Api    ${url}    ${PROJECT_LOCATION}
    Create Binary File    ${CONFIG_DIR}/${SLPROPZ_FILE_NAME}    ${response.content}
    Log    File saved to ${CONFIG_DIR}/${SLPROPZ_FILE_NAME}    level=CONSOLE

Download Config File
    [Documentation]    Downloads a config file from the URL and saves it to the specified location.
    ...
    ...    *Arguments:*
    ...    - ``CONFIG_FILE``: Path where the file should be saved
    ...
    ...    *Example:*
    ...    | Download Config File | ${CONFIG_DIR}/settings.cfg |
    [Arguments]    ${CONFIG_FILE}

    Create Session    download_session    ${URL}    verify=True
    ${response}    GET On Session    download_session    ${EMPTY}    stream=${TRUE}

    # Check if request was successful
    Should Be Equal As Strings    ${response.status_code}    200

    # Save the response content to file
    Create Binary File    ${CONFIG_FILE}    ${response.content}
    Log    File successfully downloaded and saved to ${CONFIG_FILE}

Get Snaplex Status
    [Documentation]    Retrieves and extracts the status of a Snaplex instance.
    ...
    ...    This keyword calls the Get Snaplex Status Api and then processes the response
    ...    to extract just the status field from the response structure.
    ...
    ...    *Arguments:*
    ...    - ``plex_path``: Path to the Snaplex instance
    ...    - ``expected_status``: Expected HTTP status code (default: 200)
    ...
    ...    *Returns:*
    ...    - String containing the Snaplex status value (e.g., "not_running", "up_and_running")
    ...
    ...    *Example:*
    ...    | ${status} | Get Snaplex Status | my_plex_path | 200 |
    ...    | Should Be Equal | ${status} | RUNNING |
    [Arguments]    ${plex_path}    ${expected_status}=200
    ${response}    Get Snaplex Status Api    ${plex_path}    ${expected_status}
    ${json_body}    Set Variable    ${response.json()}
    ${response_map}    Set Variable    ${json_body['response_map']}
    ${first_key}    Evaluate    list(${response_map}.keys())[0]
    ${cc_info}    Get From Dictionary    ${response_map['${first_key}']}    cc_info
    ${status}    Get From Dictionary    ${cc_info}    status
    Log To Console    \nSnaplex status is: ${status}\n
    RETURN    ${status}

Snaplex Status Should Be Running
    [Documentation]    Verifies that a snaplex is in running or alert state.
    ...
    ...    *Arguments:*
    ...    - ``plex_path``: Path to the snaplex instance
    ...
    ...    *Example:*
    ...    | Snaplex Status Should Be Running | my_plex_path |
    [Arguments]    ${plex_path}
    ${status}    Get Snaplex Status    ${plex_path}
    Log    Snaplex current status: ${status}
    Should Contain Any    ${status}    up_and_running    alert

Wait Before Suite Execution
    [Documentation]    Pauses execution for a specified number of minutes before continuing suite execution.
    ...    This is typically used to wait for snaplex startup or other initialization processes.
    ...
    ...    *Arguments:*
    ...    - ``minutes``: Number of minutes to wait
    ...
    ...    *Example:*
    ...    | Wait Before Suite Execution | 3 |
    [Arguments]    ${minutes}
    Log    waitng for 3 minutes before test suite execution for snaplex to get started    level=CONSOLE
    Sleep    ${minutes}

Wait Until Plex Status Is Up
    [Documentation]    Waits until a snaplex instance is in the 'up and running' state.
    ...    *Arguments:*
    ...    - ``plex_path``: Path to the snaplex instance
    ...    *Returns:*
    ...    - None (waits until the snaplex is up and running)
    ...    *Example:*
    ...    | Wait Until Plex Status Is Up | /org/shared/my_plex |
    [Arguments]    ${plex_path}
    # Capture start time for log and computation
    ${start_time_str}    Get Time    format=%Y-%m-%d %H:%M:%S
    ${start_ts}    Get Time    epoch

    Log    \n⏳ Waiting for Snaplex at path '${plex_path}' to become up and running...\n    level=CONSOLE
    Log    Start Time: ${start_time_str}    level=CONSOLE

    Wait Until Keyword Succeeds    4 min    10 sec    Snaplex Status Should Be Running    ${plex_path}

    # Capture end time and calculate duration
    ${end_time_str}    Get Time    format=%Y-%m-%d %H:%M:%S
    ${end_ts}    Get Time    epoch
    ${duration_secs}    Evaluate    int(${end_ts} - ${start_ts})
    ${minutes}    Evaluate    ${duration_secs} // 60
    ${seconds}    Evaluate    ${duration_secs} % 60

    Log    \n✅ Snaplex at path '${plex_path}' is now up and running.\n    level=CONSOLE
    Log    End Time: ${end_time_str}    level=CONSOLE
    Log    ⏱️ Total time taken is: ${minutes} minutes and ${seconds} seconds    level=CONSOLE

Create Account From Template
    [Documentation]    Creates an account using a given JSON payload file and an optional environment file path.
    ...    *Arguments:*
    ...    - ``payload_file_path_and_name``: Payload location followed by name of the account file (e.g., ${CONFIG_DIR}/acc_oracle.json)
    ...    *Returns:*
    ...    - None (calls Create Account keyword)
    ...    *Example:*
    ...    | Create Account From Template | ${CONFIG_DIR}/acc_oracle.json | env_file_path |
    [Arguments]    ${payload_file_path_and_name}

    ${payload_path}    Set Variable    ${payload_file_path_and_name}
    Create Account    ${payload_path}    ${env_file_path}

Connect to Oracle Database
    [Documentation]    Sets up Oracle database tables and procedures.
    ...    *Arguments:*
    ...    - None (uses environment variables for connection)
    ...    *Example:*
    ...    | Connect to Oracle Database |

    Connect To Database
    ...    oracledb
    ...    ${ORACLE_DBNAME}
    ...    ${ORACLE_DBUSER}
    ...    ${ORACLE_DBPASS}
    ...    ${ORACLE_HOST}
    ...    1521    # ${ORACLE_DBPORT}

Execute SQL queries
    [Documentation]    Executes a SQL query against the connected database.
    ...
    ...    *Arguments:*
    ...    - ``sql_query``: The SQL query string to execute
    ...
    ...    *Example:*
    ...    | Execute SQL queries | SELECT * FROM users WHERE id = 1 |
    [Arguments]    ${sql_query}
    Execute SQL String    ${CREATE_PROC_REF_VALUES}

Log Pretty JSON
    [Documentation]    Formats and logs a JSON payload with proper indentation for better readability.
    ...
    ...    *Arguments:*
    ...    - ``payload_name``: Name or label for the JSON payload in the log
    ...    - ``json_payload``: The JSON payload to format and log
    ...
    ...    *Example:*
    ...    | Log Pretty JSON | Task Configuration | ${task_payload} |
    [Arguments]    ${payload_name}    ${json_payload}
    ${pretty_json}    Evaluate    json.dumps($json_payload, indent=4)    modules=json
    Log    \n==== ✅ ${payload_name}- PAYLOAD ====\n${pretty_json}    level=CONSOLE

Import Pipelines From Template
    [Documentation]    Imports a SnapLogic pipeline with a unique ID suffix and sets suite-level
    ...    variables for tracking the pipeline instance.
    ...
    ...    This keyword is typically used in test templates where multiple pipelines
    ...    are imported dynamically. A unique identifier is appended to the pipeline name
    ...    and pipeline_snode_id to avoid naming collisions during execution
    ...    The resulting uniqie_id and pipeline's `snode_id`
    ...    is stored as a suite variable for later use in downstream test cases (e.g., to
    ...    create triggered tasks or execute the pipeline).
    ...
    ...    Arguments:
    ...    - ${unique_id}    → Unique identifier for the pipeline instance (e.g., `oracle_pl`)
    ...    - ${pipeline_file_path}
    ...    - ${pipeline_name}    → Logical name of the pipeline (used for naming during import).
    ...    - ${slp_file_name}    → Name of the .slp file to import (e.g., `ML_Oracle.slp`).
    ...
    ...    Return Values (Saved as Suite Variables that can be resused in other keywords):
    ...    - ${<slp_file_name>_snode_id}    → The returned `snode_id` from the import operation.
    ...    Example:
    ...    | Import Pipelines From Template | ${pipeline_file_path} | ${pipeline_name} | ${slp_file_name}    |
    [Arguments]    ${unique_id}    ${pipeline_file_path}    ${pipeline_name}    ${slp_file_name}

    ${pipeline_name}    Set Variable    ${pipeline_name}_${unique_id}

    ${pipeline_snode_id}    Import Pipeline
    ...    ${pipeline_file_path}/${slp_file_name}
    ...    ${pipeline_name}
    ...    ${project_path}

    # Set Suite Variable    ${${pipeline_name}_unique_id}    ${unique_id}
    Set Suite Variable    ${${pipeline_name}_snode_id}    ${pipeline_snode_id}

    # Log    📌 Set suite variable: \${${pipeline_name}_unique_id} = ${unique_id}    level=CONSOLE
    Log    📌 Set suite variable: \${${pipeline_name}_snode_id} = ${pipeline_snode_id}    level=CONSOLE

Create Triggered Task From Template
    [Documentation]    Creates a triggered task using a provided task name prefix,
    ...    a pipeline unique ID, and a pipeline snode_id.
    ...
    ...    Arguments:
    ...    - ${unique_id}    → Unique ID for the pipeline instance (e.g., `oracle_pl`)
    ...    - ${project_path}    → Project path where the task will be created
    ...    - ${pipeline_name}
    ...    - ${task_name}    → Task name prefix (e.g., ML_Oracle_Task)
    ...    - ${pipeline_params}    → Suite variable name holding unique ID (e.g., oracle_pl_unique_id)
    ...
    ...    Builds a triggered task name like ${task_name}_${unique_id} and stores it
    ...    as a suite variable: ${task_name}_unique
    [Arguments]
    ...    ${unique_id}
    ...    ${project_path}
    ...    ${pipeline_name}
    ...    ${task_name}
    ...    ${pipeline_params}=None
    ...    ${notification}=None

    ${full_task_name}    Set Variable    ${pipeline_name}_${task_name}_${unique_id}
    ${pipeline_snode_id}    Get Variable Value    ${${pipeline_name}_${unique_id}_snode_id}
    ${pipeline_params}    Get Variable Value    ${pipeline_params}

    Log    📌 pipeline_snode_id is : ${pipeline_snode_id}    level=CONSOLE
    Log    📌 FullTaskName is : ${full_task_name}    level=CONSOLE

    # ${states}    Create List    Completed    Failed
    # ${notification}    Create Dictionary    recipients=newemail@gmail.com    states=${states}

    ${task_payload}    ${task_snode_id}    Create Triggered Task
    ...    ${full_task_name}
    ...    ${pipeline_snode_id}
    ...    ${groundplex_name}
    ...    ${project_path}
    ...    pipeline_params=${pipeline_params}
    ...    notification=${notification}

    Log Pretty JSON    CREATED_TASK    ${task_payload}

    Set Suite Variable    ${${full_task_name}_payload}    ${task_payload}
    Set Suite Variable    ${${full_task_name}_snodeid}    ${task_snode_id}
    Log
    ...    📌 Set suite variable task_payoad_var: ${full_task_name}_payload=${task_payload}
    ...    level=CONSOLE
    Log
    ...    📌 Set suite variable task_snode_id: ${full_task_name}_snodeid=${task_snode_id}
    ...    level=CONSOLE

Execute Triggered Task With Parameters From Template
    [Documentation]    Updates parameters for a task created from a template.
    ...
    ...    *Arguments:*
    ...    - ``unique_id``: Unique identifier for the task instance
    ...    - ``project_path``: Path where the task is located
    ...    - ``pipeline_name``: Name of the pipeline
    ...    - ``task_name``: Name of the task to update
    ...    - ``new_parameters``: Dictionary of parameters to update or add (default: None)
    ...
    ...    *Returns:*
    ...    - A tuple containing the updated task payload and job ID
    ...
    ...    *Example:*
    ...    | ${new_params} | Create Dictionary | env=prod | debug=${FALSE} |
    ...    | ${updated_payload} | ${job_id} | Update Task Parameters From Template | unique_123 | /org/project | pipeline1 | task1 | ${new_params} |
    [Arguments]    ${unique_id}    ${project_path}    ${pipeline_name}    ${task_name}    &{new_parameters}

    ${full_task_name}    Set Variable    ${pipeline_name}_${task_name}_${unique_id}
    ${task_payload}    Get Variable Value    ${${full_task_name}_payload}
    ${task_snode_id}    Get Variable Value    ${${full_task_name}_snodeid}

    # Get the current 'parameters' block from task payload
    ${parameters_value}    Get From Dictionary    ${task_payload}    parameters

    # Extract pipeline_parameters from parameters
    ${existing_pipeline_parameters}    Get From Dictionary    ${parameters_value}    pipeline_parameters

    # 📝 Print existing pipeline_parameters before update
    ${existing_json}    Evaluate    json.dumps($existing_pipeline_parameters, indent=4)    modules=json
    Log    \n📝 Existing pipeline_parameters BEFORE any update:\n${existing_json}    level=CONSOLE

    # Check if pipeline_parameters is None and create empty dictionary if needed
    ${is_none}    Run Keyword And Return Status    Should Be Equal    ${existing_pipeline_parameters}    ${NONE}
    IF    ${is_none}
        ${existing_pipeline_parameters}    Create Dictionary
    END

    # 🔁 Merge new parameters into existing ones
    FOR    ${key}    ${value}    IN    &{new_parameters}
        Set To Dictionary    ${existing_pipeline_parameters}    ${key}=${value}
    END

    # Set merged parameters back into payload
    Set To Dictionary    ${parameters_value}    pipeline_parameters=${existing_pipeline_parameters}
    Set To Dictionary    ${task_payload}    parameters=${parameters_value}

    # Call API to update the task
    ${response}    Update Task Api    ${task_snode_id}    ${task_payload}

    # ✅ Pretty-print the final task payload
    ${pretty_json}    Evaluate    json.dumps($task_payload, indent=4)    modules=json
    Log    \n==== ✅ UPDATED TASK PAYLOAD ====\n${pretty_json}    level=CONSOLE

    Run Triggered Task    ${project_path}    ${full_task_name}

    RETURN    ${task_payload}    ${response.json()['response_map']['job_id']}
