from sqlalchemy.orm import relation, backref
from ..models import metadata
from job import Job
from spacer import Spacer
from hit import Hit
from bad_job import BadJob

Spacer.job = relation(Job,backref=backref("spacers", cascade="all,delete"))
Hit.spacer = relation(Spacer,backref=backref("hits", cascade="all,delete"))
