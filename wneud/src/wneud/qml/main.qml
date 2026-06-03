import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

import WneudModels 1.0

Kirigami.ApplicationWindow {
  id: root

  title: qsTr("Wneud")

  minimumWidth: Kirigami.Units.gridUnit * 20
  minimumHeight: Kirigami.Units.gridUnit * 20
  width: minimumWidth
  height: minimumHeight


  SDUnitsModel {
    id: sdUnitsModel
  }

  WneudWorkflowsModel {
    id: workflowsModel
    model: sdUnitsModel
  }

  WneudTriggersModel {
    id: triggersModel
    model: sdUnitsModel
  }

  Component {
    id: sdUnitsDelegate
    Kirigami.AbstractCard {
      contentItem: Item {
        implicitWidth: delegateLayout.implicitWidth
        implicitHeight: delegateLayout.implicitHeight

        GridLayout {
          id: delegateLayout
          anchors {
            left: parent.left
            right: parent.right
            top: parent.top
          }
          rowSpacing: Kirigami.Units.largeSpacing
          columnSpacing: Kirigami.Units.largeSpacing
          columns: root.wideScreen ? 4 : 2

          Kirigami.Icon {
            source: {
              const unitIcons = {
                "service": "utilities-terminal-symbolic",
                "path": "document-open-symbolic",
                "timer": "chronometer-symbolic",
              }
              unitIcons[model.item.unitType] ?? "applications-system-symbolic"
            }
          }

          ColumnLayout {
            Kirigami.Heading {
              Layout.fillWidth: true
              level: 1
              text: model.item.name
            }

            Kirigami.Separator {
              Layout.fillWidth: true
              visible: model.item.description.length > 0
            }
            Controls.Label {
              Layout.fillWidth: true
              wrapMode: Text.WordWrap
              text: model.item.description
              visible: model.item.description.length > 0
            }
          }

          Controls.Button {
            Layout.alignment: Qt.AlignRight
            Layout.columnSpan: 2
            text: "Details"
            onClicked: {
              model.item.refresh()

              const unitPages = {
                "path": "PathDetail.qml",
              }
              const page = unitPages[model.item.unitType] ?? "UnitDetail.qml"

              root.pageStack.push(Qt.resolvedUrl(page), {
                unit: model.item
              })
            }
          }
        }
      }
    }
  }


  pageStack.initialPage: Kirigami.Page {
    padding: 0
    topPadding: 0
    leftPadding: 0
    rightPadding: 0
    bottomPadding: 0

    Controls.SwipeView {
      id: swipeView
      anchors.fill: parent
      clip: true
      leftInset: 0
      onCurrentIndexChanged: footer.currentIndex = currentIndex

      Kirigami.ScrollablePage {

        Kirigami.CardsListView {
          id: sdUnitsView
          model: workflowsModel
          delegate: sdUnitsDelegate
        }
      }

      Kirigami.ScrollablePage {

        Kirigami.CardsListView {
          id: triggerList
          model: triggersModel
          delegate: sdUnitsDelegate
        }
      }
    }

    footer: Kirigami.NavigationTabBar {
      id: footer
      actions: [
        Kirigami.Action {
          icon.name: "utilities-terminal-symbolic"
          text: "Workflows"
          checked: true
          onTriggered: swipeView.currentIndex = footer.currentIndex
        },
        Kirigami.Action {
          icon.name: "chronometer-symbolic"
          text: "Triggers"
          onTriggered: swipeView.currentIndex = footer.currentIndex
        },
      ]
    }
  }
}
