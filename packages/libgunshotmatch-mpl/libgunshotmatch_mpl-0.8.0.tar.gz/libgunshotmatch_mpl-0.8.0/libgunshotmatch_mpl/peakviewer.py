#!/usr/bin/env python3
#
#  peakviewer.py
"""
Common peak drawing functionality.
"""
#
#  Copyright © 2023-2024 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
from typing import List

# 3rd party
import numpy
from domdf_python_tools.paths import PathLike
from libgunshotmatch.project import Project
from matplotlib.axes import Axes  # type: ignore[import]
from matplotlib.figure import Figure  # type: ignore[import]

# this package
from libgunshotmatch_mpl.chromatogram import draw_peak_vlines

__all__ = ("UnsupportedProject", "draw_peaks", "load_project")


class UnsupportedProject(ValueError):
	"""
	Exception raised when a project is missing certain attributes (such as the consolidated peak list).
	"""


def load_project(filename: PathLike) -> Project:
	"""
	Load a project from disk and ensure it has all required attributes for displaying chromatograms.

	:param filename:
	"""

	project = Project.from_file(filename)

	# Validation of loaded datafile
	if project.consolidated_peaks is None:
		raise UnsupportedProject("Project.consolidated_peaks is unset")

	for (name, repeat) in project.datafile_data.items():
		if repeat.qualified_peaks is None:
			raise UnsupportedProject(f"Repeat.qualified_peaks is unset for {name!r}")
		if repeat.datafile.intensity_matrix is None:
			raise UnsupportedProject(f"Datafile.intensity_matrix is unset for {name!r}")

	return project


def draw_peaks(project: Project, retention_times: List[float], figure: Figure, axes: List[Axes]) -> None:
	"""
	Draw the peaks at the given retention time for each repeat in the project.

	:param project:
	:param retention_times: List of retention times for each repeat in the project.
	:param figure:
	:param axes:

	.. versionchanged:: 0.6.0  Replaced ``peak_idx`` argument with ``retention_times``
	"""

	min_rt: float = numpy.nanmin(retention_times) - 20
	max_rt: float = numpy.nanmax(retention_times) + 20

	for repeat_idx, (_, repeat) in enumerate(project.datafile_data.items()):
		assert repeat.datafile.intensity_matrix is not None
		im = repeat.datafile.intensity_matrix
		tic = im.tic

		# Get subset of timelist within RT range
		time_list = []
		intensity_list = []
		for rt, intensity in zip(tic.time_list, tic.intensity_array):
			if min_rt <= rt <= max_rt:
				time_list.append(rt / 60)
				intensity_list.append(intensity)

		axes[repeat_idx].plot(time_list, intensity_list)
		peak_rt = retention_times[repeat_idx]
		if not numpy.isnan(peak_rt):
			draw_peak_vlines(axes[repeat_idx], peak_rt / 60, intensity_list[time_list.index(peak_rt / 60)])
			axes[repeat_idx].text(
					peak_rt / 60,
					axes[repeat_idx].get_ylim()[1] * 0.2,
					f" {peak_rt/60:0.3f}",
					)
	figure.supylabel("Intensity", fontsize="medium")
	axes[0].autoscale()
	axes[-1].set_xlabel("Retention Time (mins)")
	for ax, repeat_name in zip(axes, project.datafile_data):
		ax.ticklabel_format(axis='y', scilimits=(0, 0), useMathText=True)
		ax.set_ylim(bottom=0)
		# xmin, xmax = ax.get_xlim()
		# ax.text(xmin + (xmax-xmin)*0.05, ax.get_ylim()[1] *0.8, repeat_name)
		ax.annotate(repeat_name, (0.01, 0.8), xycoords="axes fraction")

	axes[0].set_xlim(min_rt / 60, max_rt / 60)
	# # figure.subplots_adjust(bottom=0, top=1, left=0, right=1, hspace=0, wspace=0)
	# # figure.subplots_adjust(top=0.95, right=0.95)
	# figure.subplots_adjust(bottom=0.1, left=0.1, top=0.95, right=0.98, hspace=0.3)
