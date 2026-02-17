import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

import WneudModels 1.0

Kirigami.Page {
    property var unit

    title: unit.name

    JournalLogModel {
        id: unitLogModel
        forUnit: unit.name
    }

    ColumnLayout {

        anchors.fill: parent

        Kirigami.FormLayout {

            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.maximumHeight: implicitHeight

            Controls.TextField {
                Kirigami.FormData.label: "Description:"
                text: unit.description
            }
        }

        ListView {
            id: unitLogView

            Layout.fillWidth: true
            Layout.fillHeight: true

            clip: true
            contentWidth: contentItem.childrenRect.width
            flickableDirection: Flickable.HorizontalAndVerticalFlick

            Controls.ScrollBar.vertical: Controls.ScrollBar { policy: Controls.ScrollBar.AsNeeded }
            Controls.ScrollBar.horizontal: Controls.ScrollBar { policy: Controls.ScrollBar.AsNeeded }

            model: unitLogModel
            delegate: Controls.Label {
                width: implicitWidth
                text: `${timestamp}: ${message}`
            }
        }
    }
}
