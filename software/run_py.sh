MOUNT="./mnt/microsd"
SD_LOC="/dev/mmcblk1p1"
UUID_DISK="0403-0201"
DATE=$(date "+%Y-%m-%d");
CSV_FILE="$MOUNT/$DATE.csv"

# creates a CSV file based on current date
# if csv exists, give all 777 permissions
# for python script to write to micro sdcard
# otherwise create the CSV within the mount directory
# and give 777 permissions
file_check () {
  if test -f $CSV_FILE; then
    echo "$CSV_FILE File exists!"
    echo "1875" | sudo -S chmod 777 $CSV_FILE
    return 0
  else
    echo "Creating ${DATE}.csv"
    echo "1875" | sudo -S touch $CSV_FILE
    echo "1875" | sudo -S chmod 777 $CSV_FILE
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
 #    fdisk -l
 #    e2fsck -pfv UUID=$UUID_DISK
 #    echo "1875" | sudo -S dosfsck -t $SD_LOC
 #    echo "1875" | sudo -S mount UUID=$UUID_DISK $MOUNT

      file_check
      echo "mountpoint returned 1";
      return 1
  fi
}



# will use to pass as argument 1
# in the main.py to confirm successful mount
EXIT_STATUS=$?

# auto-formatter for ease of use in a text editor
# then pass filename as argument 2 to write data to
file_check
black main.py
python3 main.py $CSV_FILE
