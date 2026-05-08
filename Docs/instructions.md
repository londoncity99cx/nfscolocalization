# Instructions for contributors

First of all, thank you for getting involved in doing fan made translations for NFSCO. Together, we can make it possible for more fans to play NFSCO in their favorite language and connect even more people to the game who don’t speak English.

## Preparation

1. **Install** [DBGate (Community Edition)](https://github.com/dbgate/dbgate) (recommended) or [DB Browser for SQLite](https://sqlitebrowser.org/).
2. **Adjust** the following setting in DBGate (important): Page Size = 10000
3. **Install** [sqlite3](https://sqlite.org/download.html) and if you're on Windows, add it to the PATH environment variable. If you don't know how, watch [this](https://www.youtube.com/watch?v=L42Qmec-jyk).
4. **Install** [Labrune](https://github.com/nlgxzef/Labrune/releases). You can also use [Labrune for NFSCO](https://github.com/londoncity99cx/Labrune-for-NFSCO/releases), a fork for implementing special functions.

## How to translate

1. **Login** to your GitHub account. You'll get an invitation to be a collaborator so you can create a new branch for your language (e.g. DE).
2. **Fetch** your branch using Git or GitHub Desktop.
3. **Open** the language database you want to edit (e.g. \languages\de\nfsco_loc_de.db) with DBGate.
4. **Edit** the strings inside the tables frontend.bin, global.bin and ingame.bin (equivalent to the language files of the same name, but WAY easier to edit than directly in any hex editor).
5. **Export** your translated strings by double clicking locexport.exe in the folder, where your language database is stored. It creates three correctly formatted Labrune dump exports.
6. **Import** the files using [Labrune](https://github.com/nlgxzef/Labrune/releases) to the binary language files in the folder Modded Game Language Files.
7. **Test** the updated language files.
8. **Commit** your changes to the main branch by doing a pull request.

You can watch a short video (4min) of translating and exporting some strings [here](https://youtu.be/-_fJ-CY8E_c).

## Guidelines

The following guidelines should be considered when doing any translations:

1. Keep translations authentic and consistent with the vanilla game.
2. Reuse existing vanilla translations whenever possible.
3. Correct spelling mistakes without changing the wording.
4. Replace highly inaccurate translations with fitting ones.
5. Fix incorrect or swapped track names in reward cards/challenge descriptions.
6. Do not translate district names unless the vanilla game already does.
7. Use the original vanilla translations for track names.
8. Translate NFSCO-specific track names only when necessary.
9. Leave iconic/popular track names (e.g. Mach Spin, Palmont & County...) untranslated when appropriate.
10. Do not translate location names within track names.
11. Keep sayings/phrases natural and close in length to the original.
12. Preserve the original meaning and tone in NFSCO-specific strings.
13. **Keep UI text concise to fit limited space.**
14. **Preserve predefined line breaks marked with "^".**
15. Do not translate racer, car, or company names.
16. Review all translation changes thoroughly in-game.
				
