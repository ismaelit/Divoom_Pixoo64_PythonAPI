#!/usr/bin/env python3
"""
DIVOOM PIXOO 64x64 Controller
Solução melhorada para controlar o PIXOO via API WiFi
"""

import requests
import json
import time
import base64
import math
import threading
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import qrcode

class PixooController:
    def __init__(self, ip_address):
        self.ip = ip_address
        self.base_url = f"http://{ip_address}:80/post"
        self.current_fps = 20  # Default FPS setting
        
    def send_command(self, command_data):
        """Envia um comando para o PIXOO"""
        try:
            response = requests.post(self.base_url, json=command_data, timeout=5)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Erro ao enviar comando: {e}")
            return None
    
    def reset_device(self):
        """Reset do dispositivo e preparação"""
        commands = [
            {"Command": "Draw/ResetHttpGifId"},
            {"Command": "Draw/ClearHttpText"},
            {"Command": "Channel/SetIndex", "SelectIndex": 4}
        ]
        
        for cmd in commands:
            result = self.send_command(cmd)
            print(f"Comando {cmd['Command']}: {'OK' if result else 'ERRO'}")
            time.sleep(0.5)
    
    def create_black_rgb_base64(self):
        """Cria dados RGB 64x64 preto limpo (não GIF!)"""
        # PIXOO usa dados RGB brutos, não GIF!
        # 64x64 pixels = 4096 pixels
        # Cada pixel = 3 bytes (R,G,B)
        # Total = 12288 bytes
        
        rgb_data = bytearray(64 * 64 * 3)  # Tudo zero = preto
        return base64.b64encode(rgb_data).decode('utf-8')
    
    def send_clean_black_gif(self):
        """Envia dados RGB pretos para preparar a tela"""
        black_rgb_data = self.create_black_rgb_base64()
        
        gif_command = {
            "Command": "Draw/SendHttpGif",
            "PicNum": 1,
            "PicWidth": 64,
            "PicOffset": 0,
            "PicID": 0,
            "PicSpeed": 1000,
            "PicData": black_rgb_data
        }
        
        result = self.send_command(gif_command)
        print(f"GIF preto enviado: {'OK' if result else 'ERRO'}")
        time.sleep(1)
        
        return result is not None
    
    def send_text(self, text, x=0, y=20, color="#FFFFFF", font_size=8, align=2, speed=70):
        """Envia texto para o display"""
        text_command = {
            "Command": "Draw/SendHttpText",
            "TextId": 1,
            "x": x,
            "y": y,
            "dir": 0,
            "font": font_size,
            "TextWidth": 64,
            "speed": speed,
            "TextString": text,
            "color": color,
            "align": align
        }
        
        result = self.send_command(text_command)
        print(f"Texto '{text}' enviado: {'OK' if result else 'ERRO'}")
        return result is not None
    
    def send_clock(self):
        """Envia relógio com fonte personalizada"""
        current_time = datetime.now().strftime("%H:%M:%S")
        return self.send_text(current_time, y=15, font_size=6, color="#00FF00")
    
    def send_marquee(self, text, color="#FFFF00"):
        """Envia texto em marquee - PIXOO ativa automaticamente quando texto é longo"""
        # O PIXOO ativa marquee automaticamente quando o texto é maior que a tela
        return self.send_text(text, x=0, y=25, color=color, font_size=4, speed=100)
    
    def create_pixel_matrix(self, pattern):
        """Cria uma matriz de pixels customizada usando dados RGB brutos"""
        rgb_data = bytearray(64 * 64 * 3)
        
        # Aplicar padrão diretamente nos dados RGB
        for y in range(64):
            for x in range(64):
                index = (y * 64 + x) * 3  # Posição no array RGB
                
                if pattern == "gradient":
                    rgb_data[index] = min(255, x * 4)      # R
                    rgb_data[index + 1] = min(255, y * 4)  # G  
                    rgb_data[index + 2] = 128              # B
                elif pattern == "checkerboard":
                    if (x + y) % 2 == 0:
                        rgb_data[index] = 255     # R
                        rgb_data[index + 1] = 255 # G
                        rgb_data[index + 2] = 255 # B
                    # Else fica preto (0,0,0)
                elif pattern == "border":
                    if x == 0 or x == 63 or y == 0 or y == 63:
                        rgb_data[index] = 0       # R
                        rgb_data[index + 1] = 255 # G
                        rgb_data[index + 2] = 255 # B
                elif pattern == "test":
                    # Padrão de teste simples
                    rgb_data[index] = x * 4 if x < 64 else 255      # R
                    rgb_data[index + 1] = y * 4 if y < 64 else 255  # G
                    rgb_data[index + 2] = 64                        # B
        
        return base64.b64encode(rgb_data).decode('utf-8')
    
    def send_pixel_matrix(self, pattern="gradient"):
        """Envia matriz de pixels customizada"""
        pixel_data = self.create_pixel_matrix(pattern)
        
        gif_command = {
            "Command": "Draw/SendHttpGif",
            "PicNum": 1,
            "PicWidth": 64,
            "PicOffset": 0,
            "PicID": 0,
            "PicSpeed": 1000,
            "PicData": pixel_data
        }
        
        result = self.send_command(gif_command)
        print(f"Matriz de pixels ({pattern}) enviada: {'OK' if result else 'ERRO'}")
        return result is not None
    
    def clear_display(self):
        """Limpa completamente o display"""
        commands = [
            {"Command": "Draw/ClearHttpText"},
            {"Command": "Draw/ResetHttpGifId"}
        ]
        
        for cmd in commands:
            self.send_command(cmd)
            time.sleep(0.5)
        
        # Enviar tela preta limpa
        self.send_clean_black_gif()
    
    def create_animation_frame(self, frame_num, total_frames, animation_type="spinner"):
        """Cria um frame de animação usando dados RGB brutos"""
        rgb_data = bytearray(64 * 64 * 3)
        
        if animation_type == "spinner":
            # Círculo giratório
            center_x, center_y = 32, 32
            radius = 20
            angle = (frame_num / total_frames) * 2 * math.pi
            
            for y in range(64):
                for x in range(64):
                    index = (y * 64 + x) * 3
                    
                    # Distância do centro
                    dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    
                    if dist <= radius + 2 and dist >= radius - 2:
                        # Anel base azul
                        rgb_data[index + 2] = 100  # B
                    
                    # Ponto giratório
                    point_x = center_x + int(radius * math.cos(angle))
                    point_y = center_y + int(radius * math.sin(angle))
                    
                    if abs(x - point_x) <= 2 and abs(y - point_y) <= 2:
                        rgb_data[index] = 255      # R
                        rgb_data[index + 1] = 100  # G
                        rgb_data[index + 2] = 0    # B
        
        elif animation_type == "wave":
            # Onda senoidal
            wave_offset = (frame_num / total_frames) * 4 * math.pi
            
            for y in range(64):
                for x in range(64):
                    index = (y * 64 + x) * 3
                    
                    # Calcular altura da onda
                    wave_y = 32 + int(15 * math.sin((x / 64.0) * 2 * math.pi + wave_offset))
                    
                    if abs(y - wave_y) <= 1:
                        intensity = 255 - abs(y - wave_y) * 100
                        rgb_data[index] = 0           # R
                        rgb_data[index + 1] = intensity  # G
                        rgb_data[index + 2] = 255     # B
        
        elif animation_type == "plasma":
            # Efeito plasma colorido
            time_offset = (frame_num / total_frames) * 2 * math.pi
            
            for y in range(64):
                for x in range(64):
                    index = (y * 64 + x) * 3
                    
                    # Múltiplas ondas senoidais para efeito plasma
                    value1 = math.sin((x / 16.0) + time_offset)
                    value2 = math.sin((y / 8.0) + time_offset * 1.5)
                    value3 = math.sin((x + y) / 16.0 + time_offset * 2)
                    
                    plasma = (value1 + value2 + value3) / 3.0
                    
                    # Converter para RGB
                    rgb_data[index] = int(127 + 127 * math.sin(plasma * math.pi))      # R
                    rgb_data[index + 1] = int(127 + 127 * math.sin(plasma * math.pi + 2))  # G
                    rgb_data[index + 2] = int(127 + 127 * math.sin(plasma * math.pi + 4))  # B
        
        elif animation_type == "bouncing_ball":
            # Bola quicando
            ball_x = int(32 + 20 * math.sin((frame_num / total_frames) * 2 * math.pi))
            ball_y = int(32 + abs(20 * math.sin((frame_num / total_frames) * 4 * math.pi)))
            ball_radius = 4
            
            for y in range(64):
                for x in range(64):
                    index = (y * 64 + x) * 3
                    
                    # Bola
                    dist = math.sqrt((x - ball_x)**2 + (y - ball_y)**2)
                    if dist <= ball_radius:
                        intensity = max(0, int(255 * (1 - dist / ball_radius)))
                        rgb_data[index] = intensity     # R
                        rgb_data[index + 1] = intensity # G
                        rgb_data[index + 2] = 0         # B
        
        return base64.b64encode(rgb_data).decode('utf-8')
    
    def send_animation(self, animation_type="spinner", total_frames=30, fps=None):
        """
        Sends animation with dynamic frames
        
        Args:
            animation_type: "spinner", "wave", "plasma", "bouncing_ball"
            total_frames: total number of frames (max 40)
            fps: frames per second (uses current_fps if None)
        """
        if fps is None:
            fps = self.current_fps
            
        if total_frames > 40:
            print("⚠️  Limiting to 40 frames (PIXOO limit)")
            total_frames = 40
        
        # Reset and preparation
        self.reset_device()
        
        print(f"🎬 Sending '{animation_type}' animation with {total_frames} frames @ {fps}fps")
        
        # Gerar e enviar frames
        for frame in range(total_frames):
            frame_data = self.create_animation_frame(frame, total_frames, animation_type)
            
            gif_command = {
                "Command": "Draw/SendHttpGif",
                "PicNum": total_frames,  # Total de frames
                "PicWidth": 64,
                "PicOffset": frame,      # Frame atual
                "PicID": 1,              # ID da animação
                "PicSpeed": max(1, int(1000 / fps)),  # Velocidade em ms
                "PicData": frame_data
            }
            
            result = self.send_command(gif_command)
            if result:
                print(f"✅ Frame {frame + 1}/{total_frames} enviado")
            else:
                print(f"❌ Erro no frame {frame + 1}")
                return False
            
            # Pequena pausa entre frames para não sobrecarregar
            time.sleep(0.1)
        
        print(f"🚀 Animation '{animation_type}' complete!")
        return True
    
    def set_fps(self, new_fps):
        """Set the global FPS setting"""
        if 1 <= new_fps <= 30:
            self.current_fps = new_fps
            print(f"✅ FPS set to {new_fps}")
            return True
        else:
            print("❌ FPS must be between 1 and 30")
            return False
    
    def send_qr_code(self, data, error_correction=qrcode.constants.ERROR_CORRECT_L):
        """
        Exibe um QR Code no display 64x64
        
        Args:
            data: String com os dados para o QR Code
            error_correction: Nível de correção de erro (L, M, Q, H)
        """
        try:
            print(f"🔄 Gerando QR Code para: '{data}'")
            
            # Reset do dispositivo antes de enviar QR code
            print("🔄 Resetando dispositivo...")
            self.reset_device()
            time.sleep(0.5)  # Pausa para garantir reset completo
            
            # Criar QR Code OTIMIZADO para máximo aproveitamento
            # - ERROR_CORRECT_L: Correção mínima (7% de dados redundantes)
            # - border=0: SEM quiet zone (bordas de segurança)
            # - Versão automática para dados mínimos
            qr = qrcode.QRCode(
                version=None,  # Auto-detectar versão mínima
                error_correction=qrcode.constants.ERROR_CORRECT_L,  # Correção mínima
                box_size=1,    # 1 pixel por módulo (será escalado depois)
                border=0,      # ZERO border - sem quiet zone
            )
            
            # Adicionar os dados
            qr.add_data(data)
            
            # Fazer o QR Code com versão mínima possível
            try:
                qr.make(fit=True)  # Auto-ajustar para menor versão possível
                print(f"📏 QR Code versão: {qr.version}")
                print(f"📐 Módulos: {qr.modules_count}x{qr.modules_count}")
                print(f"🔥 SEM bordas/quiet zone - máximo aproveitamento!")
                print(f"⚡ Correção de erro mínima (L) - menos módulos")
                
            except qrcode.exceptions.DataOverflowError:
                print("⚠️  AVISO: Dados muito complexos para QR Code mínimo!")
                return False
            
            # Obter matriz QR sem bordas
            qr_matrix = qr.get_matrix()
            qr_modules = len(qr_matrix)  # Número real de módulos N x N
            
            print(f"🗂️  Módulos QR (sem bordas): {qr_modules}x{qr_modules}")
            
            # MÁXIMO APROVEITAMENTO: Calcular maior escala inteira possível
            if qr_modules > 64:
                print(f"❌ QR Code muito grande: {qr_modules}x{qr_modules} módulos")
                print(f"❌ Display suporta máximo: 64x64 módulos")
                print(f"❌ Reduza a quantidade de dados")
                return False
            
            # Calcular escala PERFEITA para máximo aproveitamento
            scale_factor = 64 // qr_modules  # Maior fator inteiro possível
            final_size = qr_modules * scale_factor  # Tamanho final em pixels
            
            # Calcular centralização perfeita
            offset = (64 - final_size) // 2  # Offset para centralizar
            
            print(f"🎯 ESCALA PERFEITA: {scale_factor}x{scale_factor} pixels por módulo")
            print(f"📏 QR final: {final_size}x{final_size} pixels")
            print(f"📍 Centralizado com offset: {offset} pixels")
            print(f"📊 Aproveitamento: {(final_size*final_size)/(64*64)*100:.1f}% da tela")
            
            # Exemplos de aproveitamento
            if scale_factor == 1:
                print(f"💯 PERFEITO: Cada módulo = 1 pixel (máxima resolução)")
            elif scale_factor >= 3:
                print(f"🔥 EXCELENTE: Módulos {scale_factor}x{scale_factor} - super visível!")
            elif scale_factor >= 2:
                print(f"✅ ÓTIMO: Módulos {scale_factor}x{scale_factor} - bem legível")
            
            # Informações técnicas
            print(f"📋 Exemplo: QR {qr_modules}x{qr_modules} → {final_size}x{final_size} (escala {scale_factor})")
            
            # Criar canvas 64x64 RGB com fundo PRETO puro
            canvas = Image.new('RGB', (64, 64), (0, 0, 0))
            
            # Desenhar QR Code com PIXELS QUADRADOS PERFEITOS
            print("🎨 Renderizando QR Code com pixels quadrados perfeitos...")
            
            for module_row in range(qr_modules):
                for module_col in range(qr_modules):
                    # Determinar se módulo está ativo (True = dados, False = vazio)
                    is_data_module = qr_matrix[module_row][module_col]
                    
                    # MONOCROMÁTICO: BRANCO para dados, PRETO para vazio
                    pixel_color = (255, 255, 255) if is_data_module else (0, 0, 0)
                    
                    # Calcular posição do módulo no canvas (centralizado)
                    start_x = offset + (module_col * scale_factor)
                    start_y = offset + (module_row * scale_factor)
                    
                    # Desenhar módulo como bloco QUADRADO de pixels
                    for pixel_y in range(scale_factor):
                        for pixel_x in range(scale_factor):
                            canvas_x = start_x + pixel_x
                            canvas_y = start_y + pixel_y
                            
                            # Verificar se está dentro dos limites (deve sempre estar)
                            if 0 <= canvas_x < 64 and 0 <= canvas_y < 64:
                                canvas.putpixel((canvas_x, canvas_y), pixel_color)
            
            print(f"✅ QR Code renderizado: {final_size}x{final_size} pixels centralizados")
            
            # Salvar apenas um arquivo atual (sobrescrever anterior)
            import os
            current_dir = os.getcwd()
            debug_filename = os.path.join(current_dir, "qr_current.bmp")
            png_filename = os.path.join(current_dir, "qr_current.png")
            
            # Remover arquivo anterior se existir
            for old_file in [debug_filename, png_filename]:
                if os.path.exists(old_file):
                    os.remove(old_file)
            
            # Salvar BMP (formato sem transparência, ideal para LED matrix)
            canvas.save(debug_filename, 'BMP')
            print(f"💾 QR Code salvo como: '{debug_filename}'")
            
            # Salvar PNG sem transparência (fundo sólido preto)
            png_canvas = Image.new('RGB', (64, 64), (0, 0, 0))  # Garantir fundo preto sólido
            png_canvas.paste(canvas, (0, 0))
            png_canvas.save(png_filename, 'PNG')
            print(f"💾 QR Code salvo como: '{png_filename}'")
            
            # Converter canvas para dados RGB brutos
            print("🔄 Convertendo canvas para dados RGB...")
            rgb_data = bytearray(64 * 64 * 3)
            
            for y in range(64):
                for x in range(64):
                    pixel = canvas.getpixel((x, y))
                    index = (y * 64 + x) * 3
                    rgb_data[index] = pixel[0]      # R
                    rgb_data[index + 1] = pixel[1]  # G  
                    rgb_data[index + 2] = pixel[2]  # B
            
            # Análise final de aproveitamento e qualidade
            print("📊 ANÁLISE FINAL:")
            
            # Contar pixels de dados vs pixels vazios
            data_pixels = 0
            empty_pixels = 0
            
            for i in range(0, len(rgb_data), 3):
                r, g, b = rgb_data[i], rgb_data[i+1], rgb_data[i+2]
                if r == 255 and g == 255 and b == 255:  # Pixels brancos (dados)
                    data_pixels += 1
                else:  # Pixels pretos (vazio/fundo)
                    empty_pixels += 1
            
            total_display_pixels = 64 * 64
            used_pixels = final_size * final_size
            unused_pixels = total_display_pixels - used_pixels
            
            print(f"🎯 Área QR utilizada: {used_pixels}/{total_display_pixels} pixels ({used_pixels/total_display_pixels*100:.1f}%)")
            print(f"📈 Dados QR: {data_pixels} pixels brancos")
            print(f"⬛ Fundo QR: {empty_pixels - unused_pixels} pixels pretos") 
            print(f"🔲 Área não usada: {unused_pixels} pixels ({unused_pixels/total_display_pixels*100:.1f}%)")
            
            # Qualidade do QR Code
            if data_pixels > 0 and empty_pixels > 0:
                print("✅ QR Code MONOCROMÁTICO - pronto para display 64x64!")
                print(f"💯 MÁXIMO APROVEITAMENTO ALCANÇADO!")
            else:
                print("⚠️  AVISO: Problema na geração do QR code!")
            
            # Enviar para o display
            print("📡 Enviando para o PIXOO...")
            qr_data = base64.b64encode(rgb_data).decode('utf-8')
            print(f"📊 Tamanho dos dados base64: {len(qr_data)} chars")
            
            gif_command = {
                "Command": "Draw/SendHttpGif",
                "PicNum": 1,
                "PicWidth": 64,
                "PicOffset": 0,
                "PicID": 0,
                "PicSpeed": 1000,
                "PicData": qr_data
            }
            
            result = self.send_command(gif_command)
            if result:
                print(f"✅ QR Code enviado com sucesso para o PIXOO!")
                print(f"📁 Arquivos salvos: qr_current.bmp e qr_current.png")
                return True
            else:
                print("❌ Erro ao enviar QR Code para o dispositivo")
                print(f"📁 Mas você pode verificar as imagens salvas: qr_current.bmp")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao gerar QR Code: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    # Your PIXOO IP address - change this to match your device
    PIXOO_IP = "10.0.2.214"
    
    pixoo = PixooController(PIXOO_IP)
    
    print("=== DIVOOM PIXOO 64x64 Controller ===")
    print(f"Connecting to: {PIXOO_IP}")
    print(f"Current FPS: {pixoo.current_fps}")
    
    while True:
        print(f"\n📺 PIXOO Controller (FPS: {pixoo.current_fps})")
        print("1 - Reset and prepare device")
        print("2 - Send simple text")
        print("3 - Show clock")
        print("4 - Marquee text")
        print("5 - Pixel matrix (gradient)")
        print("6 - Pixel matrix (checkerboard)")  
        print("7 - Pixel matrix (border)")
        print("8 - Pixel matrix (test)")
        print("9 - Clear display")
        print("A - Animation: Spinner")
        print("B - Animation: Wave")
        print("C - Animation: Plasma")
        print("D - Animation: Bouncing Ball")
        print("Q - QR Code")
        print("F - Set FPS (current: {})".format(pixoo.current_fps))
        print("0 - Exit")
        
        choice = input("\nChoose an option: ").strip()
        
        if choice == "1":
            print("Resetting device...")
            pixoo.reset_device()
            pixoo.send_clean_black_gif()
            
        elif choice == "2":
            text = input("Enter text: ")
            pixoo.reset_device()
            pixoo.send_clean_black_gif()
            pixoo.send_text(text)
            
        elif choice == "3":
            pixoo.reset_device()
            pixoo.send_clean_black_gif()
            pixoo.send_clock()
            
        elif choice == "4":
            text = input("Enter marquee text: ")
            pixoo.reset_device()
            pixoo.send_clean_black_gif()
            pixoo.send_marquee(text)
            
        elif choice == "5":
            pixoo.reset_device()
            pixoo.send_pixel_matrix("gradient")
            
        elif choice == "6":
            pixoo.reset_device()
            pixoo.send_pixel_matrix("checkerboard")
            
        elif choice == "7":
            pixoo.reset_device()
            pixoo.send_pixel_matrix("border")
            
        elif choice == "8":
            pixoo.reset_device()
            pixoo.send_pixel_matrix("test")
            
        elif choice == "9":
            pixoo.clear_display()
            
        elif choice.upper() == "A":
            pixoo.send_animation("spinner", total_frames=30)
            
        elif choice.upper() == "B":
            pixoo.send_animation("wave", total_frames=25)
            
        elif choice.upper() == "C":
            pixoo.send_animation("plasma", total_frames=35)
            
        elif choice.upper() == "D":
            pixoo.send_animation("bouncing_ball", total_frames=20)
            
        elif choice.upper() == "Q":
            data = input("Enter data for QR Code (URL, text, etc.): ")
            pixoo.send_qr_code(data)
            
        elif choice.upper() == "F":
            try:
                new_fps = int(input(f"Enter new FPS (1-30, current: {pixoo.current_fps}): "))
                pixoo.set_fps(new_fps)
            except ValueError:
                print("❌ Please enter a valid number")
            
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option!")

if __name__ == "__main__":
    main()