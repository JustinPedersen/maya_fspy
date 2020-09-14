import json
import pprint

import pymel.core as pm

__author__ = 'Justin Pedersen'
__version__ = '1.0.0'


def create_camera_and_plane(json_path, image_path):
    """
    Create a camera and image plane given a json with data generated from fSpy.
    :param str json_path: full path to the json.
    :param str image_path: full or relative path to the image to use.
    :return: A dictionary containing the newly created nodes in the following format:
            {'camera': (camera_transform, camera_shape),
            'image_plane': (image_transform, image_shape),
            'root': group}
    :rtype: dict
    """
    with open(json_path) as json_file:
        data = json.load(json_file)

    # Group for all the created items.
    group = pm.group(em=True, n='projected_camera_grp_001')

    # Applying the matrix transformations onto a camera
    matrix_rows = [['in00', 'in10', 'in20', 'in30'],
                   ['in01', 'in11', 'in21', 'in31'],
                   ['in02', 'in12', 'in22', 'in32'],
                   ['in03', 'in13', 'in23', 'in33']]

    # Creating a camera, 4x4 matrix and decompose-matrix, then setting up the connections.
    camera_transform, camera_shape = pm.camera()
    pm.parent(camera_transform, group)
    matrix = pm.createNode('fourByFourMatrix', n='cameraTransform_fourByFourMatrix')
    decompose_matrix = pm.createNode('decomposeMatrix', n='cameraTransform_decomposeMatrix')
    pm.connectAttr(matrix.output, decompose_matrix.inputMatrix)
    pm.connectAttr(decompose_matrix.outputTranslate, camera_transform.translate)
    pm.connectAttr(decompose_matrix.outputRotate, camera_transform.rotate)

    # Setting the matrix attrs onto the 4x4 matrix.
    for i, matrix_list in enumerate(data['cameraTransform']['rows']):
        for value, attr in zip(matrix_list, matrix_rows[i]):
            pm.setAttr(matrix.attr(attr), value)

    # creating an image plane for the camera
    image_transform, image_shape = pm.imagePlane(camera=camera_transform)
    pm.setAttr(image_shape.imageName, image_path, type='string')

    # Cleanup
    pm.delete([matrix, decompose_matrix])
    for attr in ['translate', 'rotate', 'scale']:
        for ax in ['X', 'Y', 'Z']:
            camera_transform.attr(attr + ax).lock()
            image_transform.attr(attr + ax).lock()

    # Returning all the newly created items in case someone wants to grab and use them later.
    return {'camera': (camera_transform, camera_shape),
            'image_plane': (image_transform, image_shape),
            'root': group}
