Updates
10/06/26
• Improved the draw pass system and created new folder to store shaders that must be used, like simple vertex shaders and FSR.
• Translated my GitHub page from Spanish to English.
10/05/26
• Added a stop button to halt the process (ironically, it was still missing).
• Added GitHub Issues to track future ideas that were previously saved in another software.
10/04/26
• Improved the UI by adding a PySide6 styleSheet. Updated the project colors and font.
• Fixed central photo widget scaling so it now adjusts to the image size without distorting it.
• Set a maximum size for widgets like the shader list and shader properties list.
10/03/26
• Added a preview feature using an image that displays the selected shader effect.
• Sliders are now functional in both the preview and the final effect. (Note: To update the final effect, sliders must currently be adjusted while the process is running, not before).
09/27/26
• Implemented a 2-pass draw system for shaders; the second pass handles downsampling to boost performance.
• Switched back to DXCam's synchronous system to improve CPU performance.
• Added FSR (FidelityFX Super Resolution) to improve upscaling quality. This still requires further work and a better implementation.
Version 0.1 (Release)
• Fixed a high CPU usage issue caused by converting the screen color from BGRA to RGBA. The conversion has been removed, as BGRA is DXCam's native format.
• Improved CPU performance by switching from MSS to DXCam.
• Created the GUI.

