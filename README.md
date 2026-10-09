Note: This is my first actually deep project, so inside the code, things like function names, variables, and even comments are in my mother language, sorry about that.

A real-time shader visualizer made in python.

This project renders glsl shaders in real time in the screen. It utilizes Dxcam to capture the screen and pass it to the renderer, which renders the shader using ModernGl. It also counts with a GUI made with PySide6.

Files:
- main.py: This is where the dxcam and screen-capturing logic lives. It displays a borderless window that fits the whole screen, ignores mouse inputs and is always on top. The window uses pygame for now. It uses the Dxcam camera system to get the texture "behind" the window. main.py is also in charge of handling the uniform data sent from editor.py and actively change the shader's parameters based off of that. This is done by sending data to a socket using the socket library and then listening to it in renderer.py

- editor.py: The GUI and PySide6 logic is here. It handles the front-end side of the project and is the one who sends data such as uniforms values or selected shader over to the other scripts. For instance, it reads the shader folder to display available shaders, and it also uses the socket library to send uniform impormation over to main.py.

- renderer.py: Here lies Moderngl. This script contains the logic behind actually displaying the shader, using draw passes to ensure organisation and efficiency. The downscaling logic is also here.

- ventana_nativa.py: This file is the one who communicates with windows through ctypes. It gives main.py access to the window data itself and handles windows features. For instance, this is what's used to ensure the window is always on top and ignores the mouse.

- config.py: This file simply contains file paths, constants and variables that several other scripts can use.

This program counts with a folder to store shader effects.

Shader notes:
 - All of them must use Dxcam's native color format: BGRA
 - Uniforms must have explicitly declared minimum, maximum and default values through a comment. Example: uniform float my_uniform; // min=1.0 max=2.0 default=1.5
 - Uniforms like u_screen_texture, u_time and similar will be automatically skipped bin the reading process.

Note: The shaders are made with AI for now due to my lack of knowledge in glsl. This is not definitive and they will be rewritten in the future.

AI usage: Used for doubts and learning. No copy pasting was involved outside shaders and I prioritize my learning experience over having AI making stuff for me.

License: This project is openly shared for its visualization and learning as a personal project. Currently, it does not count with a free use license, so all rights are reserved. Code copy, redistribution and commercial exploitation are no allowed. If the project grows, it will be evaluated to release it for free under a formal license.
