import sys
from python_resources.index import main as process_mods
from python_resources.config import setup_config

def show_menu():
    print("\nCK3 Workshop Tool - Command Interface")
    print("====================================")
    print("1. Process all mods")
    print("2. Configure tool paths")
    print("3. Show help")
    print("4. Exit")
    print("====================================")

def show_help():
    print("\nCK3 Workshop Tool Help")
    print("---------------------")
    print("This tool helps manage CK3 mods from Steam Workshop and local files.")
    print("\nAvailable commands:")
    print("1. Process all mods - Runs the main mod processing function")
    print("2. Configure tool paths - Set up or modify directory paths")
    print("3. Show help - Display this help information")
    print("4. Exit - Quit the program")
    print("\nYou can also run specific functions directly:")
    print("- 'process' to process mods")
    print("- 'config' to configure paths")
    print("- 'help' to show help")

def main():
    if len(sys.argv) > 1:
        # Handle direct commands
        command = sys.argv[1].lower()
        if command == 'process':
            process_mods()
        elif command == 'config':
            setup_config()
        elif command == 'help':
            show_help()
        else:
            print(f"Unknown command: {command}")
            show_help()
        return

    # Interactive mode
    while True:
        show_menu()
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            print("\nProcessing mods...")
            process_mods()
        elif choice == '2':
            print("\nConfiguring tool paths...")
            setup_config()
        elif choice == '3':
            show_help()
        elif choice == '4':
            print("\nExiting CK3 Workshop Tool. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1-4.")

if __name__ == "__main__":
    main()
