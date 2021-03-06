"""
    FAST - Copyright (c) 2016 ONERA ISAE
"""

#  This file is part of FAST : A framework for rapid Overall Aircraft Design
#  Copyright (C) 2020  ONERA & ISAE-SUPAERO
#  FAST is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np
import openmdao.api as om
from openmdao.core.explicitcomponent import ExplicitComponent
from ..constants import SPAN_MESH_POINT_OPENVSP

        
class ComputeMaxCL(om.Group):
    """
    Computes maximum CL of the aircraft in landing/take-off conditions.

    3D CL is deduced from 2D CL using sweep angle.
    Contribution of high-lift devices is done apart and added.

    """
    def setup(self):
        self.add_subsystem("CL_2D_to_3D", Compute3DMaxCL(), promotes=["*"])
        self.add_subsystem("comp_cl_max", ComputeAircraftMaxCl(), promotes=["*"])
    
    
class Compute3DMaxCL(ExplicitComponent):
    """
    Computes wing 3D max CL from 2D CL (XFOIL-computed) and lift repartition
    """
    
    def setup(self):

        nans_array = np.full(SPAN_MESH_POINT_OPENVSP, np.nan)
        self.add_input("data:geometry:wing:root:y", val=np.nan, units="m")
        self.add_input("data:geometry:wing:tip:y", val=np.nan, units="m")
        self.add_input("data:aerodynamics:wing:low_speed:root:CL_max_2D", val=np.nan)
        self.add_input("data:aerodynamics:wing:low_speed:tip:CL_max_2D", val=np.nan)
        self.add_input("data:aerodynamics:aircraft:low_speed:CL0_clean", val=np.nan)
        self.add_input("data:aerodynamics:wing:low_speed:Y_vector", val=nans_array, units="m")
        self.add_input("data:aerodynamics:wing:low_speed:CL_vector", val=nans_array)

        self.add_output("data:aerodynamics:wing:low_speed:CL_max_clean")

        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):

        y_root = float(inputs["data:geometry:wing:root:y"])
        y_tip = float(inputs["data:geometry:wing:tip:y"])
        cl_max_2d_root = float(inputs["data:aerodynamics:wing:low_speed:root:CL_max_2D"])
        cl_max_2d_tip = float(inputs["data:aerodynamics:wing:low_speed:tip:CL_max_2D"])
        cl0 = inputs["data:aerodynamics:aircraft:low_speed:CL0_clean"]
        y_interp = inputs["data:aerodynamics:wing:low_speed:Y_vector"]
        cl_interp = inputs["data:aerodynamics:wing:low_speed:CL_vector"]

        y_interp, cl_interp = self._reshape_curve(y_interp, cl_interp)
        y_vect = np.linspace(max(y_root, min(y_interp)), min(y_tip, max(y_interp)), SPAN_MESH_POINT_OPENVSP)
        cl_xfoil = np.interp(y_vect, np.array([y_root, y_tip]), np.array([cl_max_2d_root, cl_max_2d_tip]))
        cl_curve = np.interp(y_vect, y_interp, cl_interp)
        ratio = cl_xfoil/cl_curve

        cl_max_clean = cl0 * np.min(ratio)
        
        outputs["data:aerodynamics:wing:low_speed:CL_max_clean"] = cl_max_clean

    @staticmethod
    def _reshape_curve(y: np.ndarray, cl: np.ndarray):
        """ Reshape data from openvsp/vlm lift curve """

        for idx in range(len(y)):
            if np.sum(y[idx:len(y)] == 0) == (len(y) - idx):
                y = y[0:idx]
                cl = cl[0:idx]
                break

        return y, cl
        
        
class ComputeAircraftMaxCl(ExplicitComponent):
    """
    Add high-lift contribution (flaps)
    """
    
    def setup(self):
        
        self.add_input("data:aerodynamics:wing:low_speed:CL_max_clean", val=np.nan)
        self.add_input("data:aerodynamics:flaps:takeoff:CL_max", val=np.nan)
        self.add_input("data:aerodynamics:flaps:landing:CL_max", val=np.nan)

        self.add_output("data:aerodynamics:aircraft:takeoff:CL_max")
        self.add_output("data:aerodynamics:aircraft:landing:CL_max")

        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        
        cl_max_clean = inputs["data:aerodynamics:wing:low_speed:CL_max_clean"]
        cl_max_takeoff = cl_max_clean + inputs["data:aerodynamics:flaps:takeoff:CL_max"]
        cl_max_landing = cl_max_clean + inputs["data:aerodynamics:flaps:landing:CL_max"]

        outputs["data:aerodynamics:aircraft:takeoff:CL_max"] = cl_max_takeoff
        outputs["data:aerodynamics:aircraft:landing:CL_max"] = cl_max_landing
