# Angenommen der jupyter folder hat folgenden Pfad:
# ~/lib/jupyter
# und OneDrive ist mit rclone (https://rclone.org/onedrive/) 
# unter ~/OneDrive gemountet
# (z.B. mit rclone --vfs-cache-mode writes mount "onedrive":  ~/OneDrive &)

cd ~/lib/jupyter
source ./env/bin/activate
jupyter lab --notebook-dir ~/OneDrive/WPFInformatik/jupyter
 
