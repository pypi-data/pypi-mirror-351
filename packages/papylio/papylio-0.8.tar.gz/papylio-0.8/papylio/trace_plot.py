# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 15:44:52 2018

@author: ivoseverins
"""
# import wx
# import wx.lib.mixins.inspection as wit
# import sys
# print('PyQt5', sys.modules.get("PyQt5.QtCore"))
# print('PySide2', sys.modules.get("PySide2.QtCore"))

###################################################
## To enable interactive plotting with PySide2 in PyCharm 2022.3
import PySide2
import sys
sys.modules['PyQt5'] = sys.modules['PySide2']
import matplotlib
matplotlib.use('Qt5Agg')
###################################################

import matplotlib.pyplot as plt

# from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
# from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
# from matplotlib.backends.backend_qtagg import FigureCanvas
# from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

import numpy as np
from pathlib2 import Path

from PySide2.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox, QLabel
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

import sys
import time

import numpy as np

# from matplotlib.backends.qt_compat import QtWidgets
from PySide2 import QtWidgets
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


class TracePlotWindow(QWidget):
    def __init__(self, dataset=None, plot_variables=['intensity', 'FRET'],
                 ylims=[(0, 35000), (0, 1)], colours=[('g', 'r'), ('b')], width=14, height=None, save_path=None, parent=None,
                 show=True):

        if height is None:
            height = max(len(plot_variables) * 3.5, 9)

        from papylio.experiment import get_QApplication
        #TODO: Use selection only if it is present.
        app = get_QApplication()

        super().__init__()

        self.parent = parent

        self.setWindowTitle("Traces")

        self.plot_variables = plot_variables
        self.ylims = ylims
        self.colours = colours

        if save_path is None:
            self.save_path = save_path
        else:
            self.save_path = Path(save_path)

        self._dataset = dataset

        self.canvas = TracePlotCanvas(self, width=width, height=height, dpi=100)

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout()

        layout_bar = QHBoxLayout()
        layout_bar.addWidget(toolbar, 0.5)

        self.molecule_index_field = QLineEdit()
        self.molecule_index_field.setFixedWidth(70)

        layout_bar.addWidget(self.molecule_index_field, 0.05)
        layout_bar.addWidget(QLabel(' out of '), 0.05)
        self.number_of_molecules_label = QLabel('0')
        self.number_of_molecules_label.setFixedWidth(70)
        layout_bar.addWidget(self.number_of_molecules_label, 0.15)
        self._selection_state = 1
        self.selected_molecules_checkbox = QCheckBox()
        self.selected_molecules_checkbox.setTristate(True)
        self.selected_molecules_checkbox.setCheckState(Qt.PartiallyChecked)
        self.selected_molecules_checkbox.stateChanged.connect(self.on_selected_molecules_checkbox_state_change)
        self.selected_molecules_checkbox.setFocusPolicy(Qt.NoFocus)


        layout_bar.addWidget(QLabel('Selected'),0.1)
        layout_bar.addWidget(self.selected_molecules_checkbox, 0.15)

        self.molecule_index_field.returnPressed.connect(self.set_molecule_index_from_molecule_index_field)
        self.molecule_index_field.returnPressed.connect(self.deactivate_line_edit)


        layout.addLayout(layout_bar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        # Create a placeholder widget to hold our toolbar and canvas.
        # widget = QWidget()
        # widget.setLayout(layout)
        # self.setCentralWidget(widget)

        self.dataset = dataset

        if show:
            self.show()

            app.exec_()

    def deactivate_line_edit(self):
        self.molecule_index_field.clearFocus()  # Clear the focus from the line edit

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, value):
        if value is not None and (hasattr(value, 'frame') or hasattr(value, 'time')):
            self._dataset = value
            self.canvas.init_plot_artists()
            self.set_selection()
            self.setDisabled(False)
        else:
            self._dataset = None
            self.setDisabled(True)
        self.molecule_index = 0

    @property
    def selection_state(self):
        return self._selection_state

    @selection_state.setter
    def selection_state(self, selection_state):
        self._selection_state = selection_state
        self.set_selection()

    def on_selected_molecules_checkbox_state_change(self, selection_state):
        self.selection_state = selection_state
        self.selected_molecules_checkbox.clearFocus()

    def set_selection(self):
        if self.selection_state == 0:
            self.dataset_molecule_indices_to_show = self.dataset.molecule.sel(molecule=~self.dataset.selected).values
        elif self.selection_state == 1:
            self.dataset_molecule_indices_to_show = self.dataset.molecule.values
        elif self.selection_state == 2:
            self.dataset_molecule_indices_to_show = self.dataset.molecule.sel(molecule=self.dataset.selected).values
        else:
            raise ValueError(f'Unknown selection_state {self.selection_state}')

    @property
    def molecule_index(self):
        return self._molecule_index

    @molecule_index.setter
    def molecule_index(self, molecule_index):
        self._molecule_index = molecule_index
        if self.dataset is not None and self.number_of_molecules_to_show > 0:
            self.molecule = self.dataset.isel(molecule=self.dataset_molecule_index)
        else:
            self.molecule = None
        self.molecule_index_field.setText(str(molecule_index))
        self.molecule_index_field.setFocusPolicy(Qt.ClickFocus)

    @property
    def dataset_molecule_index(self):
        return self.dataset_molecule_indices_to_show[self._molecule_index]

    @property
    def dataset_molecule_indices_to_show(self):
        return self._dataset_molecule_indices_to_show

    @dataset_molecule_indices_to_show.setter
    def dataset_molecule_indices_to_show(self, dataset_molecule_indices_to_show):
        self._dataset_molecule_indices_to_show = dataset_molecule_indices_to_show
        self.number_of_molecules_label.setText(f'{self.number_of_molecules_to_show}')
        self.molecule_index = 0

    @property
    def number_of_molecules_to_show(self):
        return len(self.dataset_molecule_indices_to_show)

    def set_molecule_index_from_molecule_index_field(self):
        self.molecule_index = int(self.molecule_index_field.text())

    def next_molecule(self):
        if (self.molecule_index+1) < self.number_of_molecules_to_show:
            self.molecule_index += 1

    def previous_molecule(self):
        if self.molecule_index > 0:
            self.molecule_index -= 1

    def update_current_molecule(self):
        self.molecule_index = self.molecule_index

    @property
    def molecule(self):
        return self.canvas.molecule

    @molecule.setter
    def molecule(self, molecule):
        self.canvas.molecule = molecule

    def keyPressEvent(self, e):
        key = e.key()
        if key == Qt.Key_Right: # Right arrow
            self.next_molecule()
        elif key == Qt.Key_Left: # Left arrow
            self.previous_molecule()
        elif key == Qt.Key_Space: # Spacebar
            self.dataset.selected[dict(molecule=self.dataset_molecule_index)] = ~self.dataset.selected[dict(molecule=self.dataset_molecule_index)]
            self.update_current_molecule()
        elif key == Qt.Key_S: # S
            self.canvas.save()

    # def selected_molecules_checkbox_state_changed(self, state):
    #     show_selected_mapping = {0: False, 1: None, 2: True}
    #     self.show_selected = show_selected_mapping[state]
    #     self.canvas.init_plot_artists()
    #     print('test')


class TracePlotCanvas(FigureCanvasQTAgg):
    # Kader om plot als geselecteerd
    # Autosave function
    def __init__(self, parent=None, width=14, height=7, dpi=100):
        self.figure = matplotlib.figure.Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)  # , figsize=(2, 2))
        super().__init__(self.figure)
        self.parent_window = parent
        plot_variables = self.parent_window.plot_variables

        grid = self.figure.add_gridspec(len(plot_variables), 2, width_ratios=[10, 1]) #, height_ratios=(2, 7),
                         # left=0.1, right=0.9, bottom=0.1, top=0.9,
                         # wspace=0.05, hspace=0.05)

        self.plot_axes = {}
        self.histogram_axes = {}

        for i, plot_variable in enumerate(plot_variables):
            plot = self.figure.add_subplot(grid[i, 0])
            histogram = self.figure.add_subplot(grid[i, 1], sharey=plot)

            if i > 0:
                plot.sharex(self.plot_axes[plot_variables[0]])
                # histogram.sharex(self.histogram_axes[plot_variables[0]])

            plot.set_ylim(self.parent_window.ylims[i])
            plot.set_ylabel(plot_variable)

            histogram.get_yaxis().set_visible(False)

            self.plot_axes[plot_variable] = plot
            self.histogram_axes[plot_variable] = histogram


        # self.intensity_plot = self.figure.add_subplot(grid[0, 0])
        # self.FRET_plot = self.figure.add_subplot(grid[1, 0], sharex=self.intensity_plot)
        # self.intensity_histogram = self.figure.add_subplot(grid[0, 1], sharey=self.intensity_plot)
        # self.FRET_histogram = self.figure.add_subplot(grid[1, 1], sharex=self.intensity_histogram, sharey=self.FRET_plot)

        # self.figure = plt.Figure(dpi=dpi, figsize=(2,2))
        #
        # self.axis = self.figure.gca()

        #self.figure, self.axes = mpl.figure.Figure().subplots(2,1)



        self._molecule = None

        self.plot_artists = {}
        self.histogram_artists = {}


    def show_artists(self, show, draw=True):
        for artists in self.plot_artists.values():
            for artist in artists:
                artist.set_alpha(int(show))
        for artists in self.histogram_artists.values():
            for artist in artists:
                for bar in artist:
                    bar.set_alpha(int(show)*0.5)
        if draw:
            self.draw()

    def init_plot_artists(self):
        for i, plot_variable in enumerate(self.parent_window.plot_variables):
            data_array = self.parent_window.dataset[plot_variable]

            # For excluding nan values
            dims_wihtout_frame = set(data_array.dims).difference({'frame'})
            frame_not_nan = ~data_array.isnull().all(dim=dims_wihtout_frame)
            data_array = data_array.sel(frame=frame_not_nan)

            if 'time' in self.parent_window.dataset.coords.keys():
                x = data_array.time  # self.parent_window.dataset.time[frame_not_nan]
            else:
                x = data_array.frame  # self.parent_window.dataset.frame[frame_not_nan]
            self.plot_artists[plot_variable] = self.plot_axes[plot_variable].plot(x, data_array.sel(molecule=0).T)
            if i == 0:
                self.title_artist = self.plot_axes[plot_variable].set_title('')
            for j, plot_artist in enumerate(self.plot_artists[plot_variable]):
                plot_artist.set_color(self.parent_window.colours[i][j])
            # molecule.intensity.plot.line(x='frame', ax=self.plot_axes[plot_variable], color=self.parent_window.colours[i])
            self.histogram_artists[plot_variable] = self.histogram_axes[plot_variable].hist(data_array.sel(molecule=0).T,
                                                                                            bins=50,
                                                                                            orientation='horizontal',
                                                                                            # range=self.plot_axes[
                                                                                            #     plot_variable].get_ylim(),
                                                                                            range=self.parent_window.ylims[i],
                                                                                            color=
                                                                                            self.parent_window.colours[
                                                                                                i], alpha=0.5)[2]
            if not isinstance(self.histogram_artists[plot_variable], list):
                self.histogram_artists[plot_variable] = [self.histogram_artists[plot_variable]]

            if i == len(self.parent_window.plot_variables) - 1:
                if 'time' in self.parent_window.dataset.coords.keys():
                    self.plot_axes[plot_variable].set_xlabel(f'Time ({self.parent_window.dataset.time.units})')
                else:
                    self.plot_axes[plot_variable].set_xlabel('Frame')

        # self.artists += [self.intensity_plot.plot(g, c='g')]
        # self.artists += [self.intensity_plot.plot(r, c='r')]
        # self.artists += [self.FRET_plot.plot(e, c='b')]
        # self.artists += [[self.intensity_plot.set_title('test')]]
        # self.artists += [self.intensity_histogram.hist(g, bins=100, orientation='horizontal',
        #                                                range=self.intensity_plot.get_ylim(), color='g', alpha=0.5)[2]]
        # self.artists += [self.intensity_histogram.hist(r, bins=100, orientation='horizontal',
        #                                                range=self.intensity_plot.get_ylim(), color='r', alpha=0.5)[2]]
        # self.artists += [self.FRET_histogram.hist(e, bins=100, orientation='horizontal',
        #                                           range=self.FRET_plot.get_ylim(), color='b')[2]]

        # self.axes[1].plot(molecule.E(), animate=True)
        artists = [self.title_artist] + \
                  [a for b in self.plot_artists.values() for a in b] + \
                  [a for c in self.histogram_artists.values() for b in c for a in b]
        self.bm = BlitManager(self, artists)
        self.draw()

    @property
    def molecule(self):
        return self._molecule

    @molecule.setter
    def molecule(self, molecule):
        previous_molecule = self._molecule
        self._molecule = molecule

        if molecule is None and previous_molecule is not None:
            self.show_artists(False, draw=True)
            return
        elif molecule is None and previous_molecule is None:
            return
        elif molecule is not None and previous_molecule is None:
            self.show_artists(True, draw=False)


        self._molecule['file'] = self._molecule['file'].astype(str)

        # g = molecule.intensity.sel(channel=0).values
        # r = molecule.intensity.sel(channel=1).values
        # e = molecule.FRET.values

        if not self.plot_artists:
            self.init_plot_artists()

        # for axis in self.axes:
        #     axis.cla()

        for i, plot_variable in enumerate(self.parent_window.plot_variables):
            data = np.atleast_2d(molecule[plot_variable])

            # For excluding nan values (can go wrong when trace contains nans that are not present in all molecules)
            data = data[:, ~np.isnan(data).all(axis=0)]

            if self._molecule.selected.item():
                selection_string = ' | Selected'
            else:
                selection_string = ''

            self.title_artist.set_text(f'# {self.parent_window.molecule_index} of {len(self.parent_window.dataset.molecule)} | File: {molecule.file.values} | Molecule: {molecule.molecule_in_file.values}' + selection_string)#| Sequence: {molecule.sequence_name.values}')
            self.title_artist.set_text(
                f'File: {molecule.file.values} | Molecule: {molecule.molecule_in_file.values}' + selection_string)  # | Sequence: {molecule.sequence_name.values}')

            for j in range(len(data)):
                self.plot_artists[plot_variable][j].set_ydata(data[j])
                # TODO: When you shift the view, change the y positions of the bars to the new view, if possible. use set_y
                n, _ = np.histogram(data[j], 50, range=self.parent_window.ylims[i]) # range=self.plot_axes[plot_variable].get_ylim())
                for count, artist in zip(n, self.histogram_artists[plot_variable][j]):
                    artist.set_width(count)



        # self.artists[0][0].set_ydata(g)
        # self.artists[1][0].set_ydata(r)
        # self.artists[2][0].set_ydata(e)
        # self.artists[3][0].set_text(molecule.sequence_name.values)
        # n, _ = np.histogram(g, 100, range=self.intensity_plot.get_ylim())
        # for count, artist in zip(n, self.artists[4]):
        #     artist.set_width(count)
        # n, _ = np.histogram(r, 100, range=self.intensity_plot.get_ylim())
        # for count, artist in zip(n, self.artists[5]):
        #     artist.set_width(count)
        # n, _ = np.histogram(e, 100, range=self.FRET_plot.get_ylim())
        # for count, artist in zip(n, self.artists[6]):
        #     artist.set_width(count)
        #     #for count, rect in zip(n, bar_container.patches):
        # tell the blitting manager to do its thing
        self.bm.update()



        # self.axes[0].plot(molecule.intensity.T)
        # self.axes[1].plot(molecule.E())
        # self.canvas.draw()

        # empty_cell = (0, 0)
        #
        # donor_checkbox = wx.CheckBox(self, -1, label="Donor", name="Donor")
        # acceptor_checkbox = wx.CheckBox(self, -1, label="Acceptor", name="Acceptor")
        #
        # channel_sizer = wx.FlexGridSizer(2,2, gap=wx.Size(10,0))
        # channel_sizer.Add(wx.StaticText(self, label="Channels:"), 5, wx.EXPAND, 0)
        # channel_sizer.Add(donor_checkbox, 1, wx.EXPAND, 0)
        # channel_sizer.Add(empty_cell, 0, wx.EXPAND, 0)
        # channel_sizer.Add(acceptor_checkbox, 0, wx.EXPAND, 0)
        #
        # average_image_radio_button = wx.RadioButton(self, -1, label="Average image", name="Average image")
        # maximum_projection_radio_button = wx.RadioButton(self, -1, label="Maximum projection", name="Maximum projection")
        #
        # image_type_sizer = wx.FlexGridSizer(2,2, gap=wx.Size(10,0))
        # image_type_sizer.AddGrowableCol(0,1)
        # image_type_sizer.AddGrowableCol(1,3)
        # image_type_sizer.Add(wx.StaticText(self, label="Image type atestat:"), 0, wx.EXPAND, 0)
        # image_type_sizer.Add(average_image_radio_button, 0, wx.EXPAND, 0)
        # image_type_sizer.Add(empty_cell, 0, wx.EXPAND, 0)
        # image_type_sizer.Add(maximum_projection_radio_button, 0, wx.EXPAND, 0)
        # #
        # # image_type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # # image_type_sizer.Add(wx.StaticText(self, label="Image type:"), 0, wx.EXPAND | wx.ALL, 10)
        # # image_type_sizer.Add(image_type_combobox, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        #
        # self.sizer = wx.BoxSizer(wx.VERTICAL)
        # self.sizer.Add(channel_sizer, 0, wx.EXPAND | wx.ALL, 10)
        # self.sizer.Add(image_type_sizer, 0, wx.EXPAND | wx.ALL, 10)
        # self.sizer.Add(wx.Slider(self, -1, value=0, minValue=0, maxValue=100,
        #                          name='Minimum'), 0, wx.EXPAND | wx.ALL, 10)
        # self.sizer.Add(wx.Slider(self, -1, value=0, minValue=0, maxValue=100,
        #                          name='Maximum'), 0, wx.EXPAND | wx.ALL, 10)
        # self.sizer.Add(wx.Button(self, -1, "Button 1"), 0, wx.EXPAND | wx.ALL, 10)
        # self.sizer.Add(wx.Button(self, -1, "Button 2"), 0, wx.EXPAND | wx.ALL, 10)
        # self.SetSizer(self.sizer)

    def save(self):
        save_path = self.parent_window.save_path
        if save_path is not None:
            save_path.mkdir(parents=True, exist_ok=True)
            file_name = self.molecule.file.item().replace('\\' ,' - ')+f' - mol {self.molecule.molecule_in_file.item()}.png'
            file_path = save_path.joinpath(file_name)
            self.figure.savefig(file_path, bbox_inches='tight')
        else:
            raise ValueError('No save_path set')





#
#
#
# class TraceAnalysisFrame(QMainWindow):
#     def __init__(self, parent=None, dataset=None, title='Traces', plot_variables=['intensity', 'FRET'],
#                  ylims=[(0, 35000), (0, 1)], colours=[('g', 'r'), ('b')], save_path=None):
#         wx.Frame.__init__(self, parent, title=title, size=(1400, 700))
#         self.parent = parent
#         self.dataset = dataset
#         self.plot_variables = plot_variables
#         self.ylims = ylims
#         self.colours = colours
#
#         if save_path is None:
#             self.save_path = save_path
#         else:
#             self.save_path = Path(save_path)
#         #self.Bind(wx.EVT_CLOSE, self.OnClose)
#         self.trace_panel = TraceAnalysisPanel(parent=self)
#         # self.control_panel = ControlPanel(parent=self)
#         self.Bind(wx.EVT_CHAR_HOOK, self.OnNavigationKey)
#
#         self.molecule_index = 0
#
#         self.Show()
#
#     # @property
#     # def molecules(self):
#     #     return self._molecules
#     #
#     # @molecules.setter
#     # def molecules(self, molecules):
#     #     self._molecules = molecules
#
#
#     @property
#     def molecule_index(self):
#         return self._molecule_index
#
#     @molecule_index.setter
#     def molecule_index(self, molecule_index):
#         self._molecule_index = molecule_index
#         self.molecule = self.dataset.isel(molecule=self.molecule_index)
#
#     def next_molecule(self):
#         if (self.molecule_index+1) < len(self.dataset.molecule):
#             self.molecule_index += 1
#
#     def previous_molecule(self):
#         if self.molecule_index > 0:
#             self.molecule_index -= 1
#
#     def update_current_molecule(self):
#         self.molecule_index = self.molecule_index
#
#     @property
#     def molecule(self):
#         return self.panel.molecule
#
#     @molecule.setter
#     def molecule(self, molecule):
#         self.trace_panel.molecule = molecule
#
#     def OnNavigationKey(self, event):
#         key_code = event.GetKeyCode()
#         print(key_code)
#         if key_code == 316: # Right arrow
#             self.next_molecule()
#         elif key_code == 314: # Left arrow
#             self.previous_molecule()
#         elif key_code == 32: # Spacebar
#             self.dataset.selected[dict(molecule=self.molecule_index)] = ~self.dataset.selected[dict(molecule=1)]
#             self.update_current_molecule()
#         elif key_code == 83: # S
#             self.trace_panel.save()

# class ControlPanel(wx.Panel):
# To file/molecule
# Selected button changes colour (spacebar)
# Y-axis limits
# Classification technique - change classification pannel based on specific technique

# class Threshold_classification_panel

# class HMM_classification_panel


class BlitManager:
    def __init__(self, canvas, animated_artists=()):
        """
        Parameters
        ----------
        canvas : FigureCanvasAgg
            The canvas to work with, this only works for sub-classes of the Agg
            canvas which have the `~FigureCanvasAgg.copy_from_bbox` and
            `~FigureCanvasAgg.restore_region` methods.

        animated_artists : Iterable[Artist]
            List of the artists to manage
        """
        self.canvas = canvas
        self._bg = None
        self._artists = []

        for a in animated_artists:
            self.add_artist(a)
        # grab the background on every draw
        self.cid = canvas.mpl_connect("draw_event", self.on_draw)

    def on_draw(self, event):
        """Callback to register with 'draw_event'."""
        cv = self.canvas
        if event is not None:
            if event.canvas != cv:
                raise RuntimeError
        self._bg = cv.copy_from_bbox(cv.figure.bbox)
        self._draw_animated()

    def add_artist(self, art):
        """
        Add an artist to be managed.

        Parameters
        ----------
        art : Artist

            The artist to be added.  Will be set to 'animated' (just
            to be safe).  *art* must be in the figure associated with
            the canvas this class is managing.

        """
        if art.figure != self.canvas.figure:
            raise RuntimeError
        art.set_animated(True)
        self._artists.append(art)

    def _draw_animated(self):
        """Draw all of the animated artists."""
        fig = self.canvas.figure
        for a in self._artists:
            fig.draw_artist(a)

    def update(self):
        """Update the screen with animated artists."""
        cv = self.canvas
        fig = cv.figure
        # paranoia in case we missed the draw event,
        if self._bg is None:
            self.on_draw(None)
        else:
            # restore the background
            cv.restore_region(self._bg)
            # draw all of the animated artists
            self._draw_animated()
            # update the GUI state
            cv.blit(fig.bbox)
        # let the GUI event loop process anything it has to do
        # cv.flush_events()

# class MainWindow(wx.Frame):
#    def __init__(self, parent, title):
#        wx.Frame.__init__(self, parent, title=title, size=(300, 700))
#        self.parent = parent
#        self.panel = TraceAnalysisPanel(parent=self)
#        # self.Bind(wx.EVT_CLOSE, self.OnClose)
#        self.Show()

if __name__ == "__main__":

    # # Check whether there is already a running QApplication (e.g., if running
    # # from an IDE).
    # qapp = QtWidgets.QApplication.instance()
    # if not qapp:
    #     qapp = QtWidgets.QApplication(sys.argv)
    #
    # app = ApplicationWindow()
    # app.show()
    # app.activateWindow()
    # app.raise_()
    # qapp.exec_()


    import papylio as pp
    import os, sys
    mapping_path = Path(os.getcwd()).joinpath('papylio').joinpath('mapping')
    sys.path.append(mapping_path)
    print(sys.path)
    from papylio.experiment import Experiment
    exp = Experiment(r'D:\SURFdrive\Promotie\Code\Python\traceAnalysis\twoColourExampleData\20141017 - Holliday junction - Copy')
    ds = exp.files[0].dataset

    from PySide2.QtWidgets import QApplication

    app = QApplication(sys.argv)
    frame = TracePlotWindow(ds)
        #, "Sample editor", plot_variables=['intensity', 'FRET'],  # 'classification'],
        #          ylims=[(0, 1000), (0, 1), (-1,2)], colours=[('g', 'r'), ('b'), ('k')])

    app.exec_()

    # # exp = pp.Experiment(r'D:\20200918 - Test data\Single-molecule data small')
    # #exp = pp.Experiment(r'P:\SURFdrive\Promotie\Data\Test data')
    # # exp = pp.Experiment(r'/Users/ivoseverins/SURFdrive/Promotie/Data/Test data')
    # # print(exp.files)
    # # m = exp.files[1].molecules[0]
    # # print(exp.files[2])
    # import xarray as xr
    # #file_paths = [p for p in exp.nc_file_paths if '561' in str(p)]
    # file_paths = [exp.nc_file_paths[0]]
    # with xr.open_mfdataset(file_paths, concat_dim='molecule', combine='nested') as ds:
    #     # ds_sel = ds.sel(molecule=ds.sequence_name=='HJ7_G')# .reset_index('molecule', drop=True) # HJ1_WT, HJ7_G116T
    #     app = wx.App(False)
    #     # app = wit.InspectableApp()
    #     frame = TraceAnalysisFrame(None, ds, "Sample editor", plot_variables=['intensity', 'FRET'], #'classification'],
    #              ylims=[(0, 1000), (0, 1), (-1,2)], colours=[('g', 'r'), ('b'), ('k')])
    #     # frame.molecules = exp.files[1].molecules
    #     print('test')
    #     import wx.lib.inspection
    #     wx.lib.inspection.InspectionTool().Show()
    #     app.MainLoop()





# Add time to existing .nc file
# for file in exp.files:
#     with xr.open_dataset(file.absoluteFilePath.with_suffix('.nc')) as ds:
#         i = ds.intensity.load()
#     test = i.assign_coords(time=file.movie.time)
#     test.to_netcdf(file.absoluteFilePath.with_suffix('.nc'), engine='h5netcdf', mode='a')


#
# from matplotlib import use
# use('TkAgg')
#
# import papylio as pp
# exp = pp.Experiment(r'D:\SURFdrive\Promotie\Code\Python\papylio\twoColourExampleData\20141017 - Holliday junction - Copy')
# #exp = pp.Experiment(r'J:\Ivo\20200221 - Magnetic tweezers setup (Old)\Data')
# # exp.files[-2].perform_mapping()
# # exp.files[-2].mapping.show_mapping_transformation()

# class B:
#     def __init__(self):
#         print('Badd')
#         super().__init__()
#
#
#
# class A:
#     def __init__(self):
#         print('A')
#
#
# def test(c):
#     return type(c.__name__, (c,B),{})
#
#
# @test
# class Bo(A):
#     def __init__(self):
#         print('Bo')
#         super().__init__()



# class B:
#     def __init__(self):
#         print('Badd')
#         super().__init__()
#
# # class PluginMetaClass(type):
# #     def __new__(cls, clsname, bases, attrs):
# #         bases_base = tuple(base for base in bases if not base.__name__ is clsname)
# #         attrs.pop('__qualname__')
# #         cls_base = type(clsname+'_base', bases_base, attrs)
# #         bases_main = tuple(base for base in bases if base.__name__ is clsname) + (cls_base,)
# #         return super().__new__(cls, clsname, bases_main, {})
# class PluginMetaClass(type):
#     def __new__(cls, clsname, bases_base, attrs):
#         # bases_base = tuple(base for base in bases if not base.__name__ is clsname)
#         attrs_base = attrs.copy()
#         attrs_base.pop('__qualname__')
#         #attrs_base.pop('__module__')
#         #attrs_base.pop('__classcell__')
#         cls_base = super().__new__(cls, clsname, bases_base, attrs_base)
#         #cls_base = type(clsname, bases_base, attrs)
#         added_bases = (B,)
#         bases_main = added_bases + (cls_base,)
#         test = super().__new__(cls, clsname+'main', bases_main,{})
#         print('test')
#         return test
#
# class A:
#     def __init__(self):
#         print('A')
#
# class Bo(A, metaclass=PluginMetaClass):
#     def __init__(self):
#         print('Bo')
#         super().__init__()
#



# exp = pp.Experiment(r'P:\SURFdrive\Promotie\Code\Python\papylio\twoColourExampleData\20141017 - Holliday junction - Copy')
# # exp = pp.Experiment(r'D:\SURFdrive\Promotie\Code\Python\papylio\twoColourExampleData\20141017 - Holliday junction - Copy')
# exp.files[-1].use_mapping_for_all_files()



# def add_class_to_class(base_class):
#     def add_class_to_class_decorator(added_class):
#         base_class.__bases__ += (added_class,)
#     return add_class_to_class_decorator
#
# @add_class_to_class(pp.File)
# class ExperimentPlugIn():
#     def test(self):
#         print(self.name)



# exp.files[0].find_coordinates()
#
#
# # #exp = pp.Experiment(r'D:\ivoseverins\SURFdrive\Promotie\Code\Python\papylio\twoColourExampleData\20191209 - Single-molecule setup (TIR-I)')
# # exp.files[0].perform_mapping(transformation_type='nonlinear')
# #
# import matplotlib.pyplot as plt
# figure = plt.figure()
# #exp.files[0].show_average_image(figure=figure)
# plt.imshow(exp.files[0].movie.maximum_projection_image)
# exp.files[0].show_coordinates(figure=figure)
# #exp.files[0].mapping.show_mapping_transformation(figure=figure)



# exp.files[-1].use_mapping_for_all_files()

from papylio.plotting import histogram
# exp.files[7].histogram(bins = 100, molecule_averaging=True, export=True)
# exp.histogram(bins = 100, molecule_averaging=True, export=True)
#
# import sys
# #sys.path.append(r'D:\ivoseverins\SURFdrive\Promotie\Code\Python\fastqAnalysis')
# sys.path.append(r'D:\SURFdrive\Promotie\Code\Python\fastqAnalysis')
#
# from papylio.traceAnalysisCode import Experiment
# from fastqAnalysis import FastqData
#
# from pathlib import Path # For efficient path manipulation
#
# path = Path(r'G:\Ivo\20190918 - Sequencer (MiSeq)\Analysis')
# #path = 'D:\\ivoseverins\\Desktop\\Sequencing data\\20180705\\'
# #path = 'C:\\Users\\Ivo Severins\\Desktop\\Sequencing data\\20180705\\'
# fileName = r'One_S1_L001_R1_001.fastq'
#
#
# data = FastqData(path.joinpath(fileName))
#
# data.selection(sequence = 'AA')
#
# data.matches_per_tile(sequence = 'TATCTGTATAATGAGAAATATGGAGTACAATTTTTTTTTTTTTTTTTTTT')









#import wx
#
#
#class OtherFrame(wx.Frame):
#    """
#    Class used for creating frames other than the main one
#    """
#
#    def __init__(self, title, parent=None):
#        wx.Frame.__init__(self, parent=parent, title=title)
#        self.Show()
#
#
#class MyPanel(wx.Panel):
#
#    def __init__(self, parent):
#        wx.Panel.__init__(self, parent)
#
#        btn = wx.Button(self, label='Create New Frame')
#        btn.Bind(wx.EVT_BUTTON, self.on_new_frame)
#        self.frame_number = 1
#
#    def on_new_frame(self, event):
#        title = 'SubFrame {}'.format(self.frame_number)
#        frame = OtherFrame(title=title)
#        self.frame_number += 1
#
#
#class MainFrame(wx.Frame):
#
#    def __init__(self):
#        wx.Frame.__init__(self, None, title='Main Frame', size=(800, 600))
#        panel = MyPanel(self)
#        self.Show()
#
#
#if __name__ == '__main__':
#    app = wx.App(False)
#    frame = MainFrame()
#    app.MainLoop()


# #!/usr/bin/env python
# import wx
# import wx.dataview
# import wx.lib.agw.aui as aui
# import os
#
# import wx.lib.agw.customtreectrl as CT
# #from traceAnalysisCode import Experiment
# import wx.lib.agw.hypertreelist as HTL
#
#
# import matplotlib as mpl
# from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
# from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
#
# from matplotlib import use
# use('WXAgg')
# from matplotlib import pyplot as plt
# #import matplotlib.pyplot as plt
#
#
#
# class MyFrame(wx.Frame):
#     """ We simply derive a new class of Frame. """
#     def __init__(self, parent, title):
#         wx.Frame.__init__(self, parent, title=title, size=(400,400))
#         tree_list = HTL.HyperTreeList(self)
#
#         tree_list.AddColumn("First column")
#
#         root = tree_list.AddRoot("Root")
#
#         parent = tree_list.AppendItem(root, "First child")
#         child = tree_list.AppendItem(parent, "First Grandchild")
#
#         tree_list.AppendItem(root, "Second child", ct_type=1)
#         self.Show(True)
#
# app = wx.App(False)
# frame = MyFrame(None, 'Small editor')
# app.MainLoop()