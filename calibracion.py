"""
Módulo de Calibración
Contiene toda la lógica de calibración, almacenamiento de patrones y gestión de estados
"""
import time
import json
import os

# Índices COCO
H_I, H_D = 5, 6
C_I, C_D = 7, 8
M_I, M_D = 9, 10
CAD_I, CAD_D = 11, 12
ROD_I, ROD_D = 13, 14

ARCHIVO_CONFIG = "armas_config.json"


class GestorCalbracion:
    """Gestor centralizado de calibración y patrones"""

    def __init__(self, tolerancia=12):
        """
        Inicializa el gestor de calibración.

        Args:
            tolerancia: Grados de error permitidos en la evaluación
        """
        self.tolerancia = tolerancia
        self.tiempo_calibracion = 5  # Segundos para calibrar
        self.estado_actual = "EVALUANDO"
        self.tiempo_inicio = 0

        # Arma actual seleccionada
        self.arma_actual = None

        # Memoria del sistema (Múltiples perfiles)
        self.patrones = self._patrones_vacios()

        # Cargar configuración existente
        self.config = self._cargar_config()

    def _patrones_vacios(self):
        """Retorna un diccionario de patrones vacíos"""
        return {
            "PERFIL_DERECHO": {"calibrado": False, "brazo": 0, "torso": 0, "codo_hombro_cadera": 0, "brazo_soporte": None},
            "PERFIL_IZQUIERDO": {"calibrado": False, "brazo": 0, "torso": 0, "codo_hombro_cadera": 0, "brazo_soporte": None}
        }

    def _cargar_config(self):
        """Carga la configuración desde el archivo JSON"""
        if os.path.exists(ARCHIVO_CONFIG):
            try:
                with open(ARCHIVO_CONFIG, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"armas": {}}
        return {"armas": {}}

    def _guardar_config(self):
        """Guarda la configuración actual al archivo JSON"""
        with open(ARCHIVO_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def obtener_lista_armas(self):
        """
        Obtiene la lista de armas guardadas.

        Returns:
            list: Lista de nombres de armas
        """
        return list(self.config.get("armas", {}).keys())

    def seleccionar_arma(self, nombre):
        """
        Selecciona un arma existente y carga sus patrones.

        Args:
            nombre: Nombre del arma a seleccionar
        """
        self.arma_actual = nombre
        datos = self.config.get("armas", {}).get(nombre)
        if datos:
            vacios = self._patrones_vacios()
            self.patrones = {}
            for perfil in ("PERFIL_DERECHO", "PERFIL_IZQUIERDO"):
                base = dict(vacios[perfil])
                base.update(datos.get(perfil, {}))
                self.patrones[perfil] = base
        else:
            self.patrones = self._patrones_vacios()

    def crear_arma(self, nombre):
        """
        Crea una nueva arma con patrones vacíos y la selecciona.

        Args:
            nombre: Nombre de la nueva arma
        """
        self.config.setdefault("armas", {})[nombre] = self._patrones_vacios()
        self._guardar_config()
        self.seleccionar_arma(nombre)

    def obtener_arma_actual(self):
        """
        Obtiene el nombre del arma actualmente seleccionada.

        Returns:
            str: Nombre del arma actual o None
        """
        return self.arma_actual

    def iniciar_calibracion(self):
        """Inicia el proceso de calibración"""
        self.estado_actual = "CONTEO"
        self.tiempo_inicio = time.time()

    def obtener_tiempo_restante_calibracion(self):
        """
        Obtiene el tiempo restante para completar la calibración.

        Returns:
            int: Segundos restantes (negativo si ya pasó)
        """
        return self.tiempo_calibracion - int(time.time() - self.tiempo_inicio)

    def calibracion_completada(self):
        """Verifica si la calibración se ha completado"""
        return self.obtener_tiempo_restante_calibracion() <= 0

    def guardar_patron(self, orientacion, brazo, torso, codo_hombro_cadera, brazo_soporte=None):
        """
        Guarda un patrón calibrado en la memoria y persiste al JSON.

        Args:
            orientacion: 'PERFIL_DERECHO' o 'PERFIL_IZQUIERDO'
            brazo: Ángulo del brazo
            torso: Ángulo del torso
            codo_hombro_cadera: Ángulo codo-hombro-cadera
            brazo_soporte: Ángulo del brazo de soporte (None si no es visible)
        """
        self.patrones[orientacion].update({
            "calibrado": True,
            "brazo": brazo,
            "torso": torso,
            "codo_hombro_cadera": codo_hombro_cadera,
            "brazo_soporte": brazo_soporte
        })
        self.estado_actual = "EVALUANDO"

        # Persistir al JSON si hay arma seleccionada
        if self.arma_actual:
            self.config.setdefault("armas", {})[self.arma_actual] = {
                "PERFIL_DERECHO": dict(self.patrones["PERFIL_DERECHO"]),
                "PERFIL_IZQUIERDO": dict(self.patrones["PERFIL_IZQUIERDO"])
            }
            self._guardar_config()

    def obtener_patron(self, orientacion):
        """
        Obtiene el patrón calibrado de una orientación.

        Args:
            orientacion: 'PERFIL_DERECHO' o 'PERFIL_IZQUIERDO'

        Returns:
            dict: Patrón con 'calibrado', 'brazo', 'torso', 'codo_hombro_cadera'
        """
        return self.patrones.get(orientacion, {})

    def esta_calibrado(self, orientacion):
        """
        Verifica si una orientación está calibrada.

        Args:
            orientacion: 'PERFIL_DERECHO' o 'PERFIL_IZQUIERDO'

        Returns:
            bool: True si está calibrado, False en caso contrario
        """
        return self.patrones.get(orientacion, {}).get("calibrado", False)

    def obtener_estado(self):
        """
        Obtiene el estado actual del sistema.

        Returns:
            str: 'EVALUANDO', 'CONTEO'
        """
        return self.estado_actual

    def cambiar_a_evaluacion(self):
        """Cambia el estado a EVALUANDO"""
        self.estado_actual = "EVALUANDO"

    def obtener_tolerancia(self):
        """
        Obtiene la tolerancia actual.

        Returns:
            int: Grados de error permitidos
        """
        return self.tolerancia

    def modificar_tolerancia(self, nueva_tolerancia):
        """
        Modifica la tolerancia de evaluación.

        Args:
            nueva_tolerancia: Nueva tolerancia en grados
        """
        self.tolerancia = nueva_tolerancia

    def resetear_patrones(self):
        """Reinicia todos los patrones calibrados"""
        self.patrones = self._patrones_vacios()
        self.estado_actual = "EVALUANDO"

    def obtener_todos_los_patrones(self):
        """
        Obtiene todos los patrones calibrados.

        Returns:
            dict: Todos los patrones
        """
        return self.patrones
