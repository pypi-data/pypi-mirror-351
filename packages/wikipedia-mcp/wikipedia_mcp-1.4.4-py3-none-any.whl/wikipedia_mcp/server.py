"""
Wikipedia MCP server implementation.
"""

import logging
from typing import Dict, List, Optional, Any

from mcp.server.fastmcp import FastMCP
from wikipedia_mcp.wikipedia_client import WikipediaClient

logger = logging.getLogger(__name__)

def create_server() -> FastMCP:
    """Create and configure the Wikipedia MCP server."""
    server = FastMCP(
        name="Wikipedia",
        description="Retrieve information from Wikipedia to provide context to LLMs."
    )

    # Initialize Wikipedia client
    wikipedia_client = WikipediaClient()

    # Register tools
    @server.tool()
    def search_wikipedia(query: str, limit: int = 10) -> Dict[str, Any]:
        """Search Wikipedia for articles matching a query."""
        logger.info(f"Tool: Searching Wikipedia for: {query}")
        results = wikipedia_client.search(query, limit=limit)
        return {
            "query": query,
            "results": results
        }

    @server.tool()
    def get_article(title: str) -> Dict[str, Any]:
        """Get the full content of a Wikipedia article."""
        logger.info(f"Tool: Getting article: {title}")
        article = wikipedia_client.get_article(title)
        return article

    @server.tool()
    def get_summary(title: str) -> Dict[str, Any]:
        """Get a summary of a Wikipedia article."""
        logger.info(f"Tool: Getting summary for: {title}")
        summary = wikipedia_client.get_summary(title)
        return {
            "title": title,
            "summary": summary
        }

    @server.tool()
    def get_related_topics(title: str, limit: int = 10) -> Dict[str, Any]:
        """Get topics related to a Wikipedia article based on links and categories."""
        logger.info(f"Tool: Getting related topics for: {title}")
        related = wikipedia_client.get_related_topics(title, limit=limit)
        return {
            "title": title,
            "related_topics": related
        }

    @server.tool()
    def get_sections(title: str) -> Dict[str, Any]:
        """Get the sections of a Wikipedia article."""
        logger.info(f"Tool: Getting sections for: {title}")
        sections = wikipedia_client.get_sections(title)
        return {
            "title": title,
            "sections": sections
        }

    @server.tool()
    def get_links(title: str) -> Dict[str, Any]:
        """Get the links contained within a Wikipedia article."""
        logger.info(f"Tool: Getting links for: {title}")
        links = wikipedia_client.get_links(title)
        return {
            "title": title,
            "links": links
        }

    @server.resource("/search/{query}")
    def search(query: str) -> Dict[str, Any]:
        """Search Wikipedia for articles matching a query."""
        logger.info(f"Searching Wikipedia for: {query}")
        results = wikipedia_client.search(query, limit=10)
        return {
            "query": query,
            "results": results
        }

    @server.resource("/article/{title}")
    def article(title: str) -> Dict[str, Any]:
        """Get the full content of a Wikipedia article."""
        logger.info(f"Getting article: {title}")
        article = wikipedia_client.get_article(title)
        return article

    @server.resource("/summary/{title}")
    def summary(title: str) -> Dict[str, Any]:
        """Get a summary of a Wikipedia article."""
        logger.info(f"Getting summary for: {title}")
        summary = wikipedia_client.get_summary(title)
        return {
            "title": title,
            "summary": summary
        }

    @server.resource("/sections/{title}")
    def sections(title: str) -> Dict[str, Any]:
        """Get the sections of a Wikipedia article."""
        logger.info(f"Getting sections for: {title}")
        sections = wikipedia_client.get_sections(title)
        return {
            "title": title,
            "sections": sections
        }

    @server.resource("/links/{title}")
    def links(title: str) -> Dict[str, Any]:
        """Get the links in a Wikipedia article."""
        logger.info(f"Getting links for: {title}")
        links = wikipedia_client.get_links(title)
        return {
            "title": title,
            "links": links
        }

    return server 