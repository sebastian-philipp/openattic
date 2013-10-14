# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Zpool'
        db.create_table('zfs_zpool', (
            ('volumepool_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['volumes.VolumePool'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ifconfig.Host'])),
        ))
        db.send_create_signal('zfs', ['Zpool'])

        # Adding model 'Zfs'
        db.create_table('zfs_zfs', (
            ('filesystemvolume_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['volumes.FileSystemVolume'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('zpool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['zfs.Zpool'])),
            ('parent_zfs', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['zfs.Zfs'], null=True, blank=True)),
        ))
        db.send_create_signal('zfs', ['Zfs'])


    def backwards(self, orm):
        # Deleting model 'Zpool'
        db.delete_table('zfs_zpool')

        # Deleting model 'Zfs'
        db.delete_table('zfs_zfs')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ifconfig.host': {
            'Meta': {'object_name': 'Host'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '63'})
        },
        'volumes.filesystemvolume': {
            'Meta': {'object_name': 'FileSystemVolume'},
            'capflags': ('django.db.models.fields.BigIntegerField', [], {}),
            'filesystem': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'fscritical': ('django.db.models.fields.IntegerField', [], {'default': '85'}),
            'fswarning': ('django.db.models.fields.IntegerField', [], {'default': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'blank': 'True'}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['volumes.VolumePool']", 'null': 'True', 'blank': 'True'}),
            'volume_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filesystemvolume_volume_type_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"})
        },
        'volumes.volumepool': {
            'Meta': {'object_name': 'VolumePool'},
            'capflags': ('django.db.models.fields.BigIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'volumepool_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'volumepool_volumepool_type_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"})
        },
        'zfs.zfs': {
            'Meta': {'object_name': 'Zfs', '_ormbases': ['volumes.FileSystemVolume']},
            'filesystemvolume_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['volumes.FileSystemVolume']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'parent_zfs': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['zfs.Zfs']", 'null': 'True', 'blank': 'True'}),
            'zpool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['zfs.Zpool']"})
        },
        'zfs.zpool': {
            'Meta': {'object_name': 'Zpool', '_ormbases': ['volumes.VolumePool']},
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ifconfig.Host']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'volumepool_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['volumes.VolumePool']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['zfs']