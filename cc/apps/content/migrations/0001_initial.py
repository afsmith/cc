# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'File'
        db.create_table(u'content_file', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('orig_filename', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('key', self.gf('django.db.models.fields.CharField')(default='na0hS8pzp5XXDqUk2Hkhkf', unique=True, max_length=22)),
            ('subkey_orig', self.gf('django.db.models.fields.CharField')(default='KaPGZ', max_length=5)),
            ('subkey_conv', self.gf('django.db.models.fields.CharField')(default='Wt9EO', max_length=5)),
            ('subkey_thumbnail', self.gf('django.db.models.fields.CharField')(default='wKt9s', max_length=5)),
            ('subkey_preview', self.gf('django.db.models.fields.CharField')(default='CWgEd', max_length=5)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('expires_on', self.gf('django.db.models.fields.DateField')(null=True)),
            ('delete_expired', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_downloadable', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=400, null=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=7)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CUser'], null=True)),
            ('pages_num', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('is_removed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'content', ['File'])

        # Adding M2M table for field groups on 'File'
        m2m_table_name = db.shorten_name(u'content_file_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('file', models.ForeignKey(orm[u'content.file'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['file_id', 'group_id'])

        # Adding model 'Course'
        db.create_table(u'content_course', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('objective', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('completion_msg', self.gf('django.db.models.fields.TextField')(default='Module finished', null=True, blank=True)),
            ('state_code', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('expires_on', self.gf('django.db.models.fields.DateField')(null=True)),
            ('published_on', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('deactivated_on', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=7)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CUser'], null=True)),
            ('allow_download', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_skipping', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sign_off_required', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'content', ['Course'])

        # Adding model 'Segment'
        db.create_table(u'content_segment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['content.File'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['content.Course'])),
            ('track', self.gf('django.db.models.fields.IntegerField')()),
            ('start', self.gf('django.db.models.fields.IntegerField')()),
            ('end', self.gf('django.db.models.fields.IntegerField')()),
            ('playback_mode', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'content', ['Segment'])

        # Adding model 'DownloadEvent'
        db.create_table(u'content_downloadevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('segment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['content.Segment'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CUser'])),
            ('download_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'content', ['DownloadEvent'])

        # Adding model 'CourseGroupCanBeAssignedTo'
        db.create_table(u'content_coursegroupcanbeassignedto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['content.Course'])),
        ))
        db.send_create_signal(u'content', ['CourseGroupCanBeAssignedTo'])

        # Adding model 'CourseGroup'
        db.create_table(u'content_coursegroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['content.Course'])),
            ('assigner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CUser'], null=True)),
            ('assigned_on', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'content', ['CourseGroup'])

        # Adding model 'CourseUser'
        db.create_table(u'content_courseuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CUser'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['content.Course'])),
            ('sign_off', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sign_off_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal(u'content', ['CourseUser'])


    def backwards(self, orm):
        # Deleting model 'File'
        db.delete_table(u'content_file')

        # Removing M2M table for field groups on 'File'
        db.delete_table(db.shorten_name(u'content_file_groups'))

        # Deleting model 'Course'
        db.delete_table(u'content_course')

        # Deleting model 'Segment'
        db.delete_table(u'content_segment')

        # Deleting model 'DownloadEvent'
        db.delete_table(u'content_downloadevent')

        # Deleting model 'CourseGroupCanBeAssignedTo'
        db.delete_table(u'content_coursegroupcanbeassignedto')

        # Deleting model 'CourseGroup'
        db.delete_table(u'content_coursegroup')

        # Deleting model 'CourseUser'
        db.delete_table(u'content_courseuser')


    models = {
        u'accounts.cuser': {
            'Meta': {'object_name': 'CUser'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'industry': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'content.course': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'Course'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_download': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_skipping': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'completion_msg': ('django.db.models.fields.TextField', [], {'default': "'Module finished'", 'null': 'True', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deactivated_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'expires_on': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'through': u"orm['content.CourseGroup']", 'symmetrical': 'False'}),
            'groups_can_be_assigned_to': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'course_can_assign'", 'symmetrical': 'False', 'through': u"orm['content.CourseGroupCanBeAssignedTo']", 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'objective': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CUser']", 'null': 'True'}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'sign_off_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'state_code': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'content.coursegroup': {
            'Meta': {'object_name': 'CourseGroup'},
            'assigned_on': ('django.db.models.fields.DateField', [], {}),
            'assigner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CUser']", 'null': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['content.Course']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'content.coursegroupcanbeassignedto': {
            'Meta': {'object_name': 'CourseGroupCanBeAssignedTo'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['content.Course']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'content.courseuser': {
            'Meta': {'object_name': 'CourseUser'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['content.Course']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sign_off': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sign_off_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CUser']"})
        },
        u'content.downloadevent': {
            'Meta': {'object_name': 'DownloadEvent'},
            'download_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'segment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['content.Segment']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CUser']"})
        },
        u'content.file': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'File'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'delete_expired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'expires_on': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_downloadable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'W7ZdV2xM44AqFPYxx1t0bG'", 'unique': 'True', 'max_length': '22'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True'}),
            'orig_filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CUser']", 'null': 'True'}),
            'pages_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'subkey_conv': ('django.db.models.fields.CharField', [], {'default': "'Ephwr'", 'max_length': '5'}),
            'subkey_orig': ('django.db.models.fields.CharField', [], {'default': "'bKKPT'", 'max_length': '5'}),
            'subkey_preview': ('django.db.models.fields.CharField', [], {'default': "'5CUon'", 'max_length': '5'}),
            'subkey_thumbnail': ('django.db.models.fields.CharField', [], {'default': "'d5lx0'", 'max_length': '5'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'content.segment': {
            'Meta': {'ordering': "('course', 'start', 'track')", 'object_name': 'Segment'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['content.Course']"}),
            'end': ('django.db.models.fields.IntegerField', [], {}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['content.File']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'playback_mode': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.IntegerField', [], {}),
            'track': ('django.db.models.fields.IntegerField', [], {})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['content']