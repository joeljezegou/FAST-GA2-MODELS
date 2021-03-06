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

from .components.cd0_fuselage import Cd0Fuselage
from .components.cd0_ht import Cd0HorizontalTail
from .components.cd0_lg import Cd0LandingGear
from .components.cd0_nacelle import Cd0Nacelle
from .components.cd0_total import Cd0Total
from .components.cd0_vt import Cd0VerticalTail
from .components.cd0_wing import Cd0Wing
from .components.cd0_other import Cd0Other
from .components.compute_L_D_max import ComputeLDMax
from .components.compute_reynolds import ComputeReynolds
from .components.compute_cnbeta_fuselage import ComputeCnBetaFuselage
from .components.clalpha_vt import ComputeClalphaVT

from .external.vlm import ComputeOSWALDvlm, ComputeWingCLALPHAvlm, ComputeHTPCLALPHAvlm
from .external.openvsp import ComputeOSWALDopenvsp, ComputeWingCLALPHAopenvsp, ComputeHTPCLALPHAopenvsp
from .external.xfoil import XfoilPolar

from openmdao.core.group import Group
from openmdao.core.explicitcomponent import ExplicitComponent
import numpy as np


class AerodynamicsHighSpeed(Group):
    """
    Models for high speed aerodynamics
    """

    def initialize(self):
        self.options.declare("propulsion_id", default="", types=str)
        self.options.declare("use_openvsp", default=False, types=bool)
        self.options.declare('wing_airfoil_file', default="naca23012.af", types=str, allow_none=True)
        self.options.declare('htp_airfoil_file', default="naca0012.af", types=str, allow_none=True)

    def setup(self):
        self.add_subsystem("comp_re", ComputeReynolds(), promotes=["*"])
        if not(self.options["use_openvsp"]):
            self.add_subsystem("xfoil_in", Connection(), promotes=["data:geometry:wing:MAC:length"])
            self.add_subsystem(
                "comp_polar",
                XfoilPolar(wing_airfoil_file=self.options["wing_airfoil_file"]),
                promotes=["data:geometry:wing:thickness_ratio"])
            self.add_subsystem(
                "oswald",
                ComputeOSWALDvlm(wing_airfoil_file=self.options["wing_airfoil_file"]),
                promotes=["*"])
            self.add_subsystem(
                "cl_alpha",
                ComputeWingCLALPHAvlm(wing_airfoil_file=self.options["wing_airfoil_file"]),
                promotes=["*"])
        else:
            self.add_subsystem(
                "oswald",
                ComputeOSWALDopenvsp(wing_airfoil_file=self.options["wing_airfoil_file"]),
                promotes=["*"])
            self.add_subsystem(
                "cl_alpha",
                ComputeWingCLALPHAopenvsp(wing_airfoil_file=self.options["wing_airfoil_file"]),
                promotes=["*"])
        self.add_subsystem("cd0_wing", Cd0Wing(wing_airfoil_file=self.options["wing_airfoil_file"]), promotes=["*"])
        self.add_subsystem("cd0_fuselage", Cd0Fuselage(), promotes=["*"])
        self.add_subsystem("cd0_ht", Cd0HorizontalTail(htp_airfoil_file=self.options["htp_airfoil_file"]),
                           promotes=["*"])
        self.add_subsystem("cd0_vt", Cd0VerticalTail(), promotes=["*"])
        self.add_subsystem("cd0_nacelle", Cd0Nacelle(propulsion_id=self.options["propulsion_id"]), promotes=["*"])
        self.add_subsystem("cd0_l_gear", Cd0LandingGear(), promotes=["*"])
        self.add_subsystem("cd0_other", Cd0Other(), promotes=["*"])
        self.add_subsystem("cd0_total", Cd0Total(), promotes=["*"])
        if not (self.options["use_openvsp"]):
            self.add_subsystem(
                "cl_alpha_ht",
                ComputeHTPCLALPHAvlm(
                    wing_airfoil_file=self.options["wing_airfoil_file"],
                    htp_airfoil_file=self.options["htp_airfoil_file"],
                ), promotes=["*"])
        else:
            self.add_subsystem(
                "cl_alpha_ht",
                ComputeHTPCLALPHAopenvsp(
                    wing_airfoil_file=self.options["wing_airfoil_file"],
                    htp_airfoil_file=self.options["htp_airfoil_file"],
                ), promotes=["*"])
        self.add_subsystem("L_D_max", ComputeLDMax(), promotes=["*"])
        self.add_subsystem("cnBeta_fuse", ComputeCnBetaFuselage(), promotes=["*"])
        self.add_subsystem("clAlpha_vt", ComputeClalphaVT(), promotes=["*"])

        if not(self.options["use_openvsp"]):
            self.connect("data:aerodynamics:cruise:mach", "comp_polar.xfoil:mach")
            self.connect("data:aerodynamics:cruise:unit_reynolds", "comp_polar.xfoil:unit_reynolds")
            self.connect("xfoil_in.xfoil:length", "comp_polar.xfoil:length")
            self.connect("comp_polar.xfoil:CL", "data:aerodynamics:wing:cruise:CL")
            self.connect("comp_polar.xfoil:CDp", "data:aerodynamics:wing:cruise:CDp")


class Connection(ExplicitComponent):
    def setup(self):
        self.add_input("data:geometry:wing:MAC:length", val=np.nan, units="m")
        self.add_output("xfoil:length", units="m")
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        outputs["xfoil:length"] = inputs["data:geometry:wing:MAC:length"]
