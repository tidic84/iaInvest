extends StaticBody3D
class_name TrainChassis

signal floor_placed(grid_pos: Vector2i)
signal speed_changed(speed: float)

const GRID_SIZE: float = 1.0

@export var max_width: int = 2
@export var max_length: int = 5

var grid_cells: Dictionary = {} # Vector2i -> { "floor": bool, "item": Node3D }
var floor_count: int = 0
var is_on_rails: bool = false

# Movement
var speed: float = 0.0
var max_speed: float = 4.0  # Handcar cap — upgrade to engine for more
var pump_impulse: float = 0.45  # Small per-pump kick
var friction: float = 0.35  # Low — momentum carries between pumps
var distance_traveled: float = 0.0

# Path following
var rail_curve: Curve3D = null
var rail_progress: float = 0.0

func _ready() -> void:
	if get_meta("is_preview", false):
		collision_layer = 0
		collision_mask = 0
		return
	add_to_group("wagon")
	add_to_group("chassis")
	collision_layer = 8  # Layer 4 = Train
	collision_mask = 1
	# Run BEFORE the player (default=0) so constant_linear_velocity is set
	# before CharacterBody3D.move_and_slide() reads get_platform_velocity().
	process_physics_priority = -1

func _physics_process(delta: float) -> void:
	if get_meta("is_preview", false):
		return
	if not is_on_rails:
		return
	if absf(speed) < 0.01:
		if speed != 0.0:
			speed = 0.0
			speed_changed.emit(0.0)
			_set_platform_velocity(Vector3.ZERO)
		return

	speed = move_toward(speed, 0.0, friction * delta)
	var ds: float = speed * delta
	distance_traveled += absf(ds)

	# Set constant_linear_velocity BEFORE moving so that the player's
	# move_and_slide() (which runs at priority 0, after us at -1) sees
	# the correct platform velocity via get_platform_velocity().
	var forward: Vector3 = -global_transform.basis.z
	_set_platform_velocity(forward * speed)

	if rail_curve != null and rail_curve.get_baked_length() > 0.0:
		var total: float = rail_curve.get_baked_length()
		rail_progress = clampf(rail_progress + ds, 0.0, total)
		var sample: Transform3D = rail_curve.sample_baked_with_rotation(rail_progress, true, true)
		global_position = sample.origin
		var tangent: Vector3 = -sample.basis.z.normalized()
		if tangent.length() > 0.001:
			look_at(global_position + tangent, Vector3.UP)
	else:
		global_position.z += ds

func pump(direction: float = 1.0) -> void:
	if not is_on_rails:
		return
	speed = clampf(speed + pump_impulse * direction, -max_speed, max_speed)
	speed_changed.emit(speed)

func snap_to_rails() -> void:
	is_on_rails = true
	var terrain: TerrainGenerator = _find_terrain()
	if terrain:
		rail_curve = terrain.get_rail_curve()
		if rail_curve:
			rail_progress = rail_curve.get_closest_offset(global_position)
			var sample: Transform3D = rail_curve.sample_baked_with_rotation(rail_progress, true, true)
			global_position = sample.origin
			var tangent: Vector3 = -sample.basis.z.normalized()
			if tangent.length() > 0.001:
				look_at(global_position + tangent, Vector3.UP)

func _find_terrain() -> TerrainGenerator:
	var nodes := get_tree().get_nodes_in_group("terrain")
	if nodes.size() > 0:
		return nodes[0] as TerrainGenerator
	return null

func _set_platform_velocity(vel: Vector3) -> void:
	constant_linear_velocity = vel
	for child in get_children():
		if child is StaticBody3D:
			child.constant_linear_velocity = vel

# --- Grid system ---

func get_grid_position(world_pos: Vector3) -> Vector2i:
	var local_pos := to_local(world_pos)
	var gx := int(round(local_pos.x / GRID_SIZE))
	var gz := int(round(local_pos.z / GRID_SIZE))
	return Vector2i(
		clampi(gx, _grid_min(max_width), _grid_max(max_width)),
		clampi(gz, _grid_min(max_length), _grid_max(max_length))
	)

func _grid_min(size: int) -> int:
	return -(size / 2)

func _grid_max(size: int) -> int:
	return (size - 1) / 2

func grid_to_local(grid_pos: Vector2i) -> Vector3:
	return Vector3(
		grid_pos.x * GRID_SIZE,
		0.0,
		grid_pos.y * GRID_SIZE
	)

func grid_to_world(grid_pos: Vector2i) -> Vector3:
	return to_global(grid_to_local(grid_pos))

func can_place_floor(grid_pos: Vector2i) -> bool:
	if grid_pos.x < _grid_min(max_width) or grid_pos.x > _grid_max(max_width):
		return false
	if grid_pos.y < _grid_min(max_length) or grid_pos.y > _grid_max(max_length):
		return false
	if grid_cells.has(grid_pos) and grid_cells[grid_pos].floor:
		return false
	if floor_count == 0:
		return true
	return _has_adjacent_floor(grid_pos)

func place_floor(grid_pos: Vector2i) -> void:
	if not grid_cells.has(grid_pos):
		grid_cells[grid_pos] = { "floor": false, "item": null }
	grid_cells[grid_pos].floor = true
	floor_count += 1
	floor_placed.emit(grid_pos)

func can_place_item(grid_pos: Vector2i) -> bool:
	if not grid_cells.has(grid_pos):
		return false
	if not grid_cells[grid_pos].floor:
		return false
	if grid_cells[grid_pos].item != null:
		return false
	return true

func place_item(grid_pos: Vector2i, item: Node3D) -> void:
	grid_cells[grid_pos].item = item

func remove_item(grid_pos: Vector2i) -> void:
	if grid_cells.has(grid_pos) and grid_cells[grid_pos].item:
		grid_cells[grid_pos].item = null

func has_floor_at(grid_pos: Vector2i) -> bool:
	return grid_cells.has(grid_pos) and grid_cells[grid_pos].floor

func _has_adjacent_floor(grid_pos: Vector2i) -> bool:
	var neighbors: Array[Vector2i] = [
		Vector2i(grid_pos.x + 1, grid_pos.y),
		Vector2i(grid_pos.x - 1, grid_pos.y),
		Vector2i(grid_pos.x, grid_pos.y + 1),
		Vector2i(grid_pos.x, grid_pos.y - 1),
	]
	for n in neighbors:
		if grid_cells.has(n) and grid_cells[n].floor:
			return true
	return false

func take_damage(amount: float) -> void:
	pass # TODO: chassis durability
