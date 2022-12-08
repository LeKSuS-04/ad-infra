#!/usr/bin/env bash

cd "$TEMP_DIR"/team || exit

open_time=$(echo "$NETWORK_CONFIG_JSON" | jq -r .open_time)
close_time=$(echo "$NETWORK_CONFIG_JSON" | jq -r .close_time)
timezone=$(echo "$NETWORK_CONFIG_JSON" | jq -r .timezone)

round_time=$(echo "$FORCAD_CONFIG_JSON" | jq -r .game.round_time)
flag_lifetime=$(echo "$FORCAD_CONFIG_JSON" | jq -r .game.flag_lifetime)

echo "$TEAMS_CONFIG_JSON"
teams_str=$(echo "$TEAMS_CONFIG_JSON" | jq -c -r '.teams[]')
mapfile -t teams_array <<< "$teams_str"
npc_exists=$(echo "$TEAMS_CONFIG_JSON" | jq -c -r '.add_npc')
if [[ "$npc_exists" == "true" ]]; then
    teams_array+=("🤖 NPC")
fi
vulnboxes_ip_range=[1-"${#teams_array[@]}"]

i=0
for team_name in "${teams_array[@]}"; do
    i=$(("$i" + 1))
    vulnbox_username=$(printf "team%03d" "$i")
    vulnbox_password=$(cat "$vulnbox_username"_password.txt)
    
    higher_quadrant=$(( 80 + "$i" / 256 ))
    lower_quadrant=$(( "$i" % 256 ))
    vulnbox_ip="10.$higher_quadrant.$lower_quadrant.2"

    escaped_team_name=$(echo "$team_name" | sed -r 's/[ ]{1}/_/g')
    team_token=$(cat "$escaped_team_name.txt")

    cat << END >> README.md 
# Welcome to my first Attack-Defense training!

### Your team config
* Your team: $team_name
* Jury token: $team_token
* Vulnbox ip: $vulnbox_ip
* Vulnbox creds: $vulnbox_username:$vulnbox_password
* OpenVPN clients are located inside vpn/ folder in this archive

### VPN network structure:
* Jury server (ForcAD): 10.10.10.10
* Vulnboxes: 10.80.$vulnboxes_ip_range.2
! Network opens at $open_time and closes at $close_time using $timezone timezone!

### Jury config:
* Round time: $round_time seconds
* Flag lifetime: $flag_lifetime rounds
* Public scoreboard available at $JURY_PUBLIC_IP
* Available flag submition protocols: forcad_tcp, ructf_http.

Example of submitting flags via http using curl:
\`\`\`
curl -X PUT --data '["AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="]' -H "X-Team-Token: deafbeef" http://10.10.10.10/flags
\`\`\`
Note that each request must not contain more than 100 flags

Attack data is available at /api/client/attack_data/
Example of fetching attack data:
\`\`\`
curl http://10.10.10.10/api/client/attack_data
\`\`\`

Good luck, have fun! 
From LeKSuS with <3
END

    zip "$vulnbox_username.zip" README.md
    rm README.md
    mv "$vulnbox_username.zip" "$RESULT_DIR"/"$vulnbox_username"_"$escaped_team_name".zip
done
