import uuid


# Clase base que representa a cualquier persona que interactua con la tienda
class Usuario:
    
    # Inicializa un usuario con id autogenerado, nombre y correo electronico
    def __init__(self, nombre: str, email: str) -> None:

        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.email: str = email

    # Indica si el usuario tiene privilegios de administrador
    def is_admin(self) -> bool:
        return False

    # Devuelve una representacion legible del usuario
    def __str__(self) -> str:
        
        return f"[{self.id[:8]}] {self.nombre} ({self.email})"


# Usuario de tipo cliente, con direccion postal adicional
class Cliente(Usuario):
    

    # Inicializa un cliente
    def __init__(self, nombre: str, email: str, direccion: str) -> None:

        super().__init__(nombre, email)
        self.direccion: str = direccion

    # Devuelve una representacion legible del cliente
    def __str__(self) -> str:
        
        return f"{super().__str__()} | Direccion: {self.direccion}"

# Usuario de tipo administrador, gestor de la tienda
class Administrador(Usuario):
    
    # Indica si el usuario tiene privilegios de administrador
    def is_admin(self) -> bool:
        return True

    # Devuelve una representacion legible del administrador
    def __str__(self) -> str:
        return f"{super().__str__()} | Rol: Administrador"
