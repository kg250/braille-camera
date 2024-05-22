# Braille Camera Development 

## Raspberry Pi setup 
- Install Raspbian bookworm 
- git clone braille-camera repository
- Create and start python virtual environment
  ```
  mkdir ~/venvs
  python3 -m venv ~/venvs/braille-camera
  source  ~/venvs/braille-camera/bin/activate
  pip install -r requirements.txt
  ```


## Demo
1. Connect to at2024, Password: braille#
2. Go to: http://jimbo.local:5000/


## Development with VS Code
1. Install Remote-SSH Extension in VS Code
2. Connect to at2024
3. Open Terminal
4. Run ssh-keygen
5. Run `ssh-copy-id jimbo@jimbo.local` with password: jumbo
6. From VS Code, View/Command Palette “Add New SSH Host”.  
    1. `ssh jimbo@jimbo.local`
7. Open Folder. 
8. Source code is in ~/braille-camera/src
9. Restarting the server after making modifications
    1. Launch Terminal/New Terminal in VS Code
    2. sudo systemctl status braille-camera # check if service is running
    3. sudo systemctl restart braille-camera # restart the service
10. Shutdown Raspberry PI using `sudo shutdown -h now`

