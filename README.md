# Boring Dungeon
Boring Dungeon is a simple dungeon exploration game, in which the goal is to
explore a procedurally generated dungeon in order to go as deep as possible, while
fighting monsters with the gear you loot along the way.

**Disclaimer**. The game may crash sometimes. If it does, please contact me, send
me the seed and level in which you were when it happened, and the error message you
got.

## How to play
**In the menu**, input the generation seed or leave the field blank, and press the
play button to start a new game.

**In the game**, use WASD, or the arrow keys to move around. Press E, or I to open
your inventory. While exploring a level, the exclamation points represent rooms you
can visit, and stairs are exits to the next level. While inside a room, doors are
your way out of the room back to the level, red arrows are enemies and flickering
lights on the grounds represent items you can pickup. While fighting, left click to
attack the enemy, and right click to block.

## Mechanics
**Levels**: The amount of rooms present in the level is equal to the current
difficulty (AKA level). There will always be 2 exits, or 1 if the 2nd couldn't be
generated.

**Rooms**: Items are generated following a loot table, which varies with the current
difficulty. Doors are corresponding to the possible entrances in the level (if an
exclamation mark has a path north and east of it in the level, then the room will
have doors on the north and the east). The amount of enemies is a random number
between 0 and the current difficulty, halved.

**Items**: Items you *equip* (not the ones you store) in your inventory have a
corresponding weight which will slow down your attacks in combat. Protection from
your armor reduce damage taken, but you will always take at least 1 damage from a
hit.

**Combat**: Your attack speed is the number of attacks per second you can do. It is
determined by subtracting the weight of your *equipped* gear to your base speed.
Blocking will double your protection from enemy attacks, but you can only block 0.75
after having attacked, and you can't do both at the same time.
