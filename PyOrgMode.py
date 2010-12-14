# -*- encoding: utf-8 -*-
##############################################################################
#
#    PyOrgMode, a python module for treating with orgfiles
#    Copyright (C) 2010 Jonathan BISSON (bissonjonathan on the google thing).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""
The PyOrgMode class is able to read,modify and create orgfiles. The internal
representation of the file allows the use of orgfiles easily in your projects.
"""

import re
import string

# TODO Error/Warning managment
# TODO Document every function correctly (docstrings) [10%]
# TODO Check for other OS compatibility
# TODO Do a validator (input file MUST be output file, and check every function)
# TODO TODO tags (and others)
# TODO Priority
# TODO Add more types of data (List,…) 
# BUG The drawers lost indentation and added spaces/tabs in properties :NON-BLOCKING::NO-DATA-LOSS: 

class OrgElement:
    """
    Generic class for all Elements excepted text and unrecognized ones
    """
    def __init__(self):
        self.content=[]
        self.parent=None
    def append(self,element):
        # TODO Check validity
        self.content.append(element)
        # Check if the element got a parent attribute
        # If so, we can have childrens into this element
        if hasattr(element,"parent"):
            element.parent = self
        return element

class Property(OrgElement):
    """
    A Property object, used in drawers.
    """
    def __init__(self,name="",value=""):
        OrgElement.__init__(self)
        self.name = name
        self.value = value
    def __str__(self):
        """
        Outputs the property in text format (e.g. :name: value)
        """
        return ":" + self.name + ": " + self.value

class Drawer(OrgElement):
    """
    A Drawer object, containing properties and text
    """
    # TODO has_property, get_property
    def __init__(self,name=""):
        OrgElement.__init__(self)
        self.name = name
    def __str__(self):
        output = ":" + self.name + ":\n"
        for element in self.content:
            output = output + str(element) + "\n"
        output = output + ":END:\n"
        return output

class Node(OrgElement):
    # Defines an OrgMode Node in a structure
    # The ID is auto-generated using uuid.
    # The level 0 is the document itself

    def __init__(self):
        OrgElement.__init__(self)
        self.content = []       
        self.level = 0
        self.heading = ""
        self.tags = []
        # TODO  Scheduling structure

    def __str__(self):
        output = ""

        if hasattr(self,"level"):
            output = output + "*"*self.level

        if self.parent != None:
            output = output + " " + self.heading

            for tag in self.tags:
                output= output + ":" + tag + ":"

            output = output + "\n"
  
        for element in self.content:
            output = output + element.__str__()

        return output

class Datastructure:
    """
    Data structure containing all the nodes
    The root property contains a reference to the level 0 node
    """
    # TODO Move or delete nodes (should be easy now)
    root = None

    def append(self,node):
        if (node.parent == None): # Node has no parent (so it is the level 0 node)
            self.root = node # So parent is the first added node
        else:
            node.parent.append(node)

    def load_from_file(self,name):
        current = Node()
        parent = None
        file = open(name,'r')

        re_heading_stars = re.compile("^(\*+)\s(.*?)\s*$")
        re_drawer = re.compile("^(?:\s*?)(?::)(\S.*?)(?::)\s*(.*?)$")
        re_heading = re.compile("(?:\*+)\s((.*?)(?:\s*.*?)\s*\s)((:\S(.*?)\S:$)|$)")
        # The (?!.*?\]) protects against links containing tags being considered as tags
        re_tags = re.compile("(?:::|\s:)(\S.*?\S)(?=:)(?!.*?\])")

        current_drawer = None
        for line in file:
            heading_stars = re_heading_stars.search(line)
            drawer = re_drawer.search(line)

            if type(current) == Drawer:
                if drawer:
                    if drawer.group(1) == "END":
                        current = current.parent
                    elif drawer.group(2):
                        current.append(Property(drawer.group(1),drawer.group(2)))
                else:
                    current.append(line.rstrip("\n"))
            elif drawer:
                current = current.append(Drawer(drawer.group(1)))

            elif heading_stars: # We have a heading
                self.append(current) # We append the current node as it is done

                # Is that a new level ?
                if (len(heading_stars.group(1)) > current.level): # Yes
                    parent = current # Parent is now the current node

                # If we are going back one or more levels, walk through parents
                while len(heading_stars.group(1)) < current.level:
                    current = current.parent

                # Creating a new node and assigning parameters
                current = Node() 
                current.level = len(heading_stars.group(1))
                current.heading = re_heading.findall(line)[0][0].rstrip("\n")
                current.parent = parent
                
                # Looking for tags
                current.tags = re_tags.findall(line)
            else: # Nothing special, just content
                if line != None:
                    current.append(line)

        # Add the last node
        if current.level>0:
            self.append(current)

        file.close()

    def save_to_file(self,name):
        output = open(name,'w')
        output.write(str(self.root))
        output.close()
