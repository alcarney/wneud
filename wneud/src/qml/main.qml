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

    SDUnitListModel {
        id: sdUnitsModel
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

                    Kirigami.Heading {
                        level: 2
                        text: model.item.unitType
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
                            root.pageStack.push(Qt.resolvedUrl("UnitDetail.qml"), {
                                unit: model.item
                            })
                        }
                    }
                }
            }
        }
    }

    pageStack.initialPage: Kirigami.ScrollablePage {
        Kirigami.CardsListView {
            id: sdUnitsView
            model: sdUnitsModel
            delegate: sdUnitsDelegate
        }
    }

}
