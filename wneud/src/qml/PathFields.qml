import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls

import org.kde.kirigami as Kirigami
import org.kde.kirigamiaddons.formcard as FormCard

// Expects to be embedded into an element with a property `unit`
// defined containing a systemd unit.
FormCard.FormCard {

  FormCard.FormTextFieldDelegate {
    text: unit.unit
    label: "Unit"
  }
}
