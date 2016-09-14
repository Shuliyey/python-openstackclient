#   Copyright 2013 Nebula Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import argparse
import copy
import mock
from mock import call

from osc_lib import exceptions
from osc_lib import utils

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests.unit.volume.v1 import fakes as volume_fakes
from openstackclient.volume.v1 import volume


class TestVolume(volume_fakes.TestVolumev1):

    def setUp(self):
        super(TestVolume, self).setUp()

        # Get a shortcut to the VolumeManager Mock
        self.volumes_mock = self.app.client_manager.volume.volumes
        self.volumes_mock.reset_mock()

        # Get a shortcut to the TenantManager Mock
        self.projects_mock = self.app.client_manager.identity.tenants
        self.projects_mock.reset_mock()

        # Get a shortcut to the UserManager Mock
        self.users_mock = self.app.client_manager.identity.users
        self.users_mock.reset_mock()

        # Get a shortcut to the ImageManager Mock
        self.images_mock = self.app.client_manager.image.images
        self.images_mock.reset_mock()

    def setup_volumes_mock(self, count):
        volumes = volume_fakes.FakeVolume.create_volumes(count=count)

        self.volumes_mock.get = volume_fakes.FakeVolume.get_volumes(
            volumes,
            0)
        return volumes


# TODO(dtroyer): The volume create tests are incomplete, only the minimal
#                options and the options that require additional processing
#                are implemented at this time.

class TestVolumeCreate(TestVolume):

    project = identity_fakes.FakeProject.create_one_project()
    user = identity_fakes.FakeUser.create_one_user()

    columns = (
        'attach_status',
        'availability_zone',
        'display_description',
        'display_name',
        'id',
        'properties',
        'size',
        'status',
        'type',
    )
    datalist = (
        'detached',
        volume_fakes.volume_zone,
        volume_fakes.volume_description,
        volume_fakes.volume_name,
        volume_fakes.volume_id,
        volume_fakes.volume_metadata_str,
        volume_fakes.volume_size,
        volume_fakes.volume_status,
        volume_fakes.volume_type,
    )

    def setUp(self):
        super(TestVolumeCreate, self).setUp()

        self.volumes_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.VOLUME),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = volume.CreateVolume(self.app, None)

    def test_volume_create_min_options(self):
        arglist = [
            '--size', str(volume_fakes.volume_size),
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('size', volume_fakes.volume_size),
            ('name', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            volume_fakes.volume_size,
            None,
            None,
            volume_fakes.volume_name,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_options(self):
        arglist = [
            '--size', str(volume_fakes.volume_size),
            '--description', volume_fakes.volume_description,
            '--type', volume_fakes.volume_type,
            '--availability-zone', volume_fakes.volume_zone,
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('size', volume_fakes.volume_size),
            ('description', volume_fakes.volume_description),
            ('type', volume_fakes.volume_type),
            ('availability_zone', volume_fakes.volume_zone),
            ('name', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            volume_fakes.volume_size,
            None,
            None,
            volume_fakes.volume_name,
            volume_fakes.volume_description,
            volume_fakes.volume_type,
            None,
            None,
            volume_fakes.volume_zone,
            None,
            None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_user_project_id(self):
        # Return a project
        self.projects_mock.get.return_value = self.project
        # Return a user
        self.users_mock.get.return_value = self.user

        arglist = [
            '--size', str(volume_fakes.volume_size),
            '--project', self.project.id,
            '--user', self.user.id,
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('size', volume_fakes.volume_size),
            ('project', self.project.id),
            ('user', self.user.id),
            ('name', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            volume_fakes.volume_size,
            None,
            None,
            volume_fakes.volume_name,
            None,
            None,
            self.user.id,
            self.project.id,
            None,
            None,
            None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_user_project_name(self):
        # Return a project
        self.projects_mock.get.return_value = self.project
        # Return a user
        self.users_mock.get.return_value = self.user

        arglist = [
            '--size', str(volume_fakes.volume_size),
            '--project', self.project.name,
            '--user', self.user.name,
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('size', volume_fakes.volume_size),
            ('project', self.project.name),
            ('user', self.user.name),
            ('name', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            volume_fakes.volume_size,
            None,
            None,
            volume_fakes.volume_name,
            None,
            None,
            self.user.id,
            self.project.id,
            None,
            None,
            None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_properties(self):
        arglist = [
            '--property', 'Alpha=a',
            '--property', 'Beta=b',
            '--size', str(volume_fakes.volume_size),
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('property', {'Alpha': 'a', 'Beta': 'b'}),
            ('size', volume_fakes.volume_size),
            ('name', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            volume_fakes.volume_size,
            None,
            None,
            volume_fakes.volume_name,
            None,
            None,
            None,
            None,
            None,
            {'Alpha': 'a', 'Beta': 'b'},
            None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_image_id(self):
        self.images_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.IMAGE),
            loaded=True,
        )

        arglist = [
            '--image', volume_fakes.image_id,
            '--size', str(volume_fakes.volume_size),
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('image', volume_fakes.image_id),
            ('size', volume_fakes.volume_size),
            ('name', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            volume_fakes.volume_size,
            None,
            None,
            volume_fakes.volume_name,
            None,
            None,
            None,
            None,
            None,
            None,
            volume_fakes.image_id,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_image_name(self):
        self.images_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.IMAGE),
            loaded=True,
        )

        arglist = [
            '--image', volume_fakes.image_name,
            '--size', str(volume_fakes.volume_size),
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('image', volume_fakes.image_name),
            ('size', volume_fakes.volume_size),
            ('name', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            volume_fakes.volume_size,
            None,
            None,
            volume_fakes.volume_name,
            None,
            None,
            None,
            None,
            None,
            None,
            volume_fakes.image_id,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestVolumeDelete(TestVolume):

    def setUp(self):
        super(TestVolumeDelete, self).setUp()

        self.volumes_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = volume.DeleteVolume(self.app, None)

    def test_volume_delete_one_volume(self):
        volumes = self.setup_volumes_mock(count=1)

        arglist = [
            volumes[0].id
        ]
        verifylist = [
            ("force", False),
            ("volumes", [volumes[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volumes_mock.delete.assert_called_once_with(volumes[0].id)
        self.assertIsNone(result)

    def test_volume_delete_multi_volumes(self):
        volumes = self.setup_volumes_mock(count=3)

        arglist = [v.id for v in volumes]
        verifylist = [
            ('force', False),
            ('volumes', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = [call(v.id) for v in volumes]
        self.volumes_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_volume_delete_multi_volumes_with_exception(self):
        volumes = self.setup_volumes_mock(count=2)

        arglist = [
            volumes[0].id,
            'unexist_volume',
        ]
        verifylist = [
            ('force', False),
            ('volumes', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [volumes[0], exceptions.CommandError]
        with mock.patch.object(utils, 'find_resource',
                               side_effect=find_mock_result) as find_mock:
            try:
                self.cmd.take_action(parsed_args)
                self.fail('CommandError should be raised.')
            except exceptions.CommandError as e:
                self.assertEqual('1 of 2 volumes failed to delete.',
                                 str(e))

            find_mock.assert_any_call(self.volumes_mock, volumes[0].id)
            find_mock.assert_any_call(self.volumes_mock, 'unexist_volume')

            self.assertEqual(2, find_mock.call_count)
            self.volumes_mock.delete.assert_called_once_with(volumes[0].id)

    def test_volume_delete_with_force(self):
        volumes = self.setup_volumes_mock(count=1)

        arglist = [
            '--force',
            volumes[0].id,
        ]
        verifylist = [
            ('force', True),
            ('volumes', [volumes[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volumes_mock.force_delete.assert_called_once_with(volumes[0].id)
        self.assertIsNone(result)


class TestVolumeList(TestVolume):

    columns = (
        'ID',
        'Display Name',
        'Status',
        'Size',
        'Attached to',
    )
    datalist = (
        (
            volume_fakes.volume_id,
            volume_fakes.volume_name,
            volume_fakes.volume_status,
            volume_fakes.volume_size,
            '',
        ),
    )

    def setUp(self):
        super(TestVolumeList, self).setUp()

        self.volumes_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(volume_fakes.VOLUME),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = volume.ListVolume(self.app, None)

    def test_volume_list_no_options(self):
        arglist = []
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', None),
            ('status', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_volume_list_name(self):
        arglist = [
            '--name', volume_fakes.volume_name,
        ]
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', volume_fakes.volume_name),
            ('status', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.columns, tuple(columns))
        self.assertEqual(self.datalist, tuple(data))

    def test_volume_list_status(self):
        arglist = [
            '--status', volume_fakes.volume_status,
        ]
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', None),
            ('status', volume_fakes.volume_status),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.columns, tuple(columns))
        self.assertEqual(self.datalist, tuple(data))

    def test_volume_list_all_projects(self):
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('long', False),
            ('all_projects', True),
            ('name', None),
            ('status', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.columns, tuple(columns))
        self.assertEqual(self.datalist, tuple(data))

    def test_volume_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
            ('all_projects', False),
            ('name', None),
            ('status', None),
            ('limit', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        collist = (
            'ID',
            'Display Name',
            'Status',
            'Size',
            'Type',
            'Bootable',
            'Attached to',
            'Properties',
        )
        self.assertEqual(collist, columns)

        datalist = ((
            volume_fakes.volume_id,
            volume_fakes.volume_name,
            volume_fakes.volume_status,
            volume_fakes.volume_size,
            volume_fakes.volume_type,
            '',
            '',
            "Alpha='a', Beta='b', Gamma='g'",
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_volume_list_with_limit(self):
        arglist = [
            '--limit', '2',
        ]
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', None),
            ('status', None),
            ('limit', 2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.list.assert_called_once_with(
            limit=2,
            search_opts={
                'status': None,
                'display_name': None,
                'all_tenants': False, }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_volume_list_negative_limit(self):
        arglist = [
            "--limit", "-2",
        ]
        verifylist = [
            ("limit", -2),
        ]
        self.assertRaises(argparse.ArgumentTypeError, self.check_parser,
                          self.cmd, arglist, verifylist)


class TestVolumeSet(TestVolume):

    def setUp(self):
        super(TestVolumeSet, self).setUp()

        self.volumes_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.VOLUME),
            loaded=True,
        )

        self.volumes_mock.update.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.VOLUME),
            loaded=True,
        )
        # Get the command object to test
        self.cmd = volume.SetVolume(self.app, None)

    def test_volume_set_no_options(self):
        arglist = [
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('size', None),
            ('property', None),
            ('volume', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

    def test_volume_set_name(self):
        arglist = [
            '--name', 'qwerty',
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('name', 'qwerty'),
            ('description', None),
            ('size', None),
            ('property', None),
            ('volume', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'display_name': 'qwerty',
        }
        self.volumes_mock.update.assert_called_with(
            volume_fakes.volume_id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_volume_set_description(self):
        arglist = [
            '--description', 'new desc',
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('name', None),
            ('description', 'new desc'),
            ('size', None),
            ('property', None),
            ('volume', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'display_description': 'new desc',
        }
        self.volumes_mock.update.assert_called_with(
            volume_fakes.volume_id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_volume_set_size(self):
        arglist = [
            '--size', '130',
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('size', 130),
            ('property', None),
            ('volume', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        size = 130
        self.volumes_mock.extend.assert_called_with(
            volume_fakes.volume_id,
            size
        )
        self.assertIsNone(result)

    @mock.patch.object(volume.LOG, 'error')
    def test_volume_set_size_smaller(self, mock_log_error):
        arglist = [
            '--size', '100',
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('size', 100),
            ('property', None),
            ('volume', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        mock_log_error.assert_called_with("New size must be greater "
                                          "than %s GB",
                                          volume_fakes.volume_size)
        self.assertIsNone(result)

    @mock.patch.object(volume.LOG, 'error')
    def test_volume_set_size_not_available(self, mock_log_error):
        self.volumes_mock.get.return_value.status = 'error'
        arglist = [
            '--size', '130',
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('size', 130),
            ('property', None),
            ('volume', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        mock_log_error.assert_called_with("Volume is in %s state, it must be "
                                          "available before size can be "
                                          "extended", 'error')
        self.assertIsNone(result)

    def test_volume_set_property(self):
        arglist = [
            '--property', 'myprop=myvalue',
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('size', None),
            ('property', {'myprop': 'myvalue'}),
            ('volume', volume_fakes.volume_name),
            ('bootable', False),
            ('non_bootable', False)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        metadata = {
            'myprop': 'myvalue'
        }
        self.volumes_mock.set_metadata.assert_called_with(
            volume_fakes.volume_id,
            metadata
        )
        self.assertIsNone(result)

    def test_volume_set_bootable(self):
        arglist = [
            ['--bootable', volume_fakes.volume_id],
            ['--non-bootable', volume_fakes.volume_id]
        ]
        verifylist = [
            [
                ('bootable', True),
                ('non_bootable', False),
                ('volume', volume_fakes.volume_id)
            ],
            [
                ('bootable', False),
                ('non_bootable', True),
                ('volume', volume_fakes.volume_id)
            ]
        ]
        for index in range(len(arglist)):
            parsed_args = self.check_parser(
                self.cmd, arglist[index], verifylist[index])

            self.cmd.take_action(parsed_args)
            self.volumes_mock.set_bootable.assert_called_with(
                volume_fakes.volume_id, verifylist[index][0][1])
