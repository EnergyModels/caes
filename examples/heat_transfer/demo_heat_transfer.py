import CoolProp.CoolProp as CP
from caes import pipe_heat_transfer_subsurface, pipe_heat_transfer_ocean

# ==========================================
# Run at default conditions
# ==========================================
print("\n\ndefault conditions - subsurface\n")
dT_pipe1 = pipe_heat_transfer_subsurface(debug=True)

# ==========================================
# Run at default conditions
# ==========================================
print("\n\ndefault conditions - ocean\n")
dT_pipe2 = pipe_heat_transfer_ocean(debug=True)