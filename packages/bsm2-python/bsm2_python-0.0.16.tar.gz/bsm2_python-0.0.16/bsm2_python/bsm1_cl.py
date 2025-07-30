import csv
import os

import numpy as np

import bsm2_python.bsm2.init.asm1init_bsm1 as asm1init
from bsm2_python.bsm1_base import BSM1Base
from bsm2_python.bsm2.aerationcontrol import PID, Actuator, Sensor
from bsm2_python.bsm2.init import aerationcontrolinit_bsm1 as ac_init
from bsm2_python.log import logger

path_name = os.path.dirname(__file__)

SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = np.arange(21)


class BSM1CL(BSM1Base):
    """Creates a BSM1CL object. WARNING: Not validated yet!! Use at your own risk.

    Parameters
    ----------
    data_in : np.ndarray(n, 22) | str (optional)
        Influent data. Has to be a 2D array. <br>
        First column is time [d], the rest are 21 components
        (13 ASM1 components, TSS, Q, T and 5 dummy states).
        If a string is provided, it is interpreted as a file name.
        If not provided, the influent data from BSM2 is used. \n
        [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5]
    timestep : float (optional)
        Timestep for the simulation [d]. <br>
        If not provided, the timestep is set to 1 minute. <br>
        Please note: Due to sensor sensitivity, the timestep should not be larger than 1 minute.
    endtime : float (optional)
        Endtime for the simulation [d]. <br>
        If not provided, the endtime is the last time step in the influent data.
    evaltime : int | np.ndarray(2) (optional)
        Evaluation time for the simulation [d]. <br>
        When passed as an int, it defines the number of last days of the simulation to be evaluated.
        When passed as a 1D np.ndarray with two values, it defines the start and end time of the evaluation period.
        If not provided, the last 5 days of the simulation will be assessed. \n
        [starttime, self.simtime[-1]]
    use_noise : int (optional)
        - 0: No noise is added to the sensor data.
        - 1: A noise file is used to add noise to the sensor data.
             If so, a noise_file has to be provided. Needs to have at least 2 columns: time and noise data
        - 2: A random number generator is used to add noise to the sensor data. Seed is used from noise_seed. <br>
             Default is 1.
    noise_file : str (optional)
        Noise data. Needs to be provided if use_noise is 1.
        If not provided, the default noise file is used.
    noise_seed : int (optional)
        Seed for the random number generator.
        Default is 1.
    data_out : str (optional)
        Path to the output data file. <br>
        If not provided, no output data is saved.
    tempmodel : bool (optional)
        If `True`, the temperature model dependencies are activated.
        Default is `False`.
    activate : bool (optional)
        If `True`, the dummy states are activated.
        Default is `False`.
    """

    def __init__(
        self,
        data_in: np.ndarray | str | None = None,
        timestep: float | None = 1 / 60 / 24,
        endtime: float | None = None,
        evaltime: int | np.ndarray | None = None,
        use_noise: int = 1,
        noise_file: str | None = None,
        noise_seed: int = 1,
        data_out: str | None = None,
        *,
        tempmodel: bool = False,
        activate: bool = False,
    ):
        if timestep is not None and timestep > 1 / 60 / 24:
            logger.warning(
                'Timestep should not be larger than 1 minute due to sensor sensitivity. \
                           Will continue with provided timestep, but most probably fail.'
            )

        super().__init__(
            data_in=data_in,
            timestep=timestep,
            endtime=endtime,
            evaltime=evaltime,
            tempmodel=tempmodel,
            activate=activate,
            data_out=data_out,
        )
        num_sen = 1
        num_act = 1

        den_sno2 = [
            ac_init.T_SNO2**8,
            8 * ac_init.T_SNO2**7,
            28 * ac_init.T_SNO2**6,
            56 * ac_init.T_SNO2**5,
            70 * ac_init.T_SNO2**4,
            56 * ac_init.T_SNO2**3,
            28 * ac_init.T_SNO2**2,
            8 * ac_init.T_SNO2,
            1,
        ]
        self.sno2_sensor = Sensor(num_sen, den_sno2, ac_init.MIN_SNO2, ac_init.MAX_SNO2, ac_init.STD_SNO2)
        self.qintr_pid = PID(**ac_init.PID_QINTR_PARAMS)
        den_qintr = [ac_init.QINTRT, 1]
        self.qintr_actuator = Actuator(num_act, den_qintr)

        den_sen5 = [ac_init.T_SO5**2, 2 * ac_init.T_SO5, 1]
        self.so5_sensor = Sensor(num_sen, den_sen5, ac_init.MIN_SO5, ac_init.MAX_SO5, ac_init.STD_SO5)
        self.kla5_pid = PID(**ac_init.PID_KLA5_PARAMS)
        den_act5 = [ac_init.T_KLA5**2, 2 * ac_init.T_KLA5, 1]
        self.kla5_actuator = Actuator(num_act, den_act5)

        if use_noise == 0:
            self.noise_so4 = np.zeros(2)
            self.noise_timestep = np.array((0, self.endtime)).flatten()
        elif use_noise == 1:
            if noise_file is None:
                noise_file = path_name + '/data/sensornoise.csv'
            with open(noise_file, encoding='utf-8-sig') as f:
                noise_data = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)
            if noise_data[-1, 0] < self.endtime:
                err = 'Noise file does not cover the whole simulation time.\n \
                    Please provide a valid noise file.'
                raise ValueError(err)
            noise_shape_criteria = 2
            if noise_data.shape[1] < noise_shape_criteria:
                err = 'Noise file needs to have at least 2 columns: time and noise data'
                raise ValueError(err)
            self.noise_so4 = noise_data[:, 1].flatten()
            self.noise_timestep = noise_data[:, 0].flatten()
            del noise_data

        if timestep is None:
            # calculate difference between each time step in data_in
            self.simtime = self.noise_timestep
            self.timesteps = np.diff(
                self.noise_timestep, append=(2 * self.noise_timestep[-1,] - self.noise_timestep[-2,])
            )
        else:
            self.simtime = np.arange(0, self.data_in[-1, 0], timestep)
            self.timesteps = timestep * np.ones(len(self.simtime))

        self.simtime = self.simtime[self.simtime <= self.endtime]

        rng_mode = 2  # random number generator mode
        if use_noise in {0, 1}:
            pass
        elif use_noise == rng_mode:
            np.random.seed(noise_seed)
            # create random noise array with mean 0 and variance 1
            self.noise_so4 = np.random.normal(0, 1, len(self.simtime)).flatten()
            self.noise_timestep = self.simtime
        else:
            err = 'use_noise has to be 0, 1 or 2'
            raise ValueError(err)

        self.data_time = self.data_in[:, 0]
        # self.simtime = np.arange(0, self.endtime, self.timestep)

        self.kla3_a = ac_init.KLA3_INIT
        self.kla4_a = ac_init.KLA4_INIT
        self.kla5_a = ac_init.KLA5_INIT

    def step(self, i: int, so4ref: float | None = None, sno2ref: float | None = None):
        """Simulates one time step of the BSM1 model.

        Parameters
        ----------
        i : int
            Index of the current time step [-].
        so4ref : float (optional)
            Setpoint for the dissolved oxygen concentration [g(O₂) ⋅ m⁻³] \n
            If not provided, the setpoint is set to ac_init.SO4REF.
        sno2ref : float (optional)
            Setpoint for the SNO2 concentration [g(NO₂) ⋅ m⁻³] \n
            If not provided, the setpoint is set to asm1init.SNO2REF.
        """

        if so4ref is None:
            self.kla5_pid.setpoint = ac_init.SO4REF
        else:
            self.kla5_pid.setpoint = so4ref

        if sno2ref is None:
            sno2ref = ac_init.SNO2REF
        self.qintr_pid.setpoint = sno2ref

        step: float = self.simtime[i]
        stepsize: float = self.timesteps[i]

        # get index of noise that is smaller than and closest to current time step within a small tolerance
        idx_noise = int(np.where(self.noise_timestep - 1e-7 <= step)[0][-1])

        # SNO2 Control
        self.sno2_signal = self.sno2_sensor.output(self.y_out2[SNO], stepsize, self.noise_so4[idx_noise])
        inject = ac_init.KFEEDFORWARD * (sno2ref / (sno2ref + 1)) * (asm1init.QIN * ac_init.QFFREF - self.qintr)
        self.qintr_pid_signal = self.qintr_pid.output(self.sno2_signal, stepsize, inject)
        qintr_act_signal = self.qintr_actuator.output(self.qintr_pid_signal, stepsize)
        self.qintr = qintr_act_signal

        # SO5 Control
        self.so5_signal = self.so5_sensor.output(self.y_out5[SO], stepsize, self.noise_so4[idx_noise])
        self.kla5_pid_signal = self.kla5_pid.output(self.so5_signal, stepsize)
        kla5_act_signal = self.kla5_actuator.output(self.kla5_pid_signal, stepsize)
        self.kla5_a = kla5_act_signal

        self.klas = np.array([0, 0, self.kla3_a, self.kla4_a, self.kla5_a])
        super().step(i)
