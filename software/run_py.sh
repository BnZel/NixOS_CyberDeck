MOUNT="./mnt/microsd"
SD_LOC="/dev/mmcblk1p1"
UUID_DISK="0403-0201"
DATE=$(date "+%Y-%m-%d");
GPS_CSV_FILE="$MOUNT/gps_$DATE.csv"
BARO_CSV_FILE="$MOUNT/baro_$DATE.csv"
CPU_CSV_FILE="$MOUNT/cpu_$DATE.csv"

# creates a CSV file based on current date
# first checks if $MOUNT directory exists
# creates it if it doesn't
# if csv exists, give all 777 permissions
# for python script to open and write
# otherwise create the CSV within the mount directory
# and give 777 permissions
file_check () {
  if test -d $MOUNT; then
    echo "$MOUNT exists!"
  else
    echo "Creating $MOUNT...."
    echo "YOURPASSWORD" | sudo -S mkdir $MOUNT
    echo "YOURPASSWORD" | sudo -S chmod 777 $MOUNT
  fi

  if test -f $1; then
    echo "$1 File exists!"
    echo "YOURPASSWORD" | sudo -S chmod 777 $1
    return 0
  else
    echo "Creating ${1}"
    echo "YOURPASSWORD" | sudo -S touch $1
    echo "YOURPASSWORD" | sudo -S chmod 777 $1
    return 1
  fi
}

# NOTE: ON HOLD.....
#       due to microsd mount errors
#	causing system wide crashes

# proceed if sd mounted and file check
# otherwise list disk to confirm sd is inserted
# check/repair (fsck) by UUID as bootups change partiion order
# (re)mount
mount_check () {
  if mountpoint -q $MOUNT; then
      echo "$MOUNT is mounted!";
      ls -la "$MOUNT"
      file_check
      echo "mountpoint returned 0";
      return 0
  else
      echo "$MOUNT is NOT mounted...";
      echo "Attempting to mount...";
      file_check
      echo "mountpoint returned 1";
      return 1
  fi
}

# auto-formatter for ease of use in a text editor
# then pass filenames as arguments to write data
file_check $GPS_CSV_FILE
file_check $BARO_CSV_FILE
file_check $CPU_CSV_FILE
black main.py
python3 main.py $GPS_CSV_FILE $BARO_CSV_FILE $CPU_CSV_FILE
