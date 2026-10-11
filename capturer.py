import ctypes


import os
import sys
import pygame
import dxcam
import time
import numpy as np
import socket

import sys
from config import ruta_shader as ruta_shader_por_defecto, FPS, PUERTO_UNIFORMS

ruta_shader = sys.argv[1] if len(sys.argv) > 1 else ruta_shader_por_defecto

from ventana_nativa import VentanaNativa
from renderer import Renderizador

def main():
    os.environ['SDL_VIDEO_WINDOW_POS'] = "-5000,-5000" 
    pygame.init()

    camera = dxcam.create(
    output_idx=0,
    output_color="BGRA",
    processor_backend="numpy",
    max_buffer_len=2,
    )

    camera.start(
        target_fps=60,
        video_mode=True
    )

    info_pantalla = pygame.display.Info()
    ancho = info_pantalla.current_w
    alto = info_pantalla.current_h

    pygame.display.set_mode(
        (ancho, alto),
        pygame.OPENGL | pygame.DOUBLEBUF | pygame.NOFRAME,
        vsync=1
    )

    hwnd = pygame.display.get_wm_info()['window']
    win_nativa = VentanaNativa(hwnd)

    win_nativa.establecer_click_through(True)

    pygame.display.set_window_position((0, 0))
    win_nativa.aplicar_frente(True)

    sock_uniforms = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Creo el socket para mandar los uniforms
    sock_uniforms.bind(("127.0.0.1", PUERTO_UNIFORMS))
    print(f"Escuchando uniforms en el puerto {PUERTO_UNIFORMS}")
    sock_uniforms.setblocking(False) #asi no espera a que lo haya siempre

    render = Renderizador(ruta_shader, ancho, alto, factor_escala=2, editor_ui=None)

    reloj = pygame.time.Clock()
    ejecutando = True

    estadisticas = {
        "captura": 0.0,
        "render": 0.0,
        "frames": 0,
    }

    ultimo_informe = time.perf_counter()

    while ejecutando:
        pygame.event.pump()

        for evento in pygame.event.get(): #Inputs
            if evento.type == pygame.QUIT:
                ejecutando = False
                continue

        inicio_captura = time.perf_counter()
        frame_completo = camera.get_latest_frame()

        if frame_completo is not None:
            captura = frame_completo
        else:
            captura = np.zeros((alto, ancho, 4), dtype=np.uint8)

        fin_captura = time.perf_counter()

        while True: #While para coger los datos
            try:
                datos, _ = sock_uniforms.recvfrom(1024) #Cojo el socket
            except BlockingIOError:
                break

            nombre, tipo, valor_texto = datos.decode("utf-8").split(":") #Cojo los valores
            valor = int(valor_texto) if tipo == "int" else float(valor_texto)
            print(f"Recibido: {nombre} = {valor} | ¿está en el programa? {nombre in render.pasada_efecto.prog}")

            if nombre == "factor_escala": #Paso también el factor
                render.factor_escala = valor
                render.ancho_bajo = max(1, int(render.ancho // render.factor_escala))
                render.alto_bajo = max(1, int(render.alto // render.factor_escala))

            if nombre in render.pasada_efecto.prog: #nombre
                render.pasada_efecto.prog[nombre] = valor

        inicio_render = time.perf_counter()

        render.renderizar(
            captura,
            pygame.time.get_ticks() / 1000.0
        )
        fin_render = time.perf_counter()

        pygame.display.flip()

        estadisticas["captura"] += fin_captura - inicio_captura
        estadisticas["render"] += fin_render - inicio_render
        estadisticas["frames"] += 1

        ahora = time.perf_counter()

        if ahora - ultimo_informe >= 1.0:
            n = estadisticas["frames"]

            if n > 0:
                print(
                    f"Captura: {estadisticas['captura'] / n * 1000:.2f} ms | "
                    f"Render: {estadisticas['render'] / n * 1000:.2f} ms | "
                    f"Frames: {n}"
                )

            estadisticas = {
                "captura": 0.0,
                "render": 0.0,
                "frames": 0,
            }

            ultimo_informe = ahora
            
        reloj.tick(FPS)
        #time.sleep(0.001) #Para asegurarme de esperar

    try:
        camera.stop()
        del camera # Cierro completamente
    except Exception:
        pass
    pygame.quit()

    os._exit(0) #Cierro del todo
    sys.exit()

if __name__ == "__main__":
    main()