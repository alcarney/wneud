import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls

import org.kde.kirigami as Kirigami
import org.kde.kirigamiaddons.formcard as FormCard

import WneudModels 1.0

FormCard.FormCardPage {
  property var unit

  title: unit.name

  actions: [
    Kirigami.Action {
      text: "Stop"
      icon.name: "media-playback-stop-symbolic"
      visible: unit.canStop && unit.activeState === 'active'

      onTriggered: {
        unit.stop()
      }
    },
    Kirigami.Action {
      text: "Start"
      icon.name: "media-playback-start-symbolic"
      visible: unit.canStart && unit.activeState !== 'active'

      onTriggered: {
        unit.start()
      }
    },
  ]

  JournalLogModel {
    id: unitLogModel
    forUnit: unit.id
  }


  FormCard.FormHeader {
    title: "Unit Options"
  }

  UnitFields { }

  FormCard.FormHeader {
    title: "Path Options"
    visible: unit.unitType == 'path'
  }

  PathFields {
    visible: unit.unitType == 'path'
  }

    /* ListView { */
    /*   id: unitLogView */

    /*   Layout.fillWidth: true */
    /*   Layout.fillHeight: true */

    /*   clip: true */
    /*   contentWidth: contentItem.childrenRect.width */
    /*   flickableDirection: Flickable.HorizontalAndVerticalFlick */

    /*   Controls.ScrollBar.vertical: Controls.ScrollBar { policy: Controls.ScrollBar.AsNeeded } */
    /*   Controls.ScrollBar.horizontal: Controls.ScrollBar { policy: Controls.ScrollBar.AsNeeded } */

    /*   model: unitLogModel */
    /*   delegate: Controls.Label { */
    /*     width: implicitWidth */
    /*     text: `${timestamp}: ${message}` */
    /*   } */
    /* } */
}
