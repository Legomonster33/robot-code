from library import *

studio = Studio("robotTubeUi.gen.fs")

wall_thickness = (
    CustomEnum("WallThickness", parent=studio)
    .add_value("ONE_SIXTEENTH", user_name='1/16"')
    .add_value("ONE_EIGHTH", user_name='1/8"')
    .add_custom()
)

custom_wall_thickness = custom_predicate(wall_thickness, parent=studio)

wall_predicate = UiPredicate("wallThickness", parent=studio)
wall_predicate.add(
    EnumAnnotation(
        wall_thickness, ui_hints=[UiHint.REMEMBER_PREVIOUS_VALUE, UiHint.SHOW_LABEL]
    )
)
If(custom_wall_thickness, parent=wall_predicate).add(
    LengthAnnotation("wallThickness", bound_spec=LengthBound.SHELL_OFFSET_BOUNDS)
)

tube_size = (
    CustomEnum("TubeSize", parent=studio)
    .add_value("ONE_BY_ONE", user_name="1x1")
    .add_value("TWO_BY_ONE", user_name="2x1")
    .add_custom()
)

tube_type = (
    CustomEnum("TubeType", parent=studio)
    .add_value("MAX_TUBE", user_name="MAXTube")
    .add_custom()
)

max_tube_type = (
    Enum("MaxTubeType", parent=studio)
    .add_value("NONE")
    .add_value("GRID")
    .add_value("MAX", user_name="MAX")
)

can_be_light = UiTestPredicate(
    "canBeLight", equal(max_tube_type.NONE) | equal(max_tube_type.GRID), parent=studio
).call()

type_predicates = EnumPredicates(tube_type, parent=studio)
size_predicates = EnumPredicates(tube_size, parent=studio)

is_max_tube = UiTestPredicate(
    "isMaxTube", ~size_predicates["CUSTOM"] & type_predicates["MAX_TUBE"], parent=studio
).call()

tube_predicate = UiPredicate("tubeSize", parent=studio)
tube_predicate.add(
    EnumAnnotation(
        tube_size,
        default="TWO_BY_ONE",
        ui_hints=[UiHint.REMEMBER_PREVIOUS_VALUE, UiHint.HORIZONTAL_ENUM],
    )
)

tube_if = If(size_predicates["CUSTOM"], parent=tube_predicate)
tube_if.add(LengthAnnotation("length", LengthBound.LENGTH_BOUNDS))
tube_if.add(LengthAnnotation("width", LengthBound.LENGTH_BOUNDS))

tube_if = tube_if.or_else()
tube_if.add(
    EnumAnnotation(
        tube_type,
        default="CUSTOM",
        ui_hints=[UiHint.REMEMBER_PREVIOUS_VALUE, UiHint.SHOW_LABEL],
    )
)

inner_if = If(
    size_predicates["TWO_BY_ONE"] & type_predicates["MAX_TUBE"], parent=tube_if
).add(
    EnumAnnotation(max_tube_type, user_name="Pattern type"),
)

If(can_be_light, parent=inner_if).add(
    BooleanAnnotation("isLight", user_name="Light"),
)

wall_if = If(
    size_predicates["CUSTOM"] | type_predicates["CUSTOM"], parent=tube_predicate
).add(wall_predicate.call())

fit = Enum("HoleFit", parent=studio).add_value("CLOSE").add_value("FREE")

size = (
    CustomEnum("HoleSize", parent=studio)
    .add_value("NO_8", user_name="#8")
    .add_value("NO_10", user_name="#10")
    .add_custom()
)

hole_predicate = UiPredicate("tubeHole", parent=studio)
# hole_predicate.register(If())


studio.print()
