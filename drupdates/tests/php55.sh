# Total hack to get Travis to load PHP5.5+ on precise box
cat <<EOF | sudo apt-get upgrade -y --force-yes -qq
Y
EOF
