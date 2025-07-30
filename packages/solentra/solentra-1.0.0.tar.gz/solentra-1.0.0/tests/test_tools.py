"""
Test suite for Solentra tools
"""

import pytest
from unittest.mock import Mock, patch
import numpy as np
import pandas as pd
from datetime import datetime
from solentra.tools import (
    MLTools,
    DataTools,
    ResearchTools,
    CollaborationTools,
    AgentTools
)
from unittest.mock import mock_open

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return {
        'X': np.random.randn(100, 4),
        'y': np.random.randint(0, 2, 100)
    }

@pytest.fixture
def sample_dataset():
    """Create a sample dataset for testing."""
    return pd.DataFrame({
        'A': np.random.randn(100),
        'B': np.random.randint(0, 10, 100),
        'C': ['category_' + str(i % 3) for i in range(100)]
    })

def test_ml_tools_data_preparation(sample_data):
    """Test MLTools data preparation."""
    data = MLTools.prepare_data(
        sample_data['X'],
        sample_data['y'],
        test_size=0.2
    )
    assert isinstance(data, dict)
    assert 'X_train' in data
    assert 'X_test' in data
    assert 'y_train' in data
    assert 'y_test' in data
    assert 'scaler' in data

def test_ml_tools_model_training(sample_data):
    """Test MLTools model training."""
    from sklearn.ensemble import RandomForestClassifier
    
    data = MLTools.prepare_data(
        sample_data['X'],
        sample_data['y']
    )
    
    model = RandomForestClassifier()
    training = MLTools.train_model(
        model,
        data['X_train'],
        data['y_train']
    )
    
    assert isinstance(training, dict)
    assert 'model' in training
    assert 'cv_scores' in training

def test_ml_tools_model_evaluation(sample_data):
    """Test MLTools model evaluation."""
    from sklearn.ensemble import RandomForestClassifier
    
    data = MLTools.prepare_data(
        sample_data['X'],
        sample_data['y']
    )
    
    model = RandomForestClassifier()
    training = MLTools.train_model(
        model,
        data['X_train'],
        data['y_train']
    )
    
    metrics = MLTools.evaluate_model(
        training['model'],
        data['X_test'],
        data['y_test']
    )
    
    assert isinstance(metrics, dict)
    assert 'accuracy' in metrics
    assert 'precision' in metrics
    assert 'recall' in metrics
    assert 'f1' in metrics

def test_data_tools_validation(sample_dataset):
    """Test DataTools dataset validation."""
    rules = {
        'A': {'type': 'float', 'min': -3, 'max': 3},
        'B': {'type': 'int', 'min': 0, 'max': 9},
        'C': {'type': 'str', 'values': ['category_0', 'category_1', 'category_2']}
    }
    
    validation = DataTools.validate_dataset(sample_dataset, rules)
    assert isinstance(validation, dict)
    assert 'passed' in validation
    assert 'issues' in validation
    assert 'summary' in validation

def test_data_tools_cleaning(sample_dataset):
    """Test DataTools dataset cleaning."""
    operations = [
        {'type': 'drop_na', 'columns': ['A']},
        {'type': 'fill_na', 'columns': ['B'], 'value': 0},
        {'type': 'drop_duplicates'}
    ]
    
    cleaned = DataTools.clean_dataset(sample_dataset, operations)
    assert isinstance(cleaned, dict)
    assert 'data' in cleaned
    assert 'cleaning_log' in cleaned

def test_research_tools_pdf_parsing():
    """Test ResearchTools PDF parsing."""
    with patch('builtins.open', mock_open(read_data=b'Test PDF content')):
        with patch('PyPDF2.PdfReader') as mock_reader:
            mock_reader.return_value.pages = [Mock(extract_text=lambda: "Test content")]
            
            result = ResearchTools.parse_pdf("test.pdf")
            assert isinstance(result, dict)
            assert 'text' in result
            assert 'metadata' in result

def test_research_tools_arxiv_search():
    """Test ResearchTools ArXiv search."""
    with patch('arxiv.Client') as mock_client:
        mock_author = Mock()
        mock_author.name = "Test Author"
        mock_result = Mock(
            title="Test Paper",
            authors=[mock_author],
            summary="Test summary",
            pdf_url="http://test.pdf",
            published=datetime.now(),
            updated=datetime.now(),
            doi="10.1234/test",
            entry_id="test.1234",
            categories=["cs.AI"]
        )
        mock_client.return_value.results.return_value = [mock_result]
        
        papers = ResearchTools.search_arxiv(
            "test query",
            max_results=1
        )
        assert isinstance(papers, list)
        assert len(papers) == 1
        assert 'title' in papers[0]
        assert 'authors' in papers[0]

def test_collaboration_tools_git():
    """Test CollaborationTools Git operations."""
    with patch('git.Repo') as mock_repo:
        mock_repo.return_value.remotes = []
        mock_repo.return_value.working_dir = "test_repo"
        mock_repo.return_value.active_branch = "main"
        mock_repo.return_value.is_bare = False
        
        result = CollaborationTools.init_git_repo(
            "test_repo",
            remote_url="https://github.com/test/repo.git"
        )
        assert isinstance(result, dict)
        assert 'repo_path' in result
        assert 'active_branch' in result
        assert 'is_bare' in result

def test_collaboration_tools_notebook():
    """Test CollaborationTools notebook creation."""
    cells = [
        {'type': 'markdown', 'content': '# Test'},
        {'type': 'code', 'content': 'print("test")'}
    ]
    
    with patch('nbformat.v4.new_notebook') as mock_nb:
        mock_nb.return_value = {'cells': [], 'metadata': {}}
        with patch('nbformat.write') as mock_write:
            result = CollaborationTools.create_jupyter_notebook(
                cells,
                "test.ipynb"
            )
            assert isinstance(result, dict)
            assert 'file_path' in result
            assert 'cell_count' in result
            assert 'metadata' in result

def test_agent_tools_scientific_notation():
    """Test AgentTools scientific notation parsing."""
    text = "The rate constant is 1.23e-3 M/s"
    values = AgentTools.parse_scientific_notation(text)
    assert isinstance(values, list)
    assert len(values) == 1
    assert abs(values[0] - 1.23e-3) < 1e-6

def test_agent_tools_citation_formatting():
    """Test AgentTools citation formatting."""
    citation = AgentTools.format_citation(
        authors=["Smith, J", "Jones, M"],
        title="Test Paper",
        journal="Test Journal",
        year=2023,
        doi="10.1234/test"
    )
    assert isinstance(citation, str)
    assert "Smith, J" in citation
    assert "Jones, M" in citation
    assert "2023" in citation
    assert "10.1234/test" in citation

def test_agent_tools_experiment_analysis():
    """Test AgentTools experiment data analysis."""
    data = [1.2, 1.3, 1.1, 1.4, 1.2]
    analysis = AgentTools.analyze_experiment_data(data)
    assert isinstance(analysis, dict)
    assert 'mean' in analysis
    assert 'std_dev' in analysis
    assert 'confidence_interval' in analysis

def test_agent_tools_protocol_creation():
    """Test AgentTools experiment protocol creation."""
    protocol = AgentTools.create_experiment_protocol(
        steps=["Setup", "Measure", "Analyze"],
        materials=["Sample A", "Detector"],
        duration="1 hour",
        conditions={"temperature": 25}
    )
    assert isinstance(protocol, dict)
    assert 'protocol_id' in protocol
    assert 'steps' in protocol
    assert 'materials' in protocol
    assert 'conditions' in protocol

def test_agent_tools_paper_metadata():
    """Test AgentTools paper metadata extraction."""
    text = """
    Title: Test Paper
    Abstract: This is a test paper.
    Keywords: test, paper
    References:
    1. Smith, J (2023) Test Reference
    """
    
    metadata = AgentTools.extract_paper_metadata(text)
    assert isinstance(metadata, dict)
    assert 'title' in metadata
    assert 'abstract' in metadata
    assert 'keywords' in metadata
    assert 'references' in metadata
