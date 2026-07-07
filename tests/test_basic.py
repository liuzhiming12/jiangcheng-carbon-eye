def estimate_co2(cpu_percent, duration_seconds, tdp_watts=15, om_factor=0.4364):
    hours = duration_seconds / 3600.0
    power_watts = tdp_watts * (cpu_percent / 100.0)
    energy_kwh = (power_watts * hours) / 1000.0
    co2_kg = energy_kwh * om_factor
    return co2_kg

def test_zero_load():
    assert estimate_co2(0.0, 3600, 15) == 0.0

def test_full_load():
    result = estimate_co2(100.0, 3600, 15)
    expected = (15.0 * 1.0 / 1000.0) * 0.4364
    assert abs(result - expected) < 1e-9

def test_om_factor():
    assert abs(estimate_co2(100.0, 3600, 1000, 0.4364) - 0.4364) < 1e-9

if __name__ == "__main__":
    test_zero_load()
    test_full_load()
    test_om_factor()
    print("All basic tests passed.")