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
    assert fake.calls == ["power(SpectraIII,3,30)", "laser(SpectraIII,3,on)",
                          "laser(SpectraIII,3,off)"]  # fmt: skip


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
