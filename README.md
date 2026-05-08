# Maya Shot Tool  
A Maya Python + PySide2 utility for 3D shot planning, camera-based storyboarding, and viewport capture.

## 🎬 Overview
The Maya Shot Tool is designed for layout artists, previs artists, and animators who need a fast, clean way to organize shots directly inside Maya. Instead of switching between multiple programs to plan shots or assemble boards, this tool lets you:

- Select scene cameras and assign shot numbers  
- Add notes for action, dialogue, or timing  
- Enable composition guides (rule of thirds, horizon line, crosshair, safe frame)  
- Capture still images from each selected camera  
- Prepare assets for storyboard/contact sheet generation  

This tool focuses on **Maya-native shot planning**, making it ideal for animation students and production workflows where camera staging and previs happen inside a 3D scene.

---

## 🧩 Features

### **📷 Camera Management**
- Auto-detect all cameras in the Maya scene  
- Select which cameras become storyboard shots  
- Add per-shot notes  
- Auto-generate shot numbers (Shot 01, Shot 02, etc.)

### **🎨 Composition Guides**
- Rule of thirds overlay  
- Horizon line  
- Center crosshair  
- Safe frame toggle  
- Non-destructive, viewport-only helpers

### **🖼 Viewport Capture**
- Capture still images from selected cameras  
- Choose resolution (default 1280×720)  
- Capture current frame or a specific frame  
- Saves images to Maya’s temp directory  
- Stores metadata for later storyboard assembly

---

## 🛠 Requirements
- Autodesk Maya
