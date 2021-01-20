# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Contributors Package. This package holds simulator extensions.
#  See also http://www.thevirtualbrain.org
#
# (c) 2012-2020, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)

"""
.. moduleauthor:: Lionel Kusch <lkusch@thevirtualbrain.org>
.. moduleauthor:: Dionysios Perdikis <dionperd@gmail.com>
"""

import abc

import numpy

from tvb.basic.neotraits.api import HasTraits, Attr, NArray
from tvb.simulator.coupling import Coupling, Linear
from tvb.simulator.monitors import Raw, RawVoi, AfferentCoupling


class CosimMonitor(HasTraits):
    """
    Abstract base class for cosimulation monitors implementations.
    """

    def get_sample(self, start_step, n_steps, history,cosim):
        times = []
        values = []
        for step in range(start_step, start_step + n_steps):
            if cosim:
                state = history.query(step)
            else:
                state = history.query(step)[0]
            tmp = super(self.__class__, self).sample(step, state)
            if tmp is not None:
                times.append(tmp[0])
                values.append(tmp[1])
        return [numpy.array(times), numpy.array(values)]

    @abc.abstractmethod
    def sample(self, start_step, n_steps, cosim_history, history):
        """
        This method provides monitor output, and should be overridden by subclasses.
        Use the original signature.
        """
        pass

class CosimMonitorFromCoupling(CosimMonitor):
    """
       Abstract base class for a monitor that records the future coupling values.
       !!!WARNING don't use this monitor for a time smaller than the synchronization variable!!!
    """

    coupling = Attr(
        field_type=Coupling,
        label="Long-range coupling function",
        default=Linear(),
        required=True,
        doc="""The coupling function is applied to the activity propagated
               between regions by the ``Long-range connectivity`` before it enters the local
               dynamic equations of the Model. Its primary purpose is to 'rescale' the
               incoming activity to a level appropriate to Model.""")

    def get_sample(self, start_step, n_steps, history):
        times = []
        values = []
        for step in range(start_step, start_step + n_steps):
            tmp = super(self.__class__, self).sample(step,  self.coupling(step, history))
            if tmp is not None:
                times.append(tmp[0])
                values.append(tmp[1])
        return [numpy.array(times), numpy.array(values)]


class RawCosim(Raw, CosimMonitor):
    """
    A monitor that records the output raw data
    from the partial (up to synchronization time) cosimulation history of TVB simulation.
    It collects:

        - all state variables and modes from class :Model:
        - all nodes of a region or surface based
        - all the integration time steps

    """
    _ui_name = "Cosimulation Raw recording"

    def sample(self, start_step, n_steps, cosim_history, history):
        "Return all the states of the partial (up to synchronization time) cosimulation history"
        return self.get_sample(start_step, n_steps, cosim_history, cosim=True)


class RawVoiCosim(RawVoi, CosimMonitor):
    """
    A monitor that records the output raw data of selected variables
    from the partial (up to synchronization time) history of TVB simulation.
    It collects:

        - voi state variables and all modes from class :Model:
        - all nodes of a region or surface based
        - all the integration time steps

    """
    _ui_name = "Cosimulation RawVoi recording"

    def sample(self, start_step, n_steps, cosim_history, history):
        "Return all the states of the partial (up to synchronization time) cosimulation history"
        return self.get_sample(start_step, n_steps, cosim_history, cosim=True)


class RawDelayed(Raw, CosimMonitor):
    """
    A monitor that records the output raw data of all coupling variables
    from the full history of a TVB simulation.
    It collects:

        - all coupling state variables and modes from class :Model:
        - all nodes of a region or surface based
        - all the integration time steps

    """

    _ui_name = "Cosimulation Raw Delayed recording"

    def sample(self, start_step, n_steps, cosim_history, history):
        "Return all the states of the delayed (by synchronization time) TVB history"
        return self.get_sample(start_step, n_steps, history, cosim=False)


class RawVoiDelayed(RawVoi,CosimMonitor):
    """
    A monitor that records the output raw data of selected coupling variables
    from the full history of a TVB simulation.
    It collects:

        - selected coupling state variables and all modes from class :Model:
        - all nodes of a region or surface based
        - all the integration time steps

    """

    _ui_name = "Cosimulation RawVoi Delayed recording"

    def sample(self, start_step, n_steps, cosim_history, history):
        "Return selected states of the delayed (by synchronization time) TVB history"
        return self.get_sample(start_step, n_steps, history, cosim=False)


class CosimCoupling(AfferentCoupling, CosimMonitorFromCoupling):
    """
    A monitor that records the future coupling of selected variables:
    It collects:

        - selected coupling values and all modes from class :Model:
        - all nodes of a region or surface based
        - all the integration time steps

    !!!WARNING don't use this monitor for a time smaller than the synchronization variable!!!
    """

    _ui_name = "Cosimulation Coupling recording"

    def sample(self, start_step, n_steps, cosim_history, history):
        "Return selected values of future coupling from (up to synchronization time) cosimulation history"
        return self.get_sample(start_step, n_steps, history)