import logging, time
from typing import Dict, List
from datetime import datetime
from textwrap import dedent
from rich.console import Console
from rich.markdown import Markdown

from ...core.functionality.web_search import GoogleSearcher
from ...core.agent_architecture import Hive, Agent

console = Console()
logger = logging.getLogger("hive")

class DeepResearcher:
    def __init__(
            self, 
            model, 
            provider, 
            research_task: str, 
            max_depth: int = 2, 
            breadth: int = 3, 
            links_per_query: int = 10, 
            max_content_length: int = 1000,
        ):
            
        self.output = ""
        self.model = model
        self.provider = provider
        self.max_content_length = max_content_length
        self.google_searcher = GoogleSearcher()
        self.research_task = research_task
        self.all_queries = []
        self.max_depth = max_depth
        self.breadth = breadth
        self.total_queries = sum(breadth ** i * breadth for i in range(max_depth + 1))
        self.links_per_query = links_per_query
        self.total_links = self.links_per_query * self.total_queries
        self.processed_queries = 0
        self.processed_links = []
        self.done_queries = []
        self.retry_count = 3
        self.retry_delay = 2
        self.total_run = []
        self._init_agent()
    
    def __repr__(self):
        console.rule()
        console.print(f"[bold yellow]DeepResearcher Output:[/bold yellow]")
        md_results = Markdown(self.output)
        console.print(md_results)
        console.print("")  # for spacing
        console.rule()
        return  ""
    
    def run(self):
        logger.info(f"Starting research task: {self.research_task}")
        logger.info(f"Configuration: depth={self.max_depth}, breadth={self.breadth}")
        logger.info(f"Expected total queries: {self.total_queries}")
        logger.info(f"Expected total links: {self.total_links}")
        
        self.time_tracker.set_total_items(self.total_queries + 1)
        
        try:
            initial_queries = self._generate_queries()
            
            for query in initial_queries:
                self._process_queries_recursively(query=query, current_depth=0)
                
        except KeyboardInterrupt:
            logger.info("Research interrupted. Saving results...")
            
        except Exception as e:
            logger.exception(f"An error occurred during research: {e}. Saving results...")
        
        logger.info("Research completed. Saving results...")
        logger.info("Results saved successfully")
        logger.info("Finalizing results...")
        self._finalize_results()
        logger.info("Research task completed successfully!")
        
    def _init_agent(self):
        query_json_schema = """
        {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for."
                    },
                    "research_goal": {
                        "type": "string",
                        "description": "The goal of the research as detailed as possible."
                    }
                },
                "required": ["query", "research_goal"]
            }
        }
        """
        
        self.goals_agent = Agent(
            name="Goals Generator",
            instruction="You will be given a research task and you need to generate research goals based on the task. Make sure that the goals are detailed and relevant to the search. I will give you my previous research goals to avoid repetition. You need to generate new goals based on the research task provided. Return nothing but the goals. Make sure the goals are based on the details provided in the research task. Return nothing but the goals listed. Nothing else is needed. No python code is needed.",
            provider=self.provider,
            model_name=self.model,
            enable_history=False,
        )
            
        self.query_agent = Agent(
            name="Query Generator",
            instruction="You are a research query generator that creates targeted search queries based on research goals. Make sure that no two questions are similar or matches any of the previous questions. You will be given a research goal and you need to generate a query based on the research goal. The queries will be searched on Google. Make the research goal as detailed as possible to generate a query that is relevant to the research goal. Vague queries are discouraged. Ultra-specific queries are encouraged when previous queries are provided. I have provided all the queries done till now so you avoid repetition.",
            json_mode=True,
            json_schema=query_json_schema,
            provider=self.provider,
            model_name=self.model,
            enable_history=False
        )
        
        self.summarizing_agent = Agent(
            name="Summarizer",
            instruction="You will be given a query, research goal and search results. Your task is to make a summary of the search results based on the research goal and query. Make sure to return detailed and relevant information. More detailed and longer responses are preferred. Use only the information provided in the prompt to generate the summary. Information packed summaries are encouraged.",
            provider=self.provider,
            model_name=self.model,
            enable_history=False,
        )
        
        self.final_agent = Agent(
            name="Final Summarizer",
            instruction="Given a task, queries and search results, generate a very detailed report based solely on the queries and search results. The report should be detailed and relevant to the research task. Make sure to provide detailed information based on the queries and search results. The report should be detailed and relevant to the research task. Use only the information provided in the prompt to generate the report.",
            provider="google",
            model_name="gemini-2.0-flash-thinking-exp-01-21",
            max_output_length=60_000,
            max_context=120_000,
            enable_history=False,
        )
            
    def _retry_operation(self, operation, *args, **kwargs):
        """Generic retry mechanism for operations"""
        last_exception = None
        for attempt in range(self.retry_count):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"Operation failed (attempt {attempt + 1}/{self.retry_count}): {str(e)}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
        raise last_exception
    
    def _finalize_results(self):
        stats = self.time_tracker.get_stats()
        
        estimated_time = stats["estimated_remaining_time"]
        progress = 100 * (stats["completed_items"] / stats["total_items"])
        current_task = f"Finalizing results..."

        final_prompt = dedent(f"""
        Given the research task:
        ```
        {self.research_task}
        ```
        
        And the queries and search results from multiple sources:
        ```
        {self.total_run}
        ```
        
        Generate a very detailed report based solely on the queries and search results. The report should be detailed and relevant to the research task.
        Make sure to provide detailed information based on the queries and search results.
        The report should be detailed and relevant to the research task.
        Atleast 10 pages of detailed information is expected.
        
        """).strip()
        
        output = Hive(self.final_agent).run(final_prompt).assistant_message
        self.output = output
        logger.info("Final report generated successfully")   
    
    def _generate_queries(self, previous_query={}, num_results=None):
        num_results = num_results or self.breadth
        
        goals_prompt = dedent(f"""
        Given the research task:
        ```
        {self.research_task}
        ```
        
        Generate a research goal based on the research task. Make sure that the goal is detailed and relevant to the search. I will provide you with my previous research goals to avoid repetition. You need to generate new goals based on the research task provided.
        """).strip()
        
        query_prompt = dedent(f"""
        Given the research goal: 
        ```
        {self.research_task}
        ```
        
        Generate a query to search for relevant information and the research goal behind the query.
        Each query must be generated based on what you think the research goal is. The queries will be searched on Google.
        
        Number of queries to generate: 
        ```
        {num_results}
        ```
        
        """).strip()
                        
        if previous_query:
            prompt = dedent(f"""
                            
            Previous query:
            ```
            {previous_query}
            ```
            Now generate the next queries as needed with new research goals to explore more about the research task. Previous query is provided to help you generate new queries.
            
            """).strip()
            
            query_prompt += prompt
            goals_prompt += prompt
            
        if self.done_queries:
            prompt = dedent(f"""
                            
            All queries done till now:
            ```
            {"\n".join(" - " + q for q in self.done_queries)}
            ```
            
            """).strip()
            
            query_prompt += prompt
            goals_prompt += prompt
        
        goals = Hive(self.goals_agent).run(goals_prompt).assistant_message
        
        query_prompt += dedent(f"""
                               
        Research goals generated:
        ```
        {goals}
        ```
                       
        """).strip()
        
        logger.info(f"Generating {num_results} queries...")
        logger.info(f"Prompt: {query_prompt}")
        
        json = Hive(self.query_agent).run(query_prompt)
        if not isinstance(json, list):
            logger.info(f"is json? {self.query_agent.json_mode}")
        if len(json) > num_results:
            json = json[:num_results]
        logger.info(f"Queries generated: {json}")
        return json
    
    def _summarize_results(self, query, search_results):
        summary_prompt = dedent(f"""
        Given the research goal:
        ```
        {query["research_goal"]}
        ```
        And the query:
        ```
        {query["query"]}
        ```
        
        And the search results from multiple sources:
        ```
        {search_results}
        ```
        
        Summarize the search results based on the research goal and query. 
        Make sure to provide detailed and relevant information, considering all the different sources.
        """).strip()
        
        return Hive(self.summarizing_agent).run(summary_prompt).assistant_message
    
    def _combine_search_results(self, search_results: List[Dict], query: str) -> str:
        """
        Combine multiple search results into a single text with clear separation.
        """
        combined_text = ""
        for i, result in enumerate(search_results, 1):
            combined_text += f"\nSource {i}:\n"
            combined_text += f"URL: {result.get('url', 'N/A')}\n"
            combined_text += f"Content: {result.get('content', '').strip()[:self.max_content_length]}...\n"
            combined_text += "-" * 50
            self.processed_links.append(result.get('url', 'N/A'))
        return combined_text

    def _update_progress(self):
        self.processed_queries += 1
        progress = (self.processed_queries / self.total_queries) * 100
        logger.info(f"Progress: {progress:.2f}% ({self.processed_queries}/{self.total_queries} queries processed)")

    def _process_single_query(self, query: Dict, current_depth: int) -> Dict:
        """
        Process single query with retries
        """
        def _operation():
            query_id = f"q_{current_depth}_{datetime.now().strftime('%H%M%S%f')}"
            logger.info(f"Processing query: {query['query']} (Depth: {current_depth}, ID: {query_id})")
            
            self.google_searcher.banned_links = self.processed_links
            search_results = self.google_searcher.search(query["query"], num_results=self.links_per_query)
            
            if not search_results:
                logger.warning(f"No results found for query: {query['query']}")
                self.total_run.append({
                    "id": query_id,
                    "query": query["query"],
                    "research_goal": query["research_goal"],
                    "summary": "No Summary"
                })
                return {
                    "id": query_id,
                    "query": query["query"],
                    "research_goal": query["research_goal"],
                    "summary": "No Summary"
                }
            
            combined_search_results = self._combine_search_results(search_results, query["query"])
            self.done_queries.append(query["query"])
            summary = self._summarize_results(query, combined_search_results)
            
            self.total_run.append({
                "id": query_id,
                "query": query["query"],
                "research_goal": query["research_goal"],
                "summary": summary
            })
            
            return {
                "id": query_id,
                "query": query["query"],
                "research_goal": query["research_goal"],
                "summary": summary
            }
        
        return self._retry_operation(_operation)

    def _process_queries_recursively(self, query: Dict, current_depth: int) -> Dict:
        processed_query = self._process_single_query(query, current_depth)        
         
        if current_depth < self.max_depth:
            logger.info(f"Generating child queries for: {processed_query['id']}")
            child_queries = self._generate_queries(
                previous_query=processed_query,
                num_results=self.breadth
            )
            
            for child_query in child_queries:
                self._process_queries_recursively(
                    child_query,
                    current_depth + 1
                )