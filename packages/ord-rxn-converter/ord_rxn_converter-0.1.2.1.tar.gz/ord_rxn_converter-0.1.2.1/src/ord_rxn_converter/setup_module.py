# import requirements: 
from ord_schema.proto import dataset_pb2, reaction_pb2
from google.protobuf.message import Message
import pandas as pd
from ord_rxn_converter.utility_functions_module import extract_all_enums

#generate enums_data to be accessible here TODO - have importable object instead..?
enums_data = extract_all_enums(reaction_pb2)

def extract_reaction_setup(setup, reactionID):

    """
    Extracts detailed setup information from a reaction object.

    This function processes the reaction setup section of an ORD (Open Reaction Database) 
    reaction object and extracts metadata about the vessel, its material, volume, 
    preparations, attachments, automation details, and environmental setup.

    Args:
        setup (reaction_pb2.ReactionSetup): 
            A ReactionSetup protobuf object containing details about how the reaction was set up.
        reactionID (str): 
            Unique identifier for the reaction being processed.

    Returns:
        list: 
            A list representing the reaction setup details in the following structure:
            [reactionID (str), vessel type (str), vessel material (str), vessel volume (float or None), volume unit (str or None), vessel preparations (dict or None), vessel attachments (dict or None), is automated (bool or None),  automation platform (str or None), automation code (str), reaction environment (str or None)]

    Example:
        >>> from ord_schema.proto import reaction_pb2
        >>> from setup_module import extract_reaction_setup
        >>> from ord_schema.proto import dataset_pb2
        >>> dataset = dataset_pb2.Dataset()
        >>> reaction = dataset.reactions[0] 
        >>> reaction_setup = extract_reaction_setup(reaction.setup, reactionID='rxn-042')
    """

    vessel = enums_data['Vessel.VesselType'][setup.vessel.type]
    vessel_material = enums_data['VesselMaterial.VesselMaterialType'][setup.vessel.material.type]
    attach_dict = {} 
    prep_dict = {}
    if hasattr(setup.vessel, 'preparation') and setup.vessel.preparations:
        for preparation in setup.vessel.preparations: 
            vessel_preparation = enums_data['VesselPreparation.VesselPreparationType'][preparation.type]
            prep_dict.update([(vessel_preparation, preparation.details)])
    else: prep_dict = None
    
    if setup.vessel.attachments:
        for attachment in setup.vessel.attachments:  
            vessel_attachment = enums_data['VesselAttachment.VesselAttachmentType'][attachment.type]
            attach_dict.update(zip(vessel_attachment, attachment.details))
    else: attach_dict = None

    if setup.vessel.volume:
        vessel_volume = setup.vessel.volume.value
        volume_unit = enums_data['Volume.VolumeUnit'][setup.vessel.volume.units]
    else: 
        vessel_volume = None   
        volume_unit = None

    is_automated = setup.is_automated if setup.is_automated else None
    automation_platform = setup.automation_platform if setup.automation_platform else None
    automation_code = ", ".join(f"{key}: {value}" for key, value in setup.automation_code.items()) 
    
    reaction_environment = enums_data['ReactionSetup.ReactionEnvironment.ReactionEnvironmentType'][setup.environment.type] if setup.environment else None

    reaction_setup = [reactionID, vessel, vessel_material, vessel_volume, volume_unit, prep_dict, attach_dict, is_automated, automation_platform, automation_code, reaction_environment]

    return reaction_setup