import pathlib
import shutil
from unittest import mock

import ckan.tests.factories as factories
import ckanext.dc_log_view.plugin as plugin  # noqa: F401

import dclab
from dcor_shared.testing import (
    make_dataset_via_s3, make_resource_via_s3, synchronous_enqueue_job)

import pytest

data_path = pathlib.Path(__file__).parent / "data"


def test_plugin_info():
    p = plugin.DCLogViewPlugin()
    info = p.info()
    assert info["name"] == "dc_log_view"


@pytest.mark.ckan_config('ckan.plugins', 'dcor_schemas')
@pytest.mark.usefixtures('clean_db', 'with_request_context')
@mock.patch('ckan.plugins.toolkit.enqueue_job',
            side_effect=synchronous_enqueue_job)
def test_plugin_can_view(enqueue_job_mock, tmp_path):
    user = factories.User()
    owner_org = factories.Organization(users=[{
        'name': user['id'],
        'capacity': 'admin'
    }])
    create_context = {'ignore_auth': False,
                      'user': user['name'],
                      'api_version': 3}
    # create dataset with .rtdc file
    ds_dict, res_dict_dc = make_dataset_via_s3(
        create_context=create_context,
        owner_org=owner_org,
        resource_path=data_path / "calibration_beads_47.rtdc",
        activate=False)
    # Add a text file
    path_text = tmp_path / "test.txt"
    path_text.write_text("hello world")
    res_dict_text = make_resource_via_s3(
        resource_path=path_text,
        organization_id=owner_org["id"],
        dataset_id=ds_dict["id"],
        ret_dict=True,
    )

    # test can_view for .rtdc data
    p = plugin.DCLogViewPlugin()
    print("RTDC ID", res_dict_dc["id"])
    print("TEXT ID", res_dict_text["id"])
    for key in res_dict_text:
        print("TEXT", key, res_dict_text[key])
    assert p.can_view({"resource": res_dict_dc})
    assert not p.can_view({"resource": res_dict_text})


@pytest.mark.ckan_config('ckan.plugins', 'dcor_schemas')
@pytest.mark.usefixtures('clean_db', 'with_request_context')
@mock.patch('ckan.plugins.toolkit.enqueue_job',
            side_effect=synchronous_enqueue_job)
def test_plugin_setup_template_variables(
        enqueue_job_mock, tmp_path):
    path_in = tmp_path / "test.rtdc"
    shutil.copy2(data_path / "calibration_beads_47.rtdc", path_in)

    with dclab.RTDCWriter(path_in, mode="append") as hw:
        hw.store_log("peter", ["pferde im gurkensalat",
                               "haben keinen hunger"])

    # sanity check
    with dclab.new_dataset(path_in) as ds:
        assert ds.logs["peter"][0] == "pferde im gurkensalat"

    user = factories.User()
    owner_org = factories.Organization(users=[{
        'name': user['id'],
        'capacity': 'admin'
    }])
    create_context = {'ignore_auth': False,
                      'user': user['name'],
                      'api_version': 3}
    # create dataset with .rtdc file
    ds_dict, res_dict = make_dataset_via_s3(
        create_context=create_context,
        owner_org=owner_org,
        resource_path=path_in,
        activate=True)

    # test setup_template_variables for .rtdc data
    p = plugin.DCLogViewPlugin()
    data = p.setup_template_variables(
        context=create_context,
        data_dict={"resource": res_dict})
    logs = data["logs"]
    assert len(logs) == 1
    assert logs["peter"][0] == "pferde im gurkensalat"
