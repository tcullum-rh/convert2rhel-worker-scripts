import pytest
from mock import patch, call

from scripts.c2r_script import (
    install_convert2rhel,
    ProcessError,
)


@pytest.mark.parametrize(
    ("subprocess_mock", "pkg_installed_mock", "should_undo_transaction"),
    (
        ((b"output", 0), False, True),
        ((b"output", 0), True, False),
    ),
)
def test_install_convert2rhel(
    subprocess_mock, pkg_installed_mock, should_undo_transaction
):
    with patch(
        "scripts.c2r_script.run_subprocess",
        return_value=subprocess_mock,
    ) as mock_run_subprocess:
        with patch(
            "scripts.c2r_script._check_if_package_installed",
            return_value=pkg_installed_mock,
        ) as mock_run_pkg_check:
            with patch(
                "scripts.c2r_script._get_last_yum_transaction_id", return_value=1
            ) as mock_transaction_get:
                should_undo, _ = install_convert2rhel()

    assert should_undo is should_undo_transaction
    mock_run_pkg_check.assert_called_once()
    mock_run_subprocess.assert_called_once()
    assert mock_transaction_get.call_count == (0 if pkg_installed_mock else 1)

    if pkg_installed_mock:
        expected_calls = [
            ["/usr/bin/yum", "update", "convert2rhel", "-y"],
        ]
    else:
        expected_calls = [["/usr/bin/yum", "install", "convert2rhel", "-y"]]

    assert mock_run_subprocess.call_args_list == [call(args) for args in expected_calls]


@patch("scripts.c2r_script._check_if_package_installed", return_value=False)
@patch("scripts.c2r_script.run_subprocess", return_value=(b"failed", 1))
def test_install_convert2rhel_raise_exception(mock_run_subprocess, mock_pkg_check):
    with pytest.raises(
        ProcessError,
        match="Installing convert2rhel with yum exited with code '1' and output:\nfailed",
    ):
        install_convert2rhel()

    expected_calls = [["/usr/bin/yum", "install", "convert2rhel", "-y"]]

    mock_pkg_check.assert_called_once()
    assert mock_run_subprocess.call_args_list == [call(args) for args in expected_calls]


@patch("scripts.c2r_script._check_if_package_installed", return_value=True)
@patch("scripts.c2r_script.run_subprocess", return_value=(b"failed", 1))
def test_update_convert2rhel_raise_exception(mock_run_subprocess, mock_pkg_check):
    with pytest.raises(
        ProcessError,
        match="Updating convert2rhel with yum exited with code '1' and output:\nfailed",
    ):
        install_convert2rhel()

    expected_calls = [
        ["/usr/bin/yum", "update", "convert2rhel", "-y"],
    ]

    mock_pkg_check.assert_called_once()
    assert mock_run_subprocess.call_args_list == [call(args) for args in expected_calls]
