import cv2
import time
import math
import numpy as np
from ultralytics import YOLO

# --- MEMORIA DEL SISTEMA (Múltiples perfiles) ---
patrones = {
    "FRENTE": {"calibrado": False, "izq": 0, "der": 0},
    "PERFIL_DERECHO": {"calibrado": False, "brazo": 0, "torso": 0},
    "PERFIL_IZQUIERDO": {"calibrado": False, "brazo": 0, "torso": 0}
}

estado_actual = "EVALUANDO" # Por defecto evalúa (si no hay patrón, pide calibrar)
tiempo_inicio = 0
orientacion_actual = "DESCONOCIDO"
tolerancia = 12 # Grados de error permitidos

# Índices COCO
H_I, H_D = 5, 6
C_I, C_D = 7, 8
M_I, M_D = 9, 10
CAD_I, CAD_D = 11, 12
ROD_I, ROD_D = 13, 14

def click_pantalla(evento, x, y, flags, param):
    global estado_actual, tiempo_inicio, orientacion_actual
    if evento == cv2.EVENT_LBUTTONDOWN:
        # Clic en el botón superior izquierdo (20,20 a 200,70)
        if 20 <= x <= 200 and 20 <= y <= 70:
            if orientacion_actual != "DESCONOCIDO" and estado_actual == "EVALUANDO":
                estado_actual = "CONTEO"
                tiempo_inicio = time.time()

def calcular_angulo(p1, p2, p3):
    rad = math.atan2(p3[1] - p2[1], p3[0] - p2[0]) - math.atan2(p1[1] - p2[1], p1[0] - p2[0])
    ang = abs(rad * 180.0 / math.pi)
    return int(360.0 - ang if ang > 180.0 else ang)

print("Iniciando Sistema Omnidireccional de Evaluación Táctica...")
modelo = YOLO('yolov8n-pose.pt')
cap = cv2.VideoCapture(0)

cv2.namedWindow('DINDES - Motor Biometrico IA')
cv2.setMouseCallback('DINDES - Motor Biometrico IA', click_pantalla)

while cap.isOpened():
    exito, frame = cap.read()
    if not exito: break

    resultados = modelo(frame, verbose=False)
    ui = frame.copy()

    try:
        kp = resultados[0].keypoints.xy[0].cpu().numpy()
        conf = resultados[0].keypoints.conf[0].cpu().numpy()

        # 1. DETECCIÓN AUTOMÁTICA DE ORIENTACIÓN (El Cerebro)
        dist_hombros_x = abs(kp[H_I][0] - kp[H_D][0])
        
        # Si vemos ambos hombros claramente y están separados = FRENTE
        if conf[H_I] > 0.6 and conf[H_D] > 0.6 and dist_hombros_x > 50:
            orientacion_actual = "FRENTE"
        # Si el hombro derecho se ve mejor y la distancia X es corta (oclusión) = DERECHA
        elif conf[H_D] > 0.5 and (conf[H_D] > conf[H_I] or dist_hombros_x <= 50):
            orientacion_actual = "PERFIL_DERECHO"
        # Si el hombro izquierdo domina = IZQUIERDA
        elif conf[H_I] > 0.5 and (conf[H_I] > conf[H_D] or dist_hombros_x <= 50):
            orientacion_actual = "PERFIL_IZQUIERDO"
        else:
            orientacion_actual = "DESCONOCIDO"

        # 2. INTERFAZ SUPERIOR (HUD)
        cv2.rectangle(ui, (0, 0), (640, 80), (0, 0, 0), -1) # Fondo negro HUD
        cv2.putText(ui, f"MODO: {orientacion_actual}", (230, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        estado_txt = "LISTO" if patrones.get(orientacion_actual, {}).get("calibrado") else "NO CALIBRADO"
        color_estado = (0, 255, 0) if estado_txt == "LISTO" else (0, 0, 255)
        if orientacion_actual != "DESCONOCIDO":
            cv2.putText(ui, f"MEMORIA: {estado_txt}", (230, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_estado, 2)

        # 3. LÓGICA DE CALIBRACIÓN Y EVALUACIÓN
        if orientacion_actual != "DESCONOCIDO":
            
            # Extraer ángulos según la vista actual
            ang_izq, ang_der, ang_torso_d, ang_torso_i = 0, 0, 0, 0
            
            if orientacion_actual == "FRENTE":
                ang_izq = calcular_angulo(kp[H_I], kp[C_I], kp[M_I])
                ang_der = calcular_angulo(kp[H_D], kp[C_D], kp[M_D])
            elif orientacion_actual == "PERFIL_DERECHO":
                ang_der = calcular_angulo(kp[H_D], kp[C_D], kp[M_D])
                ang_torso_d = calcular_angulo(kp[H_D], kp[CAD_D], kp[ROD_D])
            elif orientacion_actual == "PERFIL_IZQUIERDO":
                ang_izq = calcular_angulo(kp[H_I], kp[C_I], kp[M_I])
                ang_torso_i = calcular_angulo(kp[H_I], kp[CAD_I], kp[ROD_I])

            # --- ESTADO: CONTEO PARA CALIBRAR ---
            if estado_actual == "CONTEO":
                restante = 5 - int(time.time() - tiempo_inicio)
                cv2.putText(ui, f"CALIBRANDO {orientacion_actual}: {restante}", (50, 250), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 165, 255), 3)
                
                if restante <= 0:
                    if orientacion_actual == "FRENTE":
                        patrones["FRENTE"].update({"calibrado": True, "izq": ang_izq, "der": ang_der})
                    elif orientacion_actual == "PERFIL_DERECHO":
                        patrones["PERFIL_DERECHO"].update({"calibrado": True, "brazo": ang_der, "torso": ang_torso_d})
                    elif orientacion_actual == "PERFIL_IZQUIERDO":
                        patrones["PERFIL_IZQUIERDO"].update({"calibrado": True, "brazo": ang_izq, "torso": ang_torso_i})
                    estado_actual = "EVALUANDO"

            # --- ESTADO: EVALUACIÓN EN VIVO ---
            elif estado_actual == "EVALUANDO":
                # Dibujar Botón
                cv2.rectangle(ui, (20, 20), (200, 70), (200, 0, 0), -1)
                cv2.putText(ui, "NUEVO PATRON", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                if patrones[orientacion_actual]["calibrado"]:
                    if orientacion_actual == "FRENTE":
                        # Evaluar Frente
                        col_i = (0,255,0) if abs(ang_izq - patrones["FRENTE"]["izq"]) <= tolerancia else (0,0,255)
                        col_d = (0,255,0) if abs(ang_der - patrones["FRENTE"]["der"]) <= tolerancia else (0,0,255)
                        
                        cv2.line(ui, tuple(kp[H_I][:2].astype(int)), tuple(kp[C_I][:2].astype(int)), col_i, 3)
                        cv2.line(ui, tuple(kp[C_I][:2].astype(int)), tuple(kp[M_I][:2].astype(int)), col_i, 3)
                        cv2.line(ui, tuple(kp[H_D][:2].astype(int)), tuple(kp[C_D][:2].astype(int)), col_d, 3)
                        cv2.line(ui, tuple(kp[C_D][:2].astype(int)), tuple(kp[M_D][:2].astype(int)), col_d, 3)

                    elif orientacion_actual == "PERFIL_DERECHO":
                        # Evaluar Perfil Derecho
                        col_b = (0,255,0) if abs(ang_der - patrones["PERFIL_DERECHO"]["brazo"]) <= tolerancia else (0,0,255)
                        col_t = (0,255,0) if abs(ang_torso_d - patrones["PERFIL_DERECHO"]["torso"]) <= tolerancia else (0,0,255)
                        
                        cv2.line(ui, tuple(kp[H_D][:2].astype(int)), tuple(kp[C_D][:2].astype(int)), col_b, 3)
                        cv2.line(ui, tuple(kp[C_D][:2].astype(int)), tuple(kp[M_D][:2].astype(int)), col_b, 3)
                        cv2.line(ui, tuple(kp[H_D][:2].astype(int)), tuple(kp[CAD_D][:2].astype(int)), col_t, 3)
                        cv2.line(ui, tuple(kp[CAD_D][:2].astype(int)), tuple(kp[ROD_D][:2].astype(int)), col_t, 3)

                    elif orientacion_actual == "PERFIL_IZQUIERDO":
                        # Evaluar Perfil Izquierdo
                        col_b = (0,255,0) if abs(ang_izq - patrones["PERFIL_IZQUIERDO"]["brazo"]) <= tolerancia else (0,0,255)
                        col_t = (0,255,0) if abs(ang_torso_i - patrones["PERFIL_IZQUIERDO"]["torso"]) <= tolerancia else (0,0,255)
                        
                        cv2.line(ui, tuple(kp[H_I][:2].astype(int)), tuple(kp[C_I][:2].astype(int)), col_b, 3)
                        cv2.line(ui, tuple(kp[C_I][:2].astype(int)), tuple(kp[M_I][:2].astype(int)), col_b, 3)
                        cv2.line(ui, tuple(kp[H_I][:2].astype(int)), tuple(kp[CAD_I][:2].astype(int)), col_t, 3)
                        cv2.line(ui, tuple(kp[CAD_I][:2].astype(int)), tuple(kp[ROD_I][:2].astype(int)), col_t, 3)

                else:
                    cv2.putText(ui, "PRESIONA 'NUEVO PATRON' PARA DETECTAR LA POSTURA", (30, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    except Exception as e:
        pass

    cv2.imshow('DINDES - Motor Biometrico IA', ui)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()