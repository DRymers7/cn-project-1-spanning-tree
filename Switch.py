"""
/*
 * Copyright © 2022 Georgia Institute of Technology (Georgia Tech). All Rights Reserved.
 * Template code for CS 6250 Computer Networks
 * Instructors: Maria Konte
 * Head TAs: Johann Lau and Ken Westdorp
 *
 * Georgia Tech asserts copyright ownership of this template and all derivative
 * works, including solutions to the projects assigned in this course. Students
 * and other users of this template code are advised not to share it with others
 * or to make it available on publicly viewable websites including repositories
 * such as GitHub and GitLab. This copyright statement should not be removed
 * or edited. Removing it will be considered an academic integrity issue.
 *
 * We do grant permission to share solutions privately with non-students such
 * as potential employers as long as this header remains in full. However,
 * sharing with other current or future students or using a medium to share
 * where the code is widely available on the internet is prohibited and
 * subject to being investigated as a GT honor code violation.
 * Please respect the intellectual ownership of the course materials
 * (including exam keys, project requirements, etc.) and do not distribute them
 * to anyone not enrolled in the class. Use of any previous semester course
 * materials, such as tests, quizzes, homework, projects, videos, and any other
 * coursework, is prohibited in this course.
 */
"""

# Spanning Tree Protocol project for GA Tech OMSCS CS-6250: Computer Networks
#
# Copyright 2023 Vincent Hu
#           Based on prior work by Sean Donovan, Jared Scott, James Lohse, and Michael Brown

from Message import Message
from StpSwitch import StpSwitch
import os


class Switch(StpSwitch):
    """
    This class defines a Switch (node/bridge) that can send and receive messages
    to converge on a final, loop-free spanning tree. This class
    is a child class of the StpSwitch class. To remain within the spirit of
    the project, the only inherited members or functions a student is permitted
    to use are:

    switchID: int
        the ID number of this switch object)
    links: list
        the list of switch IDs connected to this switch object)
    send_message(msg: Message)
        Sends a Message object to another switch)

    Students should use the send_message function to implement the algorithm.
    Do NOT use the self.topology.send_message function. A non-distributed (centralized)
    algorithm will not receive credit. Do NOT use global variables.

    Student code should NOT access the following members, otherwise they may violate
    the spirit of the project:

    topolink: Topology
        a link to the greater Topology structure used for message passing
    self.topology: Topology
        a link to the greater Topology structure used for message passing
    """
    def __init__(self, idNum: int, topolink: object, neighbors: list):
        """
        Invokes the super class constructor (StpSwitch), which makes the following
        members available to this object:

        idNum: int
            the ID number of this switch object
        neighbors: list
            the list of switch IDs connected to this switch object
        switch_information: dict
            information tracked local to this instance of Switch for implementation of STP
        """
        super(Switch, self).__init__(idNum, topolink, neighbors)
        # TODO: Define class members to keep track of which links are part of the spanning tree

        # String constants to avoid having magic strings
        self.ROOT = "root"
        self.DISTANCE_TO_ROOT = "distance_to_root"
        self.ACTIVE_LINKS = "active_links"
        self.PATH_THROUGH = "path_through"

        # Dictionary and initialization to manage information local to each instance of a switch
        self.switch_information = {}
        self._init_switch_information()

        self._log_debug(f"Switch {self.switchID} initialized with neighbors: {neighbors}")

        
    def process_message(self, message: Message):
        """
        Processes the messages from other switches. Updates its own data (members),
        if necessary, and sends messages to its neighbors, as needed.

        message: Message
            the Message received from other Switches
        """
        # TODO: This function needs to accept an incoming message and process it accordingly.
        #      This function is called every time the switch receives a new message.

        # Boolean indication of if the switch should update based on ingress message, defaulting to false

        self._log_debug(f"\nSwitch {self.switchID} processing message: {message}")
        self._log_debug(f"Message details: root={message.root}, distance={message.distance}, origin={message.origin}, pathThrough={message.pathThrough}")
        self._log_debug(f"Current state: root={self.switch_information[self.ROOT]}, " +
                    f"distance={self.switch_information[self.DISTANCE_TO_ROOT]}, " +
                    f"active_links={self.switch_information[self.ACTIVE_LINKS]}, " +
                    f"path_through={self.switch_information[self.PATH_THROUGH]}")
        self._log_debug(f"Root comparison: message.root={message.root} < current_root={self.switch_information[self.ROOT]} = {message.root < self.switch_information[self.ROOT]}")
        should_switch_update = False

        # Handle pathThrough messages for ALL switches
        if message.pathThrough:
            self._update_paththrough(message)

        # Decrement the TTL, as this will determine if we forward the message
        message.ttl -= 1
        self._log_debug(f"TTL decremented to: {message.ttl}")

        # Check for updates
        if message.root < self.switch_information[self.ROOT]:
            self._log_debug(f"Better root found: {message.root} < {self.switch_information[self.ROOT]}")
            should_switch_update = True

        elif message.root == self.switch_information[self.ROOT]:
            should_switch_update = self._check_distances(message)
            self._log_debug(f"Equal roots, distance check result: {should_switch_update}")

        # Handle updates (this also sends the new messages to neighbors)
        if message.ttl > 0 and should_switch_update:
            self._handle_switch_updates(message)

    def generate_logstring(self):
        """
        Logs this Switch's list of Active Links in a SORTED order

        returns a String of format:
            SwitchID - ActiveLink1, SwitchID - ActiveLink2, etc.
        """
        # TODO: This function needs to return a logstring for this particular switch.  The
        #      string represents the active forwarding links for this switch and is invoked
        #      only after the simulation is complete.  Output the links included in the
        #      spanning tree by INCREASING destination switch ID on a single line.
        #
        #      Print links as '(source switch id) - (destination switch id)', separating links
        #      with a comma - ','.
        #
        #      For example, given a spanning tree (1 ----- 2 ----- 3), a correct output string
        #      for switch 2 would have the following text:
        #      2 - 1, 2 - 3
        #
        #      A full example of a valid output file is included (Logs/) in the project skeleton.

        # Get active links and sort them
        active_links = sorted(self.switch_information[self.ACTIVE_LINKS])
        
        # Generate formatted strings for each link
        link_strings_array = []
        for link in active_links:
            link_strings_array.append(f"{self.switchID} - {link}")
        
        return ", ".join(link_strings_array) if link_strings_array else f"{self.switchID}"
    
    def _update_paththrough(self, message):
        """
        Method to handle the following scenario:

        If the ID of the origin switch is not in this switch's active links array,
        so update the active links array to include it.
        :param `message` original ingress message from neighbor node
        """
        self._log_debug(f"Processing pathThrough for Switch {self.switchID}: message_origin={message.origin}")

        if message.origin not in self.switch_information[self.ACTIVE_LINKS]:
            self.switch_information[self.ACTIVE_LINKS].append(message.origin)
            self._log_debug(f"Added {message.origin} to active_links: {self.switch_information[self.ACTIVE_LINKS]}")

    def _check_distances(self, message):
        """
        Method to handle checking the distance of this switch compared to the ingress message if
        the root value is the same. Will return true or false to indicate whether the switch should
        update based on the following scenarios:

        1. If the message distance (+1) is less than this switch's distance to root, an update is needed.
        2. If the message distances are equal, then we need to check the switch IDs per assumption B.
        3. If the message distance is greater, then an update is not needed.

        :param `message` ingress message from neighbor node
        :returns boolean value indicating whether a switch update is needed or not
        """
        self._log_debug(f"Distance check for Switch {self.switchID}: message_distance+1={message.distance + 1} vs current_distance={self.switch_information[self.DISTANCE_TO_ROOT]}")

        if message.distance + 1 < self.switch_information[self.DISTANCE_TO_ROOT]:
            return True

        elif message.distance + 1 == self.switch_information[self.DISTANCE_TO_ROOT]:
            return self._check_id_tiebreaker(message)
        
        return False

    def _check_id_tiebreaker(self, message):
        """
        Method to handle breaking ties if the root ID and distance both match. This will evaluate
        based on the ID of the ingress message and this switch, which we can safely assume will always
        be positive integers and distinct (per project assumptions).

        :param `message` ingress message from neighbor node
        :returns boolean value indicating whether a switch update is needed or not
        """
        # Check the ID against the path of this switch's neighbor
        result = message.origin < self.switch_information[self.PATH_THROUGH]
        self._log_debug(f"Tiebreaker check for Switch {self.switchID}: message_origin={message.origin} vs current_path={self.switch_information[self.PATH_THROUGH]}, result={result}")
        return result 

    def _handle_switch_updates(self, message):
        """
        Handles needed updates to the switch. Performs the following functions:

        1. Updates basic information as needed (root, distance to root, path through)
        2. Updates active links if needed
        3. Handles bidirectional links if needed
        4. Sends messages to neighbors of this switch

        :param `message` ingress message from neighbor node
        """
        """Handles needed updates to the switch"""
        old_root = self.switch_information[self.ROOT]
        old_distance = self.switch_information[self.DISTANCE_TO_ROOT]
        old_path = self.switch_information[self.PATH_THROUGH]

        self._log_debug(f"\nSwitch {self.switchID} handling updates:")
        self._update_basic_information(message)

        # 2) If the root or path_through changed, prune old active links
        root_changed = (self.switch_information[self.ROOT] != old_root)
        path_changed = (self.switch_information[self.PATH_THROUGH] != old_path)

        if root_changed or path_changed:
            self._prune_active_links(new_path=message.origin)

        # self._update_active_links(message)
        self._handle_bidirectional_links(message)
        self._send_messages(message)    

    def _update_basic_information(self, message):
        self.switch_information[self.ROOT] = message.root
        self.switch_information[self.DISTANCE_TO_ROOT] = message.distance + 1
        self.switch_information[self.PATH_THROUGH] = message.origin

    def _prune_active_links(self, new_path):
        """
        Clear out old active links and keep only our new path to the root.
        This ensures we don't keep stale links from old root/distance.
        """
        self._log_debug(f"Pruning active links on switch {self.switchID}. Old links: {self.switch_information[self.ACTIVE_LINKS]}")
        
        # If the new path is actually ourselves (e.g., we remain root),
        # then we might empty everything. Otherwise, keep just the new path neighbor.
        if new_path != self.switchID:
            self.switch_information[self.ACTIVE_LINKS] = [new_path]
        else:
            self.switch_information[self.ACTIVE_LINKS] = []

        self._log_debug(f"New active links on switch {self.switchID}: {self.switch_information[self.ACTIVE_LINKS]}")

    def _update_active_links(self, message):
        # Clear old path if updating to a new path through
        self._log_debug(f"Updating active links. Current: {self.switch_information[self.ACTIVE_LINKS]}")

        # Add new path through
        if message.origin not in self.switch_information[self.ACTIVE_LINKS]:
            self.switch_information[self.ACTIVE_LINKS].append(message.origin)
            self._log_debug(f"Added new path through: {message.origin}")

    def _handle_bidirectional_links(self, message):
        self._log_debug(f"Processing bidirectional links. PathThrough: {message.pathThrough}")
        if message.pathThrough:
            if message.origin not in self.switch_information[self.ACTIVE_LINKS]:
                self.switch_information[self.ACTIVE_LINKS].append(message.origin)
                self._log_debug(f"Added bidirectional link: {message.origin}")

    def _send_messages(self, message):
        for neighbor in self.links:
            # path_through is True if this neighbor uses this switch to reach root
            path_through = (neighbor == self.switch_information[self.PATH_THROUGH])

            new_message = Message(
                self.switch_information[self.ROOT],
                self.switch_information[self.DISTANCE_TO_ROOT],
                self.switchID,
                neighbor,
                path_through,
                message.ttl
            )
            self.send_message(new_message)
            self._log_debug(f"\nFinal State of switch: {self.switchID}:")
            self._log_debug(f"Root: {self.switch_information[self.ROOT]}")
            self._log_debug(f"Distance to root: {self.switch_information[self.DISTANCE_TO_ROOT]}")
            self._log_debug(f"Active links: {self.switch_information[self.ACTIVE_LINKS]}")
            self._log_debug(f"Path through: {self.switch_information[self.PATH_THROUGH]}")

    def _init_switch_information(self):
        """
        Initialization method to create necessary member variables inside of the switch_information
        dictionary, assuming that each switch starts as the root.
        """
        self.switch_information = {
            self.ROOT: self.switchID, # Initially all switches assume they are the root
            self.DISTANCE_TO_ROOT: 0, # Distance to root node, initially at 0
            self.ACTIVE_LINKS: [], # Links in the spanning tree, order will be maintained in python arrays
            self.PATH_THROUGH: self.switchID, # Which neighbor to go through to reach root (self, since assumed root)
        }

    def _log_debug(self, message):
        """Method to store debug messages"""
        try:
            log_path = "debug_logs.log"
            with open(log_path, 'a') as log_file:
                log_file.write(f"Switch: {self.switchID} === DEBUG: {message} \n")
        except Exception as e:
            print("Error writing logs.")