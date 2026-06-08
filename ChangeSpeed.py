import ctypes
from ctypes import wintypes
import time
from pymem import Pymem
from win32api import OpenProcess, CloseHandle
from win32con import PROCESS_VM_READ, PROCESS_VM_OPERATION, PROCESS_VM_WRITE


try:
    Game = Pymem("RobloxPlayerBeta.exe")
    pid = Game.process_id
    base_exe = Game.base_address
    print(f"[+] Proceso detectado. PID: {pid} | Base Address: {hex(base_exe)}")
except Exception:
    print("[-] Error: El proceso 'RobloxPlayerBeta.exe' no fue detectado.")
    print("[*] Asegúrate de abrir primero el juego y luego ejecutar este script.")
    exit()



STATIC_VISUAL_ENGINE = 0x801dfb0
OFFSET_FAKE_DATAMODEL = 0xa90
OFFSET_REAL_DATAMODEL = 0x1d0
OFFSET_WORKSPACE = 0x178  
OFFSET_CURRENT_CAMERA = 0x4b0  
OFFSET_CAMERA_SUBJECT = 0xe8   


OFFSET_HUMANOID_WALKSPEED = 0x1dc 
OFFSET_HUMANOID_WALKSPEED_CHECK = 0x3c4 
OFFSET_HUMANOID_JUMPOWER = 0x1b0  
OFFSET_HUMANOID_JUMPHEIGHT = 0x1ac  


NUEVA_VELOCIDAD = 50.0   
POTENCIA_SALTO = 50.0  
ALTURA_SALTO = 50.0      


kernel32 = ctypes.WinDLL("kernel32.dll", use_last_error=True)

ReadProcessMemory = kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [wintypes.HANDLE, wintypes.LPCVOID, wintypes.LPVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
ReadProcessMemory.restype = wintypes.BOOL

WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.argtypes = [wintypes.HANDLE, wintypes.LPVOID, wintypes.LPCVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
WriteProcessMemory.restype = wintypes.BOOL

def leer_puntero(HANDLE, direccion):
    ptr = ctypes.c_uint64(0)
    ReadProcessMemory(int(HANDLE), int(direccion), ctypes.byref(ptr), 8, None)
    return ptr.value

def escribir_float(HANDLE, direccion, valor):
    val = ctypes.c_float(valor)
    return WriteProcessMemory(int(HANDLE), int(direccion), ctypes.byref(val), 4, None)


def speed():
    print("\n" + "="*60)
    print("     INICIANDO INYECTOR DE MOVIMIENTO SINCRONIZADO (ANTI-KICK)")
    print("="*60)

    HProcess = OpenProcess(PROCESS_VM_READ | PROCESS_VM_OPERATION | PROCESS_VM_WRITE, False, pid)
    if not HProcess:
        print("[-] Error crítico: Privilegios insuficientes.")
        print("[*] Por favor, ejecuta esta terminal de Python como Administrador.")
        exit()

    print("[*] Sincronizando memoria local... Entrando en bucle de bypass.")
    print("[*] Presiona Ctrl + C en esta ventana para cerrar de forma segura.")
    print("-" * 60)

    try:
        while True:
          
            addr_visual_engine  = leer_puntero(HProcess, base_exe + STATIC_VISUAL_ENGINE)
            addr_fake_datamodel = leer_puntero(HProcess, addr_visual_engine + OFFSET_FAKE_DATAMODEL)
            addr_real_datamodel = leer_puntero(HProcess, addr_fake_datamodel + OFFSET_REAL_DATAMODEL)
            addr_workspace      = leer_puntero(HProcess, addr_real_datamodel + OFFSET_WORKSPACE)
            addr_camera         = leer_puntero(HProcess, addr_workspace + OFFSET_CURRENT_CAMERA)
            addr_humanoid       = leer_puntero(HProcess, addr_camera + OFFSET_CAMERA_SUBJECT)
            
            if addr_humanoid != 0:
                escribir_float(HProcess, addr_humanoid + OFFSET_HUMANOID_WALKSPEED, NUEVA_VELOCIDAD)
                escribir_float(HProcess, addr_humanoid + OFFSET_HUMANOID_WALKSPEED_CHECK, NUEVA_VELOCIDAD)
                
          
                escribir_float(HProcess, addr_humanoid + OFFSET_HUMANOID_JUMPOWER, POTENCIA_SALTO)
                escribir_float(HProcess, addr_humanoid + OFFSET_HUMANOID_JUMPHEIGHT, ALTURA_SALTO)
                
                print(f"[BYPASS ACTIVO] Sincronizado en: {hex(addr_humanoid)} | Speed: {NUEVA_VELOCIDAD} studs/s", end="\r")
            else:
                print("[-] Buscando entidad activa del jugador en el mapa...", end="\r")

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n\n[*] Interrupción detectada. Restaurando valores originales por seguridad...")

        if 'addr_humanoid' in locals() and addr_humanoid != 0:
            escribir_float(HProcess, addr_humanoid + OFFSET_HUMANOID_WALKSPEED, 16.0)
            escribir_float(HProcess, addr_humanoid + OFFSET_HUMANOID_WALKSPEED_CHECK, 16.0)
            escribir_float(HProcess, addr_humanoid + OFFSET_HUMANOID_JUMPOWER, 50.0)
            escribir_float(HProcess, addr_humanoid + OFFSET_HUMANOID_JUMPHEIGHT, 5.0)
            print("[+] Valores de fábrica restablecidos correctamente.")
            
    finally:
        CloseHandle(HProcess)
        print("[*] Handles de Windows cerrados. Proceso finalizado.")
        print("="*60)

if __name__ == "__main__":
    speed()
