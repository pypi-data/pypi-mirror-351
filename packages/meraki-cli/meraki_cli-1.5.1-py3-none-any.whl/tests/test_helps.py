import unittest
import types
import os
from meraki_cli.__main__ import _cmd_title, _cmd_help, Args


class TestHelps(unittest.TestCase):

    def makeArgObjectList(self, struct):
        """
        Get all Arg() instance objects from the structure and output them
            as a simple list.
        """
        # Iterate each k,v pair in the struct dict
        for name, object in struct.items():
            # If the object is an instance of the Args class
            if isinstance(object, Args):
                # Add it to the list
                self.arg_object_list.append(object)
            else:  # If the object is NOT an instance of the Args class
                # Recurse into the object to find some Args instances
                self.makeArgObjectList(object)

    def setUp(self):
        # Use the importlib to help import the _get_structure builder from the
        #     command guide builder file
        from importlib.machinery import SourceFileLoader
        # Get the directory of this file
        filedir = os.path.abspath(os.path.join(__file__, os.pardir))
        # Get the parent dir of this dir
        pardir = os.path.dirname(filedir)
        # Build the path to the .command_guide_build.py file
        builderfile = os.path.join(pardir, '.command_guide_build.py')
        # Create the module loader from the source file
        loader = SourceFileLoader('builder', builderfile)
        # Initialize the module
        self.builder = types.ModuleType(loader.name)
        # Execute the build of the module
        loader.exec_module(self.builder)
        # Grab the class and method structure
        struct = self.builder._get_structure()
        # Start an empty list to contain all the arg objects
        self.arg_object_list = []
        # Run the method to convert the structure to our list of Args instances
        self.makeArgObjectList(struct)

    def testTitle(self):
        assert _cmd_title('oneTwoThree') == 'One Two Three'
        assert _cmd_title('OneTwoThree') == 'One Two Three'
        assert _cmd_title('onetwoThree') == 'Onetwo Three'

    def testAllCmdGuideCmdSections(self):
        """
        Test generating command guide help sections for each method
        """
        for argObject in self.arg_object_list:
            # And test building the command section for each arg object
            self.builder._cmd_section(argObject)

    def testAllCmdGuideCmdArgExamples(self):
        """
        Test generating example arguments for each method
        """
        for argObject in self.arg_object_list:
            # Test building the example arg list for this object
            self.builder._cmd_args(argObject)

    def testAllCLIHelpPages(self):
        """
        Test the help page modifications for every available function
        """
        for argObject in self.arg_object_list:
            # And test building a CLI help page for every method
            _cmd_help(argObject)
