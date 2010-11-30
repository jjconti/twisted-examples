from mango.models import *
from django.db import models

__all__ = ['Group', 'DatasourceGroup', 'UserGroup']

class Group(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class DatasourceGroup(models.Model):
    datasource = models.ForeignKey(Datasources)
    group = models.ForeignKey(Group)

    def __unicode__(self):
        return unicode(self.datasource) + unicode(self.group)

class UserGroup(models.Model):
    user = models.ForeignKey(Users, related_name="usergroup")
    group = models.ForeignKey(Group)
    perfil = models.ForeignKey(Users, related_name="perfil")

    def __unicode__(self):
        return unicode(self.user) + unicode(self.group) + unicode(self.perfil)
'''
Hay 3 usuarios, con ids 0, 1 y 2 que constituyen
los perfiles de usuario.
'''
