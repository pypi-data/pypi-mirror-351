#! /usr/bin/env bash

function bluer_sbc_session() {
    local task=${1:-start}

    if [ "$task" == "start" ]; then
        local options=$2
        local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)
        local run_sudo=$(bluer_ai_option_int "$options" sudo 0)
        local do_upload=$(bluer_ai_option_int "$options" upload 1)

        bluer_ai_log "@sbc: session @ $abcli_object_name started ..."

        bluer_objects_mlflow_tags_set \
            $abcli_object_name \
            session,host=$abcli_hostname,$BLUER_SBC_SESSION_OBJECT_TAGS

        local sudo_prefix=""
        # https://stackoverflow.com/a/8633575/17619982
        [[ "$run_sudo" == 1 ]] &&
            sudo_prefix="sudo -E "

        bluer_ai_eval dryrun=$do_dryrun \
            $sudo_prefix \
            python3 -m bluer_sbc.session \
            start \
            "${@:3}"
        local status="$?"

        [[ "$do_upload" == 1 ]] &&
            bluer_objects_upload - $abcli_object_name

        bluer_ai_log "@sbc: session ended."

        return $status
    fi

    python3 -m bluer_sbc.session "$@"
}
