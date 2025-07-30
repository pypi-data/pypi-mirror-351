"""
SolentraAgent - Core agent class for scientific research and experimentation
"""

import os
import json
import logging
import openai
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from .tools import AgentTools
from .social import SocialMediaTools

class SolentraAgent:
    """
    A powerful AI agent for scientific research and experimentation.
    
    This class provides a comprehensive interface for creating and managing
    science-themed AI agents with advanced research capabilities.
    """
    
    # Mapping of user-friendly model names to actual OpenAI model names
    MODEL_NAME_MAPPING = {
        "solentra-70b": "gpt-4",
        "solentra-3b-small": "gpt-4o-mini",
    }
    
    # Predefined agent personas
    PREDEFINED_PERSONAS = {
        "neuroscientist": "An expert in neuroscience, specializing in the study of the brain and nervous system.",
        "physicist": "An expert in physics, capable of explaining complex physical phenomena.",
        "biologist": "An expert in biology, with a focus on living organisms and ecosystems.",
    }

    def __init__(
        self,
        agent_name: str = "Default Scientist",
        model_name: str = "solentra-70b",
        tools_enabled: bool = True,
        interactive: bool = True,
        streaming_on: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 150,
        use_context: bool = True,
        persona: Optional[str] = None,
        logging_enabled: bool = False,
        log_file="solentra.log",
        twitter_config=None
    ):
        """
        Initialize a new SolentraAgent instance.
        
        Args:
            agent_name: Name/role of the AI agent
            model_name: AI model to use
            tools_enabled: Enable scientific tools
            interactive: Enable interactive mode
            streaming_on: Enable response streaming
            temperature: Response randomness (0-1)
            max_tokens: Maximum response length
            use_context: Enable conversation memory
            persona: Predefined role (physicist/biologist)
            logging_enabled: Enable activity logging
            log_file: Path to the log file
            twitter_config: Twitter API credentials for social media integration
        """
        if model_name not in self.MODEL_NAME_MAPPING:
            raise ValueError(f"Invalid model_name '{model_name}'. Choose from: {list(self.MODEL_NAME_MAPPING.keys())}")
        
        self.agent_name = agent_name
        self.model_name = self.MODEL_NAME_MAPPING[model_name]
        self.tools_enabled = tools_enabled
        self.interactive = interactive
        self.streaming_on = streaming_on
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.use_context = use_context
        self.logging_enabled = logging_enabled
        self.log_file = log_file if logging_enabled else None
        self.memory = {}
        
        # Set predefined persona
        if persona in self.PREDEFINED_PERSONAS:
            self.agent_name = persona.capitalize()
            self.persona_description = self.PREDEFINED_PERSONAS[persona]
        else:
            self.persona_description = None
        
        self.context = [] if use_context else None
        self.tools = AgentTools() if tools_enabled else None
        self.social = SocialMediaTools(twitter_config) if twitter_config else None
        self.current_task = None
        self.experiment_history = []

        # Initialize logging if enabled
        if logging_enabled:
            self._setup_logging()
        
        # Load persona if specified
        if persona:
            self._load_persona(persona)

    def _setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger("SolentraAgent")
        
    def _load_persona(self, persona: str):
        """Load predefined persona configuration."""
        persona_configs = {
            "physicist": {
                "background": "Expert in quantum mechanics and particle physics",
                "specialties": ["quantum computing", "quantum biology", "quantum chemistry"],
                "communication_style": "Precise and mathematical"
            },
            "biologist": {
                "background": "Expert in molecular biology and genetics",
                "specialties": ["protein folding", "enzyme kinetics", "genetic engineering"],
                "communication_style": "Detailed and systematic"
            },
            "chemist": {
                "background": "Expert in organic and physical chemistry",
                "specialties": ["reaction mechanisms", "catalysis", "molecular dynamics"],
                "communication_style": "Analytical and methodical"
            }
        }
        
        if persona in persona_configs:
            self.persona_config = persona_configs[persona]
        else:
            raise ValueError(f"Unknown persona: {persona}")
            
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response to the given prompt.
        
        Args:
            prompt: Input prompt for the agent
            
        Returns:
            Generated response
        """
        if self.logging_enabled:
            self.logger.info(f"Generating response for prompt: {prompt}")
            
        # Add context if enabled
        if self.use_context:
            full_prompt = self._build_contextual_prompt(prompt)
        else:
            full_prompt = prompt
            
        # Generate response (placeholder)
        response = "This is a placeholder response."
        
        if self.logging_enabled:
            self.logger.info(f"Generated response: {response}")
            
        return response
        
    def _build_contextual_prompt(self, prompt: str) -> str:
        """Build a prompt with context from previous interactions."""
        context_str = "\n".join(self.context)
        return f"{context_str}\n\nCurrent prompt: {prompt}"
        
    def create_experiment(
        self,
        steps: List[str],
        materials: List[str],
        duration: str,
        conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create an experiment protocol.
        
        Args:
            steps: List of experimental steps
            materials: List of required materials
            duration: Estimated duration
            conditions: Experimental conditions
            
        Returns:
            Protocol dictionary
        """
        protocol = {
            "protocol_id": f"EXP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "steps": steps,
            "materials": materials,
            "estimated_duration": duration,
            "conditions": conditions,
            "created_at": datetime.now().isoformat()
        }
        
        if self.logging_enabled:
            self.logger.info(f"Created experiment protocol: {protocol['protocol_id']}")
            
        return protocol
        
    def run_experiment(
        self,
        protocol: Dict[str, Any],
        variables: Dict[str, Any],
        iterations: int = 1
    ) -> Dict[str, Any]:
        """
        Run an experiment using the given protocol.
        
        Args:
            protocol: Experiment protocol
            variables: Experimental variables
            iterations: Number of iterations
            
        Returns:
            Experiment results
        """
        if self.logging_enabled:
            self.logger.info(f"Running experiment: {protocol['protocol_id']}")
            
        # Run experiment (placeholder)
        results = {
            "protocol_id": protocol["protocol_id"],
            "variables": variables,
            "iterations": iterations,
            "results": [],
            "summary_stats": {}
        }
        
        if self.logging_enabled:
            self.logger.info(f"Experiment completed: {protocol['protocol_id']}")
            
        return results
        
    def analyze_data(
        self,
        data: List[float],
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Perform statistical analysis on experimental data.
        
        Args:
            data: List of experimental measurements
            confidence_level: Confidence level for interval calculation
            
        Returns:
            Analysis results
        """
        if self.logging_enabled:
            self.logger.info(f"Analyzing data with {len(data)} points")
            
        # Analyze data (placeholder)
        analysis = {
            "mean": 0.0,
            "std_dev": 0.0,
            "sample_size": len(data),
            "confidence_interval": (0.0, 0.0)
        }
        
        if self.logging_enabled:
            self.logger.info(f"Analysis completed: {analysis}")
            
        return analysis
        
    def plan_research_task(
        self,
        objective: str,
        subtasks: List[str],
        dependencies: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Create a research task plan.
        
        Args:
            objective: Main research objective
            subtasks: List of subtasks
            dependencies: Task dependencies
            
        Returns:
            Research plan
        """
        if self.logging_enabled:
            self.logger.info(f"Planning research task: {objective}")
            
        plan = {
            "objective": objective,
            "subtasks": subtasks,
            "dependencies": dependencies or {},
            "status": "created",
            "progress": 0.0
        }
        
        if self.logging_enabled:
            self.logger.info(f"Research plan created: {plan}")
            
        return plan
        
    def update_task_progress(self, completed_tasks: List[str]) -> Dict[str, Any]:
        """
        Update the progress of a research task.
        
        Args:
            completed_tasks: List of completed task IDs
            
        Returns:
            Updated plan
        """
        if self.logging_enabled:
            self.logger.info(f"Updating task progress: {completed_tasks}")
            
        # Update progress (placeholder)
        updated_plan = {
            "status": "in_progress",
            "progress": 50.0
        }
        
        if self.logging_enabled:
            self.logger.info(f"Progress updated: {updated_plan}")
            
        return updated_plan
        
    def analyze_paper(self, paper_text: str) -> Dict[str, Any]:
        """
        Extract metadata from a research paper.
        
        Args:
            paper_text: Full text of the research paper
            
        Returns:
            Paper metadata
        """
        if self.logging_enabled:
            self.logger.info("Analyzing research paper")
            
        # Extract metadata (placeholder)
        metadata = {
            "title": "",
            "abstract": "",
            "keywords": [],
            "references": []
        }
        
        if self.logging_enabled:
            self.logger.info(f"Paper analysis completed: {metadata}")
            
        return metadata
        
    def format_citation(
        self,
        authors: List[str],
        title: str,
        journal: str,
        year: int,
        doi: Optional[str] = None
    ) -> str:
        """
        Format a scientific citation in APA style.
        
        Args:
            authors: List of author names
            title: Paper title
            journal: Journal name
            year: Publication year
            doi: DOI identifier
            
        Returns:
            Formatted citation
        """
        if self.logging_enabled:
            self.logger.info(f"Formatting citation for: {title}")
            
        # Format citation (placeholder)
        citation = f"{', '.join(authors)} ({year}). {title}. {journal}."
        
        if doi:
            citation += f" https://doi.org/{doi}"
            
        if self.logging_enabled:
            self.logger.info(f"Citation formatted: {citation}")
            
        return citation
        
    def collaborate(
        self,
        other_agent: "SolentraAgent",
        prompt: str,
        turns: int = 3
    ) -> str:
        """
        Collaborate with another agent on a research topic.
        
        Args:
            other_agent: Another SolentraAgent instance
            prompt: Discussion prompt
            turns: Number of conversation turns
            
        Returns:
            Discussion summary
        """
        if self.logging_enabled:
            self.logger.info(f"Starting collaboration with {other_agent.agent_name}")
            
        # Collaborate (placeholder)
        discussion = f"Collaboration between {self.agent_name} and {other_agent.agent_name}"
        
        if self.logging_enabled:
            self.logger.info(f"Collaboration completed: {discussion}")
            
        return discussion

    def log(self, message):
        if self.logging_enabled and self.log_file:
            with open(self.log_file, "a") as f:
                f.write(message + "\n")

    def reset_context(self):
        """Reset the conversation context."""
        if self.use_context:
            self.context = []

    def export_context(self):
        """Export the current conversation context."""
        return self.context

    def learn(self, topic, details):
        """Learn and store information about a topic."""
        self.memory[topic] = details

    def recall(self, topic):
        """Recall stored information about a topic."""
        return self.memory.get(topic, "I don't remember anything about that.")

    def summarize(self, text):
        """Summarize the given text."""
        summary_prompt = f"Summarize the following text concisely:\n\n{text}"
        return self.generate_response(summary_prompt)

    def extract_key_points(self, text):
        """Extract key points from the given text."""
        key_points_prompt = f"Extract the key points from the following text:\n\n{text}"
        return self.generate_response(key_points_prompt)

    def suggest_related_topics(self, topic):
        """Suggest related topics to the given topic."""
        suggestion_prompt = f"Suggest related topics to '{topic}' in the field of {self.agent_name.lower()}."
        return self.generate_response(suggestion_prompt)

    async def generate_response_async(self, prompt):
        """Asynchronous response generation."""
        messages = [{"role": "system", "content": f"You are a {self.agent_name}."},
                    {"role": "user", "content": prompt}]
        response = await openai.ChatCompletion.acreate(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response['choices'][0]['message']['content']

    def get_experiment_history(self) -> List[Dict[str, Any]]:
        """Retrieve the history of conducted experiments."""
        return self.experiment_history

    def post_tweet(self, content: str, media_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Post a tweet with optional media attachments."""
        if not self.social:
            raise ValueError("Social media tools not configured. Provide twitter_config during initialization.")
        return self.social.post_tweet(content, media_paths)

    def schedule_tweet(self, content: str, scheduled_time: datetime,
                      media_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Schedule a tweet for future posting."""
        if not self.social:
            raise ValueError("Social media tools not configured. Provide twitter_config during initialization.")
        return self.social.schedule_tweet(content, scheduled_time, media_paths)

    def get_tweet_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent tweet history."""
        if not self.social:
            raise ValueError("Social media tools not configured. Provide twitter_config during initialization.")
        return self.social.get_tweet_history(count)

    def analyze_tweet_engagement(self, tweet_id: str) -> Dict[str, Any]:
        """Analyze engagement metrics for a tweet."""
        if not self.social:
            raise ValueError("Social media tools not configured. Provide twitter_config during initialization.")
        return self.social.analyze_engagement(tweet_id)

    def analyze_hashtag_performance(self, hashtag: str) -> Dict[str, Any]:
        """Analyze performance metrics for a hashtag."""
        if not self.social:
            raise ValueError("Social media tools not configured. Provide twitter_config during initialization.")
        return self.social.analyze_hashtag_performance(hashtag)

    def analyze_audience_demographics(self) -> Dict[str, Any]:
        """Analyze audience demographics and interests."""
        if not self.social:
            raise ValueError("Social media tools not configured. Provide twitter_config during initialization.")
        return self.social.analyze_audience_demographics()

    def add_to_content_calendar(self, content: str, scheduled_time: datetime,
                              content_type: str = "tweet") -> Dict[str, Any]:
        """Add content to the social media calendar."""
        if not self.social:
            raise ValueError("Social media tools not configured. Provide twitter_config during initialization.")
        return self.social.add_to_content_calendar(content, scheduled_time, content_type)

    def get_content_calendar(self) -> List[Dict[str, Any]]:
        """Get the social media content calendar."""
        if not self.social:
            raise ValueError("Social media tools not configured. Provide twitter_config during initialization.")
        return self.social.get_content_calendar()

    def __repr__(self):
        tools_status = "enabled" if self.tools else "disabled"
        social_status = "enabled" if self.social else "disabled"
        return (f"<SolentraAgent(agent_name={self.agent_name}, model_name={self.model_name}, "
                f"interactive={self.interactive}, streaming_on={self.streaming_on}, "
                f"tools={tools_status}, social={social_status})>")
