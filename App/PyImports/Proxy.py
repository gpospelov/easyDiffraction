import os
import logging

from PySide2.QtCore import QUrl, QObject, Signal, Slot, Property
from PySide2.QtGui import QStandardItemModel

from PyImports.Calculators.CryspyCalculator import CryspyCalculator
from PyImports.Models.MeasuredDataModel import MeasuredDataModel
from PyImports.Models.CalculatedDataModel import CalculatedDataModel
from PyImports.Models.BraggPeaksModel import BraggPeaksModel
from PyImports.Models.CellParametersModel import CellParametersModel
from PyImports.Models.CellBoxModel import CellBoxModel
from PyImports.Models.AtomSitesModel import AtomSitesModel
from PyImports.Models.AtomAdpsModel import AtomAdpsModel
from PyImports.Models.AtomMspsModel import AtomMspsModel
from PyImports.Models.FitablesModel import FitablesModel
from PyImports.Refinement import Refiner
import PyImports.Helpers as Helpers

class Proxy(QObject):

    def __init__(self, parent=None):
        logging.info("")
        super().__init__(parent)
        #
        self._main_rcif_path = None
        self._calculator = None
        #
        self._measured_data_model = None
        self._calculated_data_model = None
        self._bragg_peaks_model = None
        self._cell_parameters_model = None
        self._cell_box_model = None
        self._atom_sites_model = None
        self._atom_adps_model = None
        self._atom_msps_model = None
        self._fitables_model = None
        #
        self._refine_thread = None
        self._refinement_running = False
        self._refinement_done = False
        self._refinement_result = None

    # Load rcif
    @Slot(str)
    def init(self, main_rcif_path):
        logging.info("")
        #
        self._main_rcif_path = QUrl(main_rcif_path).toLocalFile()
        self._calculator = CryspyCalculator(self._main_rcif_path)
        self._calculator.projectDictChanged.connect(self.projectChanged)
        #
        self._measured_data_model = MeasuredDataModel(self._calculator)
        self._calculated_data_model = CalculatedDataModel(self._calculator)
        self._bragg_peaks_model = BraggPeaksModel(self._calculator)
        self._cell_parameters_model = CellParametersModel(self._calculator)
        self._cell_box_model = CellBoxModel(self._calculator)
        self._atom_sites_model = AtomSitesModel(self._calculator)
        self._atom_adps_model = AtomAdpsModel(self._calculator)
        self._atom_msps_model = AtomMspsModel(self._calculator)
        self._fitables_model = FitablesModel(self._calculator)
        #
        self._refine_thread = Refiner(self._calculator, 'refine')

    projectChanged = Signal()
    dummySignal = Signal()

    # Project model for QML
    def getProject(self):
        logging.info("")
        if self._calculator is None:
            return ""
        return self._calculator.asDict()
    project = Property('QVariant', getProject, notify=projectChanged)

    # CIF model for QML
    def getCif(self):
        logging.info("")
        if self._calculator is None:
            return ""
        return self._calculator.asCifDict()
    cif = Property('QVariant', getCif, notify=projectChanged)

    # Measured data header model for QML
    def getMeasuredDataHeader(self):
        logging.info("")
        if self._measured_data_model is None:
            return QStandardItemModel()
        return self._measured_data_model.asHeadersModel()
    measuredDataHeader = Property('QVariant', getMeasuredDataHeader, notify=dummySignal)

    # Measured data model for QML
    def getMeasuredData(self):
        logging.info("")
        if self._measured_data_model is None:
            return QStandardItemModel()
        return self._measured_data_model.asDataModel()
    measuredData = Property('QVariant', getMeasuredData, notify=dummySignal)

    # Calculated data header model for QML
    def getCalculatedDataHeader(self):
        logging.info("")
        if self._calculated_data_model is None:
            return QStandardItemModel()
        return self._calculated_data_model.asHeadersModel()
    calculatedDataHeader = Property('QVariant', getCalculatedDataHeader, notify=dummySignal)

    # Calculated data model for QML
    def getCalculatedData(self):
        logging.info("")
        if self._calculated_data_model is None:
            return QStandardItemModel()
        return self._calculated_data_model.asDataModel()
    calculatedData = Property('QVariant', getCalculatedData, notify=dummySignal)

    # Bragg peaks model for QML
    def getBraggPeaks(self):
        logging.info("")
        if self._bragg_peaks_model is None:
            return QStandardItemModel()
        return self._bragg_peaks_model.asDataModel()
    def getBraggPeaksTicks(self):
        logging.info("")
        if self._bragg_peaks_model is None:
            return QStandardItemModel()
        return self._bragg_peaks_model.asTickModel()
    braggPeaks = Property('QVariant', getBraggPeaks, notify=dummySignal)
    braggPeaksTicks = Property('QVariant', getBraggPeaksTicks, notify=dummySignal)

    # Cell parameters model for QML
    def getCellParameters(self):
        logging.info("")
        if self._cell_parameters_model is None:
            return QStandardItemModel()
        return self._cell_parameters_model.asModel()
    cellParameters = Property('QVariant', getCellParameters, notify=dummySignal)

    # Cell box model for QML
    def getCellBox(self):
        logging.info("")
        if self._cell_box_model is None:
            return QStandardItemModel()
        return self._cell_box_model.asModel()
    cellBox = Property('QVariant', getCellBox, notify=dummySignal)

    # Atom sites model for QML
    def getAtomSites(self):
        logging.info("")
        if self._atom_sites_model is None:
            return QStandardItemModel()
        return self._atom_sites_model.asModel()
    atomSites = Property('QVariant', getAtomSites, notify=dummySignal)

    # Atom ADPs model for QML
    def getAtomAdps(self):
        logging.info("")
        if self._atom_adps_model is None:
            return QStandardItemModel()
        return self._atom_adps_model.asModel()
    atomAdps = Property('QVariant', getAtomAdps, notify=dummySignal)

    # Atom MSPs model for QML
    def getAtomMsps(self):
        logging.info("")
        if self._atom_msps_model is None:
            return QStandardItemModel()
        return self._atom_msps_model.asModel()
    atomMsps = Property('QVariant', getAtomMsps, notify=dummySignal)

    # Fitables model for QML
    def getFitables(self):
        ##logging.info("")
        if self._fitables_model is None:
            return QStandardItemModel()
        return self._fitables_model.asModel()
    fitables = Property('QVariant', getFitables, notify=dummySignal)

    # Time stamp of changes
    #timeStamp = Property(str, lambda self: str(np.datetime64('now')), notify=projectChanged)

    # ##########
    # REFINEMENT
    # ##########

    def _thread_finished(self, res):
        """
        Notfy the listeners about refinement results
        """
        logging.info("")
        self._refinement_running = False
        self._refinement_done = True
        self._refinement_result = res
        self.refinementChanged.emit()

    def _thread_failed(self, reason):
        """
        Notify the GUI about failure so a message can be shown
        """
        logging.info("Refinement failed: " + str(reason))
        self._refinement_running = False
        self._refinement_done = False
        self.refinementChanged.emit()

    @Slot()
    def refine(self):
        """
        Start refinement as a separate thread
        """
        logging.info("")
        if self._refinement_running:
            logging.info("Fitting stopped")
            # This lacks actual stopping functionality, needs to be added
            self._refinement_running = False
            self._refinement_done = True
            self.refinementChanged.emit()
            return
        self._refinement_running = True
        self._refinement_done = False
        self._refine_thread.finished.connect(self._thread_finished)
        self._refine_thread.failed.connect(self._thread_failed)
        self._refine_thread.start()
        self.refinementChanged.emit()
        logging.info("")

    refinementChanged = Signal()
    refinementRunning = Property(bool, lambda self: self._refinement_running, notify=refinementChanged)
    refinementDone = Property(bool, lambda self: self._refinement_done, notify=refinementChanged)
    refinementResult = Property('QVariant', lambda self: self._refinement_result, notify=refinementChanged)

    # ####
    # MISC
    # ####

    @Slot(str, result=str)
    def fullFilePath(self, fname):
        fpath = os.path.join(self.get_project_dir_absolute_path(), fname)
        furl = os.path.join(self.get_project_url_absolute_path(), fname)
        if os.path.isfile(fpath):
            return furl
        return ""

    def get_project_dir_absolute_path(self):
        if self._main_rcif_path:
            return os.path.dirname(os.path.abspath(self._main_rcif_path))
        return ""
    def get_project_url_absolute_path(self):
        if self._main_rcif_path:
            return str(QUrl.fromLocalFile(os.path.dirname(self._main_rcif_path)).toString())
        return ""
    project_dir_absolute_path = Property(str, get_project_dir_absolute_path, notify=projectChanged)
    project_url_absolute_path = Property(str, get_project_url_absolute_path, notify=projectChanged)

    # ######
    # REPORT
    # ######

    @Slot(str)
    def store_report(self, report=""):
        """
        Keep the QML generated HTML report for saving
        """
        self.report_html = report

    @Slot(str, str)
    def save_report(self, filename="", extension="html"):
        """
        Save the generated report to the specified file
        Currently only html
        """
        full_filename = filename + extension.lower()
        full_filename = os.path.join(self.get_project_dir_absolute_path(), full_filename)

        if not self.report_html:
            logging.info("No report to save")
            return

        # HTML can contain non-ascii, so need to open with right encoding
        with open(full_filename, 'w', encoding='utf-8') as report_file:
            report_file.write(self.report_html)
            logging.info("Report written")

        # Show the generated report in the default browser
        url = os.path.realpath(full_filename)
        Helpers.open_url(url=url)

