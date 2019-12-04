#!/usr/bin/env python

import rospy
from std_msgs.msg import Float64, Float32MultiArray
import numpy as np
from thruster_manager import ThrusterManager


class ThrusterController():

    CONTROLS_MOVE_TOPIC = '/controls/move'
    CONTROLS_MOVE_X_TOPIC = CONTROLS_MOVE_TOPIC + '/x'
    CONTROLS_MOVE_Y_TOPIC = CONTROLS_MOVE_TOPIC + '/y'
    CONTROLS_MOVE_Z_TOPIC = CONTROLS_MOVE_TOPIC + '/z'
    CONTROLS_MOVE_ROLL_TOPIC = CONTROLS_MOVE_TOPIC + '/roll'
    CONTROLS_MOVE_PITCH_TOPIC = CONTROLS_MOVE_TOPIC + '/pitch'
    CONTROLS_MOVE_YAW_TOPIC = CONTROLS_MOVE_TOPIC + '/yaw'

    SIM_PUBLISH_TOPIC = '/sim/move'

    def __init__(self):
        self.sim_pub = rospy.Publisher(self.SIM_PUBLISH_TOPIC, Float32MultiArray, queue_size=3)

        self.tm = ThrusterManager('cthulhu.config')

        rospy.Subscriber(self.CONTROLS_MOVE_X_TOPIC, Float64, self._on_x)
        rospy.Subscriber(self.CONTROLS_MOVE_Y_TOPIC, Float64, self._on_y)
        rospy.Subscriber(self.CONTROLS_MOVE_Z_TOPIC, Float64, self._on_z)
        rospy.Subscriber(self.CONTROLS_MOVE_ROLL_TOPIC, Float64, self._on_roll)
        rospy.Subscriber(self.CONTROLS_MOVE_PITCH_TOPIC, Float64, self._on_pitch)
        rospy.Subscriber(self.CONTROLS_MOVE_YAW_TOPIC, Float64, self._on_yaw)

        self.pid_outputs = np.zeros(6)
        self.t_allocs = np.zeros(8)

    def update_thruster_allocs(self):
        self.t_allocs = tm.calc_thruster_allocs(self.pid_outputs)

    def _on_x(self, x):
        self.pid_outputs[0] = x
        self.update_thruster_allocs()

    def _on_y(self, y):
        self.pid_outputs[1] = y
        self.update_thruster_allocs()

    def _on_z(self, z):
        self.pid_outputs[2] = z
        self.update_thruster_allocs()

    def _on_roll(self, roll):
        self.pid_outputs[3] = roll
        self.update_thruster_allocs()

    def _on_pitch(self, pitch):
        self.pid_outputs[4] = pitch
        self.update_thruster_allocs()

    def _on_yaw(self, yaw):
        self.pid_outputs[5] = yaw
        self.update_thruster_allocs()

    def run(self):
        rospy.init_node('thruster_controls')
        rate = rospy.Rate(10)  # 10 Hz

        while not rospy.is_shutdown():
            f32_t_allocs = Float32MultiArray()
            f32_t_allocs.data = self.t_allocs
            rospy.loginfo(f32_t_allocs)
            self.sim_pub.publish(f32_t_allocs)
            rate.sleep()


def main():
    try:
        ThrusterController().run()
    except rospy.ROSInterruptException:
        pass

if __name__ == '__main__':
    main()
