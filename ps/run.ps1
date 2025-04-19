$OutputEncoding = [Console]::InputEncoding = [Console]::OutputEncoding =[System.Text.Encoding]::GetEncoding(1251)

$yy = Get-Date -UFormat "%Y"
#$yy = Get-Date -UFormat "%H%M"
$mm = Get-Date -UFormat "%m"
$dd = Get-Date -UFormat "%d"

echo $yy-$mm-$dd

$dt = Get-Date
$dt = $dt.AddDays(0).ToString("yyyy-MM-dd")

echo $dt
logfile = $dt + ".log"



$py_dir = "D:\ecobaikal\runpy\ecobaikal"
& conda activate ecomag
& python $py_dir\run_download.py --date_today=$dt --source=Q > $logfile 2>&1

& python $py_dir\run_download.py --date_today=$dt --source=GFS >> $logfile 2>&1

& python $py_dir\run_download.py --date_today=$dt --source=ERA >> $logfile 2>&1

& python $py_dir\run_ecomag.py --date_today=$dt > $logfile 2>&1

