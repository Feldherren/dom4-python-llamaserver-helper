# dom4-python-llamaserver-helper
Helper application for playing Dominions 4 games via Llamaserver. Requires python 3.*. Currently very much in an alpha-ish state, and still needs to be run from the command line, with something like 'py llamaserver-helper.py [config file]'. 

Works with a GMail account (and has only been tested with GMail so far; let me know if it works/doesn't work with anything). You need to add the email and password to a config file and set the account accessible by less secure apps (https://www.google.com/settings/security/lesssecureapps), so you may want to create a new GMail account for this. IMAP also needs to be enabled in the GMail settings ('Forwarding and POP/IMAP').

Current eventual plans include a fancy (and probably optional) GUI, better awareness of game state (such as game turn, or llamaserver telling you off for sending the wrong thing), and the option to save all old .trn files in a subfolder (when it's aware of game turn, so it can rename the files properly). Also possibly a more-professionally-written readme at some point.
Please post any issues and suggestions you have to the project repo (https://github.com/Feldherren/dom4-python-llamaserver-helper).

# Quick-Start
Install the latest version of Python 3 (https://www.python.org/downloads/) if you don't have it.

Make a copy of config-template.ini and rename it something sensible; config.ini is good. Open it and enter your email address, password and Dom4 data directory path; the location Dom4 takes you to from 'open user data directory' in game tools.

Open command prompt (or equivalent) at location of llamaserver-helper.py for simplicity's sake.

Type this at the command prompt: py llamaserver-helper.py config.ini

# Changelog
2016/08/20: removed game name, era and nation command line arguments, replaced with the application prompting user for game name, era and nation when launched. Also, you can now customise nation aliases in the early_nations.txt, mid_nations.txt and late_nations.txt files; the format is [alias]:[file nation name], so if you want to call mid ermor 'jerks', you'd add a new line 'jerks:ermor' (sans apostrophes) to mid_nations.txt. The data file paths are defined in the config file, so you can keep multiple sets if desired (for mods adding or removing nations). Also, added how-to steps, the changelog and other useful stuff to the readme.