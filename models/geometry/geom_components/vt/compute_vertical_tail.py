"""
    Estimation of geometry of vertical tail
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


import openmdao.api as om

from .components import ComputeVTChords
from .components import ComputeVTDistance
from .components import ComputeVTMAC
from .components import ComputeVTSweep
from .components import ComputeVTWetArea
from fastoad2.models.aerodynamics.components.compute_cnbeta_vt import ComputeCnBetaVT # FIXME: change fastoad2 to fastoad
from fastoad2.models.aerodynamics.components.compute_cnbeta_fuselage import ComputeCnBetaFuselage # FIXME: change fastoad2 to fastoad

class ComputeVerticalTailGeometry(om.Group):
    """ Vertical tail geometry estimation """

    def setup(self):
        
        self.add_subsystem("vt_distance", ComputeVTDistance(), promotes=["*"])
        self.add_subsystem("vt_chords", ComputeVTChords(), promotes=["*"])
        self.add_subsystem("vt_mac", ComputeVTMAC(), promotes=["*"])
        self.add_subsystem("vt_sweep", ComputeVTSweep(), promotes=["*"])
        self.add_subsystem("vt_wet_area", ComputeVTWetArea(), promotes=["*"])
        self.add_subsystem("vt_cnbeta", ComputeCnBetaVT(), promotes=["*"])
        self.add_subsystem("fuselage_cnbeta", ComputeCnBetaFuselage(), promotes=["*"])
