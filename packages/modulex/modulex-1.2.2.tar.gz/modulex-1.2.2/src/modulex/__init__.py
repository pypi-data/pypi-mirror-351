import os
import shutil

def createfolder():
    directory = input("Enter a name for a new folder: ").strip().replace(" ", "_")
    try:
        if os.path.exists(directory):
            print("There is already file that has this name on it. Try changing it to something different.")
            createfolder()
        os.makedirs(directory)
        print(f"Successfully created folder in {directory}")
    except Exception as e:
        print(f"Error creating folder: {e}")

def deletefolder():
    try:
        directory = input("Enter the name for the folder you want to delete: ").strip().replace(" ", "_")
        if not (os.path.exists(directory)):
            print("There is not such an directory")
            deletefolder()
        else:
            try:
                os.rmdir(directory)
                print(f"Successfully deleted folder named {directory}")
            except OSError:
                # Folder not empty - use shutil.rmtree
                shutil.rmtree(directory)
                print(f"Successfully deleted folder named {directory}")
    except ValueError as error:
        print(f"Something bad happened with your code: {error}")

def createFile():
    fname = input("Enter a file name: ").strip().replace(" ", "_")
    if len(fname) > 20:
        print("You can only create a file with maximum of 10 entered symbols!")
        return
    fextension = input("Enter a file extension (supports only txt for now): ").strip()
    if not (fextension == "txt"):
        print("Sorry but it needs to be txt extension.")
        return
    # Creates an file
    try:
        file = open(f"{fname}.{fextension}", "x")
        print(f"Successfully created a new file named {fname} in this directory")
    except FileExistsError:
        print("Sorry but the file you are trying to create is already there!")
        return
    # Writes on a file
    text = input("Enter a text that will be written on the file: ")
    file_format = open(f"{fname}.{fextension}", "w")
    file_format.write(text)
    file_format.close()
    print(f"Successfully setted a text for {fname}.{fextension}: {text}")

def deleteFile():
    filename = input("Enter a file name that you want to be deleted: ").strip()
    
    # Try exact filename first
    if os.path.exists(filename) and os.path.isfile(filename):
        try:
            os.remove(filename)
            print("The file was deleted successfully")
            return
        except PermissionError:
            print("Permission denied - file might be open in another program")
            return
        except Exception as error:
            print(f"There is some weird error. Have a look: {error}")
            return
    
    # If not found, try with underscores (for files created by your program)
    filename_underscore = filename.replace(" ", "_")
    if os.path.exists(filename_underscore) and os.path.isfile(filename_underscore):
        try:
            os.remove(filename_underscore)
            print("The file was deleted successfully")
            return
        except PermissionError:
            print("Permission denied - file might be open in another program")
            return
        except Exception as error:
            print(f"There is some weird error. Have a look: {error}")
            return
    
    print("There is no found file to delete. Maybe you need first to create it!")

def mainpanel():
    """Main panel for ModuleX file management"""
    while True:
        print("\n=== ModuleX File Manager ===")
        print("1. Create Folder")
        print("2. Delete Folder") 
        print("3. Create File")
        print("4. Delete File")
        print("5. Exit")
        
        choice = input("Choose an option (1-5): ").strip()
        
        if choice == "1":
            createfolder()
        elif choice == "2":
            deletefolder()
        elif choice == "3":
            createFile()
        elif choice == "4":
            deleteFile()
        elif choice == "5":
            print("Exiting ModuleX...")
            break
        else:
            print("Invalid choice! Please enter 1-5.")