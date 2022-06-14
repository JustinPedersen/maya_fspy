"""
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
"""

import json
import struct

from pprint import pprint
from maya import cmds


class ParsingError(Exception):
    pass


def read_project(project_path):
    """
    Read information from the fspy project itself. This gives us more robust information than
    what we get in the exported json file.

    :param str project_path: Path to the fspy project.
    :returns: Dict of all info in the fspy project.
    :rtype: dict
    """

    project_file = open(project_path, "rb")

    file_id = struct.unpack('<I', project_file.read(4))[0]
    if 2037412710 != file_id:
        raise ParsingError("Trying to import a file that is not an fSpy project")

    project_version = struct.unpack('<I', project_file.read(4))[0]
    if project_version != 1:
        raise ParsingError("Unsupported fSpy project file version " + str(project_version))

    state_string_size = struct.unpack('<I', project_file.read(4))[0]
    image_buffer_size = struct.unpack('<I', project_file.read(4))[0]

    if image_buffer_size == 0:
        raise ParsingError("Trying to import an fSpy project with no image data")

    project_file.seek(16)
    return json.loads(project_file.read(state_string_size).decode('utf-8'))


def create_camera_and_plane(project_path, image_path):
    """
    Create a camera and image plane given a json with data generated from fSpy.
    :param str project_path: full path to the json.
    :param str image_path: full or relative path to the image to use.
    :return: A dictionary containing the newly created nodes in the following format:
            {'camera': (camera_transform, camera_shape),
            'image_plane': (image_transform, image_shape),
            'root': group}
    :rtype: dict
    """
    data = read_project(project_path)

    pprint(data)

    # Group for all the created items.
    group = cmds.group(empty=True, name='projected_camera_grp_001')

    # Applying the matrix transformations onto a camera
    matrix_rows = [['in00', 'in10', 'in20', 'in30'],
                   ['in01', 'in11', 'in21', 'in31'],
                   ['in02', 'in12', 'in22', 'in32'],
                   ['in03', 'in13', 'in23', 'in33']]

    # Creating a camera, 4x4 matrix and decompose-matrix, then setting up the connections.
    camera_transform, camera_shape = cmds.camera()
    cmds.parent(camera_transform, group)
    matrix = cmds.createNode('fourByFourMatrix', name='cameraTransform_fourByFourMatrix')
    decompose_matrix = cmds.createNode('decomposeMatrix', name='cameraTransform_decomposeMatrix')

    # Make connections
    cmds.connectAttr('{}.output'.format(matrix), '{}.inputMatrix'.format(decompose_matrix))
    cmds.connectAttr('{}.outputTranslate'.format(decompose_matrix), '{}.translate'.format(camera_transform))
    cmds.connectAttr('{}.outputRotate'.format(decompose_matrix), '{}.rotate'.format(camera_transform))

    # Setting the matrix attrs onto the 4x4 matrix.
    for i, matrix_list in enumerate(data['cameraParameters']['cameraTransform']['rows']):
        for value, attr in zip(matrix_list, matrix_rows[i]):
            cmds.setAttr('{}.{}'.format(matrix, attr), value)

    # creating an image plane for the camera
    image_transform, image_shape = cmds.imagePlane(camera=camera_transform)
    cmds.setAttr('{}.imageName'.format(image_shape, ), image_path, type='string')

    # setting focal length on the camera.
    absolute_focal_length = data.get('calibrationSettings1VP', {}).get('absoluteFocalLength')
    if absolute_focal_length:
        cmds.camera(camera_shape, edit=True, focalLength=absolute_focal_length)

    # Setting the sensor size
    custom_sensor_height = data.get('calibrationSettingsBase', {}).get('cameraData', {}).get('customSensorHeight')
    custom_sensor_width = data.get('calibrationSettingsBase', {}).get('cameraData', {}).get('customSensorWidth')

    if custom_sensor_height and custom_sensor_width:
        # Maya's aperture is always given is Inches
        cmds.setAttr('{}.horizontalFilmAperture'.format(camera_shape), custom_sensor_width * 0.0393701)
        cmds.setAttr('{}.verticalFilmAperture'.format(camera_shape), custom_sensor_height * 0.0393701)

    # Cleanup
    cmds.delete([matrix, decompose_matrix])
    for attr in ['translate', 'rotate', 'scale']:
        for ax in ['X', 'Y', 'Z']:
            cmds.setAttr('{}.{}'.format(camera_transform, attr + ax), lock=True)
            cmds.setAttr('{}.{}'.format(image_transform, attr + ax), lock=True)

    # Returning all the newly created items in case someone wants to grab and use them later.
    return {'camera': (camera_transform, camera_shape),
            'image_plane': (image_transform, image_shape),
            'root': group}
