"""This script will run the plant in an open loop simulation (no control) with dynamic input data together with the
energy management system.

- BSM2 base: Primary clarifier, 5 asm1 reactors, a second clarifier, sludge thickener,
adm1 fermenter, sludge dewatering and wastewater storage in dynamic simulation without any controllers.

- BSM2 energy management: Biogas compressor, biogas storage, 2 CHP units, boiler, flare, heat network, cooler
and a module for economic evaluation.

This script requires that the packages from requirements.txt are installed
within the Python environment you are running this script.

The parameters 'tempmodel' and 'activate' can be set to 'True' if you want to activate them.
"""

from bsm2_olem import BSM2OLEM

from bsm2_python.log import logger

logger.info('Initialize bsm2\n')

timestep = 15 / 24 / 60  # 15 minutes in fraction of a day
"""15 minutes in fraction of a day [d⁻¹]."""
endtime = 50  # 50 days
"""Endtime [d⁻¹]."""
total_steps = int(endtime / timestep)
"""Total simulation steps [-]."""

tempmodel = (
    False  # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
)
# if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

activate = False  # if activate is False dummy states are 0
# if activate is True dummy states are activated

bsm2 = BSM2OLEM(timestep=timestep, endtime=endtime, tempmodel=tempmodel, activate=activate)

bsm2.simulate()
