#! /usr/bin/env bash

# internal function to bluer_ai_seed.
# seed is NOT local
function bluer_ai_seed_headless_rpi() {
    bluer_sbc_seed "$@"
}
function bluer_ai_seed_jetson() {
    bluer_sbc_seed "$@"
}
function bluer_ai_seed_rpi() {
    bluer_sbc_seed "$@"
}

function bluer_sbc_seed() {
    local target=$1

    bluer_ai_seed add_kaggle

    bluer_ai_seed add_ssh_key

    seed="${seed}ssh-keyscan github.com | sudo tee -a ~/.ssh/known_hosts$delim_section"

    # https://serverfault.com/a/1093530
    # https://packages.ubuntu.com/bionic/all/ca-certificates/download
    local certificate_name="ca-certificates_20211016ubuntu0.18.04.1_all"
    seed="${seed}wget --no-check-certificate http://security.ubuntu.com/ubuntu/pool/main/c/ca-certificates/$certificate_name.deb$delim"
    seed="${seed}sudo dpkg -i $certificate_name.deb$delim_section"
    seed="${seed}sudo apt-get update --allow-releaseinfo-change$delim"
    seed="${seed}sudo apt-get install -y ca-certificates libgnutls30$delim"

    seed="${seed}sudo apt-get --yes --force-yes install git$delim_section"

    bluer_ai_seed add_repo

    [[ "$target" == "headless_rpi" ]] &&
        seed="${seed}touch ~/storage/temp/ignore/headless$delim_section"

    bluer_ai_seed add_bluer_ai_env

    seed="${seed}pip install --upgrade pip --no-input$delim"
    seed="${seed}pip3 install -e .$delim_section"

    seed="${seed}source ./bluer_ai/.abcli/bluer_ai.sh$delim_section"

    seed="${seed}source ~/.bashrc$delim_section"

    if [[ ! -z "$env_name" ]]; then
        seed="${seed}bluer_ai_env dot copy $env_name$delim"
        seed="${seed}bluer_ai init$delim_section"
    fi
}
