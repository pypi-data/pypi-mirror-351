#! /usr/bin/env nix-shell
#! nix-shell -i bash -p httpie jq

set -ex

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null 2>&1 && pwd)"


echo '{"modIds": [2382, 20338, 23350, 288981, 13592, 2398, 326516, 333072, 402180, 989270]}' \
    | http post https://api.curseforge.com/v1/mods \
        x-api-key:$CFCORE_API_KEY -b \
    | jq -r \
    > "$DIR"/curse-addon--all.json
http get 'https://api.curseforge.com/v1/mods/search?gameId=1&slug=molinari' \
        x-api-key:$CFCORE_API_KEY -b \
    | jq -r \
    > "$DIR"/curse-addon-slug-search.json
http get https://api.curseforge.com/v1/mods/20338/files \
        x-api-key:$CFCORE_API_KEY -b \
    | jq -r \
    > "$DIR"/curse-addon-files.json
http get https://api.curseforge.com/v1/mods/20338/files/4419396 \
        x-api-key:$CFCORE_API_KEY -b \
    | jq -r \
    > "$DIR"/curse-addon-file-4419396.json
http get https://api.curseforge.com/v1/mods/20338/files/5090686 \
        x-api-key:$CFCORE_API_KEY -b \
    | jq -r \
    > "$DIR"/curse-addon-file-5090686.json
http get https://api.curseforge.com/v1/mods/20338/files/3657564/changelog \
        x-api-key:$CFCORE_API_KEY -b \
    | jq -r \
    > "$DIR"/curse-addon-changelog.json


http get https://api.mmoui.com/v3/game/WOW/filelist.json -b \
    | jq -r '.[] | select(.UID == "13188") | [.]' \
    > "$DIR"/wowi-filelist.json
http get https://api.mmoui.com/v3/game/WOW/filedetails/13188.json -b \
    | jq -r \
    > "$DIR"/wowi-filedetails.json


http get 'https://api.tukui.org/v1/addon/tukui' -b \
    | jq -r \
    > "$DIR"/tukui-ui--tukui.json
http get 'https://api.tukui.org/v1/addon/elvui' -b \
    | jq -r \
    > "$DIR"/tukui-ui--elvui.json


http get 'https://api.github.com/repos/nebularg/PackagerTest' -b \
    | jq -r \
    > "$DIR"/github-repo-release-json.json
http get 'https://api.github.com/repos/nebularg/PackagerTest/releases?per_page=1' -b \
    | jq -r \
    > "$DIR"/github-release-release-json.json
http --follow get 'https://github.com/nebularg/PackagerTest/releases/download/v1.9.7/release.json' -b \
    | jq -r \
    > "$DIR"/github-release-release-json-release-json.json
http get 'https://api.github.com/repos/p3lim-wow/Molinari' -b \
    | jq -r \
    > "$DIR"/github-repo-molinari.json
http get 'https://api.github.com/repos/p3lim-wow/Molinari/releases?per_page=1' -b \
    | jq -r \
    > "$DIR"/github-release-molinari.json
http --follow get $(
    jq -r \
        '.[].assets[] | select(.name == "release.json") | .browser_download_url' \
        "$DIR"/github-release-molinari.json
) -b \
    | jq -r \
    > "$DIR"/github-release-molinari-release-json.json
http get 'https://api.github.com/repos/28/NoteworthyII' -b \
    | jq -r \
    > "$DIR"/github-repo-no-release-json.json
http get 'https://api.github.com/repos/28/NoteworthyII/releases?per_page=1' -b \
    | jq -r \
    > "$DIR"/github-release-no-release-json.json
http get 'https://api.github.com/repos/AdiAddons/AdiBags' -b \
    | jq -r \
    > "$DIR"/github-repo-no-releases.json
http get 'https://api.github.com/repos/AdiAddons/AdiButtonAuras/releases/tags/2.0.19' -b \
    | jq -r \
    > "$DIR"/github-release-no-assets.json


http get https://raw.githubusercontent.com/layday/instawow-data/data/base-catalogue-v7.compact.json -b \
    | jq -r \
    > "$DIR"/base-catalogue-v7.compact.json


echo '{
  "device_code": "3584d83530557fdd1f46af8289938c8ef79f9dc5",
  "user_code": "WDJB-MJHT",
  "verification_uri": "https://github.com/login/device",
  "expires_in": 900,
  "interval": 5
}' \
    | jq -r \
    > "$DIR"/github-oauth-login-device-code.json
echo '{
  "access_token": "gho_16C7e42F292c6912E7710c838347Ae178B4a",
  "token_type": "bearer",
  "scope": "repo,gist"
}' \
    | jq -r \
    > "$DIR"/github-oauth-login-access-token.json
