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

    """
    Notes:
    StpSwitch send_message: wrapper to invoke so we do not have to use method in Topology directly.
    Message: message used to communicate between switches, instantiated by: msg = Message(claimedRoot, distanceToRoot, originID, destinationID, pathThrough, timeToLive)

    Each node must keep track of the best config message it has received so far, and compare against config message it is receiving from neighbors that round.
    Node ID 3 first sends <3, 3, 0> -> between two configs, the node selects that one config is better if:
    - Root of the config has a smaller ID or:
    - Smaller distance from the root
    - Ties are broken with smallest ID
    - Stop sending messages over links when the node receveis a message that indicates it is not the root (either neighbor closer to root, or same distance but
    smaller ID)

    What I need to do: 
    1. Use a data struct to keep track of spanning tree
     - Must act in such a way to track each switch's own view of the three.
     - Switch only has access to its member variables, to learn from a neighbor, the neighbor must send a message.
    2. Data struct:
     - var to store switch ID that this switch sees as root (every switch should start assuming it is the root)
     - var to store distance to switch root
     - list to store active links
     - var to keep track of which neighbor it goes through to get to the root (ID I'm assuming)
    3. Implement processing messages from immediate neighbor
     - Determine whether root info update is needed (if receive message with lower claimedRoot)
     - Update distance stored in data struct if switch updates the root or there is a shorter path to the same root
     - Update switches active links (switch updates the root or there is a shorter path to same root)
     (ref 2b)
    4. Keep sending until TTL == 0
    5. Write logging function
    """
    def __init__(self, idNum: int, topolink: object, neighbors: list):
        """
        Invokes the super class constructor (StpSwitch), which makes the following
        members available to this object:

        idNum: int
            the ID number of this switch object
        neighbors: list
            the list of switch IDs connected to this switch object
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

        # Boolean indication of if the switch should update based on ingress message, defaulting to false
        should_switch_update = False

        print(f"\nSwitch {self.switchID} processing message:")
        print(f"Message details: root={message.root}, distance={message.distance}, origin={message.origin}, pathThrough={message.pathThrough}")
        print(f"Current switch state: root={self.switch_information[self.ROOT]}, distance={self.switch_information[self.DISTANCE_TO_ROOT]}")

        # Handle pathThrough messages for ALL switches
        if message.pathThrough:
            if message.origin not in self.switch_information[self.ACTIVE_LINKS]:
                self.switch_information[self.ACTIVE_LINKS].append(message.origin)

        # 1. Decrement the TTL, as this will determine if we forward the message
        message.ttl -= 1

        # 2. Should update root if message received with lower claimed root
        if message.root < self.switch_information[self.ROOT]:
            should_switch_update = True

        # 3. If the root is the same, check the distance
        elif message.root == self.switch_information[self.ROOT]:
            should_switch_update = self._check_distances(message)

        print(f"Should update: {should_switch_update}")

        # 4. Handle updates (this also sends the new message). 
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
        link_strings = [f"{self.switchID} - {link}" for link in active_links]
        
        return ", ".join(link_strings) if link_strings else f"{self.switchID}"

    def _check_distances(self, message):
        """
        Method to handle checking the distance of this switch compared to the ingress message if
        the root value is the same. 

        :param `message` ingress message from neighbor in STP
        :param `should_switch_update` simple indicator of whether the criteria have been met for switch
        to update switch_information
        """
        print(f"Distance check: message distance+1 {message.distance + 1} vs current distance {self.switch_information[self.DISTANCE_TO_ROOT]}")

        if message.distance + 1 < self.switch_information[self.DISTANCE_TO_ROOT]:
            return True

        elif message.distance + 1 == self.switch_information[self.DISTANCE_TO_ROOT]:
            return self._check_id_tiebreaker(message)
        
        return False

    def _check_id_tiebreaker(self, message):
        """
        Method to handle breaking ties if the root ID and distance both match. This will evaluate
        based on the ID of the ingress message and this switch, which we can safely assume will always
        be positive integers and distinct.

        :returns boolean flag to indicate if switch should update
        """
        result = message.origin < self.switch_information[self.PATH_THROUGH]
        print(f"Tiebreaker check: message origin {message.origin} vs current path {self.switch_information[self.PATH_THROUGH]}, result: {result}")

        return result # per assumption B

    def _handle_switch_updates(self, message):
        """Updates switch state and sends messages to neighbors.

        Three cases for active links updates:
        1. When finding new path to root through different neighbor
        2. When receiving pathThrough=True and originID not in activeLinks
        3. When receiving pathThrough=False and originID in activeLinks
        """
        old_path = self.switch_information[self.PATH_THROUGH]

        print(f"\nSwitch {self.switchID} handling updates:")
        print(f"Before update - active_links: {self.switch_information[self.ACTIVE_LINKS]}")
        print(f"Old path: {old_path}, New path: {message.origin}")
        
        # 1. Update basic info
        self.switch_information[self.ROOT] = message.root
        self.switch_information[self.DISTANCE_TO_ROOT] = message.distance + 1
        self.switch_information[self.PATH_THROUGH] = message.origin
        
        # 2. Update active links
        # Remove old path if changed
        if old_path != message.origin and old_path in self.switch_information[self.ACTIVE_LINKS]:
            self.switch_information[self.ACTIVE_LINKS].remove(old_path)
        
        # Add new path
        if message.origin not in self.switch_information[self.ACTIVE_LINKS]:
            self.switch_information[self.ACTIVE_LINKS].append(message.origin)
        
        # Handle pathThrough
        if message.pathThrough and message.origin not in self.switch_information[self.ACTIVE_LINKS]:
            self.switch_information[self.ACTIVE_LINKS].append(message.origin)
        
        print(f"After update - active_links: {self.switch_information[self.ACTIVE_LINKS]}")

        # 3. Send messages to all neighbors
        for neighbor in self.links:
            path_through = (neighbor == self.switch_information[self.PATH_THROUGH])
            print(f"neighbor={neighbor}, my_path={self.switch_information[self.PATH_THROUGH]}, pathThrough={path_through}")

            new_message = Message(
                self.switch_information[self.ROOT],
                self.switch_information[self.DISTANCE_TO_ROOT],
                self.switchID,
                neighbor,
                path_through,
                message.ttl
            )
            print(f"Sending message to {neighbor} with pathThrough={path_through}")
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