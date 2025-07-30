#!/bin/bash



# ================================================================================
#   LIST SERVICES  _---MAIN CODE
# --------------------------------------------------------------------------------
function list_services(){






check_ufw_port() {
  local port=$1
  ufw status | grep -vE '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | awk -v port="$port" '{gsub(/\/tcp|\/udp/, "", $1)} $1 == port {print $1, $2, $3, $4; exit}'
}


print_status() {
    local service=$1
    local port=$2
    local status=$(systemctl is-active "${service}.service")
    local color

  if [ "$status" = "active" ]; then
    color="\e[32m"
  elif [ "$status" = "inactive" ]; then
    color="\e[37m"
  else
    color="\e[31m"
  fi

  local ufw_status=$(check_ufw_port "$port")  #local ufw_status=""
  local ufw_color="\e[32m"
  if [[ "$ufw_status" == *"DENY"* ]]; then
      ufw_color="\e[31m"
  fi

  printf "  %-20s %b%-8s%b  Port   %+5s   %b\n"  "$service" "$color" "$status" "\e[0m"  "$port" "$ufw_color$ufw_status\e[0m"
}




function show_allowd_ports(){
    ufw status | grep -vE '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | awk '!/DENY/ {gsub(/\/tcp|\/udp/, "", $1); if ($1 ~ /^[0-9]+$/) print  $1 }' | sort -n | uniq |sed '/\s+/d' | awk '{print  $1 }'

}
function warning(){
    ufw status verbose | grep "Default: deny (incoming)" > /dev/null
    if [ "$?" != "0" ]; then
	echo "X... check default politics of ufw !!!!"
    fi
}







    echo "  sysd-service       status            port        UFW-opened"
    echo _______________________________________________________________

mapfile -t open_ports < <(show_allowd_ports)
    # 0 is when no port byt systemd yes * *****************************************************
    services=("ssh 22"
	      "ufw 0"
	      "mosquitto 1883"
	      "syncthing@${original_USER} 22000"
	      "grafana-server 3000"
	      "influxdb 8086"
	      "ntp 123"
	      "chrony 323"
	      "samba 445"
	      "docker 2375"
	      "elog 9000"
	      "nginx 80"
	      "ntfy 80"
	      "VadimUDP 8200"
	      "telegraf 0"
	     )
 for sp in "${services[@]}"; do
     #set -- $sp
     svc=${sp% *}
     prt=${sp#* }
     print_status "$svc" "$prt"
     #echo " A " $prt "${!open_ports[@]}"
     for i in "${!open_ports[@]}"; do
	 #echo $prt $i
	 if [[ "${open_ports[i]}" == *"$prt" ]]; then
	     #echo unset open_ports[i]
	     unset 'open_ports[i]'
	 fi
     done
 done

 ps -ef | grep telegraf | grep ${HOST}.conf > /dev/null
 # TELEGRAF MINE
 TLGF="inactive"
 if [ "$?" = "0" ]; then
     TLGF="\e[32m active \e[0m"
 fi

echo -e " TELEGRAF@${original_USER}         ${TLGF} "
echo _______________________________________________________________
# Capture output into array
#port_array=()
#while IFS= read -r line; do
#    port_array+=("$line")
#done < <(show_allowd_ports)
printf '%s %b\n' " Other open ports" "\e[33m: ${open_ports[@]}\e[0m"
warning
}


# ================================================================================
# ================================================================================
# ================================================================================
# ================================================================================
# ================================================================================

USER=`whoami`
if [ "$USER" != "root" ]; then
    echo X...  USE AS ROOT...
    echo X... else you will mess up at some moment
    exit 1
fi
original_USER=$(logname)

list_services
