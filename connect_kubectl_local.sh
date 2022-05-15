#!/usr/bin/env bash
pushd `pwd`

cd local_cluster

scp -i .vagrant/machines/k8s-m/libvirt/private_key vagrant@192.168.50.10:/home/vagrant/.kube/config ~/.kube/config

popd