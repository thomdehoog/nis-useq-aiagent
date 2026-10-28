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
        "port": {"position": 1, "positions": 4},
        "disk": {"shutter_open": False, "speed_rpm": 4000},
        "piezo_z": False,
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


# -- camera settings and the incubator ---------------------------------------------------


def test_reads_the_camera_with_its_frames(client):
    camera = client.request("get_camera")
    assert camera["format"] == "FMT 1x1 16" and camera["averaging"] == 1
    assert camera["integration"] == 1 and camera["width_px"] == 2048


def test_sets_binning_roi_and_averaging(client, fake):
    roi = {"left": 0, "top": 0, "right": 1024, "bottom": 1024}
    camera = client.request("set_camera", binning=2, roi=roi, averaging=4)
    assert camera["format"] == "FMT 2x2 16" and camera["roi"] == roi and camera["averaging"] == 4
    assert fake.calls == ["format(FMT 2x2 16)", "roi(0,0,1024,1024)", "averaging(4)"]


def test_a_format_the_camera_lacks_is_reported(client, fake):
    with pytest.raises(RuntimeError, match="no format 'FMT 3x3 16'; it kept 'FMT 1x1 16'"):
        client.request("set_camera", binning=3)


@pytest.mark.parametrize(
    ("args", "message"),
    [
        ({"roi": {"left": 0, "top": 0, "right": 4096, "bottom": 100}}, "inside the sensor"),
        ({"roi": {"left": 10, "top": 0, "right": 5, "bottom": 100}}, "inside the sensor"),
        ({"averaging": 0}, "from 1 to 256"),
        ({"binning": 2, "format": "FMT 2x2 16"}, "not both"),
        ({"binning": 16}, "from 1 to 8"),
        ({}, "nothing to change"),
    ],
)
def test_a_camera_change_is_checked_first(client, fake, args, message):
    with pytest.raises(ValueError, match=message):
        client.request("set_camera", **args)
    assert fake.calls == []


def test_reads_an_incubator(client, fake):
    assert client.request("get_incubator")["gas_percent"] == 0.0  # none: zeros, as NIS
    fake.incubators["Okolab"] = {
        "gas_percent": 5.0,
        "target_gas_percent": 5.0,
        "pressure_mbar": 1013.0,
        "target_pressure_mbar": 1013.0,
    }
    assert client.request("get_incubator", key="Okolab")["gas_percent"] == 5.0


# -- light path port, spinning disk, piezo Z, safe state -----------------------------------


def test_sends_the_light_to_a_port_and_runs_the_disk(client, fake):
    state = client.request("set_port", port=2, disk_speed_rpm=4000, disk_shutter=True)
    assert state["port"]["position"] == 2 and state["disk"]["shutter_open"] is True
    assert fake.calls == ["port(2)", "disk_speed(4000)", "disk_shutter(open)"]
    with pytest.raises(ValueError, match="from 0 to 4"):
        client.request("set_port", port=7)


def test_a_piezo_moves_only_where_there_is_one_and_only_a_little(client, fake):
    with pytest.raises(RuntimeError, match="no piezo Z drive"):
        client.request("move_piezo_z", distance_um=5)
    fake.piezo = 0.0
    assert client.request("move_piezo_z", distance_um=-5) == {"moved_um": -5}
    with pytest.raises(ValueError, match="at most 50 um"):
        client.request("move_piezo_z", distance_um=80)
    assert client.request("move_piezo_z", center=True) == {"centered": True}
    assert fake.calls == ["piezo(-5)", "piezo(center)"]


def test_safe_state_switches_off_everything_that_lights_the_sample(client, fake):
    fake.lasers["SpectraIII"][2]["on"] = True  # 475 nm
    fake.shutters["EPI"] = True
    fake.disk["shutter_open"] = True
    fake.lights["DIA"]["on"] = True
    assert client.request("safe_state") == {
        "lasers_off": [475],
        "shutters_closed": ["EPI", "spinning disk"],
        "lights_off": ["DIA"],
        "failed": [],
    }
    assert not fake.lasers["SpectraIII"][2]["on"] and not fake.lights["DIA"]["on"]
    assert client.request("safe_state")["lasers_off"] == []  # nothing left to switch off


def test_a_power_nis_does_not_read_back_is_noted(client, fake):
    fake.set_laser_power = lambda laser, index, power: None  # as on the Ti2 simulator
    reply = client.request("set_laser", wavelength_nm=405, power=30)
    assert reply["power"] == 0 and "not the 30 asked" in reply["note"]


def test_no_roi_is_the_full_sensor(client, fake):
    fake.roi = {"left": 0, "top": 0, "right": 0, "bottom": 0}  # what NIS says without one
    assert client.request("get_camera")["roi"] == {
        "left": 0, "top": 0, "right": 2048, "bottom": 2048,
    }  # fmt: skip
