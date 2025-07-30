"""Test PegasusStatistics object."""

import pytest

from Pegasus.braindump import Braindump
from Pegasus.db.connection import ConnectionError
from Pegasus.statistics import PegasusStatistics, PegasusStatisticsError


@pytest.mark.parametrize(
    "submit_dirs, multiple_wf, expected",
    [
        (None, False, "."),
        ("", False, "."),
        ([], False, "."),
        (None, True, "*"),
        ("", True, "*"),
        ([], True, "*"),
    ],
)
def test_initialize_empty(submit_dirs, multiple_wf, expected):
    p = PegasusStatistics(submit_dirs=submit_dirs, multiple_wf=multiple_wf)
    p._initialize()
    assert p.submit_dirs == expected


@pytest.mark.parametrize(
    "submit_dirs, multiple_wf", [(["a"], False), (["a"], True),],
)
def test_initialize_single(caplog, submit_dirs, multiple_wf):
    p = PegasusStatistics(submit_dirs=submit_dirs, multiple_wf=multiple_wf)

    p._initialize(verbose=5)
    if multiple_wf is True:
        assert (
            "Single submit-dir is specified, but multiple-wf flag is set."
            in caplog.text
        )
    assert p.multiple_wf is False
    assert p.submit_dirs == submit_dirs[0]


@pytest.mark.parametrize(
    "submit_dirs, multiple_wf", [(["a", "b"], False), (["a", "b"], True),],
)
def test_initialize_multiple(caplog, submit_dirs, multiple_wf):
    p = PegasusStatistics(submit_dirs=submit_dirs, multiple_wf=multiple_wf)

    p._initialize(verbose=5)
    if multiple_wf is False:
        assert (
            "Multiple submit-dirs are specified, but multiple-wf flag is not set."
            in caplog.text
        )
    assert p.multiple_wf is True


@pytest.mark.parametrize(
    "statistics_level, attr_name",
    [
        ({"all"}, "calc_wf_summary"),
        ({"all"}, "calc_wf_stats"),
        ({"all"}, "calc_jb_stats"),
        ({"all"}, "calc_tf_stats"),
        ({"all"}, "calc_ti_stats"),
        ({"all"}, "calc_int_stats"),
        ({"summary"}, "calc_wf_summary"),
        ({"wf_stats"}, "calc_wf_stats"),
        ({"jb_stats"}, "calc_jb_stats"),
        ({"tf_stats"}, "calc_tf_stats"),
        ({"ti_stats"}, "calc_ti_stats"),
        ({"int_stats"}, "calc_int_stats"),
    ],
)
def test_statistics_level(statistics_level, attr_name):
    p = PegasusStatistics(statistics_level=statistics_level)

    p._initialize_statistics_levels()

    assert getattr(p, attr_name) is True


def test_check_args_jb_stats(caplog):
    p = PegasusStatistics()
    p._initialize(verbose=5)

    p.multiple_wf = True
    p.calc_jb_stats = True

    with pytest.raises(PegasusStatisticsError):
        p._check_args()
        assert (
            "Job breakdown statistics cannot be computed over multiple workflows"
            in caplog.text
        )


def test_check_args_is_uuid_config(caplog):
    p = PegasusStatistics()
    p._initialize(verbose=5)

    p.is_uuid = True
    with pytest.raises(PegasusStatisticsError):
        p._check_args()
        assert (
            "A config file is required if either is-uuid flag is set or submit-dirs is not set or set to *"
            in caplog.text
        )


def test_check_args_submit_dirs_config(caplog):
    p = PegasusStatistics()
    p._initialize(verbose=5)

    p.submit_dirs = "*"
    with pytest.raises(PegasusStatisticsError):
        p._check_args()
        assert (
            "A config file is required if either is-uuid flag is set or submit-dirs is not set or set to *"
            in caplog.text
        )


@pytest.mark.parametrize("name", ["is_uuid", "multiple_wf"])
def test_check_args_output_dir(caplog, name):
    p = PegasusStatistics()
    p._initialize(verbose=5)

    p.output_dir = []
    setattr(p, name, True)
    with pytest.raises(PegasusStatisticsError):
        p._check_args()
        assert (
            "Output directory option is required when calculating statistics over multiple workflows."
            in caplog.text
        )


@pytest.mark.parametrize(
    "name, value, expected",
    [
        ("is_uuid", True, "."),
        ("submit_dirs", "*", "*"),
        ("submit_dirs", "A", "A"),
        ("submit_dirs", ["A", "B"], ["A", "A"]),
    ],
)
def test_check_workflow_dir(mocker, name, value, expected):
    mocker.patch(
        "Pegasus.statistics.PegasusStatistics._check_braindump",
        return_value=Braindump(wf_uuid="A"),
    )

    p = PegasusStatistics()
    setattr(p, name, value)
    p._initialize(verbose=5)

    p._check_workflow_dir()
    assert p.wf_uuids == expected


@pytest.mark.parametrize(
    "name, value, expected",
    [
        (
            "ignore_db_inconsistency",
            True,
            "The tool is meant to be run after the workflow completion.",
        ),
        ("is_uuid", True, None),
        (
            "submit_dirs",
            "*",
            "Statistics have to be calculated on all workflows. Tool cannot check to see if all of them have finished. Ensure that all workflows have finished",
        ),
    ],
)
def test_check_workflow_state_simple(caplog, name, value, expected):
    p = PegasusStatistics()
    setattr(p, name, value)
    p._initialize(verbose=5)

    p._check_workflow_state()
    if expected:
        assert expected in caplog.text


@pytest.mark.parametrize(
    "submit_dirs, loading_complete, monitoring_running, expected",
    [
        ("A", True, True, None),
        ("A", True, False, None),
        (
            "A",
            False,
            True,
            "pegasus-monitord still running. Please wait for it to complete.",
        ),
        (["A", "B"], False, False, "Please run pegasus monitord in replay mode."),
    ],
)
def test_check_workflow_state(
    mocker, capsys, submit_dirs, loading_complete, monitoring_running, expected
):
    mocker.patch("Pegasus.tools.utils.loading_completed", return_value=loading_complete)
    mocker.patch(
        "Pegasus.tools.utils.monitoring_running", return_value=monitoring_running
    )

    p = PegasusStatistics(submit_dirs=submit_dirs)
    p._initialize(verbose=5)

    if expected is not None:
        with pytest.raises(PegasusStatisticsError):
            p._check_workflow_state()

        captured = capsys.readouterr()
        assert expected in captured.err


@pytest.mark.parametrize(
    "name, value, expected",
    [
        ("is_pmc", True, "Calculating statistics with use of PMC clustering"),
        (
            "is_uuid",
            True,
            "Workflows are specified as UUIDs and is_pmc option is not set.",
        ),
        (
            "multiple_wf",
            True,
            "Calculating statistics over all workflows, and is_pmc option is not set.",
        ),
    ],
)
def test_get_clustering_type_simple(caplog, name, value, expected):
    p = PegasusStatistics()
    setattr(p, name, value)
    p._initialize(verbose=5)

    p._get_clustering_type()
    assert expected in caplog.text


@pytest.mark.parametrize(
    "submit_dirs, expected, expected_log",
    [
        ("A", True, None),
        (["A", "B"], True, None),
        ("a", False, None),
        (["a", "b"], False, None),
        (
            ["A", "b"],
            False,
            "Input workflows use both PMC & regular clustering! Calculating statistics with regular clustering",
        ),
    ],
)
def test_get_clustering_type(mocker, caplog, submit_dirs, expected, expected_log):
    mocker.patch(
        "Pegasus.statistics.PegasusStatistics._check_braindump",
        side_effect=lambda submit_dir: Braindump(
            uses_pmc=submit_dir == submit_dir.upper()
        ),
    )

    p = PegasusStatistics(submit_dirs=submit_dirs)
    p._initialize(verbose=5)

    p._get_clustering_type()
    assert p.is_pmc == expected

    if expected_log is not None:
        assert expected_log in caplog.text


@pytest.mark.parametrize(
    "name, value", [("is_uuid", True), ("submit_dirs", "*"),],
)
def test_get_workflow_db_url_conf(mocker, name, value):
    mocker.patch(
        "Pegasus.db.connection.url_by_properties", return_value="OUTPUT-DB-URL"
    )
    p = PegasusStatistics()
    p._initialize(verbose=5)
    setattr(p, name, value)

    p._get_workflow_db_url()
    assert p.output_db_url == "OUTPUT-DB-URL"


@pytest.mark.parametrize(
    "name, value", [("is_uuid", True), ("submit_dirs", "*"),],
)
def test_get_workflow_db_url_conf_fail(mocker, caplog, name, value):
    mocker.patch(
        "Pegasus.db.connection.url_by_properties", side_effect=ConnectionError("ERROR")
    )
    p = PegasusStatistics()
    p._initialize(verbose=5)
    setattr(p, name, value)

    with pytest.raises(PegasusStatisticsError):
        with pytest.raises(ConnectionError):
            p._get_workflow_db_url()
        assert (
            'Unable to determine database URL. Kindly specify a value for "pegasus.monitord.output" property'
            in caplog.text
        )


def test_get_workflow_db_url_multiple_wf(mocker):
    mocker.patch("Pegasus.db.connection.url_by_submitdir", return_value="OUTPUT-DB-URL")
    p = PegasusStatistics(submit_dirs=["A", "B"], multiple_wf=True)
    p._initialize(verbose=5)

    p._get_workflow_db_url()
    assert p.output_db_url == "OUTPUT-DB-URL"


def test_get_workflow_db_url_multiple_wf_fail(mocker, caplog):
    mocker.patch(
        "Pegasus.db.connection.url_by_submitdir", side_effect=ConnectionError("ERROR")
    )
    p = PegasusStatistics(submit_dirs=["A", "B"], multiple_wf=True)
    p._initialize(verbose=5)

    with pytest.raises(PegasusStatisticsError):
        with pytest.raises(ConnectionError):
            p._get_workflow_db_url()
        assert "Unable to determine database URL." in caplog.text


def test_get_workflow_db_url_multiple_wf_url_mismatch(mocker, caplog):
    mocker.patch("Pegasus.db.connection.url_by_submitdir", side_effect=lambda *a: a[0])
    p = PegasusStatistics(submit_dirs=["A", "B"], multiple_wf=True)
    p._initialize(verbose=5)

    with pytest.raises(PegasusStatisticsError):
        with pytest.raises(ConnectionError):
            p._get_workflow_db_url()
        assert (
            "Workflows are distributed across multiple databases, which is not supported"
            in caplog.text
        )


def test_get_workflow_db_url_single(mocker):
    mocker.patch("Pegasus.db.connection.url_by_submitdir", return_value="OUTPUT-DB-URL")

    p = PegasusStatistics()
    p._initialize(verbose=5)

    p._get_workflow_db_url()
    assert p.output_db_url == "OUTPUT-DB-URL"


def test_get_workflow_db_url_conf_single_fail(mocker, caplog):
    mocker.patch(
        "Pegasus.db.connection.url_by_submitdir", side_effect=ConnectionError("ERROR")
    )
    p = PegasusStatistics(submit_dirs="A")
    p._initialize(verbose=5)

    with pytest.raises(PegasusStatisticsError):
        with pytest.raises(ConnectionError):
            p._get_workflow_db_url()
        assert "Unable to determine database URL." in caplog.text


@pytest.mark.parametrize(
    "output_dir", ["statistics", None],
)
def test_initialize_output_dir(mocker, output_dir):
    m = mocker.patch("Pegasus.tools.utils.create_directory")

    p = PegasusStatistics(output_dir=output_dir)
    p._initialize(verbose=5)
    p._initialize_output_dir()
    if output_dir is not None:
        m.assert_called_once_with("statistics", delete_if_exists=False)
    else:
        m.assert_called_once_with("statistics", delete_if_exists=True)
