import subprocess
from .base import SystemCheck

def parseString(output):

    status_dict = {}
    for line in output.strip().splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            status_dict[key.strip()] = value.strip()
    
    return status_dict

class WindowsSystemCheck(SystemCheck):
    def check_disk_encryption(self):
        output = subprocess.getoutput("manage-bde -status C:")
        return "Protection On" in output

    def check_os_updates(self):
        ps_command = '''
        $Session = New-Object -ComObject Microsoft.Update.Session;
        $Searcher = $Session.CreateUpdateSearcher();
        $SearchResult = $Searcher.Search("IsInstalled=0 and Type='Software' and IsHidden=0 and IsMandatory=1");
        Write-Output $SearchResult.Updates.Count;
        '''
        try:
            completed = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                check=True
            )
            count = int(completed.stdout.strip())
            if count > 0:
                return True
            return False
        except Exception as e:
            print(f"Error checking OS updates: {e}")
            return None
        
    def check_antivirus_status(self):
        output = subprocess.getoutput("powershell Get-MpComputerStatus")
        parsed = parseString(output)
        return {
            "AntivirusEnabled": parsed.get("AntivirusEnabled"),
            "AMServiceEnabled": parsed.get("AMServiceEnabled")
        }

    def check_sleep_settings(self):
        output = subprocess.getoutput("powercfg /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE")
        parsed = parseString(output)
        return {
            "ac_time": int(parsed.get("Current AC Power Setting Index"), 16),
            "dc_time": int(parsed.get("Current DC Power Setting Index"), 16)
        }
