# import requirements: 
from ord_schema.proto import dataset_pb2, reaction_pb2
from google.protobuf.message import Message
from ord_rxn_converter.utility_functions_module import extract_all_enums
from ord_rxn_converter.inputs_module import extract_input_addition, extract_amount
from ord_rxn_converter.conditions_module import temperature_conditions, stirring_conditions
from ord_rxn_converter.identifiers_module import extract_compound_identifiers, generate_compound_table

#generate enums_data to be accessible here TODO - have importable object instead..?
enums_data = extract_all_enums(reaction_pb2)

def extract_reaction_workups(workups, reactionID):
    """
    Extracts workup details from an ORD reaction workup list.

    This function parses a list of `ReactionWorkup` protobuf messages associated with a reaction
    and extracts structured information including compound input components, input addition
    details, temperature and stirring conditions, and metadata such as pH or automation status.

    Args:
        workups (list): A list of `ReactionWorkup` messages from `reaction_pb2.Reaction.workups`.
        reactionID (str): A unique identifier for the reaction.

    Returns:
        list: A list of extracted workup information for the reaction. Each item in the list corresponds
        to a single `ReactionWorkup` and contains the following fields:

        [reactionID (str), workup_type (str), workup.details (str), workup.duration.value (float), workup_duration_unit (str),  input_components (dict or None), input_addition_details (dict or None), temperature_conditions_list (list or None), keep_phase (str), stirring_conditions_list (list or None), target_ph (float or None), is_automated (bool or None)]
    """

    # initialize lists 
    input_components = []
    input_addition_details = []
    compound_table = [] 
    workups_list = []

    for workup in workups:

        # (enum) ReactionWorkupType type = 1
        workup_type = enums_data['ReactionWorkup.ReactionWorkupType'][workup.type]
        
        # string details = 2 
        
        # Time duration = 3
        workup_duration_unit = enums_data['Time.TimeUnit'][workup.duration.units]
        
        if workup.input:

            components = workup.input.components

            for component in components:
                # identifiers = 1
                if component.identifiers:
                    identifiers = component.identifiers
                    component_identifiers = extract_compound_identifiers(identifiers)
                    compound_table.append(generate_compound_table(identifiers))
                else: 
                    component_identifiers = None
                    compound_table = None
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
                if hasattr(component, 'preparations') and component.preparations:
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
                if hasattr(component, 'analyses') and component.analyses: 
                    analyses = component.analyses
                    analyses_list = extract_analyses (analyses)
                else: analyses_list = None
                
                # Texture texture = 9 
                if component.texture: 
                    texture_type = enums_data['Texture.TextureType'][component.texture.type]
                    texture = {texture_type:component.texture.details}
                else: texture = None
                
                input_components = {'compoundIdentifiers':component_identifiers, 'amountValue':amount_value, 'amountUnit':amount_unit, 'reactionRole':reaction_role, 'isLimiting':component.is_limiting, 'compoundPreparation':compound_preparation, 
                    'componentSource':component_source, 'feautreDictionary':feature_dict, 'analysesList':analyses_list, 'texture':texture}
           
            inputKey = workup.input
            input = workup.input
            
            addition_time_unit = enums_data['Time.TimeUnit'][input.addition_time.units]  

            addition_speed = enums_data['ReactionInput.AdditionSpeed.AdditionSpeedType'][input.addition_speed.type]

            addition_duration_unit = enums_data['Time.TimeUnit'][input.addition_duration.units]

            addition_flowrate_unit = enums_data['FlowRate.FlowRateUnit'][input.flow_rate.units]

            addition_device = enums_data['ReactionInput.AdditionDevice.AdditionDeviceType'][input.addition_device.type]

            addition_temperature_unit = enums_data['Temperature.TemperatureUnit'][input.addition_temperature.units]
            
            reaction_texture = enums_data['Texture.TextureType'][input.texture.type]

            input_addition_details = {'inputKey':inputKey, 'additionOrder':input.addition_order, 'additionTimeValue':input.addition_time.value, 'additoinTimeUnit':addition_time_unit, 'additionSpeed':addition_speed, 
                'additionDurationValue':input.addition_duration.value, 'additionDurationUnit':addition_duration_unit, 'additionDevice':addition_device, 'additionTemperatureValue':input.addition_temperature.value, 'additionTemperatureUnit':addition_temperature_unit, 
                'inputFlowRateValue':input.flow_rate.value, 'additionFlowRateUnit':addition_flowrate_unit, 'reactionTexture':reaction_texture, 'textureDetails':input.texture.details}

        else: 
            input_components = None 
            input_addition_details = None
        
        # TemperatureConditions temperature = 6 
        if hasattr(workup, 'temperature') and workup.temperature:
            temperature = workup.temperature
            temperature_conditions_list = temperature_conditions(temperature)
        else: temperature_conditions_list = None

        # string keep_phase = 7;

        # StirringConditions stirring = 8
        if hasattr(workup, 'stirring') and workup.stirring:
            stirring = workup.stirring
            stirring_conditions_list = stirring_conditions(stirring)
        else: stirring_conditions_list = None

        # optional float target_ph = 9
        # optional bool is_automated = 10 
        workups_list.append([reactionID, workup_type, workup.details, workup.duration.value, workup_duration_unit, 
        input_components, input_addition_details, temperature_conditions_list, workup.keep_phase, 
        stirring_conditions_list, workup.target_ph, workup.is_automated])

    return workups_list