
# import requirements
from ord_schema.message_helpers import load_message, write_message
from ord_schema.proto import dataset_pb2, reaction_pb2
from google.protobuf.message import Message
import pandas as pd
import re
#function imports
from ord_rxn_converter.metadata_module import extract_dataset_metadata, extract_reaction_metadata
from ord_rxn_converter.identifiers_module import extract_reaction_identifiers, generate_compound_table
from ord_rxn_converter.conditions_module import extract_reaction_conditions
from ord_rxn_converter.inputs_module import extract_input_components, extract_input_addition
from ord_rxn_converter.notes_observations_module import extract_notes_observations
from ord_rxn_converter.outcomes_module import extract_reaction_outcomes
from ord_rxn_converter.setup_module import extract_reaction_setup
from ord_rxn_converter.workups_module import extract_reaction_workups
from ord_rxn_converter.utility_functions_module import extract_all_enums


def extract_dataset (filepath, compounds=pd.DataFrame(), persons=pd.DataFrame()):
    """
    Extracts all structured data from an ORD dataset file and organizes it into a dictionary of DataFrames.

    This function loads a dataset from a `.pb` or `.pbtxt` file (compressed or uncompressed), then extracts and organizes
    its reactions and associated metadata into tabular form. Each component of the reaction—identifiers, inputs, conditions, 
    setup, workups, outcomes, and more—is parsed into a separate `pandas.DataFrame`.

    If compound or person tables are provided, they will be updated to include any new compounds or people found during extraction.

    Args:
        filepath (str): Path to the input file (either zipped or unzipped Google Protobuf format).
        compounds (pd.DataFrame, optional): Existing compound table to update or append to. Defaults to an empty DataFrame.
        persons (pd.DataFrame, optional): Existing person table to update or append to. Defaults to an empty DataFrame.

    Returns:
        dict: A dictionary containing the following keys, each mapping to a `pandas.DataFrame`:
        
            - `"dataset_metadata"`: Dataset-level metadata.
            - `"reaction_metadata"`: Reaction-level metadata including provenance and contributor info.
            - `"reaction_identifiers"`: SMILES, InChI, and other identifiers for each reaction.
            - `"input_components"`: Details of each input component (compound, amount, role, etc.).
            - `"input_addition"`: Temporal details for the addition of inputs.
            - `"reaction_setup"`: Setup information including vessels and automation.
            - `"reaction_conditions"`: Environmental and operational reaction conditions.
            - `"reaction_notes"`: Observations and experimental notes.
            - `"reaction_workups"`: Post-reaction processing steps.
            - `"reaction_outcomes"`: Products and analyses of reaction outcomes.
            - `"compound"`: A table of all compounds involved across reactions.
            - `"person"`: A table of contributors extracted from provenance.

    Raises:
        FileNotFoundError: If the `filepath` does not exist.
        ValueError: If the Protobuf file is invalid or does not conform to `dataset_pb2.Dataset`.

    Example:
        >>> from ord_rxn_converter.dataset_module import extract_dataset
        >>> out = extract_dataset("example_dataset.pb")
        >>> out["reaction_metadata"].head()
    """
    enums_data = extract_all_enums(reaction_pb2)

    # 'load_message' to extract dataset from file path?
    dataset = load_message(filepath, dataset_pb2.Dataset)

    #initialize lists for compiling generated output dataframes 
    reaction_metadata = []
    reaction_identifiers = []
    input_components = []  #being weird for now
    input_addition = []
    reaction_setup = []
    reaction_conditions = []
    reaction_notes_observations = []
    reaction_workups = []
    reaction_outcomes = []

    #persons column headers
    persons_cols = ['ORCiD', 'username', 'name', 'organization', 'email']
    #compounds column headers
    compounds_cols = ['InChIKey', 'smiles', 'inchi', 'iupacName', 'name', 'casNumber', 'pubchemCID', 'chemspiderID', 'cxSmiles', 'unspecified', 'custom', 'molblock', 'xyz', 'uniprotID', 'pbdID', 'aminoAcidSequence', 'helm', 'mdl']

    #check that persons cols match expectation
    if persons.columns.tolist() != persons_cols:
        print("Persons column input headers inoperable - creating new DataFrame")
        #init column headers for empty DF
        persons = pd.DataFrame(columns=persons_cols)

    #check that the compounds cols match expectation
    if compounds.columns.tolist() != compounds_cols:
        print("Compounds column input headers inoperable - creating new DataFrame") 
        compounds = pd.DataFrame(columns=compounds_cols)


    # generate dataset metadata table
    dataset_metadata = extract_dataset_metadata(dataset)
    
    # Set a reaction to extract data from: 
    for reaction in dataset.reactions:        
        # extract reactionID
        rxnID = re.split('-', reaction.reaction_id)
        reactionID = f"mds_reaction-{rxnID[1]}" 

        provenance = reaction.provenance 
        # extract reaction metadata (reaction IDs + provenance); 
        if hasattr(reaction, 'provenance') and reaction.provenance:    #check if provenance attribtue exists before calling
            rxn_metadata, person_metadata = extract_reaction_metadata(provenance, reactionID)
            rxn_metadata = [dataset_metadata[0], reactionID] + rxn_metadata    #dataset_metadata[0] is datasetID
            reaction_metadata.append(rxn_metadata)

            #check if person table needs update
            for person in person_metadata:
                if 'ORCiD' in persons.columns and not persons['ORCiD'].str.contains(person[2]).any():
                   #update persons table if it does not exist
                   persons.loc[len(persons)] = person
       
        # extract reaction identifiers and update compound table if needed
        if hasattr(reaction, 'identifiers') and reaction.identifiers:     #check if exists before calling
            reaction_identifiers.append(extract_reaction_identifiers(reaction.identifiers, reactionID))

        # extract reaction inputs, update compound table, extract reaction addition
        if hasattr(reaction, 'inputs') and reaction.inputs:
            #extract reaction inputs
            input_components, compound_identifiers = extract_input_components(reaction.inputs, reactionID)  #append each list extracted output separately
          #  print("PRINTING COMPOUND IDENTIFIERS:", compound_identifiers)
            for identifier in compound_identifiers:
                if 'InChIKey' in compounds.columns and identifier[0] and not compounds['InChIKey'].str.contains(identifier[0]).any():  #check if contains InChIKey
                    #update compounds table if it does not exist
                    #compounds = pd.concat([compounds, identifier], ignore_index=True)
                    compounds.loc[len(compounds)] = identifier


            #extract reaction addition
            input_addition.extend(extract_input_addition(reaction.inputs, reactionID))
       
        # extract reaction setup
        if hasattr(reaction, 'setup') and reaction.setup:
            reaction_setup.append(extract_reaction_setup(reaction.setup, reactionID))

        # extract reaction conditions  
        if hasattr(reaction, 'conditions') and reaction.conditions:
            reaction_conditions.append(extract_reaction_conditions(reaction.conditions, reactionID))
            

        # extract reaction notes & observations
        if hasattr(reaction, 'notes') and hasattr(reaction, 'observations') and reaction.notes and reaction.observations:
            reaction_notes_observations.append(extract_notes_observations(reactionID, reaction.notes, reaction.observations))

        # extract reaction workups
        if hasattr(reaction, 'workups') and reaction.workups:
            reaction_workups.extend(extract_reaction_workups(reaction.workups, reactionID))

        # extract reaction outcomes 
        if hasattr(reaction, 'outcomes') and reaction.outcomes:
            outcomes, outcomes_identifiers = extract_reaction_outcomes(reactionID, reaction.outcomes)
            reaction_outcomes.extend(outcomes)
            for identifier in outcomes_identifiers: 
                if 'InChIKey' in compounds.columns and identifier[0] and not compounds['InChIKey'].str.contains(identifier[0]).any():  #check if contains InChIKey
                #update compounds table if it does not exist
                #compounds = pd.concat([compounds, identifier], ignore_index=True)
                    compounds.loc[len(compounds)] = identifier
            
    
    # return dictionary of dataframes 

    #define column headers for each dataframe
    dataset_cols = ['datasetID', 'ORDdatasetID', 'datasetName', 'datasetDescription']
    reaction_meta_cols = ['datasetID', 'reactionID', 'ORDreactionID', 'experimenter', 
                            'provenanceCity', 'experimentStart', 'doi', 'patent', 'publicationURL', 
                            'recordCreatedTime', 'recordCreatedPerson', 'recordCreatedDetails', 'modifiedTimes', 'modifiedPeople']
    reaction_identifiers_cols = ['reactionID', 'reactionCXSMILES', 'reactionSMILES', 'RDFile', 'RInChI', 
                                'reactionType', 'unspecified', 'custom', 'identifierDetails', 'isMapped']
    input_comps_cols = ['reactionID', 'inputKey', 'compoundIdenfiers', 'amount', 'amountUnit', 'reactionRole',
                        'isLimiting', 'compoundPreparation', 'compoundSource', 'features', 'analyses', 'texture']
    input_addition_cols = ['reactionID', 'inputKey', 'additionOrder', 'additionTime', 'timeUnit', 'additionSpeed', 
                            'additionDuration', 'durationUnit', 'additionDevice', 'additionTemperature', 
                            'temperatureUnit', 'flowRate', 'flowRateUnit', 'texture', 'textureDetails']
    reaction_setup_cols = ['reactionID', 'vessel', 'vesselMaterial', 'vesselVolume', 'volumeUnit', 'vesselPreparations', 
                            'vesselAttachments', 'isAutomated', 'automationPlatform', 'automationCode', 
                            'reactionEnvironment']
    reaction_conds_cols = ['reactionID', 'temperatureConditions', 'pressureConditions', 'stirringConditions', 
                            'illuminationConditions', 'electrochemistryConditions', 'flowConditions', 
                            'reflux', 'pH', 'conditionsAreDynamic', 'conditionDetails']
    reaction_notes_cols = ['reactionID', 'isHeterogeneous', 'formsPrecipitates', 'isExothermic', 'offGasses', 
                            'isSensitiveToMoisture', 'isSensitiveToOxygen', 'isSensitivetoLight', 'safetyNotes', 
                            'procedureDetails', 'observations']
    reaction_workups_cols = ['reactionID', 'workupType', 'workupDetails', 'workupDuration', 'durationUnit', 
                            'inputComponents', 'inputAdditionDetails', 'temperatureConditions', 'keepPhase', 
                            'stirringConditions', 'workupTargetPH', 'isAutomated']
    reaction_outcomes_cols = ['reactionID', 'outcomeKey', 'reactionTime', 'timeUnit', 'outcomeConversion', 'products', 'analyses']

    #create dictionary of dataframes to output
    out = {
        "dataset_metadata" : pd.DataFrame([dataset_metadata], columns=dataset_cols),
        "reaction_metadata" : pd.DataFrame(reaction_metadata, columns=reaction_meta_cols), 
        "reaction_identifiers" : pd.DataFrame(reaction_identifiers, columns=reaction_identifiers_cols) , 
        "input_components" : pd.DataFrame(input_components, columns=input_comps_cols),
        "input_addition" : pd.DataFrame(input_addition, columns=input_addition_cols),
        "reaction_setup" : pd.DataFrame(reaction_setup, columns=reaction_setup_cols), 
        "reaction_conditions" : pd.DataFrame(reaction_conditions, columns=reaction_conds_cols), 
        "reaction_notes" : pd.DataFrame(reaction_notes_observations, columns=reaction_notes_cols),
        "reaction_workups" : pd.DataFrame(reaction_workups, columns=reaction_workups_cols),
        "reaction_outcomes" : pd.DataFrame(reaction_outcomes, columns=reaction_outcomes_cols),
        "compound" : compounds,
        "person" : persons
    }
    return out