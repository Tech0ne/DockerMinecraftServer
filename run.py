from rich import print
from rich.live import Live
from rich.align import Align
from rich.panel import Panel

from requests import get

from hashlib import md5

import datetime
import shutil
import getch
import json

import sys
import os

HOST = "https://mohistmc.com"
DIR  = "/servers/"

def error(data) -> int:
    print(Panel(data, title="/!\\", title_align="left", border_style="red"))
    return 1

def clear() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def footprint(filename: str, md5_hash: str) -> bool:
    if not os.path.isfile(filename):
        error(f"No such file or directory: {filename}")
        return False
    with open(filename, 'rb') as f:
        return md5(f.read()).hexdigest() == md5_hash

def wget(url: str, subdir: str, md5_hash: str) -> str:
    response = get(url, stream=True)
    total_length = response.headers.get("content-length")
    filename = response.headers.get("content-disposition")
    if filename is None or not " filename=" in filename:
        error("No filename sent by the server")
        return ""
    filename = os.path.join(subdir, filename.split(" filename=")[-1])
    p = Panel("", border_style="blue", title="[white]"+os.path.basename(filename), title_align="left")
    with open(filename, "wb+") as f:
        if total_length is None:
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            with Live(p, refresh_per_second=20):
                for data in response.iter_content(chunk_size=4096):
                    tsize, _ = os.get_terminal_size()
                    tsize -= 6
                    dl += len(data)
                    f.write(data)
                    done = int(tsize * dl / total_length)
                    p.renderable = Align(f"[{'=' * done}{' ' * (tsize - done)}]", "center")
    if not footprint(filename, md5_hash):
        error("File hash do not match expected !")
        os.remove(filename)
        return ""
    return filename

def ask(prompt: str, choices: list[str]) -> str:
    ok = False
    index = 0
    while not ok:
        clear()
        print(Panel(prompt, title="[?]", title_align="left", border_style="green"))
        term_size = os.get_terminal_size()
        total_size = term_size[0]
        total_length = term_size[1]
        total_length -= 5
        print("  ..." if max([0, index - (total_length // 2)]) > 0 else "")
        beggining = max([0, min([len(choices) - total_length + 1, index - (total_length // 2)])])
        end = min([len(choices), max([index, (total_length // 2)]) + (total_length // 2)])
        for i in range(beggining, end):
            choice = choices[i]
            if len(choice) + 6 > total_size:
                choice = choice[:total_size - 6] + '...'
            if i == index:
                print("> " + choice)
            else:
                print("  " + choice)
        print("  ..." if min([len(choices), index + (total_length // 2)]) < len(choices) else "")
        key = ord(getch.getch())
        if key == 27:
            getch.getch()
            key = ord(getch.getch())
        if key == 10:
            ok = True
        elif key == 65:
            index -= 1
            if index < 0:
                index = 0
        elif key == 66:
            index += 1
            if index >= len(choices):
                index = len(choices) - 1
        elif key == 113:
            sys.exit(error("User abort !"))
    return choices[index]

def serialize(name: str) -> str:
    authorised_chars = "abcdefghijklmnopqrstuvwxyz0123456789_-"
    out = ""
    valid = True
    for c in name.lower():
        out += c
        if not c in authorised_chars:
            valid = False
            break
    return (out, valid)

def is_hash(data: str) -> str:
    if len(data) != 32:
        return False
    for char in data:
        if not char in "abcdefghijklmnopqrstuvwxyz0123456789":
            return False
    return True

def run(server_name: str) -> bool:
    cwd = os.getcwd()
    os.chdir(os.path.join(DIR, server_name))
    if not os.path.isfile("server_infos.json"):
        error("No \"server_infos.json\" file found !")
        os.chdir(cwd)
        return False
    infos = json.load(open("server_infos.json", 'r'))
    if type(infos) != dict:
        error("Expect JSON dictionary in \"server_infos.json\" file.")
        os.chdir(cwd)
        return False
    if not ("java-version" in infos.keys() and "file-name" in infos.keys()):
        error("Required \"java-version\" and \"file-name\" keys not set in JSON.")
        os.chdir(cwd)
        return False
    if not os.path.isfile(infos.get("file-name")) or not infos.get("java-version").isnumeric():
        error("Server infos must be valid in the server_infos.json file !")
        os.chdir(cwd)
        return False
    os.system(f"/usr/lib/jvm/java-{infos.get('java-version')}-openjdk-amd64/bin/java -jar -Xmx1G {infos.get('file-name')}")
    os.chdir(cwd)
    return True

def run_server():
    servers = os.listdir(DIR)
    while ".server_files" in servers:
        servers.remove(".server_files")
    server = ask("Chose your server", servers)
    if not run(server):
        return error("Error while running the server !")
    return 0

def delete_server() -> 0:
    servers = os.listdir(DIR)
    while ".server_files" in servers:
        servers.remove(".server_files")
    if not len(servers):
        print(Panel("No servers to delete !\nStart by creating one !!!", border_style="blue"))
        return 0
    server = ask("Chose the server you want to delete.\nThis action can't be undone ! Press Ctrl+C if you want to abort.", servers)
    shutil.rmtree(os.path.join(DIR, server))
    print(Panel("Server deleted successfully", border_style="yellow"))
    return 0

def get_server_file(infos: dict) -> str:
    file_hash = infos.get("fileMd5")
    for file in os.listdir(os.path.join(DIR, ".server_files")):
        if footprint(os.path.join(DIR, ".server_files", file), file_hash):
            print(Panel("You already downloaded this file !", border_style="green"))
            return os.path.join(DIR, ".server_files", file)
    print(Panel("Retreiving server file", border_style="blue"))
    filename = wget(infos.get("url"), os.path.join(DIR, ".server_files"), infos.get("fileMd5"))
    if not filename:
        error("Error on downloading the server file")
        return ""
    return filename

def new_server():
    # Retreive versions infos
    print(Panel("Retreiving game versions", border_style="green"))
    path = HOST + "/api/v2/projects/mohist"
    data = get(path).json()
    if (data.get("versions") is None):
        return error("Could not retreive \"versions\" from the API")
    choices = data.get("versions")
    version = ask("Select game version", choices)

    java_version = ask("Select coresponding java version", ["8", "17", "21"])

    # Get server versions
    print(Panel("Retreiving server versions", border_style="green"))
    path = HOST + f"/api/v2/projects/mohist/{version}/builds"
    data = get(path).json()
    if (data.get("builds") is None):
        return error("Could not retreive \"builds\" from the API")

    versions = [f"{int(e.get('number'))} - Forge {e.get('forgeVersion')} - {datetime.datetime.fromtimestamp(e.get('createdAt') // 1000).strftime('%H:%M:%S %d/%m/%Y')}" for e in reversed(data.get("builds"))]
    version = ask("Chose server version", versions)
    version = int(version.split(' ')[0])
    version_infos = None
    for e in data.get("builds"):
        if e.get("number") == version:
            version_infos = e
    if version_infos is None:
        return error("Could not retreive asked infos")
    if not os.path.isdir(os.path.join(DIR, ".server_files")):
        os.mkdir(os.path.join(DIR, ".server_files"))
    server_file = get_server_file(version_infos)

    serialized = serialize(input("Please enter server name: "))
    while serialized[0] == "server_files" or not serialized[1] or os.path.isdir(os.path.join(DIR, serialized[0])):
        print(Panel("This name is either already taken, or invalid !", border_style="yellow"))
        serialized = serialize(input("Please enter server name: "))
    server_name = serialized[0]
    print(Panel(f"Building {server_name}", border_style="blue"))
    os.mkdir(os.path.join(DIR, server_name))
    shutil.copy(server_file, os.path.join(DIR, server_name))

    json.dump({"java-version": java_version, "file-name": os.path.basename(server_file)}, open(os.path.join(DIR, server_name, "server_infos.json"), 'w+'), indent=4)
    print(Panel(f"{server_name} built successfully !\nStarting..."))
    if not run(server_name):
        return error("Error while running the server !")
    return 0

def access_files():
    print(Panel("Starting ranger", border_style="green"))
    os.system(f"ranger {DIR}")

def main():
    print(Panel("""┏┓          ┳┳┓
┗┓┏┓┏┓┓┏┏┓┏┓┃┃┃┏┓┏┓┏┓┏┓┏┓┏┓
┗┛┗ ┛ ┗┛┗ ┛ ┛ ┗┗┻┛┗┗┻┗┫┗ ┛
                      ┛    """, border_style="purple"))
    print()
    choices = ["Create a server", "Run a server", "Access files", "Delete a server"]
    choice = ask("What do you want to do ?", choices=choices)
    if choice == choices[0]:
        return new_server()
    elif choice == choices[1]:
        return run_server()
    elif choice == choices[2]:
        return access_files()
    return delete_server()

if __name__ == "__main__":
    sys.exit(main())