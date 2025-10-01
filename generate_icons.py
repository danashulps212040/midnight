#!/usr/bin/env python3
"""
Gerador de ícones PWA para Midnight PDV
Cria ícones PNG em diferentes tamanhos a partir do SVG base
"""

import os
from PIL import Image, ImageDraw
import cairosvg
from io import BytesIO

def create_icon(size):
    """Cria um ícone PNG no tamanho especificado"""
    try:
        # Converter SVG para PNG usando cairosvg
        svg_path = 'static/icons/icon-base.svg'
        png_data = cairosvg.svg2png(
            url=svg_path,
            output_width=size,
            output_height=size
        )
        
        # Salvar PNG
        png_path = f'static/icons/icon-{size}x{size}.png'
        with open(png_path, 'wb') as f:
            f.write(png_data)
        
        print(f"✅ Criado: {png_path}")
        return True
        
    except ImportError:
        print("⚠️ cairosvg não instalado. Criando ícone alternativo...")
        return create_fallback_icon(size)
    except Exception as e:
        print(f"❌ Erro ao criar ícone {size}x{size}: {e}")
        return create_fallback_icon(size)

def create_fallback_icon(size):
    """Cria um ícone com logo da Midnight baseado no SVG original"""
    try:
        # Criar imagem com background e cantos arredondados
        img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Background com gradiente suave e cantos arredondados
        corner_radius = size // 6  # Bordas arredondadas proporcionais
        
        # Criar máscara para cantos arredondados
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, size, size], radius=corner_radius, fill=255)
        
        # Background com gradiente
        bg_img = Image.new('RGBA', (size, size))
        bg_draw = ImageDraw.Draw(bg_img)
        
        for y in range(size):
            ratio = y / size * 0.05  # Gradiente muito sutil
            r = int(255 * (1 - ratio))
            g = int(255 * (1 - ratio))
            b = int(252 + 3 * ratio)
            bg_draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
        
        # Aplicar máscara ao background
        img.paste(bg_img, mask=mask)
        
        # Dimensões do logo (centralizado e proporcionalmente escalado)
        logo_scale = size / 512  # Escala baseada no tamanho do ícone
        
        # Centro da imagem
        center_x, center_y = size // 2, size // 2
        
        # Escalar e desenhar os paths do logo original
        # Primeira parte do logo (M) - convertendo as coordenadas SVG
        m_color = (155, 100, 227, 255)  # #9B64E3
        c_color = (0, 131, 229, 255)   # #0083E5
        
        # Escalar coordenadas do viewBox original (6.1344 x 6.8851) para o tamanho do ícone
        svg_width, svg_height = 6.1344, 6.8851
        scale_x = (size * 0.8) / svg_width  # 80% do ícone para dar margem
        scale_y = (size * 0.8) / svg_height
        
        # Offset para centralizar
        offset_x = center_x - (svg_width * scale_x) / 2
        offset_y = center_y - (svg_height * scale_y) / 2
        
        # Desenhar uma versão simplificada do logo M
        # Primeira parte (M path simplificado)
        m_points = [
            # Convertendo path complexo em retângulos/formas simples
            (4.7505 * scale_x + offset_x, 2.8756 * scale_y + offset_y),
            (4.1697 * scale_x + offset_x, 2.8756 * scale_y + offset_y),
            (4.1697 * scale_x + offset_x, 3.3441 * scale_y + offset_y),
            ((4.1697 - 0.5863) * scale_x + offset_x, 4.5347 * scale_y + offset_y),
            ((3.5869 - 0.5828) * scale_x + offset_x, 3.4772 * scale_y + offset_y),
            (3.0041 * scale_x + offset_x, 4.5347 * scale_y + offset_y),
            (3.0041 * scale_x + offset_x, 2.3864 * scale_y + offset_y),
            (3.5849 * scale_x + offset_x, 2.3864 * scale_y + offset_y),
        ]
        
        # Simplificar desenho do M com formas geométricas básicas
        m_width = int(1.2 * scale_x)
        m_height = int(1.6 * scale_y) 
        m_x = int(3.5 * scale_x + offset_x)
        m_y = int(2.4 * scale_y + offset_y)
        
        # Desenhar hastes do M
        stroke_width = max(1, int(0.2 * scale_x))
        draw.rectangle([m_x, m_y, m_x + stroke_width, m_y + m_height], fill=m_color)
        draw.rectangle([m_x + m_width - stroke_width, m_y, m_x + m_width, m_y + m_height], fill=m_color)
        
        # Diagonal central do M
        for i in range(m_height // 3):
            y_pos = m_y + i
            left_x = m_x + stroke_width + i // 3
            right_x = m_x + m_width - stroke_width - i // 3
            if left_x < right_x:
                draw.line([(left_x, y_pos), (right_x, y_pos)], fill=m_color, width=1)
        
        # Segunda parte do logo (círculo)
        circle_radius = int(1.5 * min(scale_x, scale_y))
        circle_x = int(3.4425 * scale_x + offset_x)
        circle_y = int(3.4425 * scale_y + offset_y)
        
        # Desenhar círculo com gradiente aproximado
        for r in range(circle_radius, 0, -1):
            alpha_ratio = (circle_radius - r) / circle_radius
            color_ratio = alpha_ratio * 0.5  # Simular gradiente radial
            
            # Interpolar entre as cores do gradiente
            final_r = int(155 + (0 - 155) * color_ratio)
            final_g = int(100 + (131 - 100) * color_ratio)
            final_b = int(227 + (229 - 227) * color_ratio)
            
            draw.ellipse([
                circle_x - r, circle_y - r,
                circle_x + r, circle_y + r
            ], fill=(final_r, final_g, final_b, 255))
        
        # Salvar como PNG
        png_path = f'static/icons/icon-{size}x{size}.png'
        img.save(png_path, 'PNG', optimize=True)
        print(f"✅ Criado (Logo Midnight): {png_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar ícone Midnight {size}x{size}: {e}")
        return False

def main():
    """Função principal para gerar todos os ícones"""
    print("🎨 Gerando ícones PWA para Midnight PDV...")
    
    # Tamanhos necessários para PWA
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    success_count = 0
    for size in sizes:
        if create_icon(size):
            success_count += 1
    
    print(f"\n✅ Geração concluída: {success_count}/{len(sizes)} ícones criados")
    
    if success_count == len(sizes):
        print("🎉 Todos os ícones foram criados com sucesso!")
    else:
        print("⚠️ Alguns ícones podem ter problemas. Verifique os logs acima.")

if __name__ == '__main__':
    main()