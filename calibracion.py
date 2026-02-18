"""
Módulo de Calibración
Contiene la lógica de calibración estadística, almacenamiento de patrones y gestión de estados
"""
import time
import json
import os
import numpy as np

ARCHIVO_CONFIG = "armas_config.json"

class GestorCalbracion:
    def __init__(self):
        self.tiempo_calibracion = 5
        self.estado_actual = "EVALUANDO"
        self.tiempo_inicio = 0
        self.arma_actual = None
        self.patrones = self._patrones_vacios()
        self.config = self._cargar_config()
        self.muestras = []
        self.orientacion_calibrando = None

    def _patrones_vacios(self):
        perfil = {
            "calibrado": False,
            "brazo": 0, "brazo_std": 0, "torso": 0, "torso_std": 0,
            "codo_hombro_cadera": 0, "codo_hombro_cadera_std": 0,
            "brazo_soporte": None, "brazo_soporte_std": None,
            "rodilla": None, "rodilla_std": None, "cabeza": None, "cabeza_std": None
        }
        return {"PERFIL_DERECHO": dict(perfil), "PERFIL_IZQUIERDO": dict(perfil)}

    def _cargar_config(self):
        if os.path.exists(ARCHIVO_CONFIG):
            try:
                with open(ARCHIVO_CONFIG, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {"armas": {}}

    def _guardar_config(self):
        with open(ARCHIVO_CONFIG, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def obtener_lista_armas(self):
        return list(self.config.get("armas", {}).keys())

    def seleccionar_arma(self, nombre_arma):
        self.arma_actual = nombre_arma
        if nombre_arma in self.config.get("armas", {}):
            datos_guardados = self.config["armas"][nombre_arma]
            nuevos_patrones = self._patrones_vacios()
            for orientacion in ["PERFIL_DERECHO", "PERFIL_IZQUIERDO"]:
                if orientacion in datos_guardados:
                    for k, v in datos_guardados[orientacion].items():
                        nuevos_patrones[orientacion][k] = v
            self.patrones = nuevos_patrones
            return True
        return False

    def crear_arma(self, nombre_arma):
        if nombre_arma and nombre_arma not in self.config.get("armas", {}):
            self.config.setdefault("armas", {})[nombre_arma] = self._patrones_vacios()
            self._guardar_config()
            self.seleccionar_arma(nombre_arma)
            return True
        return False

    def iniciar_calibracion(self, orientacion):
        self.estado_actual = "CONTEO"
        self.tiempo_inicio = time.time()
        self.muestras = []
        self.orientacion_calibrando = orientacion

    def agregar_muestra(self, angulos):
        self.muestras.append(dict(angulos))

    def finalizar_calibracion(self):
        if not self.muestras or not self.orientacion_calibrando:
            self.estado_actual = "EVALUANDO"
            return
        
        patron = {"calibrado": True}
        
        for key in ['brazo', 'torso', 'codo_hombro_cadera']:
            valores = [m[key] for m in self.muestras if m.get(key, 0) != 0]
            if valores:
                patron[key] = int(np.mean(valores))
                patron[f"{key}_std"] = round(float(np.std(valores)), 1)
            else:
                patron[key] = 0; patron[f"{key}_std"] = 0
                
        for key in ['brazo_soporte', 'rodilla', 'cabeza']:
            valores = [m[key] for m in self.muestras if m.get(key) is not None]
            if len(valores) >= len(self.muestras) * 0.3:
                patron[key] = int(np.mean(valores))
                patron[f"{key}_std"] = round(float(np.std(valores)), 1)
            else:
                patron[key] = None; patron[f"{key}_std"] = None
                
        self.patrones[self.orientacion_calibrando] = patron
        self.estado_actual = "EVALUANDO"
        
        if self.arma_actual:
            self.config.setdefault("armas", {})[self.arma_actual] = {
                "PERFIL_DERECHO": dict(self.patrones["PERFIL_DERECHO"]),
                "PERFIL_IZQUIERDO": dict(self.patrones["PERFIL_IZQUIERDO"])
            }
            self._guardar_config()
            
        self.muestras = []
        self.orientacion_calibrando = None

    def calibracion_completada(self):
        return (time.time() - self.tiempo_inicio) >= self.tiempo_calibracion

    def obtener_tiempo_restante_calibracion(self):
        return max(0, self.tiempo_calibracion - int(time.time() - self.tiempo_inicio))

    def obtener_patron(self, orientacion): return self.patrones.get(orientacion, {})
    def esta_calibrado(self, orientacion): return self.patrones.get(orientacion, {}).get("calibrado", False)
    def obtener_estado(self): return self.estado_actual
    def obtener_arma_actual(self): return self.arma_actual
    def obtener_todos_los_patrones(self): return self.patrones
    def resetear_patrones(self): self.patrones = self._patrones_vacios()