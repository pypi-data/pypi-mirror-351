# -*- coding: utf-8 -*-
from crewai import LLM
import json
import os

class LLMVertex:
    def __init__(self):
        self.credentials = self._get_credentials()
        self.llm = LLM(
            model="gemini-2.0-flash",
            temperature=0.0,
            vertex_credentials=self.credentials,
        )
        
    def _get_credentials(self):
        file_path = os.path.join(os.path.dirname(__file__), "service_account.json")
        with open(file_path, "r") as file:
            vertex_credentials = json.load(file)
            return json.dumps(vertex_credentials)