"""
Test suite for SolentraAgent class
"""

import pytest
from datetime import datetime, timedelta
from solentra import SolentraAgent
from solentra.tools import MLTools, DataTools, ResearchTools, CollaborationTools
from solentra.social import SocialMediaTools
from unittest.mock import patch, Mock

@pytest.fixture
def agent():
    """Create a test agent instance."""
    return SolentraAgent(
        agent_name="Test Scientist",
        model_name="solentra-70b",
        tools_enabled=True,
        interactive=True,
        streaming_on=True,
        temperature=0.7,
        max_tokens=150,
        use_context=True,
        persona=None,
        logging_enabled=False
    )

@pytest.fixture
def twitter_config():
    """Create test Twitter credentials."""
    return {
        'api_key': '8Qzce7oOb0DaXx4kC8hHJjeER',
        'api_secret': 'TCHQ5jDgEBU2clxfZ9vps2H5vcQpZ2qEMJN4T9xZtaS3sdN3e5',
        'access_token': '2895807196-wjfvwd9VuPPa5OE96QifDZKWV44EpDQ0I9gjx5y',
        'access_token_secret': 'RHVQIuBzca6UhE3amF5Rz5KJx3IxNHE3BhhfFpUcyIPlA'
    }

def test_agent_initialization(agent):
    """Test agent initialization with default parameters."""
    assert agent.agent_name == "Test Scientist"
    assert agent.model_name == "gpt-4"  # Mapped from solentra-70b
    assert agent.tools_enabled is True
    assert agent.interactive is True
    assert agent.streaming_on is True
    assert agent.temperature == 0.7
    assert agent.max_tokens == 150
    assert agent.use_context is True
    assert agent.persona_description is None
    assert agent.logging_enabled is False
    assert agent.log_file is None
    assert agent.memory == {}
    assert agent.context == []
    assert agent.tools is not None
    assert agent.social is None
    assert agent.current_task is None
    assert agent.experiment_history == []

def test_agent_with_persona():
    """Test agent initialization with a predefined persona."""
    agent = SolentraAgent(persona="physicist")
    assert agent.agent_name == "Physicist"
    assert agent.persona_description == "An expert in physics, capable of explaining complex physical phenomena."

def test_agent_with_invalid_model():
    """Test agent initialization with an invalid model name."""
    with pytest.raises(ValueError):
        SolentraAgent(model_name="invalid-model")

def test_agent_with_invalid_persona():
    """Test agent initialization with an invalid persona."""
    with pytest.raises(ValueError):
        SolentraAgent(persona="invalid-persona")

def test_generate_response(agent):
    """Test response generation."""
    response = agent.generate_response("Explain quantum tunneling")
    assert isinstance(response, str)
    assert len(response) > 0

def test_create_experiment(agent):
    """Test experiment protocol creation."""
    protocol = agent.create_experiment(
        steps=["Setup", "Measure", "Analyze"],
        materials=["Sample A", "Detector"],
        duration="1 hour",
        conditions={"temperature": 25}
    )
    assert isinstance(protocol, dict)
    assert "protocol_id" in protocol
    assert "steps" in protocol
    assert "materials" in protocol
    assert "estimated_duration" in protocol
    assert "conditions" in protocol
    assert "created_at" in protocol

def test_run_experiment(agent):
    """Test experiment execution."""
    protocol = agent.create_experiment(
        steps=["Setup", "Measure"],
        materials=["Sample"],
        duration="30 min",
        conditions={"temperature": 25}
    )
    results = agent.run_experiment(
        protocol=protocol,
        variables={"concentration": 0.5},
        iterations=2
    )
    assert isinstance(results, dict)
    assert "protocol_id" in results
    assert "variables" in results
    assert "iterations" in results
    assert "results" in results
    assert "summary_stats" in results

def test_analyze_data(agent):
    """Test data analysis."""
    data = [1.2, 1.3, 1.1, 1.4, 1.2]
    analysis = agent.analyze_data(data, confidence_level=0.95)
    assert isinstance(analysis, dict)
    assert "mean" in analysis
    assert "std_dev" in analysis
    assert "sample_size" in analysis
    assert "confidence_interval" in analysis

def test_plan_research_task(agent):
    """Test research task planning."""
    plan = agent.plan_research_task(
        objective="Study enzyme kinetics",
        subtasks=["Literature review", "Data collection"],
        dependencies={"Data collection": ["Literature review"]}
    )
    assert isinstance(plan, dict)
    assert "objective" in plan
    assert "subtasks" in plan
    assert "dependencies" in plan
    assert "status" in plan
    assert "progress" in plan

def test_update_task_progress(agent):
    """Test task progress updates."""
    plan = agent.plan_research_task(
        objective="Study enzyme kinetics",
        subtasks=["Literature review", "Data collection"]
    )
    updated_plan = agent.update_task_progress(["task-1"])
    assert isinstance(updated_plan, dict)
    assert "status" in updated_plan
    assert "progress" in updated_plan

def test_analyze_paper(agent):
    """Test paper analysis."""
    paper_text = """
    Title: Quantum Effects in Biology
    Abstract: This study investigates quantum phenomena in biological processes.
    Keywords: quantum biology, coherence
    """
    metadata = agent.analyze_paper(paper_text)
    assert isinstance(metadata, dict)
    assert "title" in metadata
    assert "abstract" in metadata
    assert "keywords" in metadata
    assert "references" in metadata

def test_format_citation(agent):
    """Test citation formatting."""
    citation = agent.format_citation(
        authors=["Smith, J"],
        title="Study Title",
        journal="Journal Name",
        year=2023,
        doi="10.1234/paper"
    )
    assert isinstance(citation, str)
    assert "Smith, J" in citation
    assert "2023" in citation
    assert "Study Title" in citation
    assert "Journal Name" in citation
    assert "10.1234/paper" in citation

def test_collaborate(agent):
    """Test agent collaboration."""
    other_agent = SolentraAgent(persona="biologist")
    discussion = agent.collaborate(
        other_agent=other_agent,
        prompt="Discuss quantum effects in biology",
        turns=2
    )
    assert isinstance(discussion, str)
    assert len(discussion) > 0

def test_context_management(agent):
    """Test context management methods."""
    # Test context reset
    agent.reset_context()
    assert agent.context == []
    
    # Test context export
    context = agent.export_context()
    assert isinstance(context, list)
    
    # Test learning and recall
    agent.learn("topic", "details")
    recalled = agent.recall("topic")
    assert recalled == "details"
    
    # Test recall of unknown topic
    unknown = agent.recall("unknown")
    assert unknown == "I don't remember anything about that."

def test_summarization(agent):
    """Test text summarization."""
    text = "This is a long text that needs to be summarized. It contains multiple sentences and should be condensed into a shorter version."
    summary = agent.summarize(text)
    assert isinstance(summary, str)
    assert len(summary) < len(text)

def test_key_points_extraction(agent):
    """Test key points extraction."""
    text = "First point. Second point. Third point."
    key_points = agent.extract_key_points(text)
    assert isinstance(key_points, str)
    assert len(key_points) > 0

def test_related_topics(agent):
    """Test related topics suggestion."""
    topics = agent.suggest_related_topics("quantum computing")
    assert isinstance(topics, str)
    assert len(topics) > 0

def test_experiment_history(agent):
    """Test experiment history retrieval."""
    history = agent.get_experiment_history()
    assert isinstance(history, list)

def test_social_media_integration(agent, twitter_config):
    """Test social media integration."""
    # Mock the SocialMediaTools class before agent initialization
    with patch('solentra.agent.SocialMediaTools') as mock_social_class:
        # Create mock instance
        mock_social = Mock()
        mock_social_class.return_value = mock_social
        
        # Initialize agent with Twitter config
        agent = SolentraAgent(twitter_config=twitter_config)
        
        # Mock tweet response
        mock_tweet = {
            'id': '12345',
            'content': 'Test tweet',
            'created_at': datetime.now().isoformat(),
            'media_count': 0
        }
        mock_social.post_tweet.return_value = mock_tweet

        tweet = agent.post_tweet("Test tweet")
        assert isinstance(tweet, dict)
        assert "content" in tweet
        assert "created_at" in tweet
        assert "id" in tweet
        assert "media_count" in tweet

        # Mock tweet with media
        mock_tweet_with_media = {
            'id': '67890',
            'content': 'Test tweet with media',
            'created_at': datetime.now().isoformat(),
            'media_count': 1
        }
        mock_social.post_tweet.return_value = mock_tweet_with_media

        tweet_with_media = agent.post_tweet(
            "Test tweet with media",
            media_paths=["test_image.jpg"]
        )
        assert isinstance(tweet_with_media, dict)
        assert tweet_with_media["media_count"] == 1

        # Mock tweet history
        mock_history = [
            {
                'id': '12345',
                'content': 'Tweet 1',
                'created_at': datetime.now().isoformat(),
                'likes': 10,
                'retweets': 5
            },
            {
                'id': '67890',
                'content': 'Tweet 2',
                'created_at': datetime.now().isoformat(),
                'likes': 20,
                'retweets': 8
            }
        ]
        mock_social.get_tweet_history.return_value = mock_history

        history = agent.get_tweet_history()
        assert isinstance(history, list)
        assert len(history) == 2
        assert all(isinstance(tweet, dict) for tweet in history)
        assert all("content" in tweet for tweet in history)
        assert all("created_at" in tweet for tweet in history)

        # Mock tweet scheduling
        mock_scheduled = {
            'content': 'Future tweet',
            'scheduled_time': datetime.now().isoformat(),
            'status': 'scheduled'
        }
        mock_social.schedule_tweet.return_value = mock_scheduled

        future = datetime.now() + timedelta(days=1)
        scheduled = agent.schedule_tweet(
            "Future tweet",
            future
        )
        assert isinstance(scheduled, dict)
        assert "content" in scheduled
        assert "scheduled_time" in scheduled
        assert "status" in scheduled

        # Mock engagement analysis
        mock_analysis = {
            'likes': 100,
            'retweets': 50,
            'replies': 25,
            'impressions': 1000
        }
        mock_social.analyze_engagement.return_value = mock_analysis

        analysis = agent.analyze_tweet_engagement("tweet_id")
        assert isinstance(analysis, dict)
        assert "likes" in analysis
        assert "retweets" in analysis
        assert "replies" in analysis
        assert "impressions" in analysis

def test_agent_representation(agent):
    """Test agent string representation."""
    repr_str = repr(agent)
    assert isinstance(repr_str, str)
    assert "SolentraAgent" in repr_str
    assert agent.agent_name in repr_str
    assert agent.model_name in repr_str
