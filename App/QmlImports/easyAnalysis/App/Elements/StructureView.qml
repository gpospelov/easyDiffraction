import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import QtDataVisualization 1.3 // versions above 1.3 are not recognized by PySide2 (Qt for Python)
import easyAnalysis 1.0 as Generic
import easyAnalysis.App.Elements 1.0 as GenericAppElements
import easyDiffraction 1.0 as Specific

Rectangle {
    property bool showInfo: true
    property real xAxisLength: 1.0
    property real yAxisLength: 1.0
    property real zAxisLength: 1.0
    property real xRotationInitial: -50.0
    property real yRotationInitial:  3.0
    property real zoomLevelInitial: 175.0
    property real xTargetInitial: 0.0
    property real yTargetInitial: 0.0
    property real zTargetInitial: 0.0
    property int animationDuration: 1000

    width: parent.width
    height: parent.height
    color: "transparent"

    clip: true

    ////////////////////////
    // Check if data changed
    ////////////////////////

    Text {
        visible: false
        text: JSON.stringify(Specific.Variables.projectDict)
        onTextChanged: {
            // At the moment only get 1st phase.
            const phase = Specific.Variables.phaseByIndex(0)
            if (!Object.keys(phase).length) {
                return
            }

            // Create dictionary b_scattering:color
            const bscatList = Array.from(new Set(phase.sites.scat_length_neutron))
            let bscatColorDict = {}
            for (let i = 0; i < bscatList.length; i++ ) {
                bscatColorDict[bscatList[i]] = Generic.Style.atomColorList[i]
            }

            // Unit cell parameters
            const a = phase.cell.length_a
            const b = phase.cell.length_b
            const c = phase.cell.length_c

            // Update axes lengths
            xAxisLength = a // in horizontal plane
            yAxisLength = b // vertical
            zAxisLength = c // in horizontal plane

            // Remove old atom scatters, but unit cell box (number 1)
            for (let i = 1, len = chart.seriesList.length; i < len; i++) {
                chart.removeSeries(chart.seriesList[1])
            }

            // Populate chart with atoms. Every atom is an individual scatter serie
            for (let i = 0, len = phase.sites.fract_x.length; i < len; i++ ) {
                var component = Qt.createComponent(Generic.Variables.qmlElementsPath + "AtomScatter3DSeries.qml")
                if (component.status === Component.Ready) {
                    var series = component.createObject()
                    if (series === null) {
                        console.log("Error creating object")
                    } else {
                        series.atomSize = Math.pow(Math.abs(parseFloat(phase.sites.scat_length_neutron[i])) * 0.075, 1/3)
                        series.atomColor = bscatColorDict[phase.sites.scat_length_neutron[i]]
                        series.atomModel.append({
                            x: phase.sites.fract_x[i] * a,
                            y: phase.sites.fract_y[i] * b,
                            z: phase.sites.fract_z[i] * c
                        })
                    }
                    chart.addSeries(series)
                }
            }
        }
    }

    ///////
    // Plot
    ///////

    Rectangle {
        id: chartContainer
        width: parent.width
        anchors.top: parent.top
        anchors.bottom: infoLabel.top

        Scatter3D {
            id: chart
            visible: Specific.Variables.phaseIds().length ? true: false
            width: Math.min(parent.width, parent.height)
            height: Math.min(parent.width, parent.height)
            anchors.centerIn: parent

            // Camera view settings
            orthoProjection: false
            //scene.activeCamera.cameraPreset: Camera3D.CameraPresetIsometricLeftHigh
            scene.activeCamera.xRotation: xRotationInitial
            scene.activeCamera.yRotation: yRotationInitial
            scene.activeCamera.zoomLevel: zoomLevelInitial
            scene.activeCamera.target.x: xTargetInitial
            scene.activeCamera.target.y: yTargetInitial
            scene.activeCamera.target.z: zTargetInitial

            // Geometrical settings
            aspectRatio: Math.max(xAxisLength, zAxisLength) / yAxisLength
            horizontalAspectRatio: xAxisLength / zAxisLength

            // Interactivity
            selectionMode: AbstractGraph3D.SelectionNone // Left mouse button will be used for "reset view" coded below

            // Visualization settings
            theme: Theme3D {
                type: Theme3D.ThemeUserDefined
                ambientLightStrength: 0.5
                lightStrength: 5.0
                windowColor: "white"
                backgroundEnabled: false
                labelBackgroundEnabled: false
                labelBorderEnabled: false
                labelTextColor: "grey"
                gridEnabled: false
                //font.pointSize: 60
                //font.family: Generic.Style.fontFamily
            }
            shadowQuality: AbstractGraph3D.ShadowQualityNone // AbstractGraph3D.ShadowQualitySoftHigh

            // Axes
            axisX: ValueAxis3D { labelFormat: "" }
            axisY: ValueAxis3D { labelFormat: "" }
            axisZ: ValueAxis3D { labelFormat: "" }

            //GenericAppElements.AtomScatter3DSeries {
            //    atomModel: Generic.Constants.proxy.cellBox
            //}

            // Unit cell chart settings
            Scatter3DSeries {
                mesh: Abstract3DSeries.MeshSphere
                itemSize: 0.03
                baseColor: "grey"
                colorStyle: Theme3D.ColorStyleUniform

                ItemModelScatterDataProxy {
                    itemModel: Specific.Variables.cellBox
                    xPosRole: "xPos"
                    yPosRole: "yPos"
                    zPosRole: "zPos"
                }
            }
        }

    }

    /////////////
    // Info area
    /////////////

    Label {
        id: infoLabel
        visible: showInfo
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: font.pixelSize * 0.5
        leftPadding: font.pixelSize * lineHeight * 0.5
        rightPadding: font.pixelSize * lineHeight * 0.5
        lineHeight: 1.5
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        text: qsTr("Rotate: Drag with right mouse button pressed") + "  •  " + qsTr("Zoom in/out: Mouse wheel") + "  •  " + qsTr("Reset: Left mouse button")
        font.family: Generic.Style.secondFontFamily
        font.weight: Font.Light
        font.pixelSize: Generic.Style.fontPixelSize
        color: "grey"
        background: Rectangle { color: "white"; opacity: 0.9; border.width: 0; radius: Generic.Style.toolbarButtonRadius }
    }

    ///////////
    // Helpers
    ///////////

    // Reset view with animation: Override default left mouse button
    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton //Qt.AllButtons
        //propagateComposedEvents: true
        //onPressed: mouse.accepted = false
        onReleased: animo.restart()
    }

    // Animation
    ParallelAnimation {
        id: animo
        NumberAnimation { easing.type: Easing.OutCubic; target: chart; property: "scene.activeCamera.target.x"; to: xTargetInitial; duration: animationDuration }
        NumberAnimation { easing.type: Easing.OutCubic; target: chart; property: "scene.activeCamera.target.y"; to: yTargetInitial; duration: animationDuration }
        NumberAnimation { easing.type: Easing.OutCubic; target: chart; property: "scene.activeCamera.target.z"; to: zTargetInitial; duration: animationDuration }
        NumberAnimation { easing.type: Easing.OutCubic; target: chart; property: "scene.activeCamera.xRotation"; to: xRotationInitial; duration: animationDuration }
        NumberAnimation { easing.type: Easing.OutCubic; target: chart; property: "scene.activeCamera.yRotation"; to: yRotationInitial; duration: animationDuration }
        NumberAnimation { easing.type: Easing.OutCubic; target: chart; property: "scene.activeCamera.zoomLevel"; to: zoomLevelInitial; duration: animationDuration }
    }

    // Save chart onRefinementDone
    Timer {
        interval: 250
        running: Specific.Variables.refinementDone
        repeat: false
        onTriggered: {
            //print("save structure")
            chartContainer.grabToImage(function(result) {
                result.saveToFile(Specific.Variables.projectControl.project_dir_absolute_path + "/structure.png")
            })
        }
    }

}
