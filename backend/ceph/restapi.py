# -*- coding: utf-8 -*-
# kate: space-indent on; indent-width 4; replace-tabs on;

"""
 *  Copyright (C) 2011-2016, it-novum GmbH <community@openattic.org>
 *
 *  openATTIC is free software; you can redistribute it and/or modify it
 *  under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; version 2.
 *
 *  This package is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
"""

from rest_framework import serializers, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.pagination import PaginationSerializer

from ceph.models import Cluster, CrushmapVersion, CephCluster, CephPool
from ceph.models import CephPoolTier

from nodb.restapi import NodbSerializer, NodbViewSet
from nodb.models import DictField
from rest import relations


class CrushmapVersionSerializer(serializers.ModelSerializer):
    crushmap = serializers.SerializerMethodField("get_crush_map")

    class Meta:
        model = CrushmapVersion

    def get_crush_map(self, obj):
        return obj.get_tree()


class ClusterSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializer for a Ceph Cluster. """
    url = serializers.HyperlinkedIdentityField(view_name="cephcluster-detail")
    crushmap = serializers.SerializerMethodField("get_crushmap")

    class Meta:
        model = Cluster
        fields = ('url', 'id', 'name', 'crushmap',
                  'auth_cluster_required', 'auth_client_required', 'auth_service_required')

    def get_crushmap(self, obj):
        return CrushmapVersionSerializer(obj.get_crushmap(), many=False, read_only=True).data


class ClusterViewSet(viewsets.ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
    filter_fields = ('name',)
    search_fields = ('name',)

    def update(self, request, *args, **kwargs):
        cluster = self.get_object()

        if "crushmap" in request.DATA:
            cluster.set_crushmap(request.DATA["crushmap"])

        cluster_ser = ClusterSerializer(cluster, many=False, context={"request": request})

        return Response(cluster_ser.data)


class CephClusterSerializer(NodbSerializer):

    class Meta:
        model = CephCluster


class CephClusterViewSet(NodbViewSet):

    def list(self, request):
        cluster = CephCluster.objects.all()
        cluster = self.paginate(cluster, request)
        serializer = PaginatedCephClusterSerializer(cluster, context={'request': request})

        return Response(serializer.data)

    def retrieve(self, request, fsid):
        cluster = CephCluster.objects.all().get(fsid=fsid)
        serializer = CephClusterSerializer(cluster, many=False, context={'request': request})

        return Response(serializer.data)


class CephPoolTierSerializer(NodbSerializer):

    class Meta:
        model = CephPoolTier


class CephPoolSerializer(NodbSerializer):

    hit_set_params = DictField
    tiers = CephPoolTierSerializer(many=True)

    class Meta:
        model = CephPool


class CephPoolViewSet(NodbViewSet):
    """Represents a Ceph pool.

    Due to the fact that we need a Ceph cluster fsid, we can't provide the ViewSet directly with
    a queryset. It needs a context which isn't available when this position is evaluated.
    """

    def retrieve(self, request, fsid, pool_id):
        cluster = CephCluster.objects.all().get(fsid=fsid)
        pools = CephPool.objects.all({'cluster': cluster})
        pool = pools.get(id=int(pool_id))
        serializer = CephPoolSerializer(pool, context={'request': request})

        return Response(serializer.data)

    def list(self, request, fsid):
        cluster = CephCluster.objects.all().get(fsid=fsid)
        pools = CephPool.objects.all({'cluster': cluster})
        pools = self.paginate(pools, request)
        serializer = PaginatedCephPoolSerializer(pools, context={'request': request})

        return Response(serializer.data)


class PaginatedCephPoolSerializer(PaginationSerializer):

    class Meta:
        object_serializer_class = CephPoolSerializer


class PaginatedCephClusterSerializer(PaginationSerializer):

    class Meta:
        object_serializer_class = CephClusterSerializer


RESTAPI_VIEWSETS = [
    ('cephclusters', ClusterViewSet, 'cephcluster'),  # Old implementation, used by the CRUSH map
]
