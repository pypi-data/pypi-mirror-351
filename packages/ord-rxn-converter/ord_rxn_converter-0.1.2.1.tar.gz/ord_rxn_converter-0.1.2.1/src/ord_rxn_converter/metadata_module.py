# %% 
import re
from ord_schema.message_helpers import load_message, write_message
from ord_schema.proto import dataset_pb2, reaction_pb2
from google.protobuf.message import Message

def extract_dataset_metadata(dataset):

    """
    Extracts key metadata from a loaded ORD dataset message.

    This function parses a loaded Protocol Buffer dataset message and extracts 
    high-level metadata such as a modified dataset ID, original ORD ID, name, 
    and description. The modified ID is formatted to reflect that the dataset 
    is stored in an MDS (custom) database.

    Args:
        dataset (dataset_pb2.Dataset): 
            A dataset message loaded via `load_message` from the ORD schema.

    Returns:
        list: 
            A list containing the following metadata fields:
            - `dataset_id` (str): Custom MDS-formatted dataset ID.
            - `ord_dataset_id` (str): Original dataset ID from ORD.
            - `name` (str): Human-readable name of the dataset.
            - `description` (str): Textual description of the dataset.

    Example:
        >>> from metadata_module import extract_dataset_metadata
        >>> dataset = load_message("example_dataset.pb", dataset_pb2.Dataset())
        >>> extract_dataset_metadata(dataset)
        ['mds_dataset-000001', 'ord_dataset-000001', '...', '...']
    """

    dsID = re.split('-', dataset.dataset_id) 
    datasetID = f"mds_dataset-{dsID[1]}"
    ORDdsID = dataset.dataset_id 

    dsName = dataset.name
    dsDes = dataset.description

    dataset_metadata = [datasetID, ORDdsID, dsName, dsDes]

    return dataset_metadata

def extract_reaction_metadata(provenance, reactionID):

    """
    Extracts reaction-level provenance and contributor metadata from a reaction.

    This function parses the `Provenance` message from a reaction in an ORD dataset, 
    extracting detailed metadata related to:
    - The reaction's source (e.g., DOI, patent, publication)
    - Timing and authorship of creation and modifications
    - Contributor identities (with ORCID and contact details)

    Args:
        provenance (reaction_pb2.Provenance): 
            A Provenance message associated with a reaction.
        reactionID (str): 
            The unique identifier of the reaction being processed.

    Returns:
        tuple:
            - `provenance_data` (list): Reaction-level metadata including:
                - `reactionID` (str)
                - `experimenter_orcid` (str)
                - `city` (str)
                - `experiment_start` (str)
                - `doi` (str)
                - `patent` (str)
                - `publication_url` (str)
                - `created_time` (str)
                - `created_person_orcid` (str)
                - `created_details` (str)
                - `modified_times` (str, comma-separated)
                - `modified_people` (str, comma-separated ORCIDs)
            - `person_metadata` (list of list of str): Contributor metadata:
                - Each inner list includes:
                    `[orcid, username, full_name, organization, email]`

    Example:
        >>> from metadata_module import extract_reaction_metada
        >>> reaction = dataset.reactions[0]
        >>> extract_reaction_metadata(reaction.provenance, "reaction-001")
        (['reaction-001', '0000-0001-...', 'Boston', ...], 
         [['jsmith', 'John Smith', '0000-0001-...', ...], ...])
    """
    
    person_metadata = []

    # experimenter = 1
    experimenter = provenance.experimenter
    person_metadata.append([experimenter.username, experimenter.name, experimenter.orcid, experimenter.organization, experimenter.email])
    
    # city = 2

    # experiment_start = 3

    # doi = 4

    # patent = 5

    # publication_url = 6
    
    # record_created = 
    created_time = provenance.record_created.time.value
    person = provenance.record_created.person
    person_metadata.append([person.username, person.name, person.orcid, person.organization, person.email])

    modified_times_list = []
    modified_person_orcid_list = []

    for record in provenance.record_modified:
        modified_times_list.append(record.time.value)
        modified_person_orcid_list.append(record.person.orcid)
    modified_people = ", ".join(modified_person_orcid_list)
    modified_times = ", ".join(modified_times_list)

    for record in provenance.record_modified:
        person = record.person
        person_metadata.append([person.orcid, person.username, person.name, person.organization, person.email])
        
    provenance_data = [reactionID, provenance.experimenter.orcid, provenance.city, provenance.experiment_start, provenance.doi, provenance.patent, provenance.publication_url, 
        provenance.record_created.time.value, provenance.record_created.person.orcid, provenance.record_created.details, 
        modified_times, modified_people]
   
    return provenance_data, person_metadata
