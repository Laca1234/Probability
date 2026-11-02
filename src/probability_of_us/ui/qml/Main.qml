import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    width: 1460
    height: 920
    minimumWidth: 1100
    minimumHeight: 720
    visible: true
    title: qsTr("Probability of Us")
    color: dark ? "#0c1220" : "#f4f6fa"

    property bool dark: appController.darkTheme
    property int pageIndex: 0
    property var analysisResult: ({})
    property var recurrenceResult: ({})
    property var simulationResult: ({})
    property int simulationDone: 0
    property int simulationTotal: 1

    readonly property color canvas: dark ? "#0c1220" : "#f4f6fa"
    readonly property color panel: dark ? "#141e30" : "#ffffff"
    readonly property color panelAlt: dark ? "#18253a" : "#edf2f7"
    readonly property color line: dark ? "#27364d" : "#dce3ec"
    readonly property color ink: dark ? "#f1f5fb" : "#182538"
    readonly property color muted: dark ? "#9aabc1" : "#617188"
    readonly property color accent: "#63d6c5"
    readonly property color accentDeep: dark ? "#183b42" : "#d8f4ed"
    readonly property color warning: "#f3bf72"

    function goTo(index) { pageIndex = index }
    function yearFrom(field, fallback) {
        const value = Number.parseInt(field.text)
        return Number.isFinite(value) ? value : fallback
    }
    function formatPercent(value) {
        if (value === undefined || value === null) return qsTr("Unknown")
        if (value === 0) return "0%"
        if (value < 0.0001) return (value * 100).toExponential(3) + "%"
        return (value * 100).toPrecision(4) + "%"
    }

    Connections {
        target: appController
        function onSimulationProgress(done, total) {
            window.simulationDone = done
            window.simulationTotal = Math.max(1, total)
        }
        function onSimulationFinished(result) {
            window.simulationResult = result
            appController.setStatus(qsTr("Simulation complete"))
        }
        function onSimulationError(message) {
            window.simulationResult = { error: message }
        }
    }

    component Surface: Rectangle {
        color: window.panel
        radius: 16
        border.width: 1
        border.color: window.line
    }

    component Field: TextField {
        implicitHeight: 44
        color: window.ink
        placeholderTextColor: window.muted
        selectionColor: window.accent
        leftPadding: 12
        rightPadding: 12
        background: Rectangle {
            radius: 9
            color: window.dark ? "#101a2b" : "#f8fafc"
            border.width: parent.activeFocus ? 2 : 1
            border.color: parent.activeFocus ? window.accent : window.line
        }
    }

    component ActionButton: Button {
        id: action
        property bool primary: false
        implicitHeight: 42
        leftPadding: 16
        rightPadding: 16
        contentItem: Text {
            text: action.text
            color: action.primary ? "#0b2426" : window.ink
            font.pixelSize: 13
            font.weight: Font.DemiBold
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
        background: Rectangle {
            radius: 10
            color: action.primary ? window.accent : (action.hovered ? window.panelAlt : window.panel)
            border.width: action.primary ? 0 : 1
            border.color: window.line
        }
    }

    component SectionTitle: Column {
        property string titleText: ""
        property string detailText: ""
        spacing: 5
        Text { text: parent.titleText; color: window.ink; font.pixelSize: 23; font.weight: Font.DemiBold }
        Text { text: parent.detailText; color: window.muted; font.pixelSize: 13; wrapMode: Text.WordWrap }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.preferredWidth: 246
            Layout.fillHeight: true
            color: dark ? "#101a2a" : "#17273a"

            ColumnLayout {
                anchors.fill: parent
                anchors.leftMargin: 17
                anchors.rightMargin: 15
                anchors.topMargin: 23
                anchors.bottomMargin: 17
                spacing: 0

                RowLayout {
                    Layout.fillWidth: true
                    Layout.bottomMargin: 29
                    spacing: 11
                    Rectangle {
                        width: 39; height: 39; radius: 12
                        color: "#204b4e"
                        Text { anchors.centerIn: parent; text: "P"; color: window.accent; font.pixelSize: 18; font.weight: Font.Bold }
                    }
                    Column {
                        spacing: 2
                        Text { text: qsTr("Probability of Us"); color: "#f5f8fc"; font.pixelSize: 15; font.weight: Font.DemiBold }
                        Text { text: qsTr("STATISTICAL DESK"); color: "#8ba0b6"; font.pixelSize: 9; font.letterSpacing: 1.7 }
                    }
                }

                Text { text: qsTr("WORKSPACE"); color: "#8095ac"; font.pixelSize: 10; font.weight: Font.DemiBold; font.letterSpacing: 1.4; Layout.bottomMargin: 10; Layout.leftMargin: 10 }
                Repeater {
                    model: [
                        { title: qsTr("Overview"), icon: "O" },
                        { title: qsTr("Story analysis"), icon: "A" },
                        { title: qsTr("Recurrence"), icon: "R" },
                        { title: qsTr("Demographics"), icon: "D" },
                        { title: qsTr("Simulation lab"), icon: "M" },
                        { title: qsTr("Saved scenarios"), icon: "S" },
                        { title: qsTr("Learning tools"), icon: "∑" },
                        { title: qsTr("Sources & settings"), icon: "G" }
                    ]
                    delegate: Button {
                        required property var modelData
                        required property int index
                        Layout.fillWidth: true
                        Layout.preferredHeight: 43
                        Layout.bottomMargin: 3
                        onClicked: window.goTo(index)
                        background: Rectangle {
                            radius: 10
                            color: window.pageIndex === index ? "#214249" : (parent.hovered ? "#1b2d40" : "transparent")
                            border.width: window.pageIndex === index ? 1 : 0
                            border.color: "#35646a"
                        }
                        contentItem: RowLayout {
                            spacing: 12
                            Text { text: modelData.icon; color: window.pageIndex === index ? window.accent : "#9fb1c4"; font.pixelSize: 18; Layout.preferredWidth: 22; horizontalAlignment: Text.AlignHCenter }
                            Text { text: modelData.title; color: window.pageIndex === index ? "#f4fbfa" : "#bdc9d6"; font.pixelSize: 13; font.weight: window.pageIndex === index ? Font.DemiBold : Font.Normal; Layout.fillWidth: true }
                        }
                    }
                }

                Item { Layout.fillHeight: true }
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 80
                    radius: 12
                    color: "#17283b"
                    border.color: "#293d52"
                    Column {
                        anchors.fill: parent; anchors.margins: 12; spacing: 5
                        Text { text: qsTr("OFFLINE BY DEFAULT"); color: window.accent; font.pixelSize: 9; font.weight: Font.DemiBold; font.letterSpacing: 1.1 }
                        Text { text: qsTr("Your scenarios stay on this device."); color: "#b2c0cf"; font.pixelSize: 11; wrapMode: Text.WordWrap; width: parent.width }
                    }
                }
                Text { text: "v" + appController.appVersion + "  ·  model " + appController.modelVersion; color: "#73879c"; font.pixelSize: 10; Layout.topMargin: 12; Layout.leftMargin: 4 }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 74
                color: dark ? "#0f1726" : "#ffffff"
                border.color: line
                RowLayout {
                    anchors.fill: parent; anchors.leftMargin: 30; anchors.rightMargin: 28
                    Text {
                        text: [qsTr("Overview"), qsTr("Story analysis"), qsTr("Recurrence calculator"), qsTr("Demographic explorer"), qsTr("Simulation lab"), qsTr("Saved scenarios"), qsTr("Learning tools"), qsTr("Sources & settings")][window.pageIndex]
                        color: ink; font.pixelSize: 18; font.weight: Font.DemiBold
                        Layout.fillWidth: true
                    }
                    Text { text: appController.statusText; color: muted; font.pixelSize: 11; elide: Text.ElideRight; Layout.maximumWidth: 340; horizontalAlignment: Text.AlignRight }
                    ActionButton { text: dark ? qsTr("Light") : qsTr("Dark"); onClicked: appController.toggleTheme() }
                }
            }

            StackLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: window.pageIndex

                // Overview
                Flickable {
                    clip: true
                    contentWidth: width
                    contentHeight: overviewColumn.implicitHeight + 60
                    ScrollBar.vertical: ScrollBar {}
                    ColumnLayout {
                        id: overviewColumn
                        anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top
                        spacing: 20
                        anchors.leftMargin: 31; anchors.rightMargin: 31; anchors.topMargin: 27
                        Text { text: qsTr("The small details behind a meeting."); color: ink; font.pixelSize: 29; font.weight: Font.DemiBold; Layout.fillWidth: true }
                        Text { text: qsTr("Explore demographic coincidences with explicit denominators, visible assumptions, and a model you can inspect."); color: muted; font.pixelSize: 14; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                        Surface {
                            Layout.fillWidth: true; Layout.preferredHeight: 112
                            RowLayout {
                                anchors.fill: parent; anchors.margins: 18; spacing: 15
                                Rectangle { width: 42; height: 42; radius: 14; color: "#533e27"; Text { anchors.centerIn: parent; text: "!"; color: warning; font.pixelSize: 22; font.weight: Font.Bold } }
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 4
                                    Text { text: qsTr("Teaching dataset loaded"); color: ink; font.pixelSize: 15; font.weight: Font.DemiBold }
                                    Text { text: qsTr("The bundled birth counts are synthetic, tiny, and cover three countries. Results are for learning the model only—not real demographic estimates."); color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                }
                                ActionButton { text: qsTr("View data"); onClicked: window.goTo(3) }
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true; spacing: 15
                            Repeater {
                                model: [
                                    { title: qsTr("Model version"), value: appController.modelVersion, note: qsTr("Exact pair counts") },
                                    { title: qsTr("Offline dataset"), value: qsTr("Synthetic demo"), note: appController.datasetSummary },
                                    { title: qsTr("Last calculation"), value: qsTr("Ready"), note: appController.lastCalculation }
                                ]
                                delegate: Surface {
                                    required property var modelData
                                    Layout.fillWidth: true; Layout.preferredHeight: 116
                                    ColumnLayout {
                                        anchors.fill: parent; anchors.margins: 16; spacing: 7
                                        Text { text: modelData.title; color: muted; font.pixelSize: 11 }
                                        Text { text: modelData.value; color: ink; font.pixelSize: 18; font.weight: Font.DemiBold }
                                        Text { text: modelData.note; color: muted; font.pixelSize: 10; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                    }
                                }
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true; spacing: 15
                            Surface {
                                Layout.fillWidth: true; Layout.preferredHeight: 228
                                ColumnLayout {
                                    anchors.fill: parent; anchors.margins: 18; spacing: 9
                                    Text { text: qsTr("A careful probability chain"); color: ink; font.pixelSize: 16; font.weight: Font.DemiBold }
                                    Text { text: qsTr("Two sampled people → birthplace conditions → age compatibility → a defined meeting → relationship formation"); color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                    Rectangle { Layout.fillWidth: true; height: 1; color: line }
                                    Text { text: qsTr("The first stages can be calculated from a suitable births dataset. Meeting and relationship probabilities stay unknown until a defensible study or an explicit scenario assumption is supplied."); color: ink; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                    Item { Layout.fillHeight: true }
                                    ActionButton { text: qsTr("Build a story analysis  →"); primary: true; onClicked: window.goTo(1) }
                                }
                            }
                            Surface {
                                Layout.fillWidth: true; Layout.preferredHeight: 228
                                ColumnLayout {
                                    anchors.fill: parent; anchors.margins: 18; spacing: 9
                                    Text { text: qsTr("What does recurrence mean?"); color: ink; font.pixelSize: 16; font.weight: Font.DemiBold }
                                    Text { text: qsTr("For N independent attempts with per-attempt probability p, the chance of at least one success is 1 − (1 − p)ᴺ. A birth, a pair, and an encounter are not interchangeable attempts."); color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                    Item { Layout.fillHeight: true }
                                    ActionButton { text: qsTr("Open recurrence calculator  →"); onClicked: window.goTo(2) }
                                }
                            }
                        }
                    }
                }

                // Story analysis
                Flickable {
                    clip: true; contentWidth: width; contentHeight: analysisColumn.implicitHeight + 55
                    ScrollBar.vertical: ScrollBar {}
                    ColumnLayout {
                        id: analysisColumn; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; spacing: 17
                        anchors.leftMargin: 30; anchors.rightMargin: 30; anchors.topMargin: 25
                        SectionTitle { titleText: qsTr("Define a story class"); detailText: qsTr("This analyzes two distinct people sampled from the births represented in the selected period. Birthplace does not mean nationality or current residence.") }
                        Surface {
                            Layout.fillWidth: true; Layout.preferredHeight: 330
                            GridLayout {
                                anchors.fill: parent; anchors.margins: 20; columns: 4; rowSpacing: 12; columnSpacing: 14
                                Text { text: qsTr("Birth country"); color: muted; font.pixelSize: 11; Layout.columnSpan: 2 }
                                Text { text: qsTr("Birth-year cohort"); color: muted; font.pixelSize: 11; Layout.columnSpan: 2 }
                                ComboBox {
                                    id: countryPicker; Layout.fillWidth: true; Layout.columnSpan: 2
                                    model: appController.countryOptions; textRole: "name"; valueRole: "code"
                                    background: Rectangle { radius: 9; color: dark ? "#101a2b" : "#f8fafc"; border.color: countryPicker.activeFocus ? accent : line }
                                    contentItem: Text { leftPadding: 10; text: countryPicker.displayText; color: ink; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
                                    Component.onCompleted: {
                                        for (let i = 0; i < count; i++) if (model[i].code === "HUN") { currentIndex = i; break }
                                    }
                                }
                                RowLayout {
                                    Layout.fillWidth: true; Layout.columnSpan: 2; spacing: 8
                                    Field {
                                        id: startYear; Layout.fillWidth: true; text: "2015"
                                        validator: IntValidator { bottom: 1; top: 9999 }
                                        horizontalAlignment: TextInput.AlignHCenter
                                    }
                                    Text { text: "to"; color: muted }
                                    Field {
                                        id: endYear; Layout.fillWidth: true; text: "2019"
                                        validator: IntValidator { bottom: 1; top: 9999 }
                                        horizontalAlignment: TextInput.AlignHCenter
                                    }
                                }
                                Text { text: qsTr("Maximum birth-year gap"); color: muted; font.pixelSize: 11; Layout.columnSpan: 2 }
                                Text { text: qsTr("Meeting probability · assumption"); color: muted; font.pixelSize: 11; Layout.columnSpan: 2 }
                                Field {
                                    id: gapInput; Layout.fillWidth: true; Layout.columnSpan: 2; text: "3"
                                    validator: IntValidator { bottom: 0; top: 100 }
                                    placeholderText: "0"
                                }
                                Field { id: meetingInput; Layout.fillWidth: true; Layout.columnSpan: 2; placeholderText: qsTr("Unknown · e.g. 1e-6"); inputMethodHints: Qt.ImhFormattedNumbersOnly }
                                Text { text: qsTr("Channel for the defined encounter"); color: muted; font.pixelSize: 11; Layout.columnSpan: 2 }
                                Text { text: qsTr("Relationship after encounter · assumption"); color: muted; font.pixelSize: 11; Layout.columnSpan: 2 }
                                ComboBox {
                                    id: meetingChannel; Layout.fillWidth: true; Layout.columnSpan: 2
                                    model: [qsTr("Not specified"), qsTr("Dating app"), qsTr("Social media"), qsTr("Online community"), qsTr("In person / shared network"), qsTr("Other")]
                                    background: Rectangle { radius: 9; color: dark ? "#101a2b" : "#f8fafc"; border.color: meetingChannel.activeFocus ? accent : line }
                                    contentItem: Text { leftPadding: 10; text: meetingChannel.displayText; color: ink; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
                                }
                                Field { id: relationshipInput; Layout.fillWidth: true; Layout.columnSpan: 2; placeholderText: qsTr("Unknown · e.g. 0.02"); inputMethodHints: Qt.ImhFormattedNumbersOnly }
                                Item { Layout.columnSpan: 2 }
                                RowLayout {
                                    Layout.columnSpan: 2; Layout.fillWidth: true; spacing: 9
                                    ActionButton {
                                        text: qsTr("Calculate analysis"); primary: true
                                        onClicked: {
                                            const result = appController.analyzeStory(countryPicker.currentValue,
                                                window.yearFrom(startYear, 2015), window.yearFrom(endYear, 2019),
                                                window.yearFrom(gapInput, 3), meetingInput.text,
                                                relationshipInput.text, meetingChannel.currentText)
                                            window.analysisResult = result
                                        }
                                    }
                                    ActionButton { text: qsTr("Export report"); enabled: analysisResult.ok === true; onClicked: appController.exportCurrent("markdown") }
                                }
                            }
                        }
                        Surface {
                            visible: analysisResult.ok === true
                            Layout.fillWidth: true; Layout.preferredHeight: analysisResult.ok ? 240 + (analysisResult.factors.length * 101) + (analysisResult.warnings.length * 27) : 0
                            ColumnLayout {
                                anchors.fill: parent; anchors.margins: 19; spacing: 11
                                Text { text: qsTr("RESULT · EXACT UNDER THE SELECTED MODEL"); color: accent; font.pixelSize: 10; font.weight: Font.DemiBold; font.letterSpacing: 1.2 }
                                RowLayout {
                                    Layout.fillWidth: true; spacing: 20
                                    ColumnLayout {
                                        Layout.fillWidth: true; spacing: 4
                                        Text { text: qsTr("Birthplace + age conditions"); color: muted; font.pixelSize: 12 }
                                        Text { text: analysisResult.demographicDisplay || "—"; color: ink; font.pixelSize: 31; font.weight: Font.DemiBold }
                                        Text { text: (analysisResult.demographicOdds || "") + "  ·  " + (analysisResult.population || ""); color: muted; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                    }
                                    Rectangle { width: 1; height: 74; color: line }
                                    ColumnLayout {
                                        Layout.preferredWidth: 250; spacing: 4
                                        Text { text: qsTr("Complete relationship story"); color: muted; font.pixelSize: 12 }
                                        Text { text: analysisResult.fullDisplay && analysisResult.fullDisplay !== "Unknown" ? analysisResult.fullDisplay : qsTr("Not calculated"); color: warning; font.pixelSize: 21; font.weight: Font.DemiBold }
                                        Text { text: qsTr("Requires explicit meeting and relationship probabilities"); color: muted; font.pixelSize: 10; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                    }
                                }
                                Rectangle { Layout.fillWidth: true; height: 1; color: line }
                                Repeater {
                                    model: analysisResult.factors || []
                                    delegate: RowLayout {
                                        required property var modelData
                                        Layout.fillWidth: true; spacing: 12
                                        Rectangle { width: 7; height: 7; radius: 4; color: modelData.evidence === "assumed" ? warning : accent; Layout.alignment: Qt.AlignTop; Layout.topMargin: 6 }
                                        ColumnLayout {
                                            Layout.fillWidth: true; spacing: 3
                                            Text { text: modelData.label + "  ·  " + modelData.display; color: ink; font.pixelSize: 12; font.weight: Font.DemiBold; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                            Text { text: modelData.formula + "  |  denominator: " + modelData.denominator + "  |  " + modelData.evidence; color: muted; font.pixelSize: 10; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                        }
                                    }
                                }
                                Repeater {
                                    model: analysisResult.warnings || []
                                    delegate: Text { required property string modelData; text: "⚠  " + modelData; color: warning; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                }
                                RowLayout {
                                    Layout.fillWidth: true
                                    Text { text: qsTr("Reproducibility ID") + ": " + (analysisResult.manifestId || ""); color: muted; font.pixelSize: 10; Layout.fillWidth: true }
                                    ActionButton { text: qsTr("JSON manifest"); onClicked: appController.exportCurrent("json") }
                                    ActionButton { text: qsTr("CSV factors"); onClicked: appController.exportCurrent("csv") }
                                }
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true; visible: analysisResult.ok === true; spacing: 9
                            Field { id: scenarioName; Layout.preferredWidth: 260; placeholderText: qsTr("Scenario name") }
                            ActionButton { text: qsTr("Save scenario locally"); primary: true; onClicked: appController.saveCurrentScenario(scenarioName.text || qsTr("Untitled scenario")) }
                        }
                    }
                }

                // Recurrence
                Flickable {
                    clip: true; contentWidth: width; contentHeight: recurrenceColumn.implicitHeight + 60
                    ScrollBar.vertical: ScrollBar {}
                    ColumnLayout {
                        id: recurrenceColumn; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; spacing: 18
                        anchors.leftMargin: 30; anchors.rightMargin: 30; anchors.topMargin: 27
                        SectionTitle { titleText: qsTr("How often would it happen again?"); detailText: qsTr("This calculator applies only to independent attempts with a constant, specified chance of success.") }
                        Surface {
                            Layout.fillWidth: true; Layout.preferredHeight: 239
                            GridLayout {
                                anchors.fill: parent; anchors.margins: 21; columns: 3; columnSpacing: 15; rowSpacing: 10
                                Text { text: qsTr("Chance per attempt p"); color: muted; font.pixelSize: 11 }
                                Text { text: qsTr("Number of independent attempts N"); color: muted; font.pixelSize: 11 }
                                Text { text: qsTr("Target probability"); color: muted; font.pixelSize: 11 }
                                Field { id: recurrenceP; Layout.fillWidth: true; text: "0.001"; placeholderText: "0.001" }
                                Field { id: recurrenceN; Layout.fillWidth: true; text: "1000"; validator: IntValidator { bottom: 0; top: 2147483647 } }
                                ComboBox { id: targetBox; Layout.fillWidth: true; model: ["1", "10", "25", "50", "63.2", "75", "90", "95", "99", "99.9", "99.99", "100"]; currentIndex: 3
                                    background: Rectangle { radius: 9; color: dark ? "#101a2b" : "#f8fafc"; border.color: targetBox.activeFocus ? accent : line }
                                    contentItem: Text { leftPadding: 10; text: targetBox.currentText + "%"; color: ink; verticalAlignment: Text.AlignVCenter }
                                }
                                Item { Layout.columnSpan: 2; Layout.fillHeight: true }
                                ActionButton { text: qsTr("Calculate recurrence"); primary: true; Layout.fillWidth: true
                                    onClicked: window.recurrenceResult = appController.calculateRecurrence(recurrenceP.text, window.yearFrom(recurrenceN, 1000), Number(targetBox.currentText)) }
                            }
                        }
                        Surface {
                            visible: recurrenceResult.ok === true
                            Layout.fillWidth: true; Layout.preferredHeight: 185
                            RowLayout {
                                anchors.fill: parent; anchors.margins: 20; spacing: 20
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 6
                                    Text { text: qsTr("Chance of ≥1 success after N attempts"); color: muted; font.pixelSize: 12 }
                                    Text { text: recurrenceResult.reachedPercent || "—"; color: ink; font.pixelSize: 32; font.weight: Font.DemiBold }
                                    Text { text: qsTr("Minimum attempts to selected target"); color: muted; font.pixelSize: 12 }
                                    Text { text: recurrenceResult.neededText || "—"; color: accent; font.pixelSize: 24; font.weight: Font.DemiBold }
                                }
                                Rectangle { width: 1; Layout.fillHeight: true; color: line }
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 8
                                    Text { text: "1 − (1 − p)ᴺ"; color: accent; font.pixelSize: 22; font.weight: Font.DemiBold }
                                    Text { text: recurrenceResult.warning || ""; color: warning; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                }
                            }
                        }
                        Surface {
                            Layout.fillWidth: true; Layout.preferredHeight: 125
                            RowLayout {
                                anchors.fill: parent; anchors.margins: 20; spacing: 14
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    Text { text: qsTr("Pair count is a different quantity"); color: ink; font.pixelSize: 15; font.weight: Font.DemiBold }
                                    Text { text: qsTr("Pairs that share a person overlap. Counting them does not create independent chances for the same two people to meet."); color: muted; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                }
                                Field { id: pairInput; Layout.preferredWidth: 110; text: "1000"; validator: IntValidator { bottom: 0; top: 2147483647 } }
                                ActionButton { text: qsTr("Count pairs"); onClicked: pairOutput.text = appController.calculatePairs(window.yearFrom(pairInput, 1000)) }
                            }
                        }
                        Text { id: pairOutput; text: ""; color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                        Text { text: recurrenceResult.error || ""; color: "#e88686"; font.pixelSize: 12 }
                    }
                }

                // Demographic explorer
                Flickable {
                    clip: true; contentWidth: width; contentHeight: demographicsColumn.implicitHeight + 60
                    ScrollBar.vertical: ScrollBar {}
                    ColumnLayout {
                        id: demographicsColumn; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; spacing: 17
                        anchors.leftMargin: 30; anchors.rightMargin: 30; anchors.topMargin: 25
                        SectionTitle { titleText: qsTr("Explore the installed birth counts"); detailText: qsTr("Shares use the sum of records in this dataset as the denominator. Coverage and provenance determine what those shares mean.") }
                        Surface {
                            Layout.fillWidth: true; Layout.preferredHeight: 117
                            RowLayout {
                                anchors.fill: parent; anchors.margins: 18; spacing: 14
                                Rectangle { width: 39; height: 39; radius: 12; color: "#533e27"; Text { anchors.centerIn: parent; text: "!"; color: warning; font.pixelSize: 20; font.weight: Font.Bold } }
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 4
                                    Text { text: appController.datasetName; color: ink; font.pixelSize: 15; font.weight: Font.DemiBold }
                                    Text { text: appController.datasetSummary + " · SHA-256 " + appController.datasetSha256.slice(0, 16) + "…"; color: muted; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                }
                                ActionButton { text: qsTr("Import CSV"); primary: true; onClicked: appController.chooseAndImportDataset() }
                            }
                        }
                        Surface {
                            Layout.fillWidth: true; Layout.preferredHeight: 95 + appController.countryShares.length * 58
                            ColumnLayout {
                                anchors.fill: parent; anchors.margins: 19; spacing: 12
                                Text { text: qsTr("Birth shares in the selected dataset period"); color: ink; font.pixelSize: 15; font.weight: Font.DemiBold }
                                Repeater {
                                    model: appController.countryShares
                                    delegate: RowLayout {
                                        required property var modelData
                                        Layout.fillWidth: true; spacing: 12
                                        ColumnLayout {
                                            Layout.preferredWidth: 150; spacing: 2
                                            Text { text: modelData.name + " · " + modelData.code; color: ink; font.pixelSize: 12; font.weight: Font.DemiBold }
                                            Text { text: modelData.continent; color: muted; font.pixelSize: 10 }
                                        }
                                        Rectangle {
                                            Layout.fillWidth: true; height: 14; radius: 7; color: panelAlt
                                            Rectangle { width: parent.width * modelData.share; height: parent.height; radius: 7; color: accent }
                                        }
                                        Text { text: formatPercent(modelData.share); color: ink; font.pixelSize: 11; Layout.preferredWidth: 72; horizontalAlignment: Text.AlignRight }
                                    }
                                }
                        Text { text: qsTr("Shares use this file's records as the denominator. Coverage is not assumed to be global."); color: warning; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                            }
                        }
                        Surface {
                            Layout.fillWidth: true; Layout.preferredHeight: 160
                            ColumnLayout {
                                anchors.fill: parent; anchors.margins: 18; spacing: 6
                                Text { text: qsTr("CSV schema for import"); color: ink; font.pixelSize: 14; font.weight: Font.DemiBold }
                                Text { text: "country_code,country_name,continent,year,births"; color: accent; font.family: "Consolas"; font.pixelSize: 12 }
                                Text { text: qsTr("UTF-8 only · 20 MB maximum · at most 200,000 records · duplicate country-year rows rejected · non-negative integer births. Add verified source, definition, coverage, and license details to your data records before interpreting results."); color: muted; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                            }
                        }
                    }
                }

                // Simulation lab
                Flickable {
                    clip: true; contentWidth: width; contentHeight: simulationColumn.implicitHeight + 55
                    ScrollBar.vertical: ScrollBar {}
                    ColumnLayout {
                        id: simulationColumn; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; spacing: 17
                        anchors.leftMargin: 30; anchors.rightMargin: 30; anchors.topMargin: 25
                        SectionTitle { titleText: qsTr("Simulation lab"); detailText: qsTr("Check a defined Bernoulli probability with a reproducible random seed. Simulation cannot reveal probabilities far below its sample budget.") }
                        Surface {
                            Layout.fillWidth: true; Layout.preferredHeight: 220
                            GridLayout {
                                anchors.fill: parent; anchors.margins: 21; columns: 3; rowSpacing: 10; columnSpacing: 13
                                Text { text: qsTr("Assumed per-trial probability"); color: muted; font.pixelSize: 11 }
                                Text { text: qsTr("Simulation budget (max 50 million)"); color: muted; font.pixelSize: 11 }
                                Text { text: qsTr("Seed"); color: muted; font.pixelSize: 11 }
                                Field { id: simulationP; Layout.fillWidth: true; text: "0.001" }
                                Field { id: simulationTrials; Layout.fillWidth: true; text: "100000"; validator: IntValidator { bottom: 1; top: 50000000 } }
                                Field { id: simulationSeed; Layout.fillWidth: true; text: "42"; validator: IntValidator { bottom: 0; top: 2147483647 } }
                                Text { text: qsTr("Progress"); color: muted; font.pixelSize: 11; Layout.columnSpan: 3 }
                                ProgressBar { id: simProgress; Layout.fillWidth: true; Layout.columnSpan: 2; from: 0; to: 1; value: window.simulationDone / window.simulationTotal }
                                RowLayout {
                                    Layout.fillWidth: true
                                    ActionButton { text: qsTr("Run locally"); primary: true; onClicked: { window.simulationDone = 0; window.simulationResult = {}; appController.startSimulation(simulationP.text, window.yearFrom(simulationTrials, 100000), window.yearFrom(simulationSeed, 42)) } }
                                    ActionButton { text: qsTr("Cancel"); onClicked: appController.cancelSimulation() }
                                }
                            }
                        }
                        Surface {
                            visible: simulationResult.probability !== undefined || simulationResult.error !== undefined
                            Layout.fillWidth: true; Layout.preferredHeight: 205
                            ColumnLayout {
                                anchors.fill: parent; anchors.margins: 19; spacing: 8
                                Text { text: simulationResult.error ? qsTr("Simulation stopped") : qsTr("Simulation result"); color: ink; font.pixelSize: 16; font.weight: Font.DemiBold }
                                Text { text: simulationResult.successes !== undefined ? simulationResult.successes + " / " + simulationResult.trials + " observed successes · seed " + simulationResult.seed : (simulationResult.error || ""); color: accent; font.pixelSize: 19; font.weight: Font.DemiBold; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                Text { text: simulationResult.lower !== undefined ? "95% interval: " + formatPercent(simulationResult.lower) + " to " + formatPercent(simulationResult.upper) + " · " + simulationResult.method : ""; color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                Text { text: simulationResult.note || qsTr("A zero count is compatible with a small non-zero probability."); color: warning; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                            }
                        }
                        Text { text: qsTr("This simulation samples independent Bernoulli trials only; it does not model a relationship network or dependent person-pairs."); color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    }
                }

                // Saved scenarios
                Flickable {
                    clip: true; contentWidth: width; contentHeight: savedColumn.implicitHeight + 55
                    ScrollBar.vertical: ScrollBar {}
                    ColumnLayout {
                        id: savedColumn; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; spacing: 17
                        anchors.leftMargin: 30; anchors.rightMargin: 30; anchors.topMargin: 25
                        SectionTitle { titleText: qsTr("Saved scenarios"); detailText: qsTr("Saved input values and result manifests remain in a local SQLite database on this device.") }
                        Repeater {
                            model: appController.savedScenarios
                            delegate: Surface {
                                required property var modelData
                                Layout.fillWidth: true; Layout.preferredHeight: 91
                                RowLayout {
                                    anchors.fill: parent; anchors.margins: 17; spacing: 13
                                    ColumnLayout {
                                        Layout.fillWidth: true; spacing: 3
                                        Text { text: modelData.name; color: ink; font.pixelSize: 14; font.weight: Font.DemiBold }
                                        Text { text: modelData.country_code + " · demographic probability " + modelData.probability + " · " + modelData.updated_at; color: muted; font.pixelSize: 10; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                    }
                                    ActionButton { text: qsTr("Load inputs"); onClicked: {
                                        const restored = appController.restoreScenario(modelData.scenario_id)
                                        for (let i = 0; i < countryPicker.count; i++) if (countryPicker.model[i].code === restored.country_code) countryPicker.currentIndex = i
                                        startYear.text = restored.start_year; endYear.text = restored.end_year; gapInput.text = restored.max_birth_year_gap
                                        meetingInput.text = restored.meeting_probability ? restored.meeting_probability : ""
                                        relationshipInput.text = restored.relationship_probability ? restored.relationship_probability : ""
                                        meetingChannel.currentIndex = 0; window.goTo(1)
                                    } }
                                    ActionButton { text: qsTr("Delete"); onClicked: appController.deleteScenario(modelData.scenario_id) }
                                }
                            }
                        }
                        Text { visible: appController.savedScenarios.length === 0; text: qsTr("No saved scenarios yet. Calculate a story analysis, then save it with a name."); color: muted; font.pixelSize: 13; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    }
                }

                // Teaching tools
                Flickable {
                    clip: true; contentWidth: width; contentHeight: learningColumn.implicitHeight + 60
                    ScrollBar.vertical: ScrollBar {}
                    ColumnLayout {
                        id: learningColumn; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; spacing: 17
                        anchors.leftMargin: 30; anchors.rightMargin: 30; anchors.topMargin: 25
                        SectionTitle { titleText: qsTr("Probability learning tools"); detailText: qsTr("Small calculators that keep the population, denominator, and sampling assumptions visible.") }
                        Surface {
                            Layout.fillWidth: true; Layout.preferredHeight: 181
                            GridLayout {
                                anchors.fill: parent; anchors.margins: 19; columns: 4; columnSpacing: 12; rowSpacing: 9
                                Text { text: qsTr("Bayes: prior P(H)"); color: muted; font.pixelSize: 10 }
                                Text { text: qsTr("Sensitivity P(+|H)"); color: muted; font.pixelSize: 10 }
                                Text { text: qsTr("False positive P(+|¬H)"); color: muted; font.pixelSize: 10 }
                                Item {}
                                Field { id: bayesPrior; Layout.fillWidth: true; text: "0.01" }
                                Field { id: bayesSensitivity; Layout.fillWidth: true; text: "0.95" }
                                Field { id: bayesFalsePositive; Layout.fillWidth: true; text: "0.05" }
                                ActionButton { text: qsTr("Calculate Bayes"); onClicked: bayesOutput.text = appController.calculateBayes(bayesPrior.text, bayesSensitivity.text, bayesFalsePositive.text) }
                                Text { id: bayesOutput; text: qsTr("Result appears here"); color: accent; font.pixelSize: 13; Layout.columnSpan: 4 }
                            }
                        }
                        Surface {
                            Layout.fillWidth: true; Layout.preferredHeight: 155
                            RowLayout {
                                anchors.fill: parent; anchors.margins: 19; spacing: 13
                                ColumnLayout {
                                    Layout.fillWidth: true; spacing: 5
                                    Text { text: qsTr("Birthday paradox"); color: ink; font.pixelSize: 15; font.weight: Font.DemiBold }
                                    Text { text: qsTr("Probability that at least two independent, uniform draws share a category."); color: muted; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                }
                                ColumnLayout {
                                    Text { text: qsTr("People"); color: muted; font.pixelSize: 10 }
                                    Field { id: birthdayPeople; text: "23"; validator: IntValidator { bottom: 0; top: 1000000 } }
                                }
                                ColumnLayout {
                                    Text { text: qsTr("Categories"); color: muted; font.pixelSize: 10 }
                                    Field { id: birthdayCategories; text: "365"; validator: IntValidator { bottom: 1; top: 1000000000 } }
                                }
                                ColumnLayout {
                                    ActionButton { text: qsTr("Calculate"); onClicked: birthdayOutput.text = appController.calculateBirthday(window.yearFrom(birthdayPeople, 23), window.yearFrom(birthdayCategories, 365)) }
                                    Text { id: birthdayOutput; text: ""; color: accent; font.pixelSize: 12 }
                                }
                            }
                        }
                        Surface {
                            Layout.fillWidth: true; Layout.preferredHeight: 116
                            ColumnLayout { anchors.fill: parent; anchors.margins: 19; spacing: 7
                                Text { text: qsTr("Why 1/p is not 100%"); color: ink; font.pixelSize: 15; font.weight: Font.DemiBold }
                                Text { text: qsTr("With small p, N = 1/p gives approximately 1 − e⁻¹ = 63.2% chance of at least one success. A 100% target needs certainty in one attempt; otherwise the exact target requires infinitely many independent attempts."); color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                            }
                        }
                    }
                }

                // Sources and settings
                Flickable {
                    clip: true; contentWidth: width; contentHeight: sourcesColumn.implicitHeight + 55
                    ScrollBar.vertical: ScrollBar {}
                    ColumnLayout {
                        id: sourcesColumn; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; spacing: 16
                        anchors.leftMargin: 30; anchors.rightMargin: 30; anchors.topMargin: 25
                        SectionTitle { titleText: qsTr("Sources, privacy & settings"); detailText: qsTr("The currently installed dataset is a synthetic teaching example. The following are candidate authoritative sources for future real data integrations.") }
                        Surface {
                            Layout.fillWidth: true; Layout.preferredHeight: 225
                            ColumnLayout {
                                anchors.fill: parent; anchors.margins: 19; spacing: 6
                                Text { text: appController.datasetName; color: ink; font.pixelSize: 15; font.weight: Font.DemiBold }
                                Text { text: qsTr("Publisher: ") + appController.datasetPublisher + " · " + qsTr("kind: ") + appController.datasetKind; color: muted; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                Text { text: qsTr("Source: ") + appController.datasetSource; color: muted; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                Text { text: qsTr("License: ") + appController.datasetLicense; color: muted; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                Text { text: qsTr("Accessed: ") + appController.datasetAccessedOn + " · SHA-256: " + appController.datasetSha256; color: muted; font.pixelSize: 10; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                Text { text: qsTr("No external service is contacted by the application. Imported files are validated and copied to your local application data folder. User assumptions are stored only when you save a scenario."); color: accent; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                Repeater {
                                    model: appController.datasetWarnings
                                    delegate: Text { required property string modelData; text: "!  " + modelData; color: warning; font.pixelSize: 10; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                }
                            }
                        }
                        Surface {
                            Layout.fillWidth: true; Layout.preferredHeight: 252
                            ColumnLayout {
                                anchors.fill: parent; anchors.margins: 19; spacing: 10
                                Text { text: qsTr("Candidate source references"); color: ink; font.pixelSize: 15; font.weight: Font.DemiBold }
                                Text { text: "UN World Population Prospects 2024 · official estimates and projections, 1950–2100\n" + "<a href='https://population.un.org/wpp'>population.un.org/wpp</a>"; textFormat: Text.RichText; onLinkActivated: Qt.openUrlExternally(link); color: muted; font.pixelSize: 12; linkColor: accent; Layout.fillWidth: true }
                                Text { text: "Hungarian Central Statistical Office · annual live births\n" + "<a href='https://www.ksh.hu/stadat_files/nep/en/nep0006.html'>ksh.hu/stadat_files/nep/en/nep0006.html</a>"; textFormat: Text.RichText; onLinkActivated: Qt.openUrlExternally(link); color: muted; font.pixelSize: 12; linkColor: accent; Layout.fillWidth: true }
                                Text { text: "Population Reference Bureau · historical estimate of cumulative births (2022 publication)\n" + "<a href='https://www.prb.org/news/how-many-people-have-ever-lived-on-earth/'>prb.org/news/how-many-people-have-ever-lived-on-earth</a>"; textFormat: Text.RichText; onLinkActivated: Qt.openUrlExternally(link); color: muted; font.pixelSize: 12; linkColor: accent; Layout.fillWidth: true }
                                Text { text: qsTr("Source availability does not imply permission to redistribute downloaded files. Verify definition, license, coverage, and publication date before importing."); color: warning; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                            }
                        }
                        Surface {
                            Layout.fillWidth: true; Layout.preferredHeight: 156
                            ColumnLayout { anchors.fill: parent; anchors.margins: 19; spacing: 6
                                Text { text: qsTr("Local diagnostics"); color: ink; font.pixelSize: 14; font.weight: Font.DemiBold }
                                Text { text: qsTr("Storage integrity: ") + qsTr("SQLite local database") + " · " + appController.lastCalculation; color: muted; font.pixelSize: 11 }
                                Text { text: qsTr("Theme") + ": " + (dark ? qsTr("Dark") : qsTr("Light")) + " · " + qsTr("Network") + ": " + qsTr("offline by default"); color: muted; font.pixelSize: 11 }
                                Text { text: qsTr("No analytics, telemetry, accounts, cloud synchronization, or background uploads are included."); color: accent; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                            }
                        }
                    }
                }
            }
        }
    }
}
