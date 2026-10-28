"""Optical configurations: the backup file (optconf.py), and editing them through the bridge.

``data/optconf_ti2_simulator.xml`` is what BackupOptConf wrote on the Ti2 simulator
(NIS-Elements 6.10.02).

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-10-28
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

import re
from pathlib import Path

import pytest

from nis_bridge import optconf

SIMULATOR = Path(__file__).parent / "data" / "optconf_ti2_simulator.xml"


@pytest.fixture
def xml() -> str:
    return optconf.read(str(SIMULATOR))


def exposures(block: str) -> list[float]:
    return [float(v) for v in re.findall(r'<Exposure runtype="double" value="([^"]*)"', block)]


# -- the backup file ------------------------------------------------------------------


def test_reads_the_simulator_backup(xml):
    assert [name for _, _, name in optconf.blocks(xml)] == ["Spinning Disk (2):BF"]
    assert optconf.settings(optconf.find(xml, "BF")) == {
        "name": "Spinning Disk (2):BF",
        "objective": "Plan Apo VC 60xA WI DIC N2",
        "camera": "Flash4.0, 9Z0022",
        "format": "16-bit - No Binning",
        "light_path": "Spinning Disk (2)",
        "exposure_ms": 20.0,
        "max_exposure_ms": 1000.0,
        "binning": 1.0,
    }


def test_a_change_touches_only_what_it_says(xml):
    block = optconf.find(xml, "Spinning Disk (2):BF")
    changed = optconf.with_exposure(block, 37.5)
    assert set(exposures(changed)) == {37.5} and len(exposures(changed)) == len(exposures(block))
    assert changed.replace("37.500000000000000", "20.000000000000000") == block
    copy = optconf.renamed(block, 'A & "B"')
    assert optconf.name_of(copy) == 'A & "B"' and 'value="A &amp; &quot;B&quot;"' in copy
    assert copy.count('value="A &amp;') == 1  # the camera and channel names stay


def test_an_import_file_holds_one_configuration_and_the_rest_of_the_backup(xml):
    block = optconf.renamed(optconf.find(xml, "BF"), "copy")
    numbered = block.replace("<Opt0 ", "<Opt7 ", 1)[: -len("</Opt0>")] + "</Opt7>"
    out = optconf.only(xml, numbered)
    assert [name for _, _, name in optconf.blocks(out)] == ["copy"]
    assert "<Opt0 " in out and "<Opt7" not in out
    tail = xml[xml.index("</OpticalConfigs>") :]
    assert out.endswith(tail) and out.startswith(xml[: optconf.blocks(xml)[0][0]])


def test_find_wants_exactly_one_match(xml):
    with pytest.raises(KeyError, match="0 optical configurations match 'GFP'"):
        optconf.find(xml, "GFP")


def test_the_file_goes_back_as_utf16(tmp_path, xml):
    path = str(tmp_path / "out.xml")
    optconf.write(path, xml)
    assert Path(path).read_bytes() == SIMULATOR.read_bytes()


# -- through the bridge, with the fake NIS ---------------------------------------------


def test_reads_one_configuration(client):
    reply = client.request("get_optical_configuration", name="FITC")
    assert reply["name"] == "FITC" and reply["exposure_ms"] == 100.0
    with pytest.raises(ValueError, match="unknown optical configuration 'GFP'"):
        client.request("get_optical_configuration", name="GFP")


def test_an_edit_changes_the_exposure_and_keeps_a_backup(client, fake):
    reply = client.request("edit_optical_configuration", name="FITC", exposure_ms=250)
    assert reply["name"] == "FITC" and reply["exposure_ms"] == 250.0
    assert fake.saved_exposures["FITC"] == 250.0 and fake.configurations.count("FITC") == 1
    assert fake.calls[-1] == "import(FITC,1)"  # over the old one; never deleted first
    before = optconf.read(reply["backup"])  # the backup still has the old value
    assert optconf.settings(optconf.find(before, "FITC"))["exposure_ms"] == 100.0


def test_an_edit_is_checked_before_anything_changes(client, fake):
    with pytest.raises(ValueError, match="nothing to change"):
        client.request("edit_optical_configuration", name="FITC")
    with pytest.raises(ValueError, match="at most 1000"):
        client.request("edit_optical_configuration", name="FITC", exposure_ms=5000)
    with pytest.raises(ValueError, match="above 0"):
        client.request("edit_optical_configuration", name="FITC", exposure_ms=0)
    assert not any(call.startswith(("delete", "import")) for call in fake.calls)


def test_an_import_that_changes_nothing_is_an_error(client, fake):
    fake.import_fails = 2
    with pytest.raises(RuntimeError, match="'FITC' did not change"):
        client.request("edit_optical_configuration", name="FITC", exposure_ms=250)
    with pytest.raises(RuntimeError, match="added 0 optical configurations"):
        client.request("copy_optical_configuration", name="FITC", new_name="FITC 2")
    assert fake.saved_exposures["FITC"] == 100.0 and "FITC 2" not in fake.configurations


def test_a_copy_gets_a_new_name_and_the_changes(client, fake):
    reply = client.request(
        "copy_optical_configuration", name="FITC", new_name="FITC fast", exposure_ms=20
    )
    assert reply["name"] == "FITC fast" and reply["exposure_ms"] == 20.0
    assert fake.saved_exposures["FITC"] == 100.0 and fake.saved_exposures["FITC fast"] == 20.0
    plain = client.request("copy_optical_configuration", name="DAPI", new_name="DAPI 2")
    assert plain["exposure_ms"] == 100.0


def test_a_copy_never_takes_a_name_nis_has(client, fake):
    # NIS would ask in a dialog which one to keep, and wait for a click
    with pytest.raises(ValueError, match="already has an optical configuration 'DAPI'"):
        client.request("copy_optical_configuration", name="FITC", new_name="DAPI")
    with pytest.raises(ValueError, match="without ':'"):
        client.request("copy_optical_configuration", name="FITC", new_name="Path:New")
    assert not any(call.startswith("import") for call in fake.calls)


def test_imports_never_ask(client, fake):
    """Options 0 would ask in a dialog which configuration to keep; the bridge never uses it."""
    client.request("edit_optical_configuration", name="DAPI", exposure_ms=50)
    client.request("copy_optical_configuration", name="DAPI", new_name="DAPI 2")
    imports = [call for call in fake.calls if call.startswith("import")]
    assert imports == ["import(DAPI,1)", "import(DAPI 2,2)"]


def test_a_delete_keeps_a_backup(client, fake):
    reply = client.request("delete_optical_configuration", name="TxRed")
    assert reply["deleted"] == "TxRed" and "TxRed" not in fake.configurations
    assert "TxRed" in [name for _, _, name in optconf.blocks(optconf.read(reply["backup"]))]


def test_a_configuration_can_be_named_without_its_light_path(client, fake):
    fake.configurations.append("Spinning Disk (2):BF")
    fake.saved_exposures["Spinning Disk (2):BF"] = 20.0
    assert client.request("get_optical_configuration", name="BF")["exposure_ms"] == 20.0
