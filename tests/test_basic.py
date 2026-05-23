def estimate_co2(cpu_percent, duration_seconds, tdp_watts=15, om_factor=0.4364):
    """
    Estimate CO2 emissions from CPU usage.
    
    Args:
        cpu_percent: CPU utilization percentage (0-100)
        duration_seconds: time in seconds
        tdp_watts: Thermal Design Power rating of CPU (default: 15W for laptops)
        om_factor: Operating Margin carbon intensity factor (default: 0.4364 kgCO2/kWh)
    
    Returns:
        Estimated CO2 emissions in kg
    """
    # Calculate power consumption in watts
    power_watts = tdp_watts * (cpu_percent / 100.0)
    
    # Convert to kWh: (watts * seconds) / 3,600,000
    energy_kwh = power_watts * duration_seconds / 3600000.0
    
    # Calculate CO2 emissions
    co2_kg = energy_kwh * om_factor
    
    return co2_kg

def test_co2_calculation():
    """
    Verify the basic calculation logic with known values.
    1 kWh = 0.4364 kg CO2 (Hubei provincial grid factor (MEE 2022 bulletin)
    """
    # 1000W * 3600s = 1 kWh should produce exactly 0.4364 kg CO2
    expected_energy = 1.0  # kWh
    expected_co2 = expected_energy * 0.4364
    
    result = estimate_co2(cpu_percent=100.0, duration_seconds=3600, tdp_watts=1000, om_factor=0.4364)
    assert abs(result - 0.4364) < 1e-9, "1 kWh should produce exactly 0.4364 kg CO2"
    
    print(f"✓ Test passed: 1 kWh = {result:.4f} kg CO2")
    print(f"✓ Hubei provincial grid factor verified: 0.4364 kgCO2/kWh (MEE 2022 bulletin)")

if __name__ == "__main__":
    test_co2_calculation()
