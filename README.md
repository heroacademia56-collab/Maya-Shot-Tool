============================================================
DIRECTOR'S STORYBOARD CONSOLE - MAYA 2024
============================================================
Author: Jasmine F. Brown
Department: ATEC, University of Texas at Dallas
Project: P02 - Storyboard Shot Setup / 3D Shot Planning Tool
GitHub URL: https://github.com/heroacademia56-collab/Maya-Shot-Tool
------------------------------------------------------------
I. OVERVIEW
------------------------------------------------------------
The Director's Storyboard Console is a Python-based Maya 
utility designed to bridge the gap between 3D layout and 
traditional storyboarding. It allows artists to organize 
scene cameras into a logical sequence, add dialogue/notes, 
and export a visual storyboard sheet directly within Maya.

------------------------------------------------------------
II. KEY FEATURES
------------------------------------------------------------
* Non-Linear Expansion: Add multiple storyboard "beats" 
  to a single camera using the (+) expansion system.
* Live Viewport Sync: Use the (👁) icon to instantly snap 
  the Maya viewport to the selected camera.
* Selection Sync: Clicking a camera name in the UI 
  automatically selects that object in the Maya scene.
* Visual Review: Generates a 2-column image grid with 
  active scene captures and notes for final review.
* Composition Tools: Built-in toggles for Rule of Thirds 
  and Safe Frames to assist in framing.

------------------------------------------------------------
III. INSTALLATION & USAGE
------------------------------------------------------------
1. Open Maya 2024.
2. Open the Script Editor (Windows > General Editors > 
   Script Editor).
3. Create a new Python tab.
4. Paste the source code from 'storyboard_console.py'.
5. Execute the script (Ctrl+Enter).
6. Use the "Sequence Builder" tab to refresh cameras and 
   assign shot numbers.
7. Use the "Final Review" tab to capture frames and 
   generate the visual storyboard sheet.

------------------------------------------------------------
IV. TECHNICAL SPECS
------------------------------------------------------------
* Compatibility: Maya 2024 (Primary), Maya 2023.
* Language: Python 3.10
* Libraries: PySide6 (with PySide2 fallback logic).
============================================================
