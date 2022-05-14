#!/usr/bin/env bash
pushd `pwd`

cd local_cluster

vagrant up --no-parallel --no-provision

vagrant provision

popd