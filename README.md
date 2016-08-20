# dom4-python-llamaserver-helper
Helper application for playing Dominions 4 games via Llamaserver. Currently very much in an alpha-ish state, and still needs to be run from the command line, with something like 'py llamaserver-helper.py [config file]'. 

Works with a GMail account. You need to add the email and password to a config file and set the account accessible by less secure apps (https://www.google.com/settings/security/lesssecureapps), so you may want to create a new GMail account for this. IMAP also needs to be enabled in the GMail settings ('Forwarding and POP/IMAP').

Current eventual plans include a fancy (and probably optional) GUI, better awareness of game state (such as game turn, or llamaserver telling you off for sending the wrong thing), and the option to save all old .trn files in a subfolder (when it's aware of game turn, so it can rename the files properly).
Please post any issues and suggestions you have to the project repo (https://github.com/Feldherren/dom4-python-llamaserver-helper).