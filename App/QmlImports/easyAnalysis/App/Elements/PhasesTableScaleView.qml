import QtQuick 2.12
import QtQuick.Controls 2.12
import QtGraphicalEffects 1.12

import easyAnalysis 1.0 as Generic
import easyAnalysis.Controls 1.0 as GenericControls
import easyAnalysis.App.ContentArea 1.0 as GenericAppContentArea
import easyAnalysis.App.Elements 1.0 as GenericAppElements

import easyDiffraction 1.0 as Specific

Column {
    property alias model: contentListView.model

    property int borderWidth: 1
    property int cellHeight: 34
    property int rowCountToDisplayWithoutHeader: 1
    property int rowCountToDisplayWithoutHeader2: 1

    property string rowBackgroundColor: 'white'
    property string alternateRowBackgroundColor: '#f7f7f7'
    property string highlightedRowBackgroundColor: "#2a99d9"
    property string rowForegroundColor: "black"
    property string highlightedRowForegroundColor: "white"
    property string headerBackgroundColor: '#eee'
    property string headerBorderColor: '#dedede'

    height: childrenRect.height
    spacing: 12

    function cellWidthProvider(column) {
        const allColumnWidth = width - borderWidth * 2
        const numberColumnWidth = 40
        const iconColumnWidth = cellHeight
        const flexibleColumnsWidth = allColumnWidth - numberColumnWidth - iconColumnWidth
        const flexibleColumnsCount = 2
        if (column === 1)
            return numberColumnWidth
        else if (column === 4)
            return iconColumnWidth
        else
            return flexibleColumnsWidth / flexibleColumnsCount
    }

    ////////////////////////
    // Check if data changed
    ////////////////////////

    Rectangle {
        id: listViewWrapper
        width: parent.width
        height: childrenRect.height
        border.color: headerBorderColor
        border.width: borderWidth

        Column {
            width: parent.width - parent.border.width * 2
            height: childrenRect.height + parent.border.width * 2
            spacing: 0
            padding: parent.border.width

            // Header
            ListView {
                id: headerListView
                width: parent.width
                height: cellHeight
                enabled: false

                header: Rectangle {
                    width: parent.width
                    height: cellHeight
                    color: headerBackgroundColor

                    Row {
                        anchors.fill: parent

                        Text {
                            width: cellWidthProvider(1)
                            height: parent.height
                            verticalAlignment: Text.AlignVCenter
                            horizontalAlignment: Text.AlignRight
                            leftPadding: font.pixelSize
                            rightPadding: leftPadding
                            font.family: Generic.Style.fontFamily
                            font.pixelSize: Generic.Style.fontPixelSize
                            text: "No."
                        }
                        Text {
                            width: cellWidthProvider(2)
                            height: parent.height
                            verticalAlignment: Text.AlignVCenter
                            horizontalAlignment: Text.AlignLeft
                            leftPadding: font.pixelSize
                            rightPadding: leftPadding
                            font.family: Generic.Style.fontFamily
                            font.pixelSize: Generic.Style.fontPixelSize
                            text: "Label"
                        }
                        Text {
                            width: cellWidthProvider(3)
                            height: parent.height
                            verticalAlignment: Text.AlignVCenter
                            horizontalAlignment: Text.AlignRight
                            leftPadding: font.pixelSize
                            rightPadding: leftPadding * 2
                            font.family: Generic.Style.fontFamily
                            font.pixelSize: Generic.Style.fontPixelSize
                            text: "Scale"
                        }
                        Text {
                            width: cellWidthProvider(4)
                            height: parent.height
                            verticalAlignment: Text.AlignVCenter
                            horizontalAlignment: Text.AlignRight
                            leftPadding: font.pixelSize
                            rightPadding: leftPadding
                            font.family: Generic.Style.fontFamily
                            font.pixelSize: Generic.Style.fontPixelSize
                            text: " "
                        }
                    }
                }
            }

            // Main content
            ListView {
                id: contentListView
                width: parent.width
                height: cellHeight * rowCountToDisplayWithoutHeader2
                clip: true
                boundsBehavior: Flickable.StopAtBounds

                ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AlwaysOff }
                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded; minimumSize: 1 / rowCountToDisplayWithoutHeader2 }

                model: Specific.Variables.projectOpened ? Specific.Variables.phaseIds() : 1

                // Content row
                delegate: Rectangle {
                    id: contentRow
                    width: parent.width
                    height: cellHeight
                    color: backgroundColor()

                    function foregroundColor() {
                        return rowForegroundColor
                    }
                    function backgroundColor() {
                        return index % 2 ? alternateRowBackgroundColor : rowBackgroundColor
                    }

                    Row {
                        anchors.fill: parent

                        Text {
                            width: cellWidthProvider(1)
                            height: parent.height
                            verticalAlignment: Text.AlignVCenter
                            horizontalAlignment: Text.AlignRight
                            leftPadding: font.pixelSize
                            rightPadding: leftPadding
                            font.family: Generic.Style.fontFamily
                            font.pixelSize: Generic.Style.fontPixelSize
                            text: index + 1
                            color: foregroundColor()
                        }
                        Text {
                            width: cellWidthProvider(2)
                            height: parent.height
                            verticalAlignment: Text.AlignVCenter
                            horizontalAlignment: Text.AlignLeft
                            leftPadding: font.pixelSize
                            rightPadding: leftPadding
                            font.family: Generic.Style.fontFamily
                            font.pixelSize: Generic.Style.fontPixelSize
                            text: Specific.Variables.projectOpened ? Specific.Variables.phaseIds()[index] : ""
                            color: foregroundColor()
                            GenericControls.EditingToolTip { type: GenericControls.EditingToolTip.NoEditingYet }
                        }
                        TextInput {
                            width: cellWidthProvider(3)
                            height: parent.height
                            enabled: !Specific.Variables.refinementRunning
                            verticalAlignment: Text.AlignVCenter
                            horizontalAlignment: Text.AlignRight
                            leftPadding: font.pixelSize
                            rightPadding: leftPadding * 2
                            color: foregroundColor()
                            GenericControls.EditingToolTip { type: GenericControls.EditingToolTip.OnAnalysisPage }
                            font.pixelSize: Generic.Style.fontPixelSize
                            font.family: Generic.Style.fontFamily
                            text: Specific.Variables.experimentByIndex(0).phase[0].scale.toFixed(4)
                        }
                        GenericAppElements.CheckBox {
                            width: cellWidthProvider(4)
                            checked: true
                            anchors.verticalCenter: parent.verticalCenter
                            GenericControls.EditingToolTip { type: GenericControls.EditingToolTip.NotYet }
                        }
                    }
                }
            }
        }
    }
}
