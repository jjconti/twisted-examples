import re
from dproj.piel.models import RobotTipo

mascaras = {}

#for r in RobotTipo.objects.all():
#    mascaras[r.id] = re.compile(r.mascara)

#TER
re.compile(r"".join(["(?P<ea%d>\d{2}\.\d{1})" % d for d in [1,2,3,4]]) +  \
           r"".join(["(?P<re%d>\d{2}\.\d{1})" % d for d in [1,2,3,4]]) +  \
           r"".join(["(?P<sd%d>\d{1})" % d for d in [1,2,3,4]]) +  \
           r"".join(["(?P<ed%d>\d{1})" % d for d in [1,2]])) 
           
#MCA           
mca = re.compile(r"".join(["(?P<ea%d>\d{3})" % d for d in [1,2,3]]) +  \
           r"(?P<ea4>\d{2}\.\d{1})" + \
           r"".join(["(?P<re%d>\d{3})" % d for d in [1,2]]) +  \
           r"(?P<re3>\d{2})" + \
           r"(?P<re4>\d{2}\.\d{1})" + \
           r"".join(["(?P<sd%d>\d{1})" % d for d in [1,2,3,4]]) +  \
           r"".join(["(?P<ed%d>\d{1})" % d for d in [1,2]]))
           
