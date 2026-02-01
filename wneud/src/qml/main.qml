import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

Kirigami.ApplicationWindow {
    id: root

    title: qsTr("Wneud")

    minimumWidth: Kirigami.Units.gridUnit * 20
    minimumHeight: Kirigami.Units.gridUnit * 20
    width: minimumWidth
    height: minimumHeight

    // TODO: Move to backed.
    ListModel {
        id: sdUnitsModel
        ListElement {
            name: "Emacs"
            description: "Emacs server daemon"
            unitType: "service"
        }
        ListElement {
            name: "Something else"
            description: "Some other server daemon"
            unitType: "service"
        }
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
                        text: unitType
                    }

                    ColumnLayout {
                        Kirigami.Heading {
                            Layout.fillWidth: true
                            level: 1
                            text: name
                        }

                        Kirigami.Separator {
                            Layout.fillWidth: true
                            visible: description.length > 0
                        }
                        Controls.Label {
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                            text: description
                            visible: description.length > 0
                        }
                    }

                    Controls.Button {
                        Layout.alignment: Qt.AlignRight
                        Layout.columnSpan: 2
                        text: "A button"
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
