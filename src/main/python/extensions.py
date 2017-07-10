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

sys.path.append('../lib/')

def find_face(robot):
    face_not_found = True
    loops = 0

    # look for person
    while face_not_found:
        robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabThinking).wait_for_completed()
        robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()

        look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.FindFaces)
        try:
            face = robot.world.wait_for_observed_face(timeout=30)
            if face != None: # and face.name != '':
                # Complete the turn action if one was in progress
                print(face)
                face_not_found = False
        except asyncio.TimeoutError:
            print("Didn't find a face :-(")
        finally:
            look_around.stop()

        if face_not_found:
            robot.turn_in_place(cozmo.util.degrees(90)).wait_for_completed()
            robot.drive_straight(cozmo.util.distance_mm(50),cozmo.util.speed_mmps(25)).wait_for_completed()
            robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabThinking).wait_for_completed()
            robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
            time.sleep(1)
            robot.say_text('I cannot find a doctor. I will keep looking.').wait_for_completed()
        else:
            robot.say_text('hello doctor. Please help me.').wait_for_completed()
            break

        loops = loops + 1
        if loops > 3:
            robot.say_text('I cannot find you. I am going home').wait_for_completed()
            break
    return face


def reset_pose(robot):

    robot.say_text('I am searching for the charger.').wait_for_completed()

    # Make sure Cozmo is clear of the charger
    if robot.is_on_charger:
        # Drive fully clear of charger (not just off the contacts)
        robot.drive_off_charger_contacts().wait_for_completed()
        robot.drive_straight(distance_mm(150), speed_mmps(50)).wait_for_completed()

        # find charger
        # Start moving the lift down
        robot.move_lift(-3)
        # turn around to look at the charger
        robot.turn_in_place(degrees(180)).wait_for_completed()
        # Tilt the head to be level
        robot.set_head_angle(degrees(0)).wait_for_completed()
        # wait half a second to ensure Cozmo has seen the charger
        time.sleep(0.5)
    else:
        # find charger
        # Start moving the lift down
        robot.move_lift(-3)
        # Tilt the head to be level
        robot.set_head_angle(degrees(0)).wait_for_completed()

        # find cubes
        look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        # try to find the charger
        try:
            robot.world.wait_until_observe_num_objects(num=1, object_type=cozmo.objects.Charger, timeout=60)
            look_around.stop()
            print("Found charger")
            robot.say_text('I have found the charger.').wait_for_completed()
        except asyncio.TimeoutError:
            print("Didn't find the charger :-(")
        finally:
            # whether we find it or not, we want to stop the behavior
            look_around.stop()

    # turn around to look away from the charger
    robot.turn_in_place(degrees(180)).wait_for_completed()
    robot.drive_straight(distance_mm(100), speed_mmps(50)).wait_for_completed()

    # turn around to look at the first cube (LookAroundInPlace does a sweep counter-clockwise)
    robot.turn_in_place(degrees(-90)).wait_for_completed()

    robot.say_text('I am searching for the cubes.').wait_for_completed()
    # find cubes
    look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    # try to find a block
    cubes = None
    try:
        cubes = robot.world.wait_until_observe_num_objects(num=3, object_type=cozmo.objects.LightCube, timeout=60)
        look_around.stop()
        print("Found cubes", cubes)
        robot.say_text('I have found the cubes.').wait_for_completed()
    except asyncio.TimeoutError:
        print("Didn't find a cube :-(")
    finally:
        # whether we find it or not, we want to stop the behavior
        look_around.stop()

