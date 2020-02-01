import logging

from PySide2.QtCore import Qt, QPointF, Slot
from PySide2.QtCharts import QtCharts

from PyImports.DisplayModels.BaseModel import BaseModel


class BraggPeaksModel(BaseModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._series = None

    def _setModelsFromProjectDict(self):
        """
        Create the model needed for GUI measured data table and chart.
        """
        logging.info("-> start")

        for calc_dict in self._project_dict['calculations'].values():
            for phase_id in self._project_dict['phases'].keys():
                column_count = len(calc_dict['bragg_peaks'][phase_id].items())
                row_count = len(list(calc_dict['bragg_peaks'][phase_id].items())[0][1])

                self._model.blockSignals(True)

                self._model.clear()
                self._model.setColumnCount(column_count)
                self._model.setRowCount(row_count)

                # Add all the columns from calc_dict['bragg_peaks'][phase_id] to self._model
                for colum_index, (data_id, data_list) in enumerate(calc_dict['bragg_peaks'][phase_id].items()):
                    for row_index, value in enumerate(data_list):
                        index = self._model.index(row_index, colum_index)
                        self._model.setData(index, value, Qt.DisplayRole)

                self._model.blockSignals(False)
                self._headers_model.blockSignals(False)

                # Emit signal which is catched by the QStandartItemModel-based
                # QML GUI elements in order to update their views
                self._model.layoutChanged.emit()

                # Update chart series here, as this method is significantly
                # faster, compared to the updating at the QML GUI side via the
                # QStandartItemModel
                self._updateQmlChartViewSeries()

        logging.info("<- end")

    def _updateQmlChartViewSeries(self):
        """
        Updates QML LineSeries of ChartView.
        """
        logging.info("=====> start")

        self._series.clear()

        for calc_dict in self._project_dict['calculations'].values():
            for phase_id in self._project_dict['phases'].keys():
                x_list = calc_dict['bragg_peaks'][phase_id]['ttheta']
                for x in x_list:
                    vertical_points = 11
                    for vertical_index in range(vertical_points):
                        self._series.append(QPointF(x, vertical_index))

        logging.info("<===== end")

    @Slot(QtCharts.QXYSeries)
    def setSeries(self, series):
        """
        Sets series to be a reference to the QML LineSeries of ChartView.
        """
        self._series = series