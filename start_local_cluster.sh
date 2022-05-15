#!/usr/bin/env bash
pushd `pwd`

cd local_cluster

vagrant up --no-provision

vagrant provision

popd