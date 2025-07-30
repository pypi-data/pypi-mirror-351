from ord_schema.proto import dataset_pb2, reaction_pb2
from google.protobuf.message import Message

# =============================================================================
#               FUNCTIONS TO EXTRACT ENUMS FROM ALL MESSAGE TYPES
# =============================================================================

# Get all of enum field names and numbers: 

def extract_enums_from_message(descriptor, parent_name=''):
    
    """
    Recursively extract enums from messages and nested messages.
    
    This function traverses through a protobuf message descriptor and extracts
    all enum types defined within it and its nested messages. For each enum type,
    it creates a mapping between enum value numbers and their names.
    
    Args:
        descriptor: The descriptor of the protobuf message to extract enums from.

        parent_name: The name of the parent message for nested messages, used for
            constructing fully qualified enum names. Default is an empty string.
    
    Returns:
        A dictionary mapping fully qualified enum names to dictionaries that map
        enum value numbers to their names. The structure is:

        {
            'EnumName': {value_number: 'VALUE_NAME', ...},
            'ParentMessage.NestedEnum': {value_number: 'VALUE_NAME', ...},
            ...
            
        }
    """

    #ensure descriptor is not None
    if not descriptor:
        return {}

    enums = {}

    # Get enums within this message
    for enum_type in descriptor.enum_types:
        full_enum_name = f'{parent_name}.{enum_type.name}' if parent_name else enum_type.name
        enums[full_enum_name] = {v.number: v.name for v in enum_type.values}

    # Recursively check nested messages
    for nested_type in descriptor.nested_types:
        nested_enums = extract_enums_from_message(nested_type, f"{parent_name}.{nested_type.name}" if parent_name else nested_type.name)
        enums.update(nested_enums)

    return enums

#should be called by public - gets full enums_data set from proto_module

def extract_all_enums(proto_module):

    """
    Extract enums from all message types in the proto module.
    
    This function serves as the main entry point for extracting all enum types from 
    a protobuf module. It iterates through all attributes of the module, identifies
    protobuf message types, and extracts all enum types defined within them.
    
    Args:
        proto_module: The protobuf module (e.g., dataset_pb2, reaction_pb2) to
            extract enums from.
    
    Returns:
        A dictionary mapping fully qualified enum names to dictionaries that map
        enum value numbers to their names. The structure is:

        {
            'MessageName.EnumName': {value_number: 'VALUE_NAME', ...},
            'MessageName.NestedMessage.NestedEnum': {value_number: 'VALUE_NAME', ...},
            ...

        }
    
    Example:
        >>> from ord_schema.proto import reaction_pb2
        >>> from utility_functions_module import extract_all_enums
        >>> enums_data = extract_all_enums(reaction_pb2)
        >>> print(enums_data['Analysis.AnalysisType'])
        {0: 'UNSPECIFIED', 1: 'CUSTOM', 2: 'LC', 3: 'GC', ...}
    """

    all_enums = {}

    for name in dir(proto_module):
        obj = getattr(proto_module, name)

        # Check if it's a message type
        if isinstance(obj, type) and hasattr(obj, 'DESCRIPTOR'):
            descriptor = obj.DESCRIPTOR
            message_enums = extract_enums_from_message(descriptor, descriptor.name)
            
            if message_enums:
                all_enums.update(message_enums)

    return all_enums