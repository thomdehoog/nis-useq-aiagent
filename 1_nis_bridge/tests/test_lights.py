"""Lights, lasers and filter changers through the bridge, with the fake NIS.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-28
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

import pytest

# -- lights -----------------------------------------------------------------------------


def test_reads_the_lights(client):
    assert client.request("get_lights") == [
        {"name": "DIA", "on": False, "voltage": None, "iris": 0.5}
    ]


def test_switches_a_light_and_sets_its_iris(client, fake):
    light = client.request("set_light", name="DIA", on=True, iris=0.8)
    assert light == {"name": "DIA", "on": True, "voltage": None, "iris": 0.8}
    assert fake.calls == ["iris(DIA,0.8)", "light(DIA,on)"]


def test_a_light_change_is_checked_first(client, fake):
    with pytest.raises(ValueError, match="unknown light 'LED'; NIS has: DIA"):
        client.request("set_light", name="LED", on=True)
    with pytest.raises(ValueError, match="does not control the voltage of 'DIA'"):
        client.request("set_light", name="DIA", voltage=6.0, on=True)
    with pytest.raises(ValueError, match="nothing to change"):
        client.request("set_light", name="DIA")
    with pytest.raises(ValueError, match="'on' must be true or false"):
        client.request("set_light", name="DIA", on="yes")
    assert fake.calls == []


def test_sets_a_voltage_where_nis_controls_it(client, fake):
    fake.lights["Halogen"] = {"on": True, "voltage": 3.0, "iris": None}
    assert client.request("set_light", name="Halogen", voltage=6.04)["voltage"] == 6.0


# -- lasers -----------------------------------------------------------------------------


def test_reads_the_laser_lines(client):
    (laser,) = client.request("get_lasers")
    assert laser["name"] == "SpectraIII" and len(laser["lines"]) == 8
    assert laser["lines"][0] == {
        "line": 1, "name": "405 nm", "wavelength_nm": 405, "on": False, "power": 0,
        "power_steps": 101,
    }  # fmt: skip


def test_a_line_is_chosen_by_number_or_wavelength(client, fake):
    reply = client.request("set_laser", wavelength_nm=475, on=True, power=30)
    assert reply["laser"] == "SpectraIII" and reply["line"] == 3
    assert reply["on"] is True and reply["power"] == 30
    assert client.request("set_laser", line=3, on=False)["on"] is False
    # line 3 is NIS's index 2: NIS counts laser lines from 0
    assert fake.calls == ["power(SpectraIII,2,30)", "laser(SpectraIII,2,on)",
                          "laser(SpectraIII,2,off)"]  # fmt: skip


def test_a_laser_change_is_checked_first(client, fake):
    with pytest.raises(ValueError, match="one line; SpectraIII has 1: 405 nm"):
        client.request("set_laser", wavelength_nm=488, on=True)
    with pytest.raises(ValueError, match="from 0 to 100"):
        client.request("set_laser", line=1, power=150)
    with pytest.raises(ValueError, match="from 0 to 100"):
        client.request("set_laser", line=1, power=12.5)
    with pytest.raises(ValueError, match="unknown laser 'Celesta'"):
        client.request("set_laser", laser="Celesta", line=1, on=True)
    with pytest.raises(ValueError, match="nothing to change"):
        client.request("set_laser", line=1)
    assert fake.calls == []


def test_with_two_light_sources_the_laser_must_be_named(client, fake):
    fake.lasers["Celesta"] = [{"name": "640 nm", "wavelength_nm": 640, "on": False, "power": 0}]
    with pytest.raises(ValueError, match="unknown laser None"):
        client.request("set_laser", line=1, on=True)
    assert client.request("set_laser", laser="Celesta", line=1, on=True)["on"] is True


# -- filter changers ---------------------------------------------------------------------


def test_reads_the_filter_changers(client):
    turret = client.request("get_filters")[0]
    assert turret["name"] == "Turret-Up" and turret["position"] == 1
    assert turret["filters"] == {"1": "DAPI", "2": "GFP", "3": "mCherry", "4": "", "5": "Cy5",
                                 "6": "Empty"}  # fmt: skip


def test_turns_a_changer_by_position_or_by_filter(client, fake):
    reply = client.request("set_filter", changer="Turret-Up", filter="mCherry")
    assert reply == {"changer": "Turret-Up", "position": 3, "filter": "mCherry"}
    assert client.request("set_filter", changer="Turret-Up", position=5)["filter"] == "Cy5"
    assert fake.calls == ["filter(Turret-Up,3)", "filter(Turret-Up,5)"]


def test_a_filter_change_is_checked_first(client, fake):
    with pytest.raises(ValueError, match="unknown filter changer 'Wheel'"):
        client.request("set_filter", changer="Wheel", position=1)
    with pytest.raises(ValueError, match="one 'filter' of Turret-Up: 1: DAPI"):
        client.request("set_filter", changer="Turret-Up", filter="FITC")
    with pytest.raises(ValueError, match="positions 1 to 6"):
        client.request("set_filter", changer="Turret-Up", position=9)
    assert fake.calls == []


# -- shutters, the light path, PFS offset and dish, heat stages ----------------------------


def test_opens_and_closes_a_shutter(client, fake):
    assert client.request("get_shutters")[0] == {"name": "DIA LED", "open": False}
    assert client.request("set_shutter", name="DIA LED", open=True) == {
        "name": "DIA LED", "open": True,
    }  # fmt: skip
    with pytest.raises(ValueError, match="unknown shutter 'Laser'; NIS has: DIA LED, EPI"):
        client.request("set_shutter", name="Laser", open=True)
    assert fake.calls == ["shutter(DIA LED,open)"]


def test_reads_and_sets_the_light_path(client, fake):
    path = client.request("get_light_path")
    assert path == {
        "condenser": {"position": 1, "positions": 7},
        "apertures": {"epi_field": {"size": 100.0, "steps": 1001}},
        "zoom": {"zoom": 1.0, "manual": True},
        "analyzer": {"inserted": False},
    }
    path = client.request(
        "set_light_path", condenser=3, aperture="epi_field", size=60, analyzer=True
    )
    assert path["condenser"]["position"] == 3 and path["apertures"]["epi_field"]["size"] == 60
    assert path["analyzer"]["inserted"] is True
    assert fake.calls == ["condenser(3)", "aperture(1,60)", "analyzer(in)"]


def test_a_light_path_change_is_checked_before_anything_moves(client, fake):
    with pytest.raises(ValueError, match="turned by hand"):
        client.request("set_light_path", condenser=2, zoom=1.5)
    with pytest.raises(ValueError, match="unknown aperture 'field'; NIS controls: epi_field"):
        client.request("set_light_path", aperture="field", size=10)
    with pytest.raises(ValueError, match="from 0 to 7"):
        client.request("set_light_path", condenser=9)
    with pytest.raises(ValueError, match="nothing to change"):
        client.request("set_light_path")
    assert fake.calls == []


def test_a_zoom_nis_controls_goes_to_its_closest_step(client, fake):
    fake.zoom_state["manual"] = False
    assert client.request("set_light_path", zoom=1.4)["zoom"]["zoom"] == 1.5


def test_an_analyzer_that_does_not_move_is_an_error(client, fake):
    fake.analyzer_moves = False  # as on the Ti2 simulator
    with pytest.raises(RuntimeError, match="analyzer did not move"):
        client.request("set_light_path", analyzer=True)


def test_pfs_offset_and_dish(client, fake):
    pfs = client.request("get_pfs")
    assert pfs["offset"] == 3000 and pfs["dish"] == "glass"
    pfs = client.request("set_pfs_offset", offset=3200, dish="plastic")
    assert pfs["offset"] == 3200 and pfs["dish"] == "plastic"
    with pytest.raises(ValueError, match="one of glass, plastic"):
        client.request("set_pfs_offset", dish="quartz")


def test_reads_the_heat_stages(client, fake):
    assert client.request("get_environment") == {"heat_stages": []}
    fake.heat_stages["Tokai Hit"] = 37.0
    assert client.request("get_environment")["heat_stages"] == [
        {"name": "Tokai Hit", "temperature": 37.0, "status": "holding"}
    ]
