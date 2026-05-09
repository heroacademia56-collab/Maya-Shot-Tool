<<<<<<< HEAD
# Brown Jasmine
# P02 - Storyboard Shot Setup / 3D Shot Planning Tool
# Maya + PySide2

from PySide2 import QtWidgets, QtCore
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance


# ----------------------------------------------------------
# Maya main window helper
# ----------------------------------------------------------

def get_maya_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)


# ----------------------------------------------------------
# Camera item widget (row in camera list)
# ----------------------------------------------------------

class CameraItem(QtWidgets.QWidget):
    """One row: checkbox + camera name + notes field + shot label."""
    def __init__(self, cam_name, parent=None):
        super(CameraItem, self).__init__(parent)

        self.cam_name = cam_name

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)

        # Checkbox
        self.checkbox = QtWidgets.QCheckBox()
        layout.addWidget(self.checkbox)

        # Camera label
        self.label = QtWidgets.QLabel(cam_name)
        self.label.setMinimumWidth(140)
        layout.addWidget(self.label)

        # Notes field
        self.notes = QtWidgets.QLineEdit()
        self.notes.setPlaceholderText("Notes / Action / Dialogue")
        layout.addWidget(self.notes)

        # Shot number (auto-assigned)
        self.shot_label = QtWidgets.QLabel("")
        self.shot_label.setMinimumWidth(70)
        self.shot_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.shot_label)

    def is_selected(self):
        return self.checkbox.isChecked()

    def get_data(self):
        return {
            "camera": self.cam_name,
            "notes": self.notes.text(),
            "shot_number": self.shot_label.text()
        }


# ----------------------------------------------------------
# Viewport overlay functions (composition guides)
# ----------------------------------------------------------

def toggle_rule_of_thirds(state):
    """Draws 2 vertical + 2 horizontal lines."""
    if state:
        if not cmds.objExists("SB_ThirdsLines"):
            grp = cmds.createNode("transform", name="SB_ThirdsLines")
            # Vertical lines
            v1 = cmds.curve(d=1, p=[(-0.33, 0, -1), (-0.33, 0, 1)], name="SB_Thirds_V1")
            v2 = cmds.curve(d=1, p=[(0.33, 0, -1), (0.33, 0, 1)], name="SB_Thirds_V2")
            # Horizontal lines
            h1 = cmds.curve(d=1, p=[(-1, 0, -0.33), (1, 0, -0.33)], name="SB_Thirds_H1")
            h2 = cmds.curve(d=1, p=[(-1, 0, 0.33), (1, 0, 0.33)], name="SB_Thirds_H2")
            cmds.parent(v1, v2, h1, h2, grp)
            cmds.setAttr(grp + ".overrideEnabled", 1)
            cmds.setAttr(grp + ".overrideColor", 17)  # light yellow
    else:
        if cmds.objExists("SB_ThirdsLines"):
            cmds.delete("SB_ThirdsLines")


def toggle_horizon(state):
    """Single horizontal line across the frame."""
    if state:
        if not cmds.objExists("SB_Horizon"):
            h = cmds.curve(d=1, p=[(-1, 0, 0), (1, 0, 0)], name="SB_Horizon")
            cmds.setAttr(h + ".overrideEnabled", 1)
            cmds.setAttr(h + ".overrideColor", 13)  # light blue
    else:
        if cmds.objExists("SB_Horizon"):
            cmds.delete("SB_Horizon")


def toggle_crosshair(state):
    """Center crosshair."""
    if state:
        if not cmds.objExists("SB_Crosshair"):
            grp = cmds.createNode("transform", name="SB_Crosshair")
            h = cmds.curve(d=1, p=[(-0.1, 0, 0), (0.1, 0, 0)], name="SB_Crosshair_H")
            v = cmds.curve(d=1, p=[(0, 0, -0.1), (0, 0, 0.1)], name="SB_Crosshair_V")
            cmds.parent(h, v, grp)
            cmds.setAttr(grp + ".overrideEnabled", 1)
            cmds.setAttr(grp + ".overrideColor", 6)  # red
    else:
        if cmds.objExists("SB_Crosshair"):
            cmds.delete("SB_Crosshair")


def toggle_safe_frame(state):
    """Uses Maya's built-in safe frame toggle on the focused modelPanel."""
    panel = cmds.getPanel(withFocus=True)
    if panel and "modelPanel" in panel:
        cmds.modelEditor(panel, e=True, safeFrame=state)


# ----------------------------------------------------------
# Main tabbed UI
# ----------------------------------------------------------

class StoryboardToolUI(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_window()):
        super(StoryboardToolUI, self).__init__(parent)

        self.setWindowTitle("Storyboard Shot Setup Tool")
        self.setMinimumWidth(650)
        self.setMinimumHeight(400)

        self.setStyleSheet("""
            QWidget {
                background-color: #f7f7f7;
                font-size: 12px;
            }
            QLineEdit {
                background: white;
                border: 1px solid #cccccc;
                padding: 3px;
            }
            QPushButton {
                background: #e6e6e6;
                border: 1px solid #bfbfbf;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: #dcdcdc;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                margin-top: -1px;
            }
            QTabBar::tab {
                background: #e6e6e6;
                padding: 4px 10px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
            }
        """)

        self.camera_items = []

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        title = QtWidgets.QLabel("Storyboard Shot Setup — Maya")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        main_layout.addWidget(title)

        self.tabs = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tabs)

        # Cameras tab
        self.cameras_tab = QtWidgets.QWidget()
        self.guides_tab = QtWidgets.QWidget()

        self.tabs.addTab(self.cameras_tab, "Cameras")
        self.tabs.addTab(self.guides_tab, "Guides")

        self.capture_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.capture_tab, "Capture")
        self._build_capture_tab()

        # Storyboard tab
        self.storyboard_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.storyboard_tab, "Storyboard")
        self._build_storyboard_tab()



        self._build_cameras_tab()
        self._build_guides_tab()

    # ---------------- Cameras Tab ----------------

    def _build_cameras_tab(self):
        layout = QtWidgets.QVBoxLayout(self.cameras_tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        info = QtWidgets.QLabel("Select scene cameras, add notes, and assign shot numbers.")
        layout.addWidget(info)

        # Scroll area for camera list
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        self.scroll_layout.setContentsMargins(4, 4, 4, 4)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(btn_layout)

        refresh_btn = QtWidgets.QPushButton("Refresh Cameras")
        refresh_btn.clicked.connect(self.load_cameras)
        btn_layout.addWidget(refresh_btn)

        assign_btn = QtWidgets.QPushButton("Assign Shot Numbers")
        assign_btn.clicked.connect(self.assign_shot_numbers)
        btn_layout.addWidget(assign_btn)

        debug_btn = QtWidgets.QPushButton("Print Shot List (Debug)")
        debug_btn.clicked.connect(self.debug_print_shots)
        btn_layout.addWidget(debug_btn)

        layout.addStretch()

        # initial load
        self.load_cameras()

    def load_cameras(self):
        """Scan Maya scene for cameras and populate UI."""
        # Clear old items
        if hasattr(self, "scroll_layout"):
            for i in reversed(range(self.scroll_layout.count())):
                widget = self.scroll_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

        self.camera_items = []

        cameras = cmds.listCameras() or []

        for cam in cameras:
            item = CameraItem(cam)
            self.camera_items.append(item)
            self.scroll_layout.addWidget(item)

        self.scroll_layout.addStretch()

    def assign_shot_numbers(self):
        """Assign Shot 01, Shot 02… to selected cameras."""
        count = 1
        for item in self.camera_items:
            if item.is_selected():
                item.shot_label.setText(f"Shot {count:02d}")
                count += 1
            else:
                item.shot_label.setText("")

    def debug_print_shots(self):
        """Print selected shot data to the script editor."""
        print("\n=== SHOT LIST ===")
        for item in self.camera_items:
            if item.is_selected():
                print(item.get_data())
        print("=================\n")

    # ---------------- Guides Tab ----------------

    def _build_guides_tab(self):
        layout = QtWidgets.QVBoxLayout(self.guides_tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        info = QtWidgets.QLabel("Toggle composition guides in the active viewport.")
        layout.addWidget(info)

        self.thirds_cb = QtWidgets.QCheckBox("Rule of Thirds")
        self.thirds_cb.stateChanged.connect(
            lambda s: toggle_rule_of_thirds(s == QtCore.Qt.Checked)
        )
        layout.addWidget(self.thirds_cb)

        self.horizon_cb = QtWidgets.QCheckBox("Horizon Line")
        self.horizon_cb.stateChanged.connect(
            lambda s: toggle_horizon(s == QtCore.Qt.Checked)
        )
        layout.addWidget(self.horizon_cb)

        self.cross_cb = QtWidgets.QCheckBox("Center Crosshair")
        self.cross_cb.stateChanged.connect(
            lambda s: toggle_crosshair(s == QtCore.Qt.Checked)
        )
        layout.addWidget(self.cross_cb)

        self.safe_cb = QtWidgets.QCheckBox("Safe Frame (active panel)")
        self.safe_cb.stateChanged.connect(
            lambda s: toggle_safe_frame(s == QtCore.Qt.Checked)
        )
        layout.addWidget(self.safe_cb)

        layout.addStretch()

    # ---------------- Capture Tab ----------------

    def _build_capture_tab(self):
        layout = QtWidgets.QVBoxLayout(self.capture_tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        info = QtWidgets.QLabel("Capture still images from selected cameras.")
        layout.addWidget(info)

        # Resolution
        res_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(res_layout)

        res_layout.addWidget(QtWidgets.QLabel("Resolution:"))
        self.width_field = QtWidgets.QLineEdit("1280")
        self.height_field = QtWidgets.QLineEdit("720")
        self.width_field.setMaximumWidth(60)
        self.height_field.setMaximumWidth(60)

        res_layout.addWidget(self.width_field)
        res_layout.addWidget(QtWidgets.QLabel("x"))
        res_layout.addWidget(self.height_field)

        # Frame selection
        frame_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(frame_layout)

        self.frame_field = QtWidgets.QLineEdit()
        self.frame_field.setPlaceholderText("Frame (blank = current frame)")
        self.frame_field.setMaximumWidth(150)
        frame_layout.addWidget(self.frame_field)

        # Capture button
        capture_btn = QtWidgets.QPushButton("Capture Selected Shots")
        capture_btn.clicked.connect(self.capture_selected_shots)
        layout.addWidget(capture_btn)

        # Output log
        self.capture_log = QtWidgets.QTextEdit()
        self.capture_log.setReadOnly(True)
        layout.addWidget(self.capture_log)

        layout.addStretch()


    def capture_selected_shots(self):
        """Capture still images from each selected camera."""
        width = int(self.width_field.text())
        height = int(self.height_field.text())

        frame_text = self.frame_field.text()
        if frame_text.strip():
            frame = int(frame_text)
        else:
            frame = cmds.currentTime(q=True)

        self.capture_log.append("Starting capture...\n")

        # Storage for Module C
        self.captured_images = []

        for item in self.camera_items:
            if not item.is_selected():
                continue

            cam = item.cam_name
            shot = item.shot_label.text()

            if not shot:
                continue

            # Build file path
            filename = f"{shot}_{cam}.png"
            filepath = cmds.internalVar(userTmpDir=True) + filename

            # Switch viewport to camera
            cmds.lookThru(cam)

            # Capture
            cmds.playblast(
                cf=filepath,
                format="image",
                viewer=False,
                showOrnaments=False,
                frame=frame,
                width=width,
                height=height,
                percent=100
            )

            self.capture_log.append(f"Captured {shot} from {cam} → {filepath}")
            self.captured_images.append({
                "shot": shot,
                "camera": cam,
                "notes": item.notes.text(),
                "path": filepath
            })

        self.capture_log.append("\nCapture complete.\n")

        # ---------------- Storyboard Tab ----------------

    def _build_storyboard_tab(self):
        layout = QtWidgets.QVBoxLayout(self.storyboard_tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        info = QtWidgets.QLabel("Generate a storyboard sheet from captured images.")
        layout.addWidget(info)

        # Page size
        page_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(page_layout)

        page_layout.addWidget(QtWidgets.QLabel("Page Size:"))
        self.page_width = QtWidgets.QLineEdit("1920")
        self.page_height = QtWidgets.QLineEdit("1080")
        self.page_width.setMaximumWidth(70)
        self.page_height.setMaximumWidth(70)

        page_layout.addWidget(self.page_width)
        page_layout.addWidget(QtWidgets.QLabel("x"))
        page_layout.addWidget(self.page_height)

        # Panel size
        panel_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(panel_layout)

        panel_layout.addWidget(QtWidgets.QLabel("Panel Size:"))
        self.panel_width = QtWidgets.QLineEdit("600")
        self.panel_height = QtWidgets.QLineEdit("350")
        self.panel_width.setMaximumWidth(70)
        self.panel_height.setMaximumWidth(70)

        panel_layout.addWidget(self.panel_width)
        panel_layout.addWidget(QtWidgets.QLabel("x"))
        panel_layout.addWidget(self.panel_height)

        # Generate button
        generate_btn = QtWidgets.QPushButton("Generate Storyboard Sheet")
        generate_btn.clicked.connect(self.generate_storyboard)
        layout.addWidget(generate_btn)

        # Log
        self.storyboard_log = QtWidgets.QTextEdit()
        self.storyboard_log.setReadOnly(True)
        layout.addWidget(self.storyboard_log)

        layout.addStretch()


    def generate_storyboard(self):
        """Create a storyboard sheet from captured images."""
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            self.storyboard_log.append("ERROR: Pillow (PIL) is not installed.")
            return

        if not hasattr(self, "captured_images") or not self.captured_images:
            self.storyboard_log.append("No captured images found. Capture shots first.")
            return

        page_w = int(self.page_width.text())
        page_h = int(self.page_height.text())
        panel_w = int(self.panel_width.text())
        panel_h = int(self.panel_height.text())

        # Create blank page
        page = Image.new("RGB", (page_w, page_h), color=(240, 240, 240))
        draw = ImageDraw.Draw(page)

        x = 20
        y = 20
        padding = 20

        for shot in self.captured_images:
            img = Image.open(shot["path"])
            img = img.resize((panel_w, panel_h))

            # Paste panel
            page.paste(img, (x, y))

            # Text under panel
            label = f"{shot['shot']} — {shot['notes']}"
            draw.text((x, y + panel_h + 5), label, fill=(0, 0, 0))

            # Move to next panel
            x += panel_w + padding

            # Wrap to next row
            if x + panel_w > page_w:
                x = 20
                y += panel_h + 80

        # Save final sheet
        output_path = cmds.internalVar(userTmpDir=True) + "StoryboardSheet.png"
        page.save(output_path)

        self.storyboard_log.append(f"Storyboard sheet saved to:\n{output_path}\n")



# ----------------------------------------------------------
# Launch function
# ----------------------------------------------------------

def launch_storyboard_tool():
    # Close existing instance
    for w in QtWidgets.QApplication.allWidgets():
        if isinstance(w, StoryboardToolUI):
            w.close()

    ui = StoryboardToolUI()
    ui.show()
    return ui


# For running directly from Script Editor
if __name__ == "__main__":
    launch_storyboard_tool()
=======
# Brown Jasmine
# P02 - Storyboard Shot Setup / 3D Shot Planning Tool
# Maya + PySide2

from PySide2 import QtWidgets, QtCore
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance


# ----------------------------------------------------------
# Maya main window helper
# ----------------------------------------------------------

def get_maya_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)


# ----------------------------------------------------------
# Camera item widget (row in camera list)
# ----------------------------------------------------------

class CameraItem(QtWidgets.QWidget):
    """One row: checkbox + camera name + notes field + shot label."""
    def __init__(self, cam_name, parent=None):
        super(CameraItem, self).__init__(parent)

        self.cam_name = cam_name

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)

        # Checkbox
        self.checkbox = QtWidgets.QCheckBox()
        layout.addWidget(self.checkbox)

        # Camera label
        self.label = QtWidgets.QLabel(cam_name)
        self.label.setMinimumWidth(140)
        layout.addWidget(self.label)

        # Notes field
        self.notes = QtWidgets.QLineEdit()
        self.notes.setPlaceholderText("Notes / Action / Dialogue")
        layout.addWidget(self.notes)

        # Shot number (auto-assigned)
        self.shot_label = QtWidgets.QLabel("")
        self.shot_label.setMinimumWidth(70)
        self.shot_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.shot_label)

    def is_selected(self):
        return self.checkbox.isChecked()

    def get_data(self):
        return {
            "camera": self.cam_name,
            "notes": self.notes.text(),
            "shot_number": self.shot_label.text()
        }


# ----------------------------------------------------------
# Viewport overlay functions (composition guides)
# ----------------------------------------------------------

def toggle_rule_of_thirds(state):
    """Draws 2 vertical + 2 horizontal lines."""
    if state:
        if not cmds.objExists("SB_ThirdsLines"):
            grp = cmds.createNode("transform", name="SB_ThirdsLines")
            # Vertical lines
            v1 = cmds.curve(d=1, p=[(-0.33, 0, -1), (-0.33, 0, 1)], name="SB_Thirds_V1")
            v2 = cmds.curve(d=1, p=[(0.33, 0, -1), (0.33, 0, 1)], name="SB_Thirds_V2")
            # Horizontal lines
            h1 = cmds.curve(d=1, p=[(-1, 0, -0.33), (1, 0, -0.33)], name="SB_Thirds_H1")
            h2 = cmds.curve(d=1, p=[(-1, 0, 0.33), (1, 0, 0.33)], name="SB_Thirds_H2")
            cmds.parent(v1, v2, h1, h2, grp)
            cmds.setAttr(grp + ".overrideEnabled", 1)
            cmds.setAttr(grp + ".overrideColor", 17)  # light yellow
    else:
        if cmds.objExists("SB_ThirdsLines"):
            cmds.delete("SB_ThirdsLines")


def toggle_horizon(state):
    """Single horizontal line across the frame."""
    if state:
        if not cmds.objExists("SB_Horizon"):
            h = cmds.curve(d=1, p=[(-1, 0, 0), (1, 0, 0)], name="SB_Horizon")
            cmds.setAttr(h + ".overrideEnabled", 1)
            cmds.setAttr(h + ".overrideColor", 13)  # light blue
    else:
        if cmds.objExists("SB_Horizon"):
            cmds.delete("SB_Horizon")


def toggle_crosshair(state):
    """Center crosshair."""
    if state:
        if not cmds.objExists("SB_Crosshair"):
            grp = cmds.createNode("transform", name="SB_Crosshair")
            h = cmds.curve(d=1, p=[(-0.1, 0, 0), (0.1, 0, 0)], name="SB_Crosshair_H")
            v = cmds.curve(d=1, p=[(0, 0, -0.1), (0, 0, 0.1)], name="SB_Crosshair_V")
            cmds.parent(h, v, grp)
            cmds.setAttr(grp + ".overrideEnabled", 1)
            cmds.setAttr(grp + ".overrideColor", 6)  # red
    else:
        if cmds.objExists("SB_Crosshair"):
            cmds.delete("SB_Crosshair")


def toggle_safe_frame(state):
    """Uses Maya's built-in safe frame toggle on the focused modelPanel."""
    panel = cmds.getPanel(withFocus=True)
    if panel and "modelPanel" in panel:
        cmds.modelEditor(panel, e=True, safeFrame=state)


# ----------------------------------------------------------
# Main tabbed UI
# ----------------------------------------------------------

class StoryboardToolUI(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_window()):
        super(StoryboardToolUI, self).__init__(parent)

        self.setWindowTitle("Storyboard Shot Setup Tool")
        self.setMinimumWidth(650)
        self.setMinimumHeight(400)

        self.setStyleSheet("""
            QWidget {
                background-color: #f7f7f7;
                font-size: 12px;
            }
            QLineEdit {
                background: white;
                border: 1px solid #cccccc;
                padding: 3px;
            }
            QPushButton {
                background: #e6e6e6;
                border: 1px solid #bfbfbf;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: #dcdcdc;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                margin-top: -1px;
            }
            QTabBar::tab {
                background: #e6e6e6;
                padding: 4px 10px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
            }
        """)

        self.camera_items = []

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        title = QtWidgets.QLabel("Storyboard Shot Setup — Maya")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        main_layout.addWidget(title)

        self.tabs = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tabs)

        # Cameras tab
        self.cameras_tab = QtWidgets.QWidget()
        self.guides_tab = QtWidgets.QWidget()

        self.tabs.addTab(self.cameras_tab, "Cameras")
        self.tabs.addTab(self.guides_tab, "Guides")

        self.capture_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.capture_tab, "Capture")
        self._build_capture_tab()


        self._build_cameras_tab()
        self._build_guides_tab()

    # ---------------- Cameras Tab ----------------

    def _build_cameras_tab(self):
        layout = QtWidgets.QVBoxLayout(self.cameras_tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        info = QtWidgets.QLabel("Select scene cameras, add notes, and assign shot numbers.")
        layout.addWidget(info)

        # Scroll area for camera list
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        self.scroll_layout.setContentsMargins(4, 4, 4, 4)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(btn_layout)

        refresh_btn = QtWidgets.QPushButton("Refresh Cameras")
        refresh_btn.clicked.connect(self.load_cameras)
        btn_layout.addWidget(refresh_btn)

        assign_btn = QtWidgets.QPushButton("Assign Shot Numbers")
        assign_btn.clicked.connect(self.assign_shot_numbers)
        btn_layout.addWidget(assign_btn)

        debug_btn = QtWidgets.QPushButton("Print Shot List (Debug)")
        debug_btn.clicked.connect(self.debug_print_shots)
        btn_layout.addWidget(debug_btn)

        layout.addStretch()

        # initial load
        self.load_cameras()

    def load_cameras(self):
        """Scan Maya scene for cameras and populate UI."""
        # Clear old items
        if hasattr(self, "scroll_layout"):
            for i in reversed(range(self.scroll_layout.count())):
                widget = self.scroll_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

        self.camera_items = []

        cameras = cmds.listCameras() or []

        for cam in cameras:
            item = CameraItem(cam)
            self.camera_items.append(item)
            self.scroll_layout.addWidget(item)

        self.scroll_layout.addStretch()

    def assign_shot_numbers(self):
        """Assign Shot 01, Shot 02… to selected cameras."""
        count = 1
        for item in self.camera_items:
            if item.is_selected():
                item.shot_label.setText(f"Shot {count:02d}")
                count += 1
            else:
                item.shot_label.setText("")

    def debug_print_shots(self):
        """Print selected shot data to the script editor."""
        print("\n=== SHOT LIST ===")
        for item in self.camera_items:
            if item.is_selected():
                print(item.get_data())
        print("=================\n")

    # ---------------- Guides Tab ----------------

    def _build_guides_tab(self):
        layout = QtWidgets.QVBoxLayout(self.guides_tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        info = QtWidgets.QLabel("Toggle composition guides in the active viewport.")
        layout.addWidget(info)

        self.thirds_cb = QtWidgets.QCheckBox("Rule of Thirds")
        self.thirds_cb.stateChanged.connect(
            lambda s: toggle_rule_of_thirds(s == QtCore.Qt.Checked)
        )
        layout.addWidget(self.thirds_cb)

        self.horizon_cb = QtWidgets.QCheckBox("Horizon Line")
        self.horizon_cb.stateChanged.connect(
            lambda s: toggle_horizon(s == QtCore.Qt.Checked)
        )
        layout.addWidget(self.horizon_cb)

        self.cross_cb = QtWidgets.QCheckBox("Center Crosshair")
        self.cross_cb.stateChanged.connect(
            lambda s: toggle_crosshair(s == QtCore.Qt.Checked)
        )
        layout.addWidget(self.cross_cb)

        self.safe_cb = QtWidgets.QCheckBox("Safe Frame (active panel)")
        self.safe_cb.stateChanged.connect(
            lambda s: toggle_safe_frame(s == QtCore.Qt.Checked)
        )
        layout.addWidget(self.safe_cb)

        layout.addStretch()

# ---------------- Capture Tab ----------------

def _build_capture_tab(self):
    layout = QtWidgets.QVBoxLayout(self.capture_tab)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(8)

    info = QtWidgets.QLabel("Capture still images from selected cameras.")
    layout.addWidget(info)

    # Resolution
    res_layout = QtWidgets.QHBoxLayout()
    layout.addLayout(res_layout)

    res_layout.addWidget(QtWidgets.QLabel("Resolution:"))
    self.width_field = QtWidgets.QLineEdit("1280")
    self.height_field = QtWidgets.QLineEdit("720")
    self.width_field.setMaximumWidth(60)
    self.height_field.setMaximumWidth(60)

    res_layout.addWidget(self.width_field)
    res_layout.addWidget(QtWidgets.QLabel("x"))
    res_layout.addWidget(self.height_field)

    # Frame selection
    frame_layout = QtWidgets.QHBoxLayout()
    layout.addLayout(frame_layout)

    self.frame_field = QtWidgets.QLineEdit()
    self.frame_field.setPlaceholderText("Frame (blank = current frame)")
    self.frame_field.setMaximumWidth(150)
    frame_layout.addWidget(self.frame_field)

    # Capture button
    capture_btn = QtWidgets.QPushButton("Capture Selected Shots")
    capture_btn.clicked.connect(self.capture_selected_shots)
    layout.addWidget(capture_btn)

    # Output log
    self.capture_log = QtWidgets.QTextEdit()
    self.capture_log.setReadOnly(True)
    layout.addWidget(self.capture_log)

    layout.addStretch()


def capture_selected_shots(self):
    """Capture still images from each selected camera."""
    width = int(self.width_field.text())
    height = int(self.height_field.text())

    frame_text = self.frame_field.text()
    if frame_text.strip():
        frame = int(frame_text)
    else:
        frame = cmds.currentTime(q=True)

    self.capture_log.append("Starting capture...\n")

    # Storage for Module C
    self.captured_images = []

    for item in self.camera_items:
        if not item.is_selected():
            continue

        cam = item.cam_name
        shot = item.shot_label.text()

        if not shot:
            continue

        # Build file path
        filename = f"{shot}_{cam}.png"
        filepath = cmds.internalVar(userTmpDir=True) + filename

        # Switch viewport to camera
        cmds.lookThru(cam)

        # Capture
        cmds.playblast(
            cf=filepath,
            format="image",
            viewer=False,
            showOrnaments=False,
            frame=frame,
            width=width,
            height=height,
            percent=100
        )

        self.capture_log.append(f"Captured {shot} from {cam} → {filepath}")
        self.captured_images.append({
            "shot": shot,
            "camera": cam,
            "notes": item.notes.text(),
            "path": filepath
        })

    self.capture_log.append("\nCapture complete.\n")


# ----------------------------------------------------------
# Launch function
# ----------------------------------------------------------

def launch_storyboard_tool():
    # Close existing instance
    for w in QtWidgets.QApplication.allWidgets():
        if isinstance(w, StoryboardToolUI):
            w.close()

    ui = StoryboardToolUI()
    ui.show()
    return ui


# For running directly from Script Editor
if __name__ == "__main__":
    launch_storyboard_tool()
>>>>>>> 854a0e2c8925ef13a31f9675a288f9b88e0d3576
