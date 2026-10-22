Updates

10/22/26

• Added a toon shader which is actually coded by me (Needs a bit more work)

• Added a color bleeding effect to the general post-processing shader.

10/17/26

• Added the json file where values now get stored and read.

• Added a tools folder where i made a script that reads the shaders folder and rewrites the entire json file to fit shaders, uniforms, etc. This is for convenience for later when i change shaders and add more of them.

• Fixed anti-aliasing and FSR. They used to receive the downscaled resolution instead of the full one, basically making them useless (that's why it didn't look like they did much before). It now looks 10x better. Rookie mistake.

10/15/26

• Expanded the performance Window. It now shows VRAM, gpu usage and gpu temperature.

• Tried making it so that the execute button also executes the shader with the correct uniform values. Came to the realisation that the best architecture would be to use a JSON file to save uniform configurations, which would also allow for saving configurations.

10/12/26

• Began implementing the performance window to monitor the resources used by the program. It still needs a lot of work but is funcional.

10/11/26

• Added functionalities to the menu, now you can also change the central photo to another one inside the images folder.

• Now the front end is in English

• Overhauled the Ui architecture. Renamed mani.py to capturer.py and made an actual main.py that executes the app. Now the UI is divided into several files inside the UI folder.

10/09/26

• Added a simple Anti-aliasing right after upscaling. (Note: it is made with Ai for now but will be rewritten by me)

• Added the option to change the resolution ratio in the options menu. (It kind of works but needs a lot of improvement)

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

