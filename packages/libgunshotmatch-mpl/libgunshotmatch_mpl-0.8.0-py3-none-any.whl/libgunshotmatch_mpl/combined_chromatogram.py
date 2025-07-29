#!/usr/bin/env python3
#
#  combined_chromatogram.py
"""
Combined "chromatogram" drawing functionality.

A bar chart for peak area/height styled as a chromatogram, with time on the x-axis.

.. versionadded:: 0.5.0
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
from operator import attrgetter
from typing import TYPE_CHECKING, Any, Callable, Dict, List, NamedTuple, Optional, Sequence, Tuple, Type, Union

# 3rd party
import numpy
from libgunshotmatch.consolidate import ConsolidatedPeak
from libgunshotmatch.project import Project
from libgunshotmatch.utils import get_rt_range
from matplotlib.axes import Axes  # type: ignore[import]
from matplotlib.collections import PathCollection  # type: ignore[import]
from matplotlib.colors import Colormap  # type: ignore[import]
from matplotlib.container import BarContainer, ErrorbarContainer  # type: ignore[import]
from matplotlib.figure import Figure  # type: ignore[import]
from matplotlib.ticker import AutoMinorLocator  # type: ignore[import]

if TYPE_CHECKING:
	# 3rd party
	from pyms.Spectrum import MassSpectrum

__all__ = (
		"CCPeak",
		"CominedChromatogram",
		"draw_combined_chromatogram",
		"get_cc_peak",
		"get_combined_chromatogram_data",
		"get_y_label"
		)


class CCPeak(NamedTuple):
	"""
	Data for a peak in a combined "chromatogram".
	"""

	area_or_height: float
	area_or_height_list: List[float]
	rt: float
	rt_list: List[float]
	errorbar: Union[float, Tuple[List[float], List[float]]]


def get_cc_peak(
		peak: ConsolidatedPeak,
		use_median: bool = False,
		use_peak_height: bool = False,
		) -> CCPeak:
	"""
	Return data on a peak for a combined "chromatogram".

	:param peak:
	:param use_median: Show the median and inter-quartile range, rather than the mean and standard deviation.
	:param use_peak_height: Show the peak height and not the peak area.
	"""

	if use_peak_height:
		areas = []
		ms: Optional["MassSpectrum"]
		for ms in peak.ms_list:
			if ms is not None:
				areas.append(sum(ms.intensity_list))
	else:
		areas = peak.area_list

	if use_median:
		area: float = numpy.nanmedian(areas)
		_25th_percentile: float = numpy.nanpercentile(areas, 25)
		_75th_percentile: float = numpy.nanpercentile(areas, 75)
		errorbar = ([area - _25th_percentile], [_75th_percentile - area])

		return CCPeak(
				area_or_height=area,
				area_or_height_list=areas,
				rt=peak.rt / 60,
				rt_list=peak.rt_list,
				errorbar=errorbar,
				)
	else:
		return CCPeak(
				area_or_height=numpy.nanmean(areas),
				area_or_height_list=areas,
				rt=peak.rt / 60,
				rt_list=peak.rt_list,
				errorbar=numpy.nanstd(areas),
				)


def get_combined_chromatogram_data_from_peaks(
		consolidated_peaks: Sequence[Optional[ConsolidatedPeak]],
		*,
		top_n_peaks: Optional[int] = None,
		threshold: float = 0,
		use_median: bool = False,
		use_peak_height: bool = False,
		) -> List[CCPeak]:
	"""
	Returns data for a combined "chromatogram" for the project.

	:param consolidated_peaks:
	:param top_n_peaks: Show only the n largest peaks.
	:param threshold: Show only peaks larger than the given area (or peak height, as applicable).
	:param use_median: Show the median and inter-quartile range, rather than the mean and standard deviation.
	:param use_peak_height: Show the peak height and not the peak area.
	:param show_points: Show individual retention time / peak area scatter points.

	:rtype:

	.. versionadded:: 0.8.0
	"""

	peaks: List[CCPeak] = []
	for peak in consolidated_peaks:
		if peak is None:
			continue

		peak_data = get_cc_peak(peak, use_median, use_peak_height)
		if peak_data.area_or_height < threshold:
			continue
		peaks.append(peak_data)

	if top_n_peaks:
		# Sort by peak area and take largest ``top_n_peaks``
		peaks = sorted(peaks, key=attrgetter("area_or_height"), reverse=True)[:top_n_peaks]

		# Resort by retention time
		peaks.sort(key=attrgetter("rt"))

	return peaks


def get_combined_chromatogram_data(
		project: Project,
		*,
		top_n_peaks: Optional[int] = None,
		threshold: float = 0,
		use_median: bool = False,
		use_peak_height: bool = False,
		) -> List[CCPeak]:
	"""
	Returns data for a combined "chromatogram" for the project.

	:param project:
	:param top_n_peaks: Show only the n largest peaks.
	:param threshold: Show only peaks larger than the given area (or peak height, as applicable).
	:param use_median: Show the median and inter-quartile range, rather than the mean and standard deviation.
	:param use_peak_height: Show the peak height and not the peak area.
	:param show_points: Show individual retention time / peak area scatter points.
	"""

	assert project.consolidated_peaks is not None

	return get_combined_chromatogram_data_from_peaks(
			project.consolidated_peaks,
			top_n_peaks=top_n_peaks,
			threshold=threshold,
			use_median=use_median,
			use_peak_height=use_peak_height
			)


class CombinedChromatogram(NamedTuple):
	"""
	Settings and drawing function for a combined "chromatogram".
	"""

	#: The project name
	name: str

	#: X-axis (retention) time limits.
	xlim: Tuple[float, float]

	colourmap: Callable[[float], Optional[Tuple[int, int, int, int]]]
	"""
	Colourmap function for the bars, which calculates the bar colour from the retention time.

	The function must return a tuple of RGBA values when given a float between 0 and 1.
	"""

	@classmethod
	def from_project(
			cls: Type["CombinedChromatogram"],
			project: Project,
			colourmap: Union[Colormap, Callable[[float], Tuple[int, int, int, int]], None] = None,
			) -> "CombinedChromatogram":
		"""
		Alternative constructor from a :class:`libgunshotmatch.project.Project`.

		:param project:
		:param colourmap: Optional colourmap function for the bars.
			By default sequential bars are given colours from the default colour cycle.
			If ``colourmap`` is provided this function calculates the bar colour from the retention time.
			The function must return a tuple of RGBA values when given a float between 0 and 1.
		"""

		name = project.name
		xlim = get_rt_range(project)

		if colourmap is None:
			return cls(name, xlim, colourmap=lambda x: None)
		else:
			return cls(name, xlim, colourmap=colourmap)

	def draw_peak(
			self,
			ax: Axes,
			peak: CCPeak,
			*,
			show_points: bool = False,
			bar_kwargs: Dict[str, Any] = {},
			scatter_kwargs: Dict[str, Any] = {},
			errorbar_kwargs: Dict[str, Any] = {},
			) -> Tuple[BarContainer, Optional[PathCollection], Optional[ErrorbarContainer]]:
		"""
		Draw a peak on the given axes.

		:param ax:
		:param peak:
		:param show_points: Show individual retention time / peak area scatter points.

		:rtype:

		.. versionchanged:: 0.8.0

			Added ``bar_kwargs``, ``scatter_kwargs`` and ``errorbar_kwargs`` options to allow
			the bar, scatter points and errorbars to be customised.
		"""

		default_bar_kwargs = dict(
				width=0.2,
				color=self.colourmap(peak.rt / self.xlim[1]),
				)
		default_bar_kwargs.update(bar_kwargs)

		bar: BarContainer = ax.bar(
				peak.rt,
				peak.area_or_height,
				**default_bar_kwargs,
				)

		if show_points:
			default_scatter_kwargs = dict(
					s=50,
					color=bar.patches[0].get_facecolor(),  # So they match
					marker='x',
					)
			default_scatter_kwargs.update(scatter_kwargs)
			points = ax.scatter(
					[rt / 60 for rt in peak.rt_list],
					peak.area_or_height_list,
					**default_scatter_kwargs,
					)
		else:
			points = None

		if len(peak.rt_list) > 1:
			# Only show error bars if there's more than one datapoint
			default_errorbar_kwargs = dict(
					yerr=peak.errorbar,
					color="darkgrey",
					capsize=5,
					clip_on=False,
					)
			default_errorbar_kwargs.update(errorbar_kwargs)
			errorbars: ErrorbarContainer = ax.errorbar(peak.rt, peak.area_or_height, **default_errorbar_kwargs)

			# for eb in errorbars[1]:
			# 	eb.set_clip_on(False)
		else:
			errorbars = None

		return bar, points, errorbars


def get_y_label(use_median: bool = False, use_peak_height: bool = False) -> str:
	"""
	Returns the appropriate label for the y-axis.

	:param use_median: Whether the combined chromatogram shows the median and inter-quartile range, rather than the mean and standard deviation.
	:param use_peak_height: Whether the combined chromatogram shows the peak height and not the peak area.
	"""

	if use_peak_height and use_median:
		return "Median Peak Height"
	elif use_peak_height:
		return "Mean Peak Height"
	elif use_median:
		return "Median Peak Area"
	else:
		return "Mean Peak Area"


def draw_combined_chromatogram(
		project: Project,
		figure: Figure,
		ax: Axes,
		*,
		top_n_peaks: Optional[int] = None,
		minimum_area: float = 0,
		use_median: bool = False,
		use_peak_height: bool = False,
		use_range: bool = False,
		show_points: bool = False,
		colourmap: Union[Colormap, Callable[[float], Tuple[int, int, int, int]], None] = None
		) -> None:
	"""
	Draw a combined "chromatogram" for the project.

	A bar chart for peak area/height styled as a chromatogram, with time on the x-axis.

	:param project:
	:param figure:
	:param ax:
	:param top_n_peaks: Show only the n largest peaks.
	:param minimum_area: Show only peaks larger than the given area (or peak height, as applicable).
	:param use_median: Show the median and inter-quartile range, rather than the mean and standard deviation.
	:param use_peak_height: Show the peak height and not the peak area.
	:param use_range: Show the minimum and maximum values in error bar rather than stdev or IQR.
	:param show_points: Show individual retention time / peak area scatter points.
	:param colourmap: Optional colourmap function for the bars.
		By default sequential bars are given colours from the default colour cycle.
		If ``colourmap`` is provided this function calculates the bar colour from the retention time.
		The function must return a tuple of RGBA values when given a float between 0 and 1.

	:rtype:

	.. versionadded:: 0.2.0
	.. versionchanged:: 0.4.0  Added the ``use_median``, ``use_peak_height`` and ``show_points`` keyword arguments.

	.. versionchanged:: 0.5.0

		* Moved to the :mod:`~.combined_chromatogram` module.
		* Y-axis label now reflects ``use_median`` and ``use_peak_height`` options.

	.. versionchanged:: 0.7.0  Added ``use_range`` keyword-only argument.
	"""

	# this package
	from libgunshotmatch_mpl.chromatogram import ylabel_sci_1dp

	assert project.consolidated_peaks is not None

	peaks = get_combined_chromatogram_data(
			project,
			top_n_peaks=top_n_peaks,
			threshold=minimum_area,
			use_median=use_median,
			use_peak_height=use_peak_height,
			)

	cc = CombinedChromatogram.from_project(project, colourmap=colourmap)

	for peak in peaks:
		if use_range:
			min_peak_area = min(peak.area_or_height_list)
			max_peak_area = max(peak.area_or_height_list)
			peak_area = peak.area_or_height
			peak = peak._replace(errorbar=([peak_area - min_peak_area], [max_peak_area - peak_area]))

		cc.draw_peak(ax, peak, show_points=show_points)

	# ylabel_use_sci(ax)
	ylabel_sci_1dp(ax)
	ax.set_ylim(bottom=0)
	ax.set_ylabel(get_y_label(use_median, use_peak_height))

	ax.set_xlim(*cc.xlim)
	ax.set_xlabel("Retention Time (mins)")
	ax.xaxis.set_minor_locator(AutoMinorLocator())

	figure.suptitle(project.name)
