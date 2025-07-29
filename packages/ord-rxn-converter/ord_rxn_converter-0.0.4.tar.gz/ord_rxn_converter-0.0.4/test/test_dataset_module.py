import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ord_rxn_converter import dataset_module

path = '~ ord_rxn_converter/test/data' # relative path only 

file_list = []
for root, dirs, files in os.walk(path):
    for name in files: 
        if name.startswith('ord_dataset'):
            file_path = os.path.join(root, name)
            file_list.append(file_path)
file_path = file_list[1]

expected = dataset_module.extract_dataset(file_path)

def test_extract_dataset ():
    # arrange:    
    expected_result = expected

    # act:
    result = dataset_module.extract_dataset(file_path)

    assert set(result.keys()) == set(expected_result.keys()), "Dictionaries have different keys"
    import pandas as pd
    for key in result.keys():
        pd.testing.assert_frame_equal(result[key], expected_result[key], 
                                    check_dtype=True, check_index_type=True,
                                    check_column_type=True, check_frame_type=True)


