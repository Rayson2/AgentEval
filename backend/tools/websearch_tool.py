import os
import re
import time
from datetime import datetime
from crewai.tools import tool
from crewai_tools import SerperDevTool
from core.settings import (
	MAX_SEARCH_CALLS,
	SERPER_COUNTRY,
	SERPER_LOCALE,
	SERPER_RESULTS,
)


def requires_web_search(question: str) -> tuple[bool, str]:
	"""Determine whether a query requires current or external information."""

	query = re.sub(r"\s+", " ", question.lower().strip())
	current_year = datetime.now().year

	latest_keywords = [
		"latest", "current", "currently", "recent", "recently", "today",
		"todays", "today's", "yesterday", "tomorrow", "this week",
		"this month", "this year", "upcoming", "breaking", "newly released",
		"new release", "real-time", "live", "as of", "updated", "update",
		"now", "trending", "latest developments", "latest news",
	]

	date_patterns = [
		r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
		r"\b\d{4}-\d{2}-\d{2}\b",
		r"\b(january|february|march|april|may|june|july|august|"
		r"september|october|november|december)\s+\d{1,2},?\s+\d{4}\b",
		r"\b(january|february|march|april|may|june|july|august|"
		r"september|october|november|december)\s+\d{4}\b",
		r"\b(?:19|20)\d{2}\b",
	]

	external_keywords = [
		"weather", "forecast", "news", "election results",
		"government notification", "official announcement", "release date",
		"version released", "current version", "latest version",
		"current price", "market price", "stock price", "availability",
		"available in india", "is it available", "is it supported",
		"official documentation", "latest documentation", "current regulations",
		"current policy", "recent statistics", "current statistics",
		"latest research papers", "published papers", "recent publications",
	]

	for keyword in latest_keywords:
		if re.search(r"\b" + re.escape(keyword) + r"\b", query):
			return True, f"Time-sensitive query: {keyword}"

	for pattern in date_patterns:
		if re.search(pattern, query):
			return True, "Date-specific query"

	for keyword in external_keywords:
		if keyword in query:
			return True, f"External information required: {keyword}"

	if str(current_year) in query:
		return True, f"Query references current year: {current_year}"

	return False, "Existing knowledge may be sufficient"


class WebSearchSession:
	"""Manage bounded web searches for one research task."""

	max_search_calls = MAX_SEARCH_CALLS

	def __init__(self) -> None:
		if not os.getenv("SERPER_API_KEY"):
			raise RuntimeError(
				"SERPER_API_KEY is missing. Check your backend .env file."
			)

		self.search_count = 0
		self.search_time = 0.0
		self.serper = SerperDevTool(
			n_results=SERPER_RESULTS,
			country=SERPER_COUNTRY,
			locale=SERPER_LOCALE,
		)

		@tool("Bounded Serper Web Search")
		def bounded_web_search(search_query: str) -> str:
			"""Search for current or externally verifiable information."""

			return self.execute_search(search_query)

		self.tool = bounded_web_search

	def search(self, search_query: str) -> str:
		"""Search the web through the session's bounded Serper client."""
		return self.execute_search(search_query)

	def execute_search(self, search_query: str) -> str:
		if self.search_count >= self.max_search_calls:
			return "Search limit reached. Use previously retrieved search results."

		self.search_count += 1
		search_start = time.perf_counter()

		try:
			print(
				f"\n[WEB SEARCH {self.search_count}/{self.max_search_calls}] "
				f"{search_query}",
				flush=True,
			)
			return str(self.serper.run(search_query=search_query))
		except Exception as error:
			print(f"Search error: {error}", flush=True)
			return f"Web search failed: {error}"
		finally:
			self.search_time += time.perf_counter() - search_start

