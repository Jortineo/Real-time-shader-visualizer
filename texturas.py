import moderngl
from PIL import Image, ImageDraw, ImageFont

def crear_atlas_font(ctx, ruta_ttf, caracteres, alto_celda=32, aspecto = 1):
    ancho_celda = int(alto_celda * aspecto)
    fuente = ImageFont.truetype(ruta_ttf, int(alto_celda * 0.8))
    atlas = Image.new("L", (ancho_celda * len(caracteres), alto_celda), 0) #grises y fondo negro
    dibujo = ImageDraw.Draw(atlas)

    for i,c in enumerate(caracteres):
        caja = dibujo.textbbox((0,0), c, font=fuente) #izq, arriba, dch, abajo
        w, h = caja[2] - caja[0], caja[3] - caja[1]
        x = i * ancho_celda + (ancho_celda - w) // 2 - caja[0] #centrado en su celda
        y = (alto_celda - h) // 2 - caja[1]
        dibujo.text((x, y), c, font=fuente, fill = 255)

    atlas = atlas.transpose(Image.Transpose.FLIP_TOP_BOTTOM) #Pil cuenta al revés que opengl
    tex = ctx.texture(atlas.size, 1, atlas.tobytes())
    tex.filter = (moderngl.LINEAR, moderngl.LINEAR)

    return tex