from ClashRecruit.services.builder_base_leagues import (
    builder_base_league_id_from_trophies,
    builder_base_league_name,
)


def test_builder_base_league_id_from_trophies_maps_thresholds():
    assert builder_base_league_id_from_trophies(0) == 1
    assert builder_base_league_id_from_trophies(99) == 1
    assert builder_base_league_id_from_trophies(100) == 2
    assert builder_base_league_id_from_trophies(1200) == 13
    assert builder_base_league_id_from_trophies(2200) == 22
    assert builder_base_league_id_from_trophies(6200) == 42
    assert builder_base_league_id_from_trophies(9999) == 42


def test_builder_base_league_id_from_trophies_can_treat_zero_as_no_requirement():
    assert builder_base_league_id_from_trophies(
        0,
        zero_as_no_requirement=True,
    ) == 0
    assert builder_base_league_id_from_trophies(
        1,
        zero_as_no_requirement=True,
    ) == 1


def test_builder_base_league_name_formats_known_values():
    assert builder_base_league_name(0) == "No Builder Base Requirement"
    assert builder_base_league_name(1) == "Wood V"
    assert builder_base_league_name(42) == "Diamond"
    assert builder_base_league_name(999) == "Unknown"
