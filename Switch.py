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

        print(f"\nSwitch {self.switchID} received message: root={message.root}, dist={message.distance}, origin={message.origin}, pathThrough={message.pathThrough}, ttl={message.ttl}")
        print(f"Switch {self.switchID} current state: root={self.switch_information[self.ROOT]}, dist={self.switch_information[self.DISTANCE_TO_ROOT]}, path={self.switch_information[self.PATH_THROUGH]}")

        # Part a: Determine if root update is needed
        should_update = False
        
        if message.root < self.switch_information[self.ROOT]:
            should_update = True
            print(f"Switch {self.switchID} updating due to lower root: {message.root} < {self.switch_information[self.ROOT]}")
        
        elif message.root == self.switch_information[self.ROOT]:
            if message.distance + 1 < self.switch_information[self.DISTANCE_TO_ROOT]:
                should_update = True
                print(f"Switch {self.switchID} updating due to shorter path: {message.distance + 1} < {self.switch_information[self.DISTANCE_TO_ROOT]}")
            elif message.distance + 1 == self.switch_information[self.DISTANCE_TO_ROOT]:
                if message.origin < self.switch_information[self.PATH_THROUGH]:
                    should_update = True
                    print(f"Switch {self.switchID} updating due to lower neighbor ID: {message.origin} < {self.switch_information[self.PATH_THROUGH]}")
                
        if should_update:
            old_path = self.switch_information[self.PATH_THROUGH]
            
            self.switch_information[self.ROOT] = message.root
            self.switch_information[self.DISTANCE_TO_ROOT] = message.distance + 1
            self.switch_information[self.PATH_THROUGH] = message.origin
            print(f"Switch {self.switchID} after update: root={self.switch_information[self.ROOT]}, dist={self.switch_information[self.DISTANCE_TO_ROOT]}, path={self.switch_information[self.PATH_THROUGH]}")

            if old_path != self.switchID:  
                if old_path in self.switch_information[self.ACTIVE_LINKS]:
                    print(f"Switch {self.switchID} removing old path {old_path} from active links")
                    self.switch_information[self.ACTIVE_LINKS].remove(old_path)
            
            if message.origin not in self.switch_information[self.ACTIVE_LINKS]:
                print(f"Switch {self.switchID} adding new path {message.origin} to active links")
                self.switch_information[self.ACTIVE_LINKS].append(message.origin)
                
        if message.pathThrough:
            if message.origin not in self.switch_information[self.ACTIVE_LINKS]:
                print(f"Switch {self.switchID} adding {message.origin} to active links due to pathThrough=True")
                self.switch_information[self.ACTIVE_LINKS].append(message.origin)
        elif message.origin != self.switch_information[self.PATH_THROUGH]:
            if message.origin in self.switch_information[self.ACTIVE_LINKS]:
                print(f"Switch {self.switchID} removing {message.origin} from active links due to pathThrough=False")
                self.switch_information[self.ACTIVE_LINKS].remove(message.origin)

        print(f"Switch {self.switchID} final state: active_links={self.switch_information[self.ACTIVE_LINKS]}")

        # Part c: Message sending
        message.ttl -= 1
            
        if message.ttl > 0:
            print(f"Switch {self.switchID} sending messages to neighbors, ttl={message.ttl}")
            for neighbor in self.links:
                # If this neighbor uses us to get to root OR we use them to get to root
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
        else:
            print(f"Switch {self.switchID} TTL=0, not forwarding messages")

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
        if message.origin not in self.switch_information[self.ACTIVE_LINKS]:
            self.switch_information[self.ACTIVE_LINKS].append(message.origin)

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
        self._update_basic_information(message)
        self._update_active_links(message)
        self._handle_bidirectional_links(message)
        self._send_messages(message)    

    def _update_basic_information(self, message):
        self.switch_information[self.ROOT] = message.root
        self.switch_information[self.DISTANCE_TO_ROOT] = message.distance + 1
        self.switch_information[self.PATH_THROUGH] = message.origin

    def _update_active_links(self, message):
        if message.origin not in self.switch_information[self.ACTIVE_LINKS]:
            self.switch_information[self.ACTIVE_LINKS].append(message.origin)

    def _handle_bidirectional_links(self, message):
        if message.pathThrough:
            if message.origin not in self.switch_information[self.ACTIVE_LINKS]:
                self.switch_information[self.ACTIVE_LINKS].append(message.origin)

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