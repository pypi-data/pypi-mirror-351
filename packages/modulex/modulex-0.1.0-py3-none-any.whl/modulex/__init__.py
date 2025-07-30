import os
def createfolder():
    directory = input("Enter a name for a new folder: ").strip().replace(" ", "_")
    try:
        if os.path.exists(directory):
            print("There is already file that has this name on it. Try chainging it to something difrent.")
            createfolder()
        os.makedirs(directory)
        print(f"Successfully created folder in {directory}")
    except Exception as e:
        a = 5
def deletefolder():
    try:

        directory = input("Enter the name for the folder you want to delete: ").strip().replace(" ", "_")
        if not (os.path.exists(directory)):
            print("There is not such an directory")
            deletefolder()
        else:
            os.rmdir(directory)
            print(f"Successfully deleted folder named {directory}")

    except ValueError as error:
        print(f"Someting bad happend with your code: {error}")
def createFile():
    fname = input("Enter a file name: ").strip().replace(" ", "_")
    if len(fname) > 20:
        print("You can only create a file with maximum of 10 entered symbols!")
        exit()
    fextension = input("Enter a file extension (supports only txt for now): ").strip()
    if not (fextension == "txt"):
        print("Sorry but it needs to be txt extension.")
        exit()
    # Creates an file
    try:
        file = open(f"{fname}.{fextension}", "x")
        print(f"Successfully created a new file named {fname} in this directory")
    except FileExistsError:
        print("Sorry but the file you are trying to create is already there!")
        exit()
    # Writes on a file
    text = input("Enter a text that will be written on the file: ")
    file_format = open(f"{fname}.{fextension}", "w")
    file_format.write(text)
    file_format.close()
    print(f"Succefully setted a text for {fname}.{fextension}: {text}")
def deleteFile():
    directory = input("Enter a file name that you want to be deleted: ").strip().replace(" ", "_")
    try:
        if not (os.path.exists(directory)):
            print("There is no found file to delete. Maybe you need first to create it!")
            deleteFile()
    except FileNotFoundError:
        print("The fail you want to access is unavailable")
        deleteFile()
    try:
        os.remove(directory)
        print("The file was deleted successfully")
    except Exception as error:
        print(f"There is some weird error. Have a look: {error}")