$yy = Get-Date -UFormat "%Y"
#$yy = Get-Date -UFormat "%H%M"
$mm = Get-Date -UFormat "%m"
$dd = Get-Date -UFormat "%d"

$dt = Get-Date
$dt = $dt.AddDays(0).ToString("yyyy-MM-dd")

echo $dt

$py_dir = "C:\Users\gonchukov-lv\Documents\GitHub\ecobaikal"

& conda activate ecomag

& python $py_dir\run_download.py --date_today=$dt --source=Q
& python $py_dir\run_download.py --date_today=$dt --source=ERA
& python $py_dir\run_download.py --date_today=$dt --source=GFS
