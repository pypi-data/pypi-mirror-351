# import requirements: 
from ord_schema.proto import dataset_pb2, reaction_pb2
from google.protobuf.message import Message
from ord_rxn_converter.utility_functions_module import extract_all_enums

#generate enums_data to be accessible here TODO - have importable object instead..?
enums_data = extract_all_enums(reaction_pb2)

def extract_reaction_conditions(conditions, reactionID: str) -> list:

    """
    Extracts reaction condition information from an ORD reaction message.

    This function aggregates all available reaction condition data from an
    Open Reaction Database (ORD) `reaction` message, including temperature,
    pressure, stirring, illumination, electrochemistry, and flow conditions.

    Args:
        reaction (message.Reaction): The ORD reaction message from which to
            extract condition data.

    Returns:
        Dict[str, Dict[str, Union[str, float, bool]]]: A dictionary where keys
        represent condition types (e.g., "temperature", "pressure", etc.) and
        values are dictionaries of extracted parameters for each condition.
        If a condition is not present in the reaction message, it is omitted
        from the output.

    Example:
        >>> from ord_schema.proto import reaction_pb2
        >>> from ord_schema.proto import dataset_pb2
        >>> dataset = dataset_pb2.Dataset()
        >>> reaction = dataset.reactions[0] 
        >>> conditions = extract_reaction_conditions(reaction.conditions, reactionID='rxn-028')
    """

    # TODO: If object temperature is not None, run the extract_temperature_conditions function
    if hasattr(conditions, 'temperature') and conditions.temperature:
        temperature = conditions.temperature
        temp_condition = temperature_conditions(temperature)
    else: temp_condition = None

    # TODO: If detects pressure conditions, run the pressure condition function
    if hasattr(conditions, 'pressure') and conditions.pressure:
        pressure = conditions.pressure
        press_condition = pressure_conditions(pressure)
    else: press_condition = None

    # TODO: If detects stirring conditions, run the stirring condition function
    if hasattr(conditions, 'stirring') and conditions.stirring:
        stirring = conditions.stirring 
        stir_condition = stirring_conditions(stirring)
    else: stir_condition = None
    
    # TODO: If detects illumination conditions, run the illumination condition function
    if hasattr(conditions, 'illumination') and conditions.illumination:
        illumination = conditions.illumination
        illum_condition = illumination_conditions(illumination)
    else: illum_condition = None
    
    # TODO: If detects electrochemistry conditions, run the electrochemistry condition function
    if hasattr(conditions, 'electrochemistry') and conditions.electrochemistry: 
        electrochemistry = conditions.electrochemistry
        electro_condition = electrochemistry_conditions(electrochemistry)
    else: electro_condition = None
    
    # TODO: If detects flow conditions, run the flow condition function
    if hasattr(conditions, 'flow') and conditions.flow:
        flow = conditions.flow 
        flow_condition = flow_conditions(flow)
    else: flow_condition = None
    
    #optional bool reflux = 7
    if hasattr(conditions, 'reflux') and conditions.reflux:
        reflux_condition = conditions.reflux
    else: reflux_condition = None

    #optional float ph = 8
    if hasattr(conditions, 'ph') and conditions.ph:
        ph_condition = conditions.ph
    else: ph_condition = None

    #option bool conditions_are_dynamic = 9
    if hasattr(conditions, 'conditions_are_dynamic') and conditions.conditions_are_dynamic:
        dynamic_condition = conditions.conditions_are_dynamic
    else: dynamic_condition = None

    #string details = 10 
    if conditions.details:
        details_condition = conditions.details
    else: details_condition = None

    reaction_conditions = [reactionID, temp_condition, press_condition, stir_condition, illum_condition, electro_condition, flow_condition, 
        reflux_condition, ph_condition, dynamic_condition, details_condition]
    
    return reaction_conditions

def temperature_conditions(temperature) -> dict:

    """
    Extracts temperature condition from an ORD reaction message.

    Args:
        reaction (message.Reaction): The reaction message containing temperature conditions.

    Returns:
        Optional[Dict[str, Union[str, float]]]: A dictionary with temperature
        condition details, or None if no temperature condition is found. Keys
        may include "value", "units", "setpoint", and "control".
    """
    # temperature control = 1 
    if temperature.control: 
        control_type = enums_data['TemperatureConditions.TemperatureControl.TemperatureControlType'][temperature.control.type]
        temperature_control = {control_type:temperature.control.details}
    else: temperature_control = None

    # temperature setpoint = 2
    if temperature.setpoint:
        setpoint_value = temperature.setpoint.value
        setpoint_unit = enums_data['Temperature.TemperatureUnit'][temperature.setpoint.units]
    else: 
        setpoint_value = None
        setpoint_unit = None

    # temperature measurements = 3
    if temperature.measurements:
        temperature_measurement = temperature.measurements
        temperature_measurement_list = []
        for measurement in temperature_measurement:
            measurement_type = enums_data['TemperatureConditions.TemperatureMeasurement.TemperatureMeasurementType'][measurement.type]
            measurement_time_unit = enums_data['Time.TimeUnit'][measurement.time.units]
            measurement_temperature_unit = enums_data['Temperature.TemperatureUnit'][measurement.temperature.units]
            temperature_measurement_list.append([measurement_type, measurement.details, measurement.time.value, measurement_time_unit, measurement.temperature.value, measurement_temperature_unit])
    else: temperature_measurement_list = None
    
    temperature_condition = {'temperatureControl': temperature_control, 'temperatureSetpoint': setpoint_value, 'temperatureUnit': setpoint_unit, 'temperatureMeasurements':temperature_measurement_list}

    return temperature_condition

def pressure_conditions(pressure) -> dict: 

    """
    Extracts pressure condition from an ORD reaction message.

    Args:
        reaction (message.Reaction): The reaction message containing pressure conditions.

    Returns:
        Optional[Dict[str, Union[str, float]]]: A dictionary with pressure
        condition details, or None if no pressure condition is found. Keys may
        include "value", "units", and "control".
    """
    # pressure control = 1 
    if pressure.control:
        control_type = enums_data['PressureConditions.PressureControl.PressureControlType'][pressure.control.type]
        pressure_control = {control_type:pressure.control.details}
    else: pressure_control = None 

    # pressure setpoint = 2 
    if pressure.setpoint:
        pressure_setpoint = pressure.setpoint.value
        pressure_unit = enums_data['Pressure.PressureUnit'][pressure.setpoint.units]
    else:
        pressure_setpoint = None
        pressure_unit = None
    
    # atmosphere = 3
    atmosphere = enums_data['PressureConditions.Atmosphere.AtmosphereType'][pressure.atmosphere.type] if pressure.atmosphere else None

    # pressure measurements = 4
    if pressure.measurements:
        pressure_measurements = pressure.measurements
        pressure_measurement_list = []
        for measurement in pressure_measurements:
            measurement_type = enums_data['PressureConditions.PressureMeasurement.PressureMeasurementType'][measurement.type]
            measurement_time_unit = enums_data['Time.TimeUnit'][measurement.time.units]
            measurement_pressure_unit = enums_data['Pressure.PressureUnit'][measurement.pressure.units]
            pressure_measurement_list.append([measurement_type, measurement.details, measurement.time.value, measurement_time_unit, measurement.pressure.value, measurement_pressure_unit])
    else:
        pressure_measurement_list = None

    pressure_condition = {'pressureControl':pressure_control, 'pressureSetpoint':pressure_setpoint, 'pressureUnit':pressure_unit, 'reactionAtmosphere':atmosphere, 'pressureMeasurements':pressure_measurement_list}

    return pressure_condition

def stirring_conditions(stirring) -> dict:

    """
    Extracts stirring condition from an ORD reaction message.

    Args:
        reaction (message.Reaction): The reaction message containing stirring conditions.

    Returns:
        Optional[Dict[str, Union[str, float, bool]]]: A dictionary with stirring
        condition details, or None if no stirring condition is found. Keys may
        include "type", "rate", "units", and "control".
    """
    # stirring method type = 1
    stirring_method = enums_data['StirringConditions.StirringMethodType'][stirring.type]

    # details = 2

    # stirring rate = 3
    rate_type = enums_data['StirringConditions.StirringRate.StirringRateType'][stirring.rate.type] if stirring.rate else None

    stirring_condition = {'stirringMethod':stirring_method, 'stirringDetails':stirring.details, 'stirringRate': rate_type, 'rateDetails':stirring.rate.details if stirring.rate else None, 'rpm':stirring.rate.rpm if stirring.rate else None}

    return stirring_condition

def illumination_conditions(illumination) -> dict:

    """
    Extracts illumination condition from an ORD reaction message.

    Args:
        reaction (message.Reaction): The reaction message containing illumination conditions.

    Returns:
        Optional[Dict[str, Union[str, float]]]: A dictionary with illumination
        condition details, or None if no illumination condition is found. Keys
        may include "type", "wavelength", and "wavelength_units".
    """
    # type = 1
    illumination_type = enums_data['IlluminationConditions.IlluminationType'][illumination.type]

    # details = 2

    # peak wavelength = 3
    if illumination.peak_wavelength:
        peak_Wavelength = illumination.peak_wavelength.value
        wavelength_unit = enums_data['Wavelength.WavelengthUnit'][illumination.peak_wavelength.units]
    else: 
        peak_Wavelength = None
        wavelength_unit = None
    # color = 4

    # distance_to_vessel = 5 
    if illumination.distance_to_vessel:
        distance_to_vessel = illumination.distance_to_vessel.value
        distance_unit = enums_data['Length.LengthUnit'][illumination.distance_to_vessel.units]
    else:
        distance_to_vessle = None
        distance_unit = None

    illumination_condition = {'illuminationType':illumination_type, 'illuminationDetails':illumination.details, 'peakWavelength': peak_Wavelength, 'wavelengthUnit': wavelength_unit, 
        'illuminationColor': illumination.color if illumination.color else None, 'distanceToVessel':distance_to_vessel, 'distanceUnit':distance_unit}

    return illumination_condition

def electrochemistry_conditions(electrochemistry) -> dict:

    """
    Extracts electrochemistry condition from an ORD reaction message.

    Args:
        reaction (message.Reaction): The reaction message containing electrochemistry conditions.

    Returns:
        Optional[Dict[str, Union[str, float]]]: A dictionary with electrochemistry
        condition details, or None if no electrochemistry condition is found.
        Keys may include "type", "current", "potential", "cell_type", "anode",
        and "cathode".
    """

    # type = 1 
    electrochemistry_type = enums_data['ElectrochemistryConditions.ElectrochemistryType'][electrochemistry.type]

    # details = 2
    
    # current = 3
    if electrochemistry.current:
        current = electrochemistry.current.value
        current_unit = enums_data["Current.CurrentUnit"][electrochemistry.current.units]
    else:
        current = None
        current_unit = None

    #voltage = 4 
    if electrochemistry.voltage:
        voltage = electrochemistry.voltage.value
        voltage_unit = enums_data["Voltage.VoltageUnit"][electrochemistry.voltage.units]
    else: 
        voltage = None
        voltage_unit = None
    
    # anodeMaterial (string) = 5
    anode_material = electrochemistry.anode_material
    
    # cathodeMaterial (string) = 6 
    cathode_material = electrochemistry.cathode_material

    # electrode_separation = 7 
    if electrochemistry.electrode_separation:
        electrode_separation = electrochemistry.electrode_separation.value
        separation_unit = enums_data["Length.LengthUnit"][electrochemistry.electrode_separation.units]
    else: 
        electrode_separation = None
        separation_unit = None
    # measurements = 8 
    if electrochemistry.measurements:
        electrochemistry_measurements = electrochemistry.measurements
        meausurement_list = [] 
        for measurement in electrochemistry_measurements:
            measurement_time = measurement.time.value
            time_unit = enums_data['Time.TimeUnit'][measurement.time.units]
            measurement_current = measurement.current.value
            current_unit = enums_data['Current.CurrentUnit'][measurement.current.units]
            measurement_voltage = measurement.voltage.value
            voltage_unit = enums_data['Voltage.VoltageUnit'][measurement.voltage.units]
            measurement_list.append([measurement_time, time_unit, measurement_current, current_unit, measurement_voltage, voltage_unit])
    else: measurement_list = None
    
    # cell = 9
    cell_type = enums_data['ElectrochemistryConditions.ElectrochemistryCell.ElectrochemistryCellType'][electrochemistry.cell.type]
    electrochem_cell = dict(zip(cell_type, electrochemistry.cell.details))
    
    # Create a list to store all of the electrochemistry conditions:
    electrochemistry_condition = {'electrochemistryType':electrochemistry_type, 'electrochemistryDetails':electrochemistry.details, 'current':current, 'currentUnit':current_unit, 
        'voltage':voltage, 'voltageUnit':voltage_unit, 'anodeMaterial':anode_material, 'cathodeMaterial':cathode_material, 'electrodeSeparation': electrode_separation, 'separationUnit':separation_unit, 
        'electrochemistryMeasurements':measurement_list, 'electrochemistryCell':electrochem_cell}

    return electrochemistry_condition

def flow_conditions(flow) -> dict:

    """
    Extracts flow condition from an ORD reaction message.

    Args:
        reaction (message.Reaction): The reaction message containing flow conditions.

    Returns:
        Optional[Dict[str, Union[str, float]]]: A dictionary with flow
        condition details, or None if no flow condition is found. Keys may
        include "flow_rate", "flow_rate_units", "residence_time",
        "residence_time_units", and "slug_diameter".
    """
    # type = 1
    flow_type = enums_data['FlowConditions.FlowType'][flow.type]

    # details = 2

    # pump_type = 3

    # tubing = 4
    if flow.tubing:
        tubing_type = enums_data['FlowConditions.Tubing.TubingType'][flow.tubing.type]
        tubing_diameter = flow.tubing.diameter.value
        diameter_unit = enums_data['Length.LengthUnit'][flow.tubing.diameter.units]
    else: 
        tubing_type = None
        tubing_diameter = None
        diameter_unit = None

    flow_condition = {'flowType':flow_type, 'flowDetails':flow.details, 'pumpType':flow.pump_type, 'tubingType':tubing_type, 'tubingDetails':flow.tubing.details, 'tubingDiameter':tubing_diameter, 'diameterUnit':diameter_unit}
    
    return flow_condition