# Fraud Game (Python)

A console roguelike game inspired by **Rogue (1980)**  with procedural dungeon generation, implemented in **Python 3.12**. \
The game is fully turn-based: every player action triggers actions from enemies.

Консольная игра в стиле **Rogue (1980)** с генерацией
подземелий, реализованная на **Python 3.12**. \
Игра полностью пошаговая: каждое действие игрока запускает действия
противников.

------------------------------------------------------------------------

# Features. Особенности проекта

-   21 procedurally generated dungeon levels \
    21 случайным оразом сгенерированный уровень подземелий
-   9 rooms per level \
    9 комнат на каждом уровне
-   Rooms connected by corridors (guaranteed connectivity) \
    Комнаты соединены коридорами (гарантированная связность)
-   Turn-based combat system \
    Пошаговая система боя
-   6 enemy types with unique behaviour \
    6 типов уникальных противников с разным поведением
-   Inventory and item system \
    Инвентарь и система предметов
-   Fog of War \
    Туман войны
-   Game statistics and leaderboard \
    Система статистики и таблица рекордов
-   Save/load system (JSON) \
    Сохранение и загрузка игрового прогресса (JSON)
-   Terminal-based interface \
    Консольный интерфейс





------------------------------------------------------------------------

# Architecture. Архитектура

    .
    ├── common              # Общие константы
    │   ├── characters.py
    │   ├── constants.py
    │   ├── drawing_const.py
    │   ├── keymap.py
    │   └── playground.py
    ├── controller          # Центр управления игрой
    │   └── conrtoller.py
    ├── core                # Отображение и ввод пользователя
    │   ├── command_interpreter.py
    │   ├── drawing.py
    │   ├── flat_render.py
    │   ├── main_render.py
    │   ├── menu_render.py
    │   ├── raycasting.py
    │   └── terminal.py
    ├── datalayer            # Сохранение и загрузка данных
    │   ├── loader.py
    │   └── records.py
    ├── domain               # Игровая логика
    │   ├── adapter.py
    │   ├── bresenham.py
    │   ├── dungeon.py
    │   ├── entity.py
    │   ├── generator.py
    │   ├── layout.py
    │   ├── model_factory.py
    │   ├── model.py
    │   ├── monsters.py
    │   ├── navigator.py
    │   └── player.py
    └── main.py              # Точка входа


### Domain

  
Contains all gameplay logic \
Содержит всю игровую логику:

-   dungeon generation \
    генерацию уровней
-   combat mechanics \
    систему боя
-   monster behaviour \
    поведение монстров
-   player control \
    управление персонажем
-   item system \
    работу предметов
-   game rules \
    правила игры


### Core

Responsible for: \
Отвечает за:

-   map rendering \
    отрисовку карты
-   UI rendering \
    отображение интерфейса
-   user input handling \
    ввод пользователя

### DataLayer

Responsible for: \
Отвечает за:

-   saving progress \
    сохранение прогресса
-   loading game sessions \
    загрузку игровой сессии
-   leaderboard records \
    таблицу рекордов

Data is stored in JSON format \
Формат хранения --- **JSON**.

------------------------------------------------------------------------

------------------------------------------------------------------------

# Game Entities. Игровые сущности

## Game Session. Игровая сессия

Stores:  
Хранит:

- current level  
  текущий уровень
- player character  
  персонажа
- gameplay statistics  
  статистику прохождения
- player progress  
  прогресс игрока


## Level. Уровень

Contains:  
Содержит:

- 9 rooms  
  9 комнат
- corridors connecting rooms  
  коридоры
- enemies  
  противников
- items  
  предметы
- entrance point  
  точку входа
- exit point  
  точку выхода


## Player. Персонаж

Attributes:  
Характеристики:

- `health` — health points  
  здоровье
- `max_health` — maximum health  
  максимальное здоровье
- `dexterity` — affects hit chance  
  ловкость
- `strength` — affects damage  
  сила
- `weapon` — equipped weapon  
  оружие

Additional data: \
Дополнительно:

- backpack / inventory  
  рюкзак
- treasure count  
  количество сокровищ
- gameplay statistics  
  статистика действий


## Backpack. Рюкзак

Stores:  
Хранит:

- food  
  еду
- potions  
  эликсиры
- scrolls  
  свитки
- weapons  
  оружие
- treasures  
  сокровища

Limitations: \
Ограничения:

- maximum **9 items of each type**  
  максимум **9 предметов каждого типа**


## Enemies  
## Противники

Enemy types:  
Типы врагов:

| Type | Symbol | Feature | Особенности |
|-----|-----|----------|----------|
| Zombie | Z | high HP |  высокий HP
| Vampire | V | first attack always misses | первый удар по нему — промах
| Ghost | G | teleport ability |телепортация |
| Ogre | O | powerful attacks |сильные атаки |
| Snake | S | diagonal movement |диагональное движение |


Each enemy has:  
Каждый враг имеет:

- health  
  здоровье
- strength  
  силу
- dexterity  
  ловкость
- hostility / aggression  
  враждебность

------------------------------------------------------------------------

# Item System. Система предметов

Item categories:  
Типы предметов:

### Treasures. Сокровища

- dropped by monsters  
  выпадают из монстров
- increase final score  
  увеличивают итоговый счет

### Food. Еда

- restores player health  
  восстанавливает здоровье

### Potions. Эликсиры

- temporarily increase player attributes  
  временно увеличивают характеристики

### Scrolls. Свитки

- permanently increase player attributes  
  постоянно увеличивают характеристики

### Weapons. Оружие

- affects damage calculation  
  влияет на формулу урона

------------------------------------------------------------------------

# Combat System. Система боя

Combat consists of **three stages**:  
Бой происходит в **3 этапа**:

1. Hit check  
   Проверка попадания
2. Damage calculation  
   Расчет урона
3. Damage application  
   Применение урона

Hit probability depends on:  
Формула попадания зависит от:

- attacker dexterity  
  ловкости атакующего
- target dexterity  
  ловкости цели

Damage calculation depends on:  
Формула урона зависит от:

- strength  
  силы
- weapon modifiers  
  оружия

------------------------------------------------------------------------

# Level Generation. Генерация уровней

Each level: \
Каждый уровень:

- contains **9 rooms of random size**  
  содержит **9 комнат случайного размера**
- rooms are connected with corridors  
  комнаты соединены коридорами
- the room graph is always **connected**  
  граф комнат всегда **связный**

Guaranteed: \
Гарантируется:

- one start room  
  одна стартовая комната
- one exit room  
  одна конечная комната

------------------------------------------------------------------------

# Fog of War

The game implements a **fog of war system**:  
Используется система **тумана войны**:

- unexplored rooms are hidden  
  неизвестные комнаты не отображаются
- visited rooms show only walls  
  посещенные комнаты показывают только стены
- the current room is fully visible  
  текущая комната полностью видна

Visibility calculation uses:

Видимость рассчитывается с помощью:

- Ray Casting
- Bresenham line algorithm  
  алгоритма Брезенхэма

------------------------------------------------------------------------

# Controls. Управление

| Key | Action in 2D view| Action in 3D view
|-----|-----|-----|
| w | move up / вверх | move forward / вперед |
| s | move down / вниз | move backward / назад |
| a | move left / влево | rotate left / поворот налево |
| d | move right / вправо| rotate right / поворот направо |
| h | use weapon | использовать оружие |
| j | eat food | съесть еду |
| k | drink potion | выпить зелье | 
| u | read scroll | прочитать свиток |
| m | open door with key | открыть дверь |



When using items a menu appears: \
При использовании предметов появляется список: 
- choose item (1 - 9) \
  Выберите предмет (1–9)


------------------------------------------------------------------------

# Statistics. Статистика

The game tracks detailed statistics:

В игре собирается статистика:

- collected treasures  
  количество сокровищ
- reached level  
  достигнутый уровень
- defeated enemies  
  побежденные противники
- food eaten  
  съеденная еда
- potions used  
  выпитые эликсиры
- scrolls used  
  прочитанные свитки
- hits dealt  
  нанесенные удары
- hits received  
  полученные удары
- tiles explored  
  пройденные клетки

All runs are stored and displayed in a **leaderboard**.

Все попытки сохраняются и отображаются в **таблице рекордов**.

------------------------------------------------------------------------

# Save System. Сохранение игры

Game progress is saved in **JSON format**.

Прогресс сохраняется в **JSON**.

Saved data includes:

Сохраняется:

- current level  
  текущий уровень
- player state  
  состояние игрока
- dungeon map  
  карта уровня
- entity positions  
  позиции всех сущностей
- gameplay statistics  
  статистика

The game can continue from the last saved session. \
После перезапуска можно продолжить последнюю сессию.

------------------------------------------------------------------------
# Running the Project. Запуск проекта

```bash
python3 -m main
```

------------------------------------------------------------------------

# Requirements. Требования

Python 3.12

Linux and MacOS are supported directly. \
Linux / MacOS поддерживаются напрямую.

On Windows it is recommended to use WSL. \
На Windows рекомендуется использовать WSL.

------------------------------------------------------------------------

# Improvements. Улучшения


key and door mechanics \
система ключей и дверей

dynamic difficulty balancing \
динамическая балансировка сложности

new enemy Mimic \
новый враг Mimic

experimental 3D ray casting mode \
режим 3D Ray Casting


