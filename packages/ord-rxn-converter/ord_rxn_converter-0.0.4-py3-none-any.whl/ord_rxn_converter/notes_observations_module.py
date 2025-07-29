from ord_schema.proto import dataset_pb2, reaction_pb2
from google.protobuf.message import Message
from ord_rxn_converter.utility_functions_module import extract_all_enums

#generate enums_data to be accessible here TODO - have importable object instead..?
enums_data = extract_all_enums(reaction_pb2)

# TODO: notes are available but observations sometimes are not available, how to make notes or observations optional? 
def extract_notes_observations(reactionID, notes, observations=None):

    """
    Extracts reaction notes and optional observations from ORD reaction data.

    This function takes a reaction ID, notes, and optionally observations, and returns
    a list summarizing various reaction notes and details from observations if provided.
    The notes include flags for reaction characteristics, safety notes, and procedure details.
    Observations include time, comments, and image metadata.

    Args:
        reactionID (str): Unique identifier for the reaction.
        notes (object): Notes object containing reaction flags and textual details.
            Expected attributes:
                - is_heterogeneous (bool)
                - forms_precipitate (bool)
                - is_exothermic (bool)
                - offgasses (bool)
                - is_sensitive_to_moisture (bool)
                - is_sensitive_to_oxygen (bool)
                - is_sensitive_to_light (bool)
                - safety_notes (str)
                - procedure_details (str)
        observations (list, optional): List of observation objects, each possibly containing:
            - time.value (float)
            - time.units (enum int)
            - comment (str)
            - image with kind, description, and format attributes

    Returns:
        list: A list containing the following elements in order:
            [reactionID (str), is_heterogeneous (bool), forms_precipitate (bool), is_exothermic (bool), offgasses (bool), is_sensitive_to_moisture (bool), is_sensitive_to_oxygen (bool), is_sensitive_to_light (bool), safety_notes (str), procedure_details (str), observations (list of dict or None)]

        Each dict in observations contains keys:
            - 'time': float
            - 'timeUnit': str
            - 'comment': str
            - 'imageKind': str
            - 'imageDescription': str
            - 'imageFormat': str
    """

    # optional bool is_heterogeneous = 1 
    
    # optional bool forms_precipitate = 2 

    # optional bool is_exothermic = 3 

    # optional bool offgasses = 4

    # optional bool is_sensitive_to_moisture = 5

    # optional bool is_sensitive_to_oxygen = 6

    # optional bool is_sensitive_to_light = 7

    # string safety_notes = 8 

    # string procedure_details = 9; 

    observation_list = []
    if observations: 
        for observation in observations:
            # get reaction_observation_time if exists:
            time_observation = observation.time.value 
            time_unit = enums_data['Time.TimeUnit'][observation.time.units] 
            
            # get reaction_observation_comments if exists: 
            comment = observation.comment

            # get reaction_observation_image if exists:
            if observation.image and isinstance(observation.image.WhichOneof('kind'), str): 
                image_kind = getattr(observation.image, observation.image.WhichOneof('kind'))
                description = observation.image.description
                image_format = observation.image.format
                observation_list.append({'time':time_observation, 
                                        'timeUnit':time_unit, 
                                        'commonet':observation.comment, 
                                        'imageKind':image_kind, 
                                        'imageDescription':observation.image.description, 
                                        'imageFormat':observation.image.format})
            else: pass
    else: 
        observation_list = None

    reaction_notes_observations = [reactionID, notes.is_heterogeneous, notes.forms_precipitate, notes.is_exothermic , 
        notes.offgasses, notes.is_sensitive_to_moisture, notes.is_sensitive_to_oxygen, notes.is_sensitive_to_light, 
        notes.safety_notes, notes.procedure_details, observation_list
    ]
    
    return reaction_notes_observations
