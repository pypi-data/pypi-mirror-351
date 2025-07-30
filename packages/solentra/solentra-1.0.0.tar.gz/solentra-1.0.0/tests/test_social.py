"""
Test suite for social media integration
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from solentra import SolentraAgent
from solentra.social import SocialMediaTools

@pytest.fixture
def mock_twitter_api():
    """Create a mock Twitter API."""
    with patch('tweepy.API') as mock_api:
        yield mock_api

@pytest.fixture
def twitter_config():
    """Create test Twitter credentials."""
    return {
        'api_key': 'test_api_key',
        'api_secret': 'test_api_secret',
        'access_token': 'test_access_token',
        'access_token_secret': 'test_access_token_secret'
    }

@pytest.fixture
def agent(twitter_config, mock_twitter_api):
    """Create a test agent instance with Twitter configuration."""
    return SolentraAgent(
        agent_name="Test Scientist",
        model_name="solentra-70b",
        twitter_config=twitter_config
    )

def test_tweet_posting(agent, mock_twitter_api):
    """Test posting tweets."""
    # Mock tweet response
    mock_tweet = Mock()
    mock_tweet.id = '12345'
    mock_tweet.text = 'Test tweet'
    mock_tweet.created_at = datetime.now()
    mock_twitter_api.return_value.update_status.return_value = mock_tweet
    
    # Test basic tweet
    tweet = agent.post_tweet("Test tweet")
    assert isinstance(tweet, dict)
    assert "content" in tweet
    assert "created_at" in tweet
    assert "id" in tweet
    assert "media_count" in tweet
    
    # Test tweet with media
    mock_media = Mock()
    mock_media.media_id = 'media123'
    mock_twitter_api.return_value.media_upload.return_value = mock_media
    
    tweet_with_media = agent.post_tweet(
        "Test tweet with media",
        media_paths=["test_image.jpg"]
    )
    assert isinstance(tweet_with_media, dict)
    assert tweet_with_media["media_count"] == 1

def test_tweet_scheduling(agent):
    """Test scheduling tweets."""
    future = datetime.now()
    scheduled = agent.schedule_tweet(
        "Future tweet",
        future
    )
    assert isinstance(scheduled, dict)
    assert "content" in scheduled
    assert "scheduled_time" in scheduled
    assert "status" in scheduled

def test_tweet_history(agent, mock_twitter_api):
    """Test retrieving tweet history."""
    # Mock timeline tweets
    mock_tweet1 = Mock()
    mock_tweet1.id = '12345'
    mock_tweet1.text = 'Tweet 1'
    mock_tweet1.created_at = datetime.now()
    mock_tweet1.favorite_count = 10
    mock_tweet1.retweet_count = 5
    
    mock_tweet2 = Mock()
    mock_tweet2.id = '67890'
    mock_tweet2.text = 'Tweet 2'
    mock_tweet2.created_at = datetime.now()
    mock_tweet2.favorite_count = 20
    mock_tweet2.retweet_count = 8
    
    mock_twitter_api.return_value.user_timeline.return_value = [mock_tweet1, mock_tweet2]
    
    history = agent.get_tweet_history()
    assert isinstance(history, list)
    assert all(isinstance(tweet, dict) for tweet in history)
    assert all("content" in tweet for tweet in history)
    assert all("created_at" in tweet for tweet in history)

def test_engagement_analysis(agent, mock_twitter_api):
    """Test analyzing tweet engagement."""
    # Mock tweet response
    mock_tweet = Mock()
    mock_tweet.favorite_count = 100
    mock_tweet.retweet_count = 50
    mock_twitter_api.return_value.get_status.return_value = mock_tweet
    
    analysis = agent.analyze_tweet_engagement("tweet_id")
    assert isinstance(analysis, dict)
    assert "likes" in analysis
    assert "retweets" in analysis
    assert "replies" in analysis
    assert "impressions" in analysis

def test_hashtag_analysis(agent):
    """Test analyzing hashtag performance."""
    analysis = agent.analyze_hashtag_performance("#science")
    assert isinstance(analysis, dict)
    assert "tweet_count" in analysis
    assert "engagement_rate" in analysis
    assert "reach" in analysis

def test_audience_analysis(agent):
    """Test analyzing audience demographics."""
    analysis = agent.analyze_audience_demographics()
    assert isinstance(analysis, dict)
    assert "followers_count" in analysis
    assert "demographics" in analysis
    assert "interests" in analysis

def test_content_calendar(agent):
    """Test managing content calendar."""
    # Test adding content
    content = agent.add_to_content_calendar(
        "Test content",
        datetime.now(),
        content_type="article"
    )
    assert isinstance(content, dict)
    assert "content" in content
    assert "scheduled_time" in content
    assert "type" in content
    
    # Test retrieving calendar
    calendar = agent.get_content_calendar()
    assert isinstance(calendar, list)
    assert all(isinstance(item, dict) for item in calendar)
    assert all("content" in item for item in calendar)
    assert all("scheduled_time" in item for item in calendar)

def test_social_media_not_configured():
    """Test behavior when social media is not configured."""
    agent = SolentraAgent(agent_name="Test Scientist")
    
    with pytest.raises(ValueError):
        agent.post_tweet("Test tweet")
    
    with pytest.raises(ValueError):
        agent.schedule_tweet("Future tweet", datetime.now())
    
    with pytest.raises(ValueError):
        agent.get_tweet_history()
    
    with pytest.raises(ValueError):
        agent.analyze_tweet_engagement("tweet_id")
    
    with pytest.raises(ValueError):
        agent.analyze_hashtag_performance("#test")
    
    with pytest.raises(ValueError):
        agent.analyze_audience_demographics()
    
    with pytest.raises(ValueError):
        agent.add_to_content_calendar("Test content", datetime.now())
    
    with pytest.raises(ValueError):
        agent.get_content_calendar()
