###############################################################################
# (c) Copyright 2025 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import json

from typer.testing import CliRunner

from LbProdRun.__main__ import app

runner = CliRunner()


RUN3_MOORE_CONFIG = {
    "spec_version": 1,
    "application": {
        "data_pkgs": ["SprucingConfig.v25r5"],
        "name": "Franklin",
        "number_of_processors": 1,
        "version": "v1r9999",
        "event_timeout": None,
    },
    "options": {
        "entrypoint": "SprucingConfig.Spruce25.Sprucing_production_physics_pp_Collision25c0:turbospruce",
        "extra_options": {
            "input_process": "Hlt2",
            "write_options_to_fsr": True,
            "process": "TurboSpruce",
            "input_type": "RAW",
            "input_raw_format": 0.5,
            "data_type": "Upgrade",
            "simulation": False,
            "geometry_version": "run3/2025-v00.01",
            "conditions_version": "master",
            "output_type": "ROOT",
        },
        "extra_args": [],
    },
    "db_tags": {},
    "input": {
        "files": ["./320171_00080000_0002.raw"],
        "first_event_number": 0,
        "tck": "",
        "xml_file_catalog": "pool_xml_catalog.xml",
        "xml_summary_file": "summaryMoore_00289988_00000004_1.xml",
        "n_of_events": -1,
        "run_number": "320171",
    },
    "output": {
        "prefix": "00289988_00000004_1",
        "types": [
            "b2cc.dst",
            "b2oc.dst",
            "b2oclow.dst",
            "bandq.dst",
            "bandqlow.dst",
            "bnoc.dst",
            "bnoclow.dst",
            "charmcpv.dst",
            "charmlow.dst",
            "charmrare.dst",
            "charmspectr.dst",
            "ift.dst",
            "iftlow.dst",
            "qee.dst",
            "qeelow.dst",
            "rd.dst",
            "rdlow.dst",
            "trackeff.dst",
        ],
    },
}


def test_franklin_run3_moore(tmp_path, monkeypatch):
    tmp_path = tmp_path / "prod_spec.json"
    tmp_path.write_text(json.dumps(RUN3_MOORE_CONFIG))
    result = runner.invoke(app, [str(tmp_path), "--verbose", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "Franklin/v1r9999" in result.output
    assert (
        "SprucingConfig.Spruce25.Sprucing_production_physics_pp_Collision25c0:turbospruce"
        in result.output
    )
    assert "ProdConf" not in result.output

    # monkeypatch.setattr("os.execvpe", lambda *x: True)
    # result = runner.invoke(app, str(tmp_path))
    # assert result.exit_code == 0
    # assert "DaVinci/v45r8" in result.stdout
