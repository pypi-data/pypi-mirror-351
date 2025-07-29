
---

# Redis Facade

## Instalación

```bash
pip3 install redisfacade
```

## Manual de uso
1. **Variables de Entorno**

| Variable | Tipo de dato |
|:-|-:|
|REDIS_HOST|string|
|REDIS_PORT|int|
|REDIS_PASSWORD|string|

2. **Funciones**:
   - **`set_key_value(db: int, key:str, value: Any) -> bool`**: Este método permite guardar en redis un tipo de dato key - value.
   - **`get_key_value(db: int, key: str, ttl: timedelta) -> Any`**: Este método permite obtener un tipo de dato key - value.
   - **`set_list_str(db: int, list_name: str, intems: List[str]) -> bool`**: Este método permite guartar un tipo de dato lista de string.
   - **`get_list_str(db: int, list_name: str) -> List[str]`**: Este método permite obtener una lista de string completa.
   - **`pop_list_str(db: int, list_name: str) -> str`**: Este método permite hacer pop del primer elemento en una lista.
   - **`len_list(db: int, list_name: str) -> str`**: Este método permite ver el tamaño de una lista.
   - **`set_json_data(db: int, json_name, json_key, json_data: Any, ttl: timedelta) -> bool`**: Este método permite guardar un objeto de tipo json.
   - **`get_key_json_data(self, db: int, json_name: str, json_key: str) -> Any`**: Este método permite obtener una llave de objeto de tipo json.
   - **`def get_json_data(self, db: int, json_name: str) -> Any`**: Este método permite obtener un objeto de tipo json.

3. **Ejemplos de Uso**
```py

from redisfacade.facade import RedisFacade
from typing import Any

if __name__ == "__main__":
   # inicializar singleton
   redisdb = RedisFacade()

   # guardar datos de tipo clave - valor
   redisdb.set_key_value(0, "hola", "mundo", ttl=timedelta(days=3))

   # obtener datos de clave en especifico
   value: Any = redisdb.get_key_value(0, "hola")
   print(value)
   
   # guardar datos en lista
   is_save: bool = redisdb.set_list_str(0, "mylist", ["hola", "mundo", "beetmann"])
   print(is_save)
   
   # obtener datos de lista
   list = redisdb.get_list_str(0, "mylist")
   print(list)
   
   # pop del primer elemento de la lista
   list = redisdb.pop_list_str(0, "mylist")
   print(list)
   
   # tamaño de lista
   print(redisdb.len_list(0, "mylist"))
   
   # Guardar dato de tipo json
   is_saved: bool 
   is_saved = redisdb.set_json_data(0, "json_1", "1", "hola_mundo", ttl=timedelta(days=3))
   print(is_saved)
   # obtener dato de tipo json
   is_saved = redisdb.set_json_data(0, "json_1", "2", {"hola": "mundo"}, ttl=timedelta(days=3))
   print(is_saved)

   # obtine una llave de un json
   json_value_1 = redisdb.get_key_json_data(0, "json_1", "3", ttl=timedelta(days=3))
   print(json_value_1)
   
   # obtine un json completo
   json_value = redisdb.get_json_data(0, "json_1")
   print(json_value)

```

---

By: Alan Medina ⚙️
