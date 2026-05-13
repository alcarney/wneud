import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

import WneudModels 1.0

Kirigami.Page {
  property var unit

  title: unit.name

  Component.onCompleted: {
    unit.refresh()
  }

  actions: [
    Kirigami.Action {
      text: "Stop"
      icon.name: "media-playback-stop-symbolic"
      visible: unit.canStop

      onTriggered: {
        unit.stop()
      }
    },
    Kirigami.Action {
      text: "Restart"
      icon.name: "view-refresh-symbolic"
      visible: unit.canReload

      onTriggered: {
        unit.restart()
      }
    },
    Kirigami.Action {
      text: "Start"
      icon.name: "media-playback-start-symbolic"
      visible: unit.canStart

      onTriggered: {
        unit.start()
      }
    },
  ]

  JournalLogModel {
    id: unitLogModel
    forUnit: unit.id
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
