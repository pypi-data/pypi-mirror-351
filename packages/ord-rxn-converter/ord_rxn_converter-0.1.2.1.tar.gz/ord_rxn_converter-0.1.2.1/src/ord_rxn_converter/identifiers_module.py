# import requirements: 
from ord_schema.proto import dataset_pb2, reaction_pb2
from google.protobuf.message import Message
from rdkit import Chem
from rdkit.Chem import AllChem
from ord_rxn_converter.utility_functions_module import extract_all_enums

#generate enums_data to be accessible here TODO - have importable object instead..?
enums_data = extract_all_enums(reaction_pb2)

def extract_reaction_identifiers(identifiers, reactionID: str) -> list:
    """
    Extracts detailed reaction identifier information for a given reaction.

    Args:
        identifiers (list): A list of `ReactionIdentifier` protobuf messages.
        reactionID (str): Unique reaction ID string.

    Returns:
        list: A list in the format:
            [reactionID, reaction_smiles, reaction_cxsmiles, rdfile, rinchi, reaction_type, unspecified, custom, details_dict, mapped_dict]

    Example:
        >>> from identifiers_module import extract_reaction_identifiers
        >>> extract_reaction_identifiers(reaction.identifiers, 'rxn-000001')
        ['rxn-000001', 'CCO>>CC=O', None, None, None,
         'REACTION_TYPE_XYZ', None, None,
         {'REACTION_CXSMILES': 'CCO>>CC=O'}, {'REACTION_CXSMILES': True}]
    """

    # Initiate empty lists to store identifier type, details, value, and is_mapped.
    identifier_type= []
    identifier_details = []
    identifier_value = []
    identifier_mapped = []

    for identifier in identifiers: 
        # append lists
        identifier_type.append(enums_data['ReactionIdentifier.ReactionIdentifierType'][identifier.type])
        identifier_value.append(identifier.value)
        identifier_details.append(identifier.details)
        identifier_mapped.append(identifier.is_mapped)

    # create a dictionary of identifier types and values and a dictionary of identifier types and details
    identifier_dict = dict(zip(identifier_type, identifier_value))
    details_dict = dict(zip(identifier_type, identifier_details))
    mapped_dict = dict(zip(identifier_type, identifier_mapped))

    # extract values
    unspecified = identifier_dict.get('UNSPECIFIED')
    custom = identifier_dict.get('CUSTOM')
    reaction_smiles = identifier_dict.get('REACTION_SMILES')
    reaction_cxsmiles = identifier_dict.get('REACTION_CXSMILES') 
    rdfile = identifier_dict.get('RDFILE')  
    rinchi = identifier_dict.get('RINCHI')
    reaction_type = identifier_dict.get('REACTION_TYPE')

    reaction_identifiers = [reactionID, reaction_smiles, reaction_cxsmiles, rdfile, rinchi, reaction_type, unspecified, custom, details_dict, mapped_dict]

    return reaction_identifiers

from rdkit import Chem

def extract_compound_identifiers(compound_identifiers):

    """
    Extracts compound identifier values and ensures key identifiers are present.

    Generates missing InChI keys and CXSMILES if possible using RDKit.

    Args:
        compound_identifiers (list): A list of `CompoundIdentifier` protobuf messages.

    Returns:
        tuple: 
            - str: InChI key of the compound.
            - dict: Dictionary of identifier types to their values.

    Example:
        >>> from identifiers_module import extract_compound_identifiers
        >>> compound_identifiers = reaction.inputs['...'].components[0].identifiers
        >>> extract_compound_identifiers(compound_identifiers)
        ('ROSDSFDQCJNGOL-UHFFFAOYSA-N', {'NAME': 'dimethylamine', 'SMILES': 'CCO', ...})
    """
    
    identifier_type_list = []
    identifier_details_list = []
    identifier_value_list = []

    for identifier in compound_identifiers:
        identifier_type = enums_data['CompoundIdentifier.CompoundIdentifierType'][identifier.type]
        identifier_type_list.append(identifier_type)
        identifier_value_list.append(identifier.value)
        identifier_details_list.append(identifier.details)

    identifier_dict = dict(zip(identifier_type_list, identifier_value_list))

    # Safely access keys - get() ensures they return None if they do not exist
    inchi_key = identifier_dict.get('INCHI_KEY')
    inchi = identifier_dict.get('INCHI')
    smiles = identifier_dict.get('SMILES')
    cxsmiles = identifier_dict.get('CXSMILES')

    if inchi_key is None and inchi:
        rdkit_mol = Chem.MolFromInchi(inchi)
        if rdkit_mol:
            identifier_dict['INCHI_KEY'] = Chem.MolToInchiKey(rdkit_mol)
            inchi_key = identifier_dict.get('INCHI_KEY')

    elif inchi_key is None and inchi is None and smiles:
        rdkit_mol = Chem.MolFromSmiles(smiles)
        if rdkit_mol:
            identifier_dict['INCHI'] = Chem.MolToInchi(rdkit_mol)
            identifier_dict['INCHI_KEY'] = Chem.MolToInchiKey(rdkit_mol)
            inchi_key = identifier_dict.get('INCHI_KEY')

    if smiles and cxsmiles is None:
        rdkit_mol = Chem.MolFromSmiles(smiles)
        identifier_dict['CXSMILES'] = Chem.MolToCXSmiles(rdkit_mol)
    
    else: pass

    return inchi_key, identifier_dict

def generate_compound_table (compound_identifiers):

    """
    Generates a full set of compound identifiers in a fixed order.

    If InChI key or CXSMILES are missing, attempts to generate them using RDKit.

    Args:
        compound_identifiers (list): A list of `CompoundIdentifier` protobuf messages,
            typically accessed via `reaction.inputs['m1_m2'].components[0].identifiers`.

    Returns:
        list: A list of compound identifier values in this order:
            [inchi_key, smiles, inchi, iupac_name, name, cas_number, pubchem_cid, chemspider_id, cxsmiles, unspecified, custom, molblock, xyz, uniprot_id, pdb_id, amino_acid_sequence, helm, mdl]

    Example:
        >>> from identifiers_module import generate_compound_table
        >>> compound_identifiers = reaction.inputs['...'].components[0].identifiers
        >>> generate_compound_table(compound_identifiers)
        ['BQJCRHHNABKAKU-KBQPJGBKSA-N', 'CCO', 'InChI=1S/C2H6O/...', ...]
    """

    identifier_type_list = []
    identifier_details_list = []
    identifier_value_list = []

    for identifier in compound_identifiers:
        identifier_type = enums_data['CompoundIdentifier.CompoundIdentifierType'][identifier.type]

        identifier_type_list.append(identifier_type)
        identifier_value_list.append(identifier.value)
        identifier_details_list.append(identifier.details)

    identifier_dict = dict(zip(identifier_type_list, identifier_value_list))
    details_dict = dict(zip(identifier_type_list, identifier_details_list))

    if identifier_dict.get('INCHI_KEY') is None and identifier_dict.get('INCHI'): 
        inchi = identifier_dict.get('INCHI')
        rdkit_mol = Chem.MolFromInchi(inchi)
        identifier_dict['INCHI_KEY'] = Chem.MolToInchiKey(rdkit_mol)
    
    elif identifier_dict.get('INCHI_KEY') is None and identifier_dict.get('INCHI') is None:
        smiles_string = identifier_dict.get('SMILES')
        rdkit_mol = None
        identifier_dict['INCHI'] = None
        identifier_dict['INCHI_KEY'] = None
        if smiles_string:  #Chem.MolFromSmiles errors if passed None
            rdkit_mol = Chem.MolFromSmiles(smiles_string)
            identifier_dict['INCHI'] = Chem.MolToInchi(rdkit_mol)
            identifier_dict['INCHI_KEY'] = Chem.MolToInchiKey(rdkit_mol)

    else: pass

    if identifier_dict.get('SMILES') and identifier_dict.get('CXSMILES') is None: 
        smiles_string = identifier_dict.get('SMILES')
        rdkit_mol = None
        if smiles_string:  #Chem.MolFromSmiles errors if passed None
            rdkit_mol = Chem.MolFromSmiles(smiles_string)
        identifier_dict['CXSMILES'] = Chem.MolToCXSmiles(rdkit_mol) 
    
    else: pass

    # extract values
    inchi_key = identifier_dict.get('INCHI_KEY')
    smiles = identifier_dict.get('SMILES')
    inchi = identifier_dict.get('INCHI')
    iupac_name = identifier_dict.get('IUPAC_NAME')
    name = identifier_dict.get('NAME')
    cas_number = identifier_dict.get('CAS_NUMBER')
    pubchem_cid = identifier_dict.get('PUBCHEM_CID')
    chemspider_id = identifier_dict.get('CHEMSPIDER_ID')
    cxsmiles = identifier_dict.get('CXSMILES')
    unspecified = identifier_dict.get('UNSPECIFIED')
    custom = identifier_dict.get('CUSTOM')
    molblock = identifier_dict.get('MOLBLOCK')
    xyz = identifier_dict.get('XYZ')
    uniprot_id = identifier_dict.get('UNIPROT_ID')
    pdb_id = identifier_dict.get('PDB_ID')
    amino_acid_sequence = identifier_dict.get('AMINO_ACID_SEQUENCE')
    helm = identifier_dict.get('HELM')
    mdl = identifier_dict.get('MDL')

    compound_identifiers = [inchi_key, smiles, inchi, iupac_name, name, cas_number, pubchem_cid, chemspider_id, cxsmiles, unspecified, custom, molblock, xyz, uniprot_id, pdb_id, amino_acid_sequence, helm, mdl]

    #TODO - figure out what to do with details_dict

    return compound_identifiers
