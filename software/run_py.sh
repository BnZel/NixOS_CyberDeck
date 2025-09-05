MOUNT="./mnt/microsd"
UUID_DISK="35ca8de7-6df8-45bc-8af7-95fa93dcc2d3"
DATE=$(date "+%Y-%m-%d");
FILE="$MOUNT/$DATE.csv"

# creates a CSV file based on current date
# if csv exists, give all 777 permissions
# for python script to write to micro sdcard
# otherwise create the CSV within the mount directory
# and give 777 permissions
file_check () {
  if test -f $FILE; then
    echo "$FILE File exists!"
    sudo chmod 777 $FILE
    return 0
  else
    echo "Creating ${DATE}.csv"
    sudo touch $FILE
    sudo chmod 777 $FILE
    return 1
  fi
}

# proceed if sd mounted and file check
# otherwise list disk to confirm sd is inserted
# check/repair (fsck) by UUID as bootups change partiion order
# (re)mount
if mountpoint -q $MOUNT; then
    echo "$MOUNT is mounted!";
    ls -la "$MOUNT"
    file_check
else
    echo "$MOUNT is NOT mounted...";
    echo "Attempting to mount...";
    fdisk -l
    fsck UUID=$UUID_DISK
    sudo mount UUID=$UUID_DISK $MOUNT
    file_check
fi

# will use to pass as argument 1
# in the main.py to confirm successful mount
EXIT_STATUS=$?
echo "mountpoint returned $EXIT_STATUS"

# auto-formatter for ease of use in a text editor
# then pass filename as argument 2 to write data to
black main.py
python3 main.py $EXIT_STATUS $FILE
