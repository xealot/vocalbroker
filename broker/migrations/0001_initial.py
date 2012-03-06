# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Caller'
        db.create_table('broker_caller', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('name_recording', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('name_transcription', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('name_transcription_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('broker', ['Caller'])

        # Adding model 'Call'
        db.create_table('broker_call', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('caller', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['broker.Caller'])),
            ('call_sid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75)),
            ('account_sid', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('call_from', self.gf('django.db.models.fields.CharField')(max_length=75, null=True, blank=True)),
            ('call_to', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('direction', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('forwarded', self.gf('django.db.models.fields.CharField')(max_length=75, null=True, blank=True)),
            ('caller_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('from_city', self.gf('django.db.models.fields.CharField')(max_length=75, null=True, blank=True)),
            ('from_state', self.gf('django.db.models.fields.CharField')(max_length=75, null=True, blank=True)),
            ('from_zip', self.gf('django.db.models.fields.CharField')(max_length=75, null=True, blank=True)),
            ('from_country', self.gf('django.db.models.fields.CharField')(max_length=75, null=True, blank=True)),
            ('to_city', self.gf('django.db.models.fields.CharField')(max_length=75, null=True, blank=True)),
            ('to_state', self.gf('django.db.models.fields.CharField')(max_length=75, null=True, blank=True)),
            ('to_zip', self.gf('django.db.models.fields.CharField')(max_length=75, null=True, blank=True)),
            ('to_country', self.gf('django.db.models.fields.CharField')(max_length=75, null=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('session_data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('broker', ['Call'])


    def backwards(self, orm):
        
        # Deleting model 'Caller'
        db.delete_table('broker_caller')

        # Deleting model 'Call'
        db.delete_table('broker_call')


    models = {
        'broker.call': {
            'Meta': {'object_name': 'Call'},
            'account_sid': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'call_from': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'call_sid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75'}),
            'call_to': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'caller': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['broker.Caller']"}),
            'caller_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'forwarded': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'from_city': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'from_country': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'from_state': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'from_zip': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session_data': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'to_city': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'to_country': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'to_state': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'to_zip': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'})
        },
        'broker.caller': {
            'Meta': {'object_name': 'Caller'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_recording': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_transcription': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name_transcription_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['broker']
