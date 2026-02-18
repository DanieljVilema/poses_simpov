"""
Módulo de Calibración
Contiene toda la lógica de calibración, almacenamiento de patrones y gestión de estados
"""
import time

# Índices COCO
H_I, H_D = 5, 6
C_I, C_D = 7, 8
M_I, M_D = 9, 10
CAD_I, CAD_D = 11, 12
ROD_I, ROD_D = 13, 14


class GestorCalbracion:
    """Gestor centralizado de calibración y patrones"""
    
    def __init__(self, tolerancia=12):
        """
        Inicializa el gestor de calibración.
        
        Args:
            tolerancia: Grados de error permitidos en la evaluación
        """
        # Memoria del sistema (Múltiples perfiles)
        self.patrones = {
            "PERFIL_DERECHO": {"calibrado": False, "brazo": 0, "torso": 0, "codo_hombro_cadera": 0},
            "PERFIL_IZQUIERDO": {"calibrado": False, "brazo": 0, "torso": 0, "codo_hombro_cadera": 0}
        }
        
        self.estado_actual = "EVALUANDO"  # Por defecto evalúa
        self.tiempo_inicio = 0
        self.tolerancia = tolerancia
        self.tiempo_calibracion = 5  # Segundos para calibrar


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


    def guardar_patron(self, orientacion, brazo, torso, codo_hombro_cadera):
        """
        Guarda un patrón calibrado en la memoria.
        
        Args:
            orientacion: 'PERFIL_DERECHO' o 'PERFIL_IZQUIERDO'
            brazo: Ángulo del brazo
            torso: Ángulo del torso
            codo_hombro_cadera: Ángulo codo-hombro-cadera
        """
        self.patrones[orientacion].update({
            "calibrado": True,
            "brazo": brazo,
            "torso": torso,
            "codo_hombro_cadera": codo_hombro_cadera
        })
        self.estado_actual = "EVALUANDO"


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
        self.patrones = {
            "PERFIL_DERECHO": {"calibrado": False, "brazo": 0, "torso": 0, "codo_hombro_cadera": 0},
            "PERFIL_IZQUIERDO": {"calibrado": False, "brazo": 0, "torso": 0, "codo_hombro_cadera": 0}
        }
        self.estado_actual = "EVALUANDO"


    def obtener_todos_los_patrones(self):
        """
        Obtiene todos los patrones calibrados.
        
        Returns:
            dict: Todos los patrones
        """
        return self.patrones
