#!/usr/bin/env bash
pushd `pwd`

cat <<EOF > hosts
[k8s_master]
EOF

grep "k8s-m" local_cluster/.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory | awk '{ split($2, host, "="); print host[2]}' >> hosts

cd local_cluster

scp -i .vagrant/machines/k8s-m/libvirt/private_key vagrant@192.168.50.10:/home/vagrant/.kube/config ~/.kube/config

popd