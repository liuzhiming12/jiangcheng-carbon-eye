def calculate_emissions(power_consumption: float, duration: float, carbon_intensity: float = 0.562, scope: int = 2) -> dict:
    """
    Calculate carbon emissions from code execution

    Args:
    power_consumption: float - Power consumption in watts
    duration: float - Runtime in seconds
    carbon_intensity: float - Carbon intensity in kgCO2/kWh (default: Hubei grid carbon intensity)
    scope: int - Emission scope (1: direct, 2: indirect, 3: other indirect)

    Returns:
    dict - Dictionary with energy consumption (kWh) and emissions (kgCO2)
    """
    energy_kwh = (power_consumption * duration) / (1000 * 3600)
    emissions = energy_kwh * carbon_intensity
    return {
        "energy_consumption": energy_kwh,
        "emissions": emissions,
        "scope": scope
    }
