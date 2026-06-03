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

  /* JournalLogModel { */
  /*   id: unitLogModel */
  /*   forUnit: unit.id */
  /* } */

  UnitFields { }

  FormCard.FormHeader {
    title: "Path Options"
  }

  FormCard.FormCard {

    FormCard.FormTextFieldDelegate {
      text: unit.unit
      label: "Unit"
    }

    ListView {
      id: pathConfigList

      Layout.fillWidth: true
      implicitHeight: 200

      clip: true

      model: unit.pathTriggerModel
      delegate: Controls.ItemDelegate {
        required property string path
        required property string trigger

        width: pathConfigList.width

        contentItem: RowLayout {
          spacing: Kirigami.Units.smallSpacing

          Controls.Label {
            text: path
            textFormat: Text.PlainText
            elide: Text.ElideRight

            Layout.fillWidth: true
          }

          Controls.CheckBox {
            text: "Exists"
          }

          Controls.CheckBox {
            text: "Modified"
          }

          Controls.Button {
            icon.name: "edit-delete-remove"
            text: "Remove"

            display: Controls.AbstractButton.IconOnly
            Controls.ToolTip.text: text
            Controls.ToolTip.visible: hovered || activeFocus
            Controls.ToolTip.delay: Kirigami.Units.toolTipDelay
          }
        }
      }

      headerPositioning: ListView.OverlayHeader
      header: Kirigami.InlineViewHeader {
        width: pathConfigList.width
        text: "Triggered By"

        actions: [
          Kirigami.Action {
            text: "Add Trigger"
            icon.name: "list-add-symbolic"
            onTriggered: {

            }
          }
        ]
      }
    }
  }
}
