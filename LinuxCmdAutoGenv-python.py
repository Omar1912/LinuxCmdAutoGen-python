import subprocess
import xml.etree.ElementTree as ET

class CommandManual:
    def __init__(self, command):
        # Initialize the CommandManual object with the specified command
        self.command = command
        # Generate a clean version of the command name
        self.clean_command_name = self.clean_command_name()
        # Retrieve the description of the command from its manual
        self.description = self.get_description()
        # Retrieve the version history of the command
        self.version_history = self.get_version_history()
        # Retrieve an example usage of the command
        self.example = self.get_example()
        # Retrieve related commands of the current command
        self.related_commands = self.get_related_commands()

    def clean_command_name(self):
        # Clean the command name by removing non-alphanumeric characters
        return ''.join(char for char in self.command if char.isalnum())

    def get_description(self):
        try:
            # Fetch the manual of the command and extract its description
            man_output = subprocess.check_output(['man', self.command], universal_newlines=True)
            description_start = man_output.find("DESCRIPTION")
            if description_start != -1:
                description_line_start = man_output.find('\n', description_start) + 1
                description_line_end = man_output.find('\n', description_line_start)
                description = man_output[description_line_start:description_line_end].strip()
                return description
            else:
                return f"Error: 'DESCRIPTION' not found in the manual for command '{self.command}'."
        except subprocess.CalledProcessError as e:
            return f"Error retrieving description for command '{self.command}': {e}"
        except Exception as e:
            return f"Unexpected error retrieving description for command '{self.command}': {e}"

    def get_version_history(self):
        try:
            # Retrieve the version history of the command
            version_output = subprocess.check_output([self.command, '--version'], stderr=subprocess.STDOUT, universal_newlines=True)
            return version_output.strip()
        except subprocess.CalledProcessError as e:
            return f"Error retrieving version history for command '{self.command}': {e.output.strip()}"
        except Exception as e:
            return f"Unexpected error retrieving version history for command '{self.command}': {e}"

    def get_example(self):
     try:
        # Fetch the manual of the command and extract its example usage
        man_output = subprocess.check_output(['man', self.command], universal_newlines=True)
        example_start = man_output.find("EXAMPLES")
        if example_start != -1:
            example_lines = man_output[example_start:]
            # Extract the first non-empty line after "EXAMPLES"
            example = "\n".join(line.strip() for line in example_lines.split('\n')[1:2] if line.strip())
            return example
        else:
            return f"Error: 'EXAMPLES' not found in the manual for command '{self.command}'."
     except subprocess.CalledProcessError as e:
        return f"Error retrieving example for command '{self.command}': {e}"
     except Exception as e:
        return f"Unexpected error retrieving example for command '{self.command}': {e}"

    def get_related_commands(self):
     try:
        # Fetch the manual of the command and extract related commands from the "SEE ALSO" section
        man_output = subprocess.check_output(['man', self.command], universal_newlines=True)
        start_index = man_output.find("SEE ALSO")
        end_index = man_output.find("\n\n", start_index)  # Find the first empty line after "SEE ALSO"
        if start_index != -1 and end_index != -1:
            related_commands = man_output[start_index:end_index].strip()
            # Extract only the first line after "SEE ALSO"
            related_commands_lines = related_commands.split('\n')
            if len(related_commands_lines) > 1:
                return related_commands_lines[1].strip()
            else:
                return ""  # If there is no line after "SEE ALSO"
        else:
            return "SEE ALSO section not found in the manual."
     except subprocess.CalledProcessError as e:
        return f"Error retrieving related commands: {e}"
     except Exception as e:
        return f"Unexpected error retrieving related commands: {e}"

     # Method to convert CommandManual object to XML format
    def to_xml(self):
        try:
            # Create XML structure for the CommandManual object
            command_manual_element = ET.Element('CommandManual')
            command_name_element = ET.SubElement(command_manual_element, 'CommandName')
            command_name_element.text = self.command
            command_description_element = ET.SubElement(command_manual_element, 'CommandDescription')
            command_description_element.text = self.get_description()
            version_history_element = ET.SubElement(command_manual_element, 'VersionHistory')
            version_history_element.text = self.get_version_history()
            example_element = ET.SubElement(command_manual_element, 'Example')
            example_element.text = self.get_example()
            related_commands_element = ET.SubElement(command_manual_element, 'RelatedCommands')
            related_commands_element.text = self.get_related_commands()
            # Convert XML content to string and format it for readability
            xml_content = ET.tostring(command_manual_element, encoding='utf-8', method='xml').decode('utf-8')
            formatted_xml = xml_content.replace('><', '>\n<')

            return formatted_xml
        except Exception as e:
            return f"Error creating XML for command '{self.command}': {str(e)} - {repr(e)}"

# Class responsible for serializing CommandManual objects to XML
class XmlSerializer:
    @staticmethod
    def serialize(command_manual):
        return command_manual.to_xml()

# Class to generate CommandManual objects from input files
class CommandManualGenerator:
    def __init__(self, input_file):
        # Check if the input file exists
        if self.is_file_exists(input_file):
            # Read commands from the input file
            self.commands = self.read_commands_from_file(input_file)
            # List to store CommandManual objects
            self.command_manuals = []
            # Load existing manuals for commands
            self.load_existing_manuals()
        else:
            raise FileNotFoundError(f"The provided input '{input_file}' is not a valid file.")

    # Check if the file exists at the specified path
    def is_file_exists(self, file_path):
        try:
            with open(file_path):
                pass
            return True
        except FileNotFoundError:
            return False
    def read_commands_from_file(self, input_file):
        with open(input_file, 'r') as file:
            return [line.strip() for line in file.readlines()]

    # Method to load existing manuals from XML files for provided commands
    def load_existing_manuals(self):
    # Dictionary to store existing manuals
     self.existing_manuals = {}
     for command in self.commands:
        xml_file = f"{command}.xml"
        # Check if XML file exists for the command
        if self.is_file_exists(xml_file):  
            # Load manual from XML file and add it to existing manuals dictionary
            existing_manual = self.load_manual_from_xml_file(command)
            if existing_manual:
                self.existing_manuals[existing_manual.clean_command_name] = existing_manual

    # Method to load a manual from an XML file
    def load_manual_from_xml_file(self, command):
     xml_file = f"{command}.xml"
     try:
        # Parse XML file and extract manual information
        tree = ET.parse(xml_file)
        root = tree.getroot()
        command_name = root.find('CommandName').text
        description = root.find('CommandDescription').text
        version_history = root.find('VersionHistory').text
        example = root.find('Example').text
        related_commands = root.find('RelatedCommands').text

        # Create a CommandManual object with the extracted information
        command_manual = CommandManual(command_name)
        command_manual.description = description
        command_manual.version_history = version_history
        command_manual.example = example
        command_manual.related_commands = related_commands

        return command_manual
     except Exception as e:
        print(f"Error loading manual from XML file '{xml_file}': {e}")
        return None

    # Method to save CommandManual objects to XML files
    def save_to_xml_files(self):
     for command_manual in self.command_manuals:
        # Serialize CommandManual object to XML format
        xml_content = XmlSerializer.serialize(command_manual)
        output_file = f"{command_manual.clean_command_name}.xml"
        # Write XML content to file
        with open(output_file, 'w') as file:
            file.write(xml_content)

    # Method to generate manuals for provided commands
    def generate_manuals(self):
     for command in self.commands:
        # Create CommandManual objects for each command and add them to the list
        command_manual = CommandManual(command)
        self.command_manuals.append(command_manual)

    # Method to generate temporary XML files for command manuals
    def generate_temporary_xml_files(self):
     for command_manual in self.command_manuals:
        # Create temporary XML file for each command manual
        temp_xml_file = f"temp_{command_manual.clean_command_name}.xml"
        xml_content = XmlSerializer.serialize(command_manual)
        with open(temp_xml_file, 'w') as file:
            file.write(xml_content)

    # Method to display the content of an XML file for a given command
    def display_xml_file(self, command_name):
     try:
        xml_file_path = f"{command_name}.xml"
        # Check if the XML file exists
        if self.is_file_exists(xml_file_path):
            with open(xml_file_path, 'r') as xml_file:
                xml_content = xml_file.read()
                # Display the XML file content
                print(f"XML file content for command '{command_name}':\n")
                print(xml_content)
        else:
            print(f"XML file for command '{command_name}' not found.")
     except Exception as e:
        print(f"Error during XML file display: {e}")

    # Method to verify changes between original and temporary XML files
    def verify_changes(self):
     try:
        for command in self.commands:
            original_xml_file = f"{command}.xml"
            temp_xml_file = f"temp_{command}.xml"

            # Check if both original and temporary XML files exist
            if self.is_file_exists(original_xml_file) and self.is_file_exists(temp_xml_file):
                try:
                    # Perform a diff operation between the files
                    subprocess.check_output(['diff', '-u', original_xml_file, temp_xml_file])
                    print(f"Pass: No changes detected for command '{command}'.")
                except subprocess.CalledProcessError as e:
                    print(f"Changes detected for command '{command}':")
                    print(e.output.strip())
                    print("\n")
            else:
                print(f"Error: XML file for command '{command}' not found.")

        print("Verification complete.")
     except Exception as e:
        print(f"Error during verification: {e}")

    def search_functionality(self):
     try:
        # Prompt user for search preference
        search = input("Do you want to find specific information about any command? (y/n): ")
        if search.lower() == "y":
            # Get user input for command name and desired information
            part3name = input("Please write the command name: ")
            info_choice = input("Enter what you want to know about this command (1. Description, 2. Version History, 3. Example, 4. Related Commands): ")

            found_in_xml = False
            # Determine the type of information to retrieve from XML
            if info_choice == "1":
                found_in_xml = self.display_info_from_xml(part3name, "Description", lambda x: x.get_description())
            elif info_choice == "2":
                found_in_xml = self.display_info_from_xml(part3name, "Version History", lambda x: x.get_version_history())
            elif info_choice == "3":
                found_in_xml = self.display_info_from_xml(part3name, "Example", lambda x: x.get_example())
            elif info_choice == "4":
                found_in_xml = self.display_info_from_xml(part3name, "Related Commands", lambda x: x.get_related_commands())
            else:
                print("Invalid choice")

            # If information is not found in XML, try fetching from the command line
            if not found_in_xml:
                print(f"Information not found in XML for command '{part3name}'. Fetching from the command line.")

        # Prompt user for searching a word in command descriptions
        search1 = input("Do you want to search for a word in the command's Description (XML)? (y/n): ")
        if search1.lower() == "y":
            search_word = input("Please write the word you want to search in command descriptions: ")
            print(f"Searching for the word '{search_word}' in command descriptions (XML)...")
            found_in_description = self.search_word_in_descriptions(search_word)
            if not found_in_description:
                print(f"No commands found with the word '{search_word}' in descriptions (XML).")

     except Exception as e:
        print(f"Error during search: {e}")

    # Method to display specific information about a command from XML
    def display_info_from_xml(self, command_name, info_type, info_extractor):
     if command_name in self.existing_manuals:
        command_manual = self.existing_manuals[command_name]
        info = info_extractor(command_manual)
        if info:
            print(f"{info_type} from XML: {info}")
            return True
        return False

    def search_word_in_descriptions(self, search_word):
     found_in_description = False
     # Iterate through command manuals and check if the search word is in the description
     for command_manual in self.command_manuals:
        cmd_description = command_manual.get_description()
        if search_word.lower() in cmd_description.lower():
            print(f"Command: {command_manual.command}")
            found_in_description = True
        return found_in_description

    # Lists of commands categorized by functionality
    SystemInformation = ["info", "man", "find", "lshw", "cat", "date"]
    Networking = ["tcpdump", "nmcli"]
    ProcessManagment = ["ps", "kill", "awk"]
    Fourletters = ["tmux", "date", "comm", "file"]
    locale = ["locale"]
    compression = ["zip", "unzip"]

    # Method to provide recommendations based on command categories
    def command_recommendation_system(self, command):
     # Clean the command name for comparison
     clean_command_name = ''.join(char for char in command if char.isalnum())
     recommendation_found = False

    # Check if the command belongs to any predefined category and print recommendations
     if clean_command_name in CommandManualGenerator.SystemInformation:
        print("System Information:")
        print('\n'.join(CommandManualGenerator.SystemInformation))
        recommendation_found = True

     if clean_command_name in CommandManualGenerator.Networking:
        print("Recommendations for Networking:")
        print(CommandManualGenerator.Networking)
        recommendation_found = True

     if clean_command_name in CommandManualGenerator.ProcessManagment:
        print("Recommendations for Process Management:")
        print(CommandManualGenerator.ProcessManagment)
        recommendation_found = True

     if clean_command_name in CommandManualGenerator.Fourletters:
        print("Recommendations for Four letters:")
        print(CommandManualGenerator.Fourletters)
        recommendation_found = True

     if clean_command_name in CommandManualGenerator.locale:
        print("Recommendations for locale:")
        print(CommandManualGenerator.locale)
        recommendation_found = True

     if clean_command_name in CommandManualGenerator.compression:
        print("Recommendations for compression:")
        print(CommandManualGenerator.compression)
        recommendation_found = True

    # If no recommendations are found for the command
     if not recommendation_found:
        print("No specific recommendations found for the command.")

if __name__ == "__main__":
    # Initialize the CommandManualGenerator with the input file
    input_file = "commands1.txt"
    try:
        generator = CommandManualGenerator(input_file)
        # Display menu options and handle user input
        while True:
            print("\nMenu:")
            print("1. Generate Manuals")
            print("2. Show Manual for a Command")
            print("3. Verify Changes")
            print("4. Search Functionality")
            print("5. Command Recommendation System")
            print("6. Exit")
            choice = input("Enter your choice (1-6): ")

            # Perform actions based on user choice
            if choice == "1":
                generator.generate_manuals()
                generator.save_to_xml_files()
                generator.generate_temporary_xml_files()
            elif choice == "2":
                command_to_display_xml = input("Enter the command name to display its XML file: ")
                generator.display_xml_file(command_to_display_xml)
            elif choice == "3":
                generator.verify_changes()
            elif choice == "4":
                generator.search_functionality()
            elif choice == "5":
                command_to_recommend = input("Enter the command for recommendations: ")
                generator.command_recommendation_system(command_to_recommend)
            elif choice == "6":
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
    except FileNotFoundError as e:
        print(f"Error: {e}")
