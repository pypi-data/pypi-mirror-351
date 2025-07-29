# import requirements: 
from ord_schema.proto import dataset_pb2, reaction_pb2
from google.protobuf.message import Message
from ord_rxn_converter.utility_functions_module import extract_all_enums
from ord_rxn_converter.identifiers_module import extract_compound_identifiers, generate_compound_table

#generate enums_data to be accessible here TODO - have importable object instead..?
enums_data = extract_all_enums(reaction_pb2)

def extract_input_addition (inputs, reactionID = ''):

    """
    Extracts detailed addition information from reaction inputs.

    This function processes the reaction inputs and extracts detailed 
    information about each addition, such as timing, speed, device, temperature, 
    flow rate, and texture information.

    Args:
        inputs (dict): Reaction inputs from a reaction object (protobuf-based ORD schema).
            Typically accessed as `reaction.inputs['input_key']`.
        reactionID (str, optional): Unique identifier for the reaction. Defaults to ''.

    Returns:
        list: A list of lists, each containing addition details:
            [reactionID, input key, addition order, addition time value, 
             addition time unit, addition speed, addition duration value,
             addition duration unit, addition device, addition temperature value,
             addition temperature unit, flow rate value, flow rate unit, 
             reaction texture, input texture details]

    Example:
        >>> from inputs_module import extract_input_addition
        >>> extract_input_addition(reaction.inputs, reactionID='rxn-001')
        [['', 'm1_m2', 0, 0.0, 'UNSPECIFIED', ...]]
    """
    input_addition_details = [] 

    for input in inputs: 
        inputKey = input
        input = inputs[input]
        
        addition_time_unit = enums_data['Time.TimeUnit'][input.addition_time.units]  

        addition_speed = enums_data['ReactionInput.AdditionSpeed.AdditionSpeedType'][input.addition_speed.type]

        addition_duration_unit = enums_data['Time.TimeUnit'][input.addition_duration.units]

        addition_flowrate_unit = enums_data['FlowRate.FlowRateUnit'][input.flow_rate.units]

        addition_device = enums_data['ReactionInput.AdditionDevice.AdditionDeviceType'][input.addition_device.type]

        addition_temperature_unit = enums_data['Temperature.TemperatureUnit'][input.addition_temperature.units]
        
        reaction_texture = enums_data['Texture.TextureType'][input.texture.type]

        input_addition_details.append([reactionID, inputKey, input.addition_order, input.addition_time.value, addition_time_unit, addition_speed, 
            input.addition_duration.value, addition_duration_unit, addition_device, input.addition_temperature.value, addition_temperature_unit, 
            input.flow_rate.value, addition_flowrate_unit, reaction_texture, input.texture.details])
    
    return input_addition_details

def extract_input_components (inputs, reactionID = ''):
    """
    Extracts detailed information about reaction input components and their compound identifiers.

    Processes each input and its components, extracting chemical and experimental details
    including identifiers, amounts, roles, preparations, sources, features, analyses, and texture.

    Args:
        inputs (dict): Reaction inputs from a reaction object (protobuf-based ORD schema).
            Typically accessed as `reaction.inputs['input_key']`.
        reactionID (str, optional): Unique identifier for the reaction. Defaults to ''.

    Returns:
        tuple: 
            - list: List of input component details with structure:
              [reactionID, input key, inchi_key, amount value, amount unit, reaction role, is limiting (bool), compound preparation (list of dicts), component source (dict), feature dictionary, analyses list, texture dictionary]
            - list: List of compound identifier tables (each a list of compound identifiers).

    Example:
        >>> from inputs_module import extract_input_components
        >>> components, compound_table = extract_input_components(reaction.inputs, reactionID='rxn-001')
    """
    input_components = []
    compound_table = [] 


    # loop through each input in a reaction: 
    for input in inputs: 
        components = inputs[input].components

        for component in components:
            # identifiers = 1
            if component.identifiers:
                identifiers = component.identifiers
                inchi_key, component_identifiers = extract_compound_identifiers(identifiers)
                compound_table.append(generate_compound_table(identifiers))
            else: 
                component_identifiers = None
            # Amount amount = 2 
            if component.amount and component.amount.WhichOneof('kind'):
                amount_value, amount_unit = extract_amount(component)
            else: 
                amount_value = None
                amount_unit = None
            
            # ReactionRole.ReactionRoleType reaction_role = 3
            reaction_role = enums_data['ReactionRole.ReactionRoleType'][component.reaction_role] if component.reaction_role else None
            
            # optional bool is_limiting = 4

            # repeated CompoundPreparation preparations = 5 
            if component.preparations:
                compound_preparation = []
                for preparation in component.preparations:
                    preparation_type = enums_data['CompoundPreparation.CompoundPreparationType'][preparation.type]
                    preparation_dict = {'Type':preparation_type, 'Details':preparation.details}
                    compound_preparation.append(preparation_dict)
            else: compound_preparation = None

            # Source source = 6 
            component_source = {'Vendor':component.source.vendor, 'catalogID':component.source.catalog_id} if component.source else None

            # map<string,Data> features = 7 
            feature_dict = {feature_key: feature for feature_key, feature in component.features} if component.features else None

            # map<string, Analysis> analyses = 8 
            if component.analyses: 
                analyses = component.analyses
                analyses_list = extract_analyses (analyses)
            else: analyses_list = None
            
            # Texture texture = 9 
            if component.texture: 
                texture_type = enums_data['Texture.TextureType'][component.texture.type]
                texture = {texture_type:component.texture.details}
            else: texture = None
            
            input_components.append([reactionID, input, inchi_key, amount_value, amount_unit, reaction_role, component.is_limiting, compound_preparation, 
                component_source, feature_dict, analyses_list, texture])

    return input_components, compound_table

def extract_amount (compound):
    """
    Extracts the amount value and unit from a compound's amount field.

    This function reads the nested `amount` field from a compound (which is a protobuf oneof)
    and returns its numerical value and the unit as a string.

    Args:
        compound (protobuf message): A compound component of a reaction with an `amount` field.

    Returns:
        tuple:
            - float: Amount value.
            - str: Amount unit name (e.g., 'MASS', 'MOLE', 'GRAM').

    Example:
        >>> from inputs_module import extract_amount
        >>> amount_value, amount_unit = extract_amount(component)
    """
    
    nested_message = getattr(compound.amount, compound.amount.WhichOneof('kind')) # amount is oneof message type; must use WhichOneof('kind') to extract the inner message
    amount_value = getattr(nested_message, 'value')  # extract the value of the inner message
    enum_value = getattr(nested_message, 'units') # extract the unit of the inner message
    amount_unit = nested_message.DESCRIPTOR.fields_by_name['units'].enum_type.values_by_number[enum_value].name # descriptor to get the fields by name, choose the enum_types in 'units', then get the values of the enums by number and then its name
    
    return amount_value, amount_unit