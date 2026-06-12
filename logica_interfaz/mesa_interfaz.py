import pygame
from recursos_graficos import constantes
from logica_interfaz.archivo_de_importaciones import importar_desde_carpeta

# ===== IMPORTACIONES =====
# Importaciones de clases de interfaz
Mazo = importar_desde_carpeta(
    nombre_archivo="mazo_interfaz.py",
    nombre_clase="Mazo_interfaz",
    nombre_carpeta="logica_interfaz"
)
Jugador = importar_desde_carpeta(
    nombre_archivo="jugador_interfaz.py",
    nombre_clase="Jugador_interfaz",
    nombre_carpeta="logica_interfaz"
)
Carta = importar_desde_carpeta(
    nombre_archivo="cartas_interfaz.py",
    nombre_clase="Cartas_interfaz",
    nombre_carpeta="logica_interfaz"
)
BotonLogoMenu = importar_desde_carpeta("elementos_de_interfaz_de_usuario.py","BotonLogoMenu","recursos_graficos")

# Importar recursos graficos
Menu = importar_desde_carpeta("menu.py","Menu","recursos_graficos")
Boton = importar_desde_carpeta("elementos_de_interfaz_de_usuario.py","Boton","recursos_graficos")
CartelAlerta = importar_desde_carpeta("elementos_de_interfaz_de_usuario.py","CartelAlerta","recursos_graficos")

# ===== IMPORTACIONES DE MIXINS =====
from logica_interfaz.core.layout.posicionamiento import PosicionamientoMixin
from logica_interfaz.core.configuracion.utilidades import UtilidadesMixin
from logica_interfaz.core.datos.carga_datos import CargaDatosMixin
from logica_interfaz.core.datos.carga_visuales import CargaVisualesMixin
from logica_interfaz.core.logica_juego.turnos import TurnosMixin
from logica_interfaz.core.controles_ui.botones import BotonesMixin
from logica_interfaz.core.renderizado.mostrar import MostrarMixin
from logica_interfaz.core.configuracion.creacion import CreacionMesaMixin
from logica_interfaz.core.renderizado.actualizacion import ActualizacionMixin
from logica_interfaz.core.logica_juego.procesamiento import ProcesamientoMixin
from logica_interfaz.core.logica_juego.mano import ManoMixin
from logica_interfaz.core.red.acciones_red import AccionesRedMixin
from logica_interfaz.core.logica_juego.puntos import PuntosMixin
from logica_interfaz.core.controles_ui.menu_opciones import MenuOpcionesMixin
from logica_interfaz.core.controles_ui.alertas import AlertasMixin
from logica_interfaz.core.logica_juego.rondas import RondasMixin
from logica_interfaz.core.ui.menu_adaptado import Menu_adaptado

# ===== MIXIN ORDENAMIENTO (NUEVO) =====
from logica_interfaz.core.controles_ui.ordenamiento_mano import OrdenamientoManoMixin


class Mesa_interfaz(
    OrdenamientoManoMixin,      # <── NUEVO: ordenamiento de mano del jugador
    PosicionamientoMixin,
    UtilidadesMixin,
    CargaDatosMixin,
    CargaVisualesMixin,
    TurnosMixin,
    BotonesMixin,
    MostrarMixin,
    CreacionMesaMixin,
    ActualizacionMixin,
    ProcesamientoMixin,
    ManoMixin,
    AccionesRedMixin,
    PuntosMixin,
    MenuOpcionesMixin,
    AlertasMixin,
    RondasMixin
):
    _cartas_imagenes = None  # cache estático

    def __init__(self, un_juego):

        # Inicialización de datos del juego interfaz-redes
        self.elementos_mesa = {
            "id_jugador": None,
            "jugador_mano": None,
            "cantidad_cartas_mazo": 0,
            "cantidad_cartas_quema": 0,
            "dato_carta_quema":None,
            "dato_carta_descarte": None,
            "datos_mano_jugador": [],
            "cantidad_manos_jugadores": [],
            "datos_lista_jugadores": [],
            "turno_robar": False,
            "jugada":[],
            "jugadas_jugadores":[],
            "nro_jugada":1,
        }

        # Objetos del juego
        self.carta_descarte = None
        self.lista_jugadores_objetos = []
        self._jugadores_dict = None  # Cache para búsqueda optimizada de jugadores
        self.mano = []
        self.mazo_quema = None
        self.carta_quema = None
        self.un_juego = un_juego
        self.instacia_conexion = None
        self.mesa = None
        self.jugadores = []
        self.jugadas_jugadores = {}
        self.jugada = []
        self.trio = []
        self.seguidilla = []

        self.debug_ver_posiciones_7 = False #simulacion de 7 jugadores momentaneos

        # Estados del juego
        self.tu_turno = False
        self.turno_robar = False

        # Contador de puntos
        self.puntos_acumulados = 0
        self.puntos_ronda_actual = 0

        self.menu_opciones = None
        self.menu_puntuacion = None
        self.menus_activos = []  # Lista para menus activos de la mesa
        self.boton_menu_opciones = None

        # Elementos de interfaz
        self.botones_accion = {}
        self.accion_seleccionada = None

        # Estado del ordenamiento (instancia propia para no compartir con otras instancias)
        self._modo_orden = 'trios'
        self._boton_ordenar = None

        # Referencia de elementos surface mesa-ventana
        self.referencia_elementos = {
                    "elementos_mis_cartas":[],
                    "elemento_carta_descarte":None,
                    "elemento_mazo_quema":None,
                    "elemento_jugadores":[],
                    "reversos_por_jugador":[],
                    "contadores_mano_por_jugador":[],
                    "jugadas_por_jugador":[],
                    "elementos_jugadas_jugadores":[],
                    "elementos_mi_jugada":[],
                    "elemento_mazo":None,
                    "elemento_carta_quema":None,
                    "indicador_turno":None,
                    "contador_puntos":None
        }

        # Configuración de posiciones
        self._inicializar_configuracion_posiciones()

    # ===== INICIALIZACIÓN Y CONFIGURACIÓN =====
    def _inicializar_configuracion_posiciones(self):
        """Configura las posiciones y permutaciones para los jugadores"""
        self.posiciones_por_cantidad = {
            2: [
                ("abajo", 0.50),
                ("arriba", 0.50),
            ],

            3: [
                ("abajo", 0.50),
                ("derecha", 0.75),
                ("izquierda", 0.75),
            ],

            4: [
                ("abajo", 0.50),
                ("derecha", 0.75),
                ("arriba", 0.50),
                ("izquierda", 0.75),
            ],

            5: [
                ("abajo", 0.50),
                ("arriba", 0.65),
                ("derecha", 0.75),
                ("arriba", 0.33),
                ("izquierda", 0.75),
            ],

            6: [
                ("abajo", 0.50),
                ("derecha", 0.95),
                ("derecha", 0.50),
                ("arriba", 0.50),
                ("izquierda", 0.50),
                ("izquierda", 0.95),
            ],

            7: [
                ("abajo", 0.50),
                ("derecha", 0.95),
                ("derecha", 0.50),
                ("arriba", 0.65),
                ("arriba", 0.33),
                ("izquierda", 0.50),
                ("izquierda", 0.95),
            ],

            8: [
                ("abajo", 0.50),
                ("derecha", 0.85),
                ("derecha", 0.50),
                ("arriba", 0.80),
                ("arriba", 0.20),
                ("izquierda", 0.50),
                ("izquierda", 0.85),
                ("arriba", 0.50),
            ],
        }

        self.permutaciones_por_jugador = {
            2: {
                1: [0, 1],
                2: [1, 0],
            },

            3: {
                1: [0, 1, 2],
                2: [2, 0, 1],
                3: [1, 2, 0],
            },

            4: {
                1: [0, 1, 2, 3],
                2: [3, 0, 1, 2],
                3: [2, 3, 0, 1],
                4: [1, 2, 3, 0],
            },

            5: {
                1: [0, 1, 2, 3, 4],
                2: [4, 0, 1, 2, 3],
                3: [3, 4, 0, 1, 2],
                4: [2, 3, 4, 0, 1],
                5: [1, 2, 3, 4, 0],
            },

            6: {
                1: [0, 1, 2, 3, 4, 5],
                2: [5, 0, 1, 2, 3, 4],
                3: [4, 5, 0, 1, 2, 3],
                4: [3, 4, 5, 0, 1, 2],
                5: [2, 3, 4, 5, 0, 1],
                6: [1, 2, 3, 4, 5, 0],
            },

            7: {
                1: [0, 1, 2, 3, 4, 5, 6],
                2: [6, 0, 1, 2, 3, 4, 5],
                3: [5, 6, 0, 1, 2, 3, 4],
                4: [4, 5, 6, 0, 1, 2, 3],
                5: [3, 4, 5, 6, 0, 1, 2],
                6: [2, 3, 4, 5, 6, 0, 1],
                7: [1, 2, 3, 4, 5, 6, 0],
            },
        }

    def dibujar_debug_posiciones_jugadores(self, cantidad = 7):
            ancho = constantes.ANCHO_VENTANA
            alto = constantes.ALTO_VENTANA

            posiciones = self.posiciones_por_cantidad[cantidad]

            for i, (lado, factor) in enumerate(posiciones):
                if lado == "abajo":
                    x = int(ancho * factor)
                    y = int(alto * 0.82)
                elif lado == "arriba":
                    x = int(ancho * factor)
                    y = int(alto * 0.08)
                elif lado == "derecha":
                    x = int(ancho * 0.88)
                    y = int(alto * factor)
                elif lado == "izquierda":
                    x = int(ancho * 0.08)
                    y = int(alto * factor)

                rect = pygame.Rect(x - 60, y - 35, 120, 70)

                pygame.draw.rect(self.un_juego.pantalla, (255, 255, 255), rect, 2)
                pygame.draw.circle(self.un_juego.pantalla, (255, 0, 0), (x, y), 6)

                fuente = pygame.font.SysFont(None, 28)
                texto = fuente.render(f"J{i+1} {lado} {factor}", True, (255, 255, 255))
                self.un_juego.pantalla.blit(texto, (x - 55, y - 10))     
