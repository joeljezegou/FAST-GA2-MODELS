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

from ..components.cd0_fuselage import Cd0Fuselage
from ..components.cd0_ht import Cd0HorizontalTail
from ..components.cd0_lg import Cd0LandingGear
from ..components.cd0_nacelle import Cd0Nacelle
from ..components.cd0_vt import Cd0VerticalTail
from ..components.cd0_wing import Cd0Wing
from ..components.cd0_other import Cd0Other
from ..components.cd0_total import Cd0Total
from openmdao.core.group import Group


class CD0(Group):
    def initialize(self):
        self.options.declare("low_speed_aero", default=False, types=bool)
        self.options.declare("propulsion_id", default="", types=str)
        
    def setup(self):
        if self.options["low_speed_aero"]:
            self.add_subsystem("cd0_wing", Cd0Wing(low_speed_aero=True), promotes=["*"])
            self.add_subsystem("cd0_fuselage", Cd0Fuselage(low_speed_aero=True), promotes=["*"])
            self.add_subsystem("cd0_ht", Cd0HorizontalTail(low_speed_aero=True), promotes=["*"])
            self.add_subsystem("cd0_vt", Cd0VerticalTail(low_speed_aero=True), promotes=["*"])
            self.add_subsystem("cd0_nac", Cd0Nacelle(
                propulsion_id=self.options["propulsion_id"],
                low_speed_aero=True
            ), promotes=["*"])
            self.add_subsystem("cd0_lg", Cd0LandingGear(low_speed_aero=True), promotes=["*"])
            self.add_subsystem("cd0_other", Cd0Other(low_speed_aero=True), promotes=["*"])
            self.add_subsystem("cd0_total", Cd0Total(low_speed_aero=True), promotes=["*"])
        else:
            self.add_subsystem("cd0_wing", Cd0Wing(), promotes=["*"])
            self.add_subsystem("cd0_fuselage", Cd0Fuselage(), promotes=["*"])
            self.add_subsystem("cd0_ht", Cd0HorizontalTail(), promotes=["*"])
            self.add_subsystem("cd0_vt", Cd0VerticalTail(), promotes=["*"])
            self.add_subsystem("cd0_nac", Cd0Nacelle(propulsion_id=self.options["propulsion_id"]), promotes=["*"])
            self.add_subsystem("cd0_lg", Cd0LandingGear(), promotes=["*"])
            self.add_subsystem("cd0_other", Cd0Other(), promotes=["*"])
            self.add_subsystem("cd0_total", Cd0Total(), promotes=["*"])
