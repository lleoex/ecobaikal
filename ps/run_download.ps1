$yy = Get-Date -UFormat "%Y"
#$yy = Get-Date -UFormat "%H%M"
$mm = Get-Date -UFormat "%m"
$dd = Get-Date -UFormat "%d"

echo $yy-$mm-$dd

$py_dir = "C:\Users\gonchukov-lv\Documents\GitHub\ecobaikal"
& conda activate ecomag
& python $py_dir\run_download.py --date_today=$yy-$mm-$dd --source=Q

