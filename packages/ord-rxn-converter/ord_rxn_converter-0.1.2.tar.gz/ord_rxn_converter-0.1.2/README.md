# Project Description for ord_rxn_converter

## Introduction

`ord_rxn_converter` is a Python package designed to streamline the transformation of chemical reaction data from the Open Reaction Database (ORD) in Google Protocol Buffer format into structured datasets suitable for downstream machine learning and data analysis tasks. It provides modular tools for parsing, extracting, and converting complex reaction schema into interpretable tables, lists, and dictionaries that can be easily ingested by models or used in exploratory chemical data analysis.

The library is organized into specialized modules that handle different components of the reaction schema — including identifiers, inputs, conditions, setup, workups, outcomes, and notes/observations — as well as utility functions for key operations and dataset generation. The package is structured for clarity and extendibility, enabling researchers to adapt it to varying needs in computational chemistry or cheminformatics pipelines.

The codebase is written in Python 3 and supports integration into Jupyter notebooks, standalone scripts, or larger ML pipelines for tasks such as property prediction, reaction classification, or synthesis planning.

## Motivation

Chemical reaction data is often stored in highly nested or semi-structured formats that are difficult to work with directly in data science workflows. The Open Reaction Database provides a valuable standardized format, but researchers and developers often require a flat, structured format with clean fields to build models or perform analysis.

`ord_rxn_converter` was developed to automate and standardize this transformation process. It allows users to systematically convert the complex data in ORD protobuf files into simplified Python structures (lists, dictionaries, Pandas DataFrames), reducing time spent on preprocessing and improving reproducibility in ML workflows. By modularizing the conversion process, the package promotes clarity, flexibility, and easier debugging.

The project originated as part of a broader effort to accelerate machine learning-driven synthesis planning by improving the usability of publicly available chemical data.

## Limitations

- The package currently assumes that input ORD data conforms closely to the expected schema. It may require modification or additional error handling for incomplete or non-standard records.

- Complex reaction pathways involving multi-step synthesis or overlapping outcomes may not be fully supported in this version.

- The current modules focus primarily on extraction rather than validation or correction of chemical information. Users are advised to preprocess or sanitize their data before applying the conversion tools if needed.

- While the package is modular, it is not yet fully abstracted for plug-and-play use in non-ORD schemas. Adapting it to other chemical data formats (e.g., USPTO, Reaxys) would require extension.

- The project is in active development, and interface or function-level changes may occur in future versions.

## Affiliations: 
Materials Data Science for Stockpile Stewardship Center of Excellence (MDS3-COE),
Solar Durability and Lifetime Extension (SDLE) Research Center, 
Materials Science and Engineering,
Case Western Reserve University,
Cleveland, OH 44106, USA

## Package Usage: 
The package will convert a dataset (that contains hundreds to thousands of reactions) in ORD schema in Google Protocol Buffers format into a dictionary of pandas DataFrames for each reaction portion: reaction identifiers, reaction inputs, reaction conditions, reaction setup, reaction outcomes, reaction notes and observations. 

## Python package documentation
https://sphinx-rtd-tutorial.readthedocs.io/en/latest/index.html

## Acknowledgements: 

This work was supported by the U.S. Department of Energy’s Office of Energy Efficiency and Renewable Energy (EERE) under Solar Energy Technologies Office (SETO) Agreement Numbers DE-EE0009353 and DE-EE0009347, Department of Energy (National Nuclear Security Administration) under Award Number DE-NA0004104 and Contract number B647887, and U.S. National Science Foundation Award under Award Number 2133576.