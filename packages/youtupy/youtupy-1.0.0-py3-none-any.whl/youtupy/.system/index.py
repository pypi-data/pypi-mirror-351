from imports import *


class index:
    ####################################################################################// Load
    def __init__(self, app="", cwd="", args=[]):
        self.app, self.cwd, self.args = app, cwd, args
        # ...
        self.chars = cli.read(self.app + "/.system/sources/chars.yml").splitlines()
        self.sysdir = self.__loadSysDir("youtupy")
        cli.dev = "-dev" in args
        pass

    def __exit__(self):
        # ...
        pass

    ####################################################################################// Main
    def add(self, cmd=""):  # Add a new playlist or location
        cli.info("When registering a location for single downloads, skip the URL input")

        params = {
            "name": cli.input("Name", True),
            "url": cli.input("Playlist URL"),
            "dir": cli.input("Downloads DIR", True).replace("\\", "/"),
        }

        params["name"] += " (location)" if not params["url"].strip() else " (playlist)"
        name = params["name"].strip()

        file = self.sysdir + f"/{name}.json"
        if cli.isFile(file):
            return "\nConnection with this name already exists!"

        if not cli.write(file, json.dumps(params, indent=4)):
            return "\nCould not add new connection!"

        return "Connection added successfully"

    def download(self, mp3=""):  # (-mp3) - Download the full playlist or a single one
        mp3 = mp3 == "-mp3"
        selected = self.__select("playlist or location for downloading")
        if not selected:
            return "No connections were found!"

        params = self.__params(selected)
        if not cli.isFolder(params.dir):
            return "Invalid download location!"

        single = cli.input("Video URL", True) if not params.url else ""

        if single:
            return self.__single(single, params.dir, mp3)

        return self.__playlist(params.url, params.dir, mp3)

    def list(self, cmd=""):  # List existing playlists and locations
        files = os.listdir(self.sysdir)
        if not files:
            return "No connections were found!"
        for file in files:
            cli.hint(file.replace(".json", ""))
        pass

    def drop(self, cmd=""):  # Drop playlist or location
        selected = self.__select("connection to drop")
        if not selected:
            return "No connections were found!"

        name = selected.replace(".json", "")
        file = self.sysdir + f"/{name}.json"
        if not cli.isFile(file):
            return "Connection with this name does not exist!"

        os.remove(file)

        return "Connection dropped successfully"

    ####################################################################################// Helpers
    def __single(self, url: str, folder: str, mp3: bool):
        cli.trace("Downloading single video: " + url)
        files = self.__download(url, folder, False, mp3)

        if not files or not files[0]:
            return "Could not download the video!"
        if mp3:
            return "Audio file downloaded successfully"
        return "Video file downloaded successfully"

    def __playlist(self, url: str, folder: str, mp3: bool):
        cli.trace("Downloading playlist videos: " + url)
        files = self.__download(url, folder, True, mp3)

        if not files:
            return "Could not download the playlist!"
        if mp3:
            return "Playlist audio files downloaded successfully"
        return "Playlist video files downloaded successfully"

    def __params(self, connection=""):
        file = self.sysdir + f"/{connection}.json"
        if not cli.isFile(file):
            return None

        data = json.loads(cli.read(file))
        if not data:
            return None

        return SimpleNamespace(**data)

    def __select(self, hint=""):
        files = [x.replace(".json", "") for x in os.listdir(self.sysdir)]
        if not files:
            return False

        return cli.selection("Select " + hint, files, True)

    def __download(self, url="", folder=".", playlist=False, mp3=False):
        if not url or not os.path.exists(folder):
            cli.error("Invalid download params!")
            return []

        config = {}
        if mp3:
            config = {
                "format": "bestaudio/best",
                "ffmpeg_location": imageio_ffmpeg.get_ffmpeg_exe(),
                "outtmpl": f"{folder}/%(title)s.%(ext)s",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "320",
                    }
                ],
            }
        else:
            config = {
                "format": "bestvideo[vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[ext=mp4]",
                "ffmpeg_location": imageio_ffmpeg.get_ffmpeg_exe(),
                "merge_output_format": "mp4",
                "outtmpl": f"{folder}/%(title)s.%(ext)s",
                "noplaylist": not playlist,
                "quiet": False,
            }

        try:
            collect = []
            ext = ".mp3" if mp3 else ".mp4"
            with yt_dlp.YoutubeDL(config) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                if "entries" in info_dict:
                    for video in info_dict["entries"]:
                        files = [self.__sanitize(x) for x in os.listdir(folder)]
                        file = self.__sanitize(video.get("title") + ext)
                        if file not in files:
                            ydl.download([video["webpage_url"]])
                        collect.append(file)
                else:
                    files = [self.__sanitize(x) for x in os.listdir(folder)]
                    file = self.__sanitize(info_dict.get("title") + ext)
                    if file not in files:
                        ydl.download([info_dict["webpage_url"]])
                    collect.append(file)
            return collect
        except Exception as e:
            cli.error(f"Error: {e}")
        return []

    def __loadSysDir(self, name=""):
        if not name:
            cli.error("Invalid system folder name")
            sys.exit()

        sysdir = Path.home()
        if not os.path.exists(sysdir):
            cli.error("Invalid system folder")
            sys.exit()

        folder = f"{sysdir}/.{name}"
        os.makedirs(folder, exist_ok=True)

        return folder

    def __sanitize(self, text=""):
        for char in self.chars:
            text = text.replace(char, "_")

        return text
