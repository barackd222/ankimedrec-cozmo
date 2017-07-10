#!/usr/bin/env python3

# Copyright (c) 2016 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Cozmo the Find_Blocks.

Cozmo patrols your desk, looks out for unknown faces, and reports them to you.
'''

import asyncio
from random import randint
import sys
import time

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps
from cozmo.objects import LightCube1Id, LightCube2Id, LightCube3Id
from extensions import find_face, reset_pose
from extensions_medrec import create_patient, create_physician, create_observation, create_consultation, create_prescription

sys.path.append('../lib/')

def sick_scenario(robot):

    # Turn on image receiving by the camera
    robot.camera.image_stream_enabled = True
    robot.camera.enable_auto_exposure()
    robot.set_head_light(True)
    robot.camera.color_image_enabled = True
    robot.enable_facial_expression_estimation(True)

    robot.say_text('Lets play a game. I am the patient and you are the doctor.').wait_for_completed()

    patient_id = create_patient()
    physician_id = create_physician()

    reset_pose(robot)

    # set up cubes
    robot.set_all_backpack_lights(cozmo.lights.green_light)
    cube1 = robot.world.get_light_cube(LightCube1Id)  # looks like a paperclip
    cube2 = robot.world.get_light_cube(LightCube2Id)  # looks like a lamp / heart
    cube3 = robot.world.get_light_cube(LightCube3Id)  # looks like the letters 'ab' over 'T'
    cube1.set_lights(cozmo.lights.red_light)
    robot.say_text('The red cube represents dizziness.').wait_for_completed()
    # cube2.set_lights(cozmo.lights.green_light)
    cube2.set_lights(cozmo.lights.Light(cozmo.lights.Color(rgb=(255, 0, 255))))
    robot.say_text('The purple cube represents fatigue.').wait_for_completed()
    cube3.set_lights(cozmo.lights.blue_light)
    robot.say_text('The blue cube represents a cold.').wait_for_completed()
    print(cube1.object_id)
    print(cube2.object_id)
    print(cube3.object_id)
    robot.say_text('Tap one of the cubes.').wait_for_completed()

    # start demonstration
    while True:

        # wait for cube tap sensor
        try:
            obj = robot.world.wait_for(cozmo.objects.EvtObjectTapped)
        except asyncio.TimeoutError:
            print('timeout caught')
            continue

        print (obj)
        print (obj.tap_intensity)
        robot.say_text('I do not feel well. I do not know what I have.').wait_for_completed()

        # each cube has a different illness
        cubeid = None
        if obj.obj.object_id == cube1.object_id:
            robot.go_to_object(cube1, cozmo.util.distance_mm(60.0)).wait_for_completed()
            robot.drive_straight(distance_mm(-15), speed_mmps(50)).wait_for_completed()
            robot.play_anim_trigger(cozmo.anim.Triggers.DizzyReactionHard).wait_for_completed()
            robot.set_all_backpack_lights(cozmo.lights.red_light)
            condition = 'I am nautious.'
            selfdiagnosis = 'I need to have sit down for a little while.'
            cubeid = LightCube1Id
        elif obj.obj.object_id == cube2.object_id:
            robot.go_to_object(cube2, cozmo.util.distance_mm(60.0)).wait_for_completed()
            robot.drive_straight(distance_mm(-15), speed_mmps(50)).wait_for_completed()
            robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabSleep).wait_for_completed()
            robot.set_all_backpack_lights(cozmo.lights.Light(cozmo.lights.Color(rgb=(255,0,255))))
            condition = 'I am very sleepy. I cannot sleep.'
            selfdiagnosis = 'I need to have some sleep therapy.'
            cubeid = LightCube1Id
        elif obj.obj.object_id == cube3.object_id:
            robot.go_to_object(cube3, cozmo.util.distance_mm(60.0)).wait_for_completed()
            robot.drive_straight(distance_mm(-15), speed_mmps(50)).wait_for_completed()
            robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabSneeze).wait_for_completed()
            robot.set_all_backpack_lights(cozmo.lights.blue_light)
            condition = 'I have an allergy.'
            selfdiagnosis = 'I need to have some ventolin.'
            cubeid = LightCube1Id

        create_observation(patient_id,robot,obj,cubeid,condition,selfdiagnosis)
        robot.say_text('I need to find a doctor.').wait_for_completed()

        # Tilt head up to look for people
        robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()

        face_not_found = True
        face = None
        loops = 0

        face = find_face(robot)
        create_consultation(patient_id,physician_id,robot,face)
        create_prescription(patient_id,physician_id,robot)

        # reset and go back to charger
        robot.go_to_object(robot.world.charger, cozmo.util.distance_mm(50.0)).wait_for_completed()
        robot.drive_straight(cozmo.util.distance_mm(-10), cozmo.util.speed_mmps(25)).wait_for_completed()
        robot.set_all_backpack_lights(cozmo.lights.green_light)
        robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabVictory).wait_for_completed()
        robot.say_text('Thank you. I am now well again.').wait_for_completed()
        create_observation(patient_id,robot)

        robot.play_anim_trigger(cozmo.anim.Triggers.FistBumpRequestOnce).wait_for_completed()

        # find person to start next loop
        robot.set_all_backpack_lights(cozmo.lights.off_light)
        reset_pose(robot)
        robot.set_all_backpack_lights(cozmo.lights.green_light)
        robot.say_text('Let us play again. That was fun.').wait_for_completed()

def run(sdk_conn):
    '''The run method runs once the Cozmo SDK is connected.'''
    robot = sdk_conn.wait_for_robot()

    try:
        sick_scenario(robot)
    except KeyboardInterrupt:
        print("")
        print("Exit requested by user")


if __name__ == '__main__':
    cozmo.setup_basic_logging()
    cozmo.robot.Robot.drive_off_charger_on_connect = False  # Stay on charger until init
    try:
        cozmo.connect_with_tkviewer(run, force_on_top=True)
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)

