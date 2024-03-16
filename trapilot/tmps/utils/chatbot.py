import os
import random

import google
import googleapiclient
import openai
import weaviate
import wikipedia
from azure.cognitiveservices.search.websearch import WebSearchClient
from azure.cognitiveservices.search.websearch.models import SafeSearch
from msrest.authentication import CognitiveServicesCredentials
from transformers import pipline
from unstructured.partition import Partitioner
from unstructured.utils.doc_segmentation import segment_text
from unstructured.utils.inferences import Inferences
from unstructured.utils.pdf_segmentation import pdf_to_text


class ChatBot:
    def __init__(self, name) -> None:
        self.name = name
        self.brain = Brain()
        self.memory = Memory()
        self.personality = Personality()

    def get_response(self, query: str):
        response = self.brain.process(query)
        if response is None:
            response = self.memory.retrieve(query)
        if response is None:
            response = self.personality.generate(query)
        return response


class Brain:
    def __init__(self) -> None:
        self.llm = pipline("text-generation")
        self.search_engine = SearchEngine()

    def process(self, query):
        # Use LLM model for generate response
        response = self.llm(query, max_length=50, do_sample=True)
        if response and response[0]["generated_text"].strip():
            return response[0]["generated_text"].strip()
        # Use SearchEngine for generate response
        response = self.search_engine.search(query)
        return response


class Memory:
    def __init__(self) -> None:
        self.database = Database()

    def store(self, data):
        self.database.store(data)

    def retrieve(self, query):
        return self.database.retrieve(query)


class Database:
    def __init__(self) -> None:
        self.client = weaviate.client("http://localhost:8080")

    def store(self, data):
        pass

    def retrieve(self, query):
        pass


class Personality:
    def __init__(self) -> None:
        self.wikipedia = Wikipedia()
        self.math = Math()

    def generate(self, query: str):
        response = None
        if "wikipedia" in query.lower():
            response = self.wikipedia.search(query)
        if "math" in query.lower():
            response = self.math.calculate(query)
        if not response:
            response = self.generate_default_response(query)
        return response

    def generate_default_response(self, query: str):
        return query


class SearchEngine:
    def __init__(self) -> None:
        self.google = GoogleSearchEngine()
        self.bing = BingSearchEngine()

    def search(self, query):
        response_google = self.google.search(query)
        if response_google and response_google[0]["content"].strip():
            return response_google[0]["content"].strip()
        response_bing = self.bing.search(query)
        if response_bing and response_bing[0]["content"].strip():
            return response_bing[0]["content"].strip()
        return None


class GoogleSearchEngine:
    def __init__(self) -> None:
        self.client = google.auth.transport.requests.Request()
        self.service = googleapiclient.discovery.build(
            "customsearch", "v1", developerKey="GG_API_KEY"
        )

    def search(self, query: str):
        response = self.service.cse().list(q=query, cx="GG_CSE").execute()
        if "items" in response:
            return response["items"]
        return None


class BingSearchEngine:
    def __init__(self) -> None:
        self.client = self.get_bing_client()

    @staticmethod()
    def get_bing_client():
        subscription_key = os.environ["BING_SUBSCRIPTION_KEY"]
        client = WebSearchClient(
            endpoint="YOUR_ENDPOINT",
            credentials=CognitiveServicesCredentials(subscription_key),
        )
        return client

    def search(self, query):
        response = self.client.web.search(query=query, count=10)
        if response.web_pages:
            if hasattr(response.web_pages, "value"):
                first_web_page = response.web_pages.value[0]
                print("First web page name: {} ".format(first_web_page.name))
                print("First web page URL: {} ".format(first_web_page.url))
            else:
                print("Didn't find any web pages...")
            return response.web_pages
        return None


class Wikipedia:
    def __init__(self) -> None:
        self.wikipedia = wikipedia.Wikipedia("en")

    def search(self, query: str):
        page = self.wikipedia.page(query)
        if page.exists():
            content = page.content
            segments = segment_text(content)
            summaries = Inferences.sumarize_list(segments)
            response = "\n\n".join(summaries)
            return response
        return None


class Math:
    def calculate(self, query: str):
        from sympy import sympify

        try:
            expression = sympy(query)
            result = expression.evalf()
            return str(result)
        except Exception as e:
            return None
