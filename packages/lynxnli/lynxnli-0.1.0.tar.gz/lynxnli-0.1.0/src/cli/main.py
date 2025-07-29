import os
import time
import xml.etree.ElementTree as ET
from agents.trinity import TriadOfWises
from dotenv import load_dotenv


def format_content_for_xml(content):
    """Ensures content is XML-safe by converting it to a string.
    
    Args:
        content: Any data type that needs to be stored in XML
        
    Returns:
        str: XML-safe string representation of the content
    """
    if content is None:
        return ""
    return str(content)


def main():
    """Main function that handles the interactive CLI loop and XML session logging."""
    
    # Initialize environment and core components
    try:
        load_dotenv(dotenv_path=".env")
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        exit(1)

    # Display welcome message
    print("\n🤖 Welcome to the Triad Interaction Loop!")
    print("Enter your query below. Type 'q' or 'quit' to exit.")

    print(f"{'-' * 80}")
    triad = TriadOfWises(
        max_cycles=2
    )
    print(f"{'-' * 80}")
    
    # Main interaction loop
    while True:
        try:
            # Get user input with proper error handling
            user_input = input("🔍 Enter query: ")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Interruption detected. Exiting.")
            break

        # Handle exit commands
        if user_input.lower() in ['q', 'quit']:
            print("👋 Quit command received. Exiting loop.")
            break

        # Validate input
        if user_input.strip() == "":
            print("⚠️ Empty input detected. Please enter a valid query.")
            continue

        # Process query through the Triad system
        try:
            final_agent_state = triad.run(user_input)

        except Exception as e:
            # Log any processing errors
            error_message = f"❌ An error occurred during processing: {e}"
            print(error_message)
        
        print(f"{'-' * 15} Your query is completed, it's ready for next query{'-'*15}\n")

    # Save session data to XML file
    print("\n💾 Saving complete session...")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
        
    # Create XML structure
    xml_root = ET.Element("session", timestamp=timestamp)
    for queries in final_agent_state["context"].get_context():
        if queries["role"] == "query":
            query_element = ET.SubElement(xml_root, queries["input"])
            query_element.text = format_content_for_xml(queries["content"])

        # step_element = ET.SubElement(xml_root, task["name"])
        # step_element.text = format_content_for_xml(task["solution"])

    try:
        # Ensure output directory exists and save XML file
        os.makedirs("outputs", exist_ok=True)
        xml_path = os.path.join("outputs", f"session_{timestamp}.xml")
        tree = ET.ElementTree(xml_root)
            
        # Pretty print XML (Python 3.9+)
        if hasattr(ET, 'indent'):
            ET.indent(tree, space="\t", level=0)
            
        # Write XML file with proper encoding
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)
        print(f"✅ Session saved successfully as XML: {xml_path}")
            
    except Exception as e:
        print(f"❌ Error saving XML file: {e}")
    
    print("\n👋 Program finished.")


if __name__ == "__main__":
    main()