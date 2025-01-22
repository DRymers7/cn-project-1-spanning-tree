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
        
    def process_message(self, message: Message):
        """
        Processes the messages from other switches. Updates its own data (members),
        if necessary, and sends messages to its neighbors, as needed.

        message: Message
            the Message received from other Switches
        """
        # TODO: This function needs to accept an incoming message and process it accordingly.
        #      This function is called every time the switch receives a new message.

        # Boolean value to determine if update needed (part a)
        should_update = False
        
        # If the message root is lower than the perceived root
        if message.root < self.switch_information[self.ROOT]:
            should_update = True

        # If the roots match, handle tie-breaking or improved distances
        elif message.root == self.switch_information[self.ROOT]:
            should_update = self._handle_distance_check(message)
            
        # Update information on the switch, if should_update is true
        if should_update:
            self._handle_switch_updates(message)
                
        # Handle path through updates (part b - III)
        if message.pathThrough:
            if message.origin not in self.switch_information[self.ACTIVE_LINKS]:
                self.switch_information[self.ACTIVE_LINKS].append(message.origin)
        else:
            # If this neighbor was previously marked active, but now says pathThrough=False
            if message.origin in self.switch_information[self.ACTIVE_LINKS]:
                # and it's not our current path-through, remove it
                if message.origin != self.switch_information[self.PATH_THROUGH]:
                    self.switch_information[self.ACTIVE_LINKS].remove(message.origin)

        # Decrement TTL AFTER the message has been processed (part c)
        message.ttl -= 1
            
        # Handle message sending to enighbors (part c)
        if message.ttl > 0:
            self._send_messages_to_neighbors(message)

    def _handle_distance_check(self, message):
        """
        Method to handle distance check (if root value is even)

        1. Evaluates if the message distance (+1) is lower than the distance on the switch
        2. If this value is equal, then if the message is a better path to the root, then we should
        also update.
        """
        if (message.distance + 1) < self.switch_information[self.DISTANCE_TO_ROOT]:
            return True

        # If the distance is the same, check the tie-break rule:
        # we choose the neighbor with the lower ID as our path to the root
        elif message.distance + 1 == self.switch_information[self.DISTANCE_TO_ROOT]:
            # Only use lower ID tie-breaker if both paths are valid
            if message.origin < self.switch_information[self.PATH_THROUGH]:
                return True
        return False
            
    def _handle_switch_updates(self, message):
        """
        Method to handle switch updates. Handles the following:

        1. Updates the switch perceived root to that value on the ingress message
        2. Updates the distance to the distance on the message + 1
        3. Updates the path through value to be the origin of the message 
        4. Checks to remove the old path from active links if applicable (part b)
        5. Checks to add message origin to active links if applicable (part b)
        """
        old_path = self.switch_information[self.PATH_THROUGH]
        
        self.switch_information[self.ROOT] = message.root
        self.switch_information[self.DISTANCE_TO_ROOT] = message.distance + 1
        self.switch_information[self.PATH_THROUGH] = message.origin

        if old_path != self.switchID:  
            if old_path in self.switch_information[self.ACTIVE_LINKS]:
                self.switch_information[self.ACTIVE_LINKS].remove(old_path)
        
        if message.origin not in self.switch_information[self.ACTIVE_LINKS]:
            self.switch_information[self.ACTIVE_LINKS].append(message.origin)

    def _send_messages_to_neighbors(self, message):
        """
        Method to handle forwarding messages to neighbors of this switch. Does the following:

        1. For each neighbor in the links struct
        2. Evaluate if that neighbor uses us to get to the root or if we use them to get to the root
        3. Populate and send a new instance of `Message()`
        """
        for neighbor in self.links:
            path_through = (neighbor == self.switch_information[self.PATH_THROUGH] or 
                        self.switchID == self.switch_information[self.PATH_THROUGH])
            
            new_message = Message(
                self.switch_information[self.ROOT],
                self.switch_information[self.DISTANCE_TO_ROOT],
                self.switchID,
                neighbor,
                path_through,
                message.ttl
            )
            self.send_message(new_message)

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