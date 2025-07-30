# __init__.py
import os

from vectorshift.pipeline import Pipeline
from vectorshift.knowledge_base import KnowledgeBase

api_key = os.environ.get('VECTORSHIFT_API_KEY')
