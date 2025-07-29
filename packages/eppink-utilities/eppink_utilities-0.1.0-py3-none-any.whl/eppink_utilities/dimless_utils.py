from CoolProp.CoolProp import PropsSI


def calculate_rayleigh(L, Tin, Tout, fluid='Nitrogen', P=101325):
    """
    Calculates the Rayleigh number for a fluid using CoolProp based on real gas data.

    Parameters:
        L (float): Gap width [m]
        Tin (float): Inner temperature [K]
        Tout (float): Outer temperature [K]
        fluid (str): Fluid name (e.g., 'Nitrogen', 'Air', etc.)
        P (float): Pressure [Pa]

    Returns:
        Ra (float): Rayleigh number
        props (dict): Dictionary of evaluated fluid properties at T_avg
    """
    # Gravity
    g = 9.81  # m/s^2

    # Average temperature and temperature difference
    T_avg = 0.5 * (Tin + Tout)
    dT = abs(Tin - Tout)

    try:
        # Get properties at average temperature and specified pressure
        rho = PropsSI('D', 'T', T_avg, 'P', P, fluid)     # Density [kg/m^3]
        mu = PropsSI('V', 'T', T_avg, 'P', P, fluid)      # Dynamic viscosity [Pa·s]
        k = PropsSI('L', 'T', T_avg, 'P', P, fluid)       # Thermal conductivity [W/m·K]
        cp = PropsSI('C', 'T', T_avg, 'P', P, fluid)      # Specific heat at constant pressure [J/kg·K]
        beta = PropsSI('ISOBARIC_EXPANSION_COEFFICIENT', 'T', T_avg, 'P', P, fluid)  # [1/K]
    except Exception as e:
        raise RuntimeError(f"Error retrieving properties from CoolProp: {e}")

    # Derived properties
    nu = mu / rho                   # Kinematic viscosity [m²/s]
    alpha = k / (rho * cp)         # Thermal diffusivity [m²/s]

    # Rayleigh number
    Ra = g * beta * dT * L**3 / (nu * alpha)

    # Return Rayleigh number and all properties
    props = {
        'T_avg [K]': T_avg,
        'rho [kg/m³]': rho,
        'mu [Pa·s]': mu,
        'k [W/m·K]': k,
        'cp [J/kg·K]': cp,
        'beta [1/K]': beta,
        'nu [m²/s]': nu,
        'alpha [m²/s]': alpha,
        'Ra [-]': Ra
    }

    return Ra, props


if __name__ == "__main__":
    # Example usage
    L = 7/1000     # m
    Tin = 300      # K
    Tout = 100     # K
    P = 101325     # Pa
    fluid = 'Nitrogen'

    Ra, props = calculate_rayleigh(L, Tin, Tout, fluid, P)

    print(f"Rayleigh number: {Ra:.2e}")
