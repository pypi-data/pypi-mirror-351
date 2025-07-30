"""
Solentra Tools - Utility classes for scientific research and experimentation
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import requests
import PyPDF2
import arxiv
import networkx as nx
from collections import defaultdict
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_curve, auc
)
from sklearn.preprocessing import StandardScaler
import joblib
import pandas as pd
import hashlib
import shutil
import yaml
from typing import Set
import git
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
import markdown2
import logging

class CollaborationTools:
    """Utilities for collaboration and documentation."""
    
    @staticmethod
    def init_git_repo(path: str,
                     remote_url: Optional[str] = None) -> Dict[str, Any]:
        """Initialize a Git repository."""
        try:
            repo = git.Repo.init(path)
            
            if remote_url:
                origin = repo.create_remote('origin', remote_url)
            
            return {
                'repo_path': str(repo.working_dir),
                'is_bare': repo.bare,
                'active_branch': str(repo.active_branch),
                'remotes': [{'name': r.name, 'url': r.url} for r in repo.remotes]
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def create_jupyter_notebook(cells: List[Dict[str, Any]],
                              output_path: str,
                              metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a Jupyter notebook from cell contents."""
        nb = new_notebook()
        
        for cell in cells:
            cell_type = cell['type']
            content = cell['content']
            
            if cell_type == 'markdown':
                nb.cells.append(new_markdown_cell(content))
            elif cell_type == 'code':
                nb.cells.append(new_code_cell(content))
        
        if metadata:
            nb.metadata.update(metadata)
        
        # Save notebook
        with open(output_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        
        return {
            'file_path': output_path,
            'cell_count': len(nb.cells),
            'metadata': dict(nb.metadata)
        }
    
    @staticmethod
    def generate_markdown_report(content: Dict[str, Any],
                               template: Optional[str] = None) -> Dict[str, Any]:
        """Generate a Markdown report from structured content."""
        if template:
            # Use provided template
            with open(template, 'r') as f:
                template_content = f.read()
                
            # Replace placeholders in template
            markdown_content = template_content
            for key, value in content.items():
                placeholder = f"{{{{ {key} }}}}"
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, indent=2)
                markdown_content = markdown_content.replace(placeholder, str(value))
        else:
            # Generate default report structure
            sections = []
            
            if 'title' in content:
                sections.append(f"# {content['title']}\n")
            
            if 'summary' in content:
                sections.append(f"## Summary\n\n{content['summary']}\n")
            
            if 'methods' in content:
                sections.append("## Methods\n")
                if isinstance(content['methods'], list):
                    for method in content['methods']:
                        sections.append(f"- {method}\n")
                else:
                    sections.append(f"{content['methods']}\n")
            
            if 'results' in content:
                sections.append("## Results\n")
                if isinstance(content['results'], dict):
                    for key, value in content['results'].items():
                        sections.append(f"### {key}\n{value}\n")
                else:
                    sections.append(f"{content['results']}\n")
            
            if 'conclusions' in content:
                sections.append(f"## Conclusions\n\n{content['conclusions']}\n")
            
            markdown_content = "\n".join(sections)
        
        # Convert to HTML for preview
        html_content = markdown2.markdown(markdown_content)
        
        return {
            'markdown': markdown_content,
            'html': html_content,
            'word_count': len(markdown_content.split())
        }
    
    @staticmethod
    def track_changes(original: str,
                     modified: str,
                     context_lines: int = 3) -> Dict[str, Any]:
        """Track changes between two text versions."""
        from difflib import unified_diff
        
        # Split into lines
        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)
        
        # Generate diff
        diff = list(unified_diff(
            original_lines,
            modified_lines,
            fromfile='original',
            tofile='modified',
            n=context_lines
        ))
        
        # Parse changes
        additions = []
        deletions = []
        changes = []
        
        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                additions.append(line[1:].strip())
            elif line.startswith('-') and not line.startswith('---'):
                deletions.append(line[1:].strip())
            elif not line.startswith('@@'):
                changes.append(line.strip())
        
        return {
            'diff': ''.join(diff),
            'additions': additions,
            'deletions': deletions,
            'changes': changes,
            'stats': {
                'added_lines': len(additions),
                'deleted_lines': len(deletions),
                'total_changes': len(additions) + len(deletions)
            }
        }


class DataTools:
    """Data management and quality control utilities."""
    
    @staticmethod
    def validate_dataset(data: Union[pd.DataFrame, np.ndarray],
                        rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a dataset against specified rules."""
        if isinstance(data, np.ndarray):
            data = pd.DataFrame(data)
            
        validation_results = {
            'passed': True,
            'issues': [],
            'summary': {
                'total_rows': len(data),
                'total_columns': len(data.columns),
                'missing_values': data.isnull().sum().to_dict()
            }
        }
        
        # Check data types
        if 'dtypes' in rules:
            for col, dtype in rules['dtypes'].items():
                if col in data and str(data[col].dtype) != dtype:
                    validation_results['issues'].append(
                        f"Column '{col}' has type {data[col].dtype}, expected {dtype}"
                    )
        
        # Check value ranges
        if 'ranges' in rules:
            for col, (min_val, max_val) in rules['ranges'].items():
                if col in data:
                    out_of_range = data[
                        (data[col] < min_val) | (data[col] > max_val)
                    ]
                    if not out_of_range.empty:
                        validation_results['issues'].append(
                            f"Column '{col}' has {len(out_of_range)} values outside range [{min_val}, {max_val}]"
                        )
        
        # Check for required columns
        if 'required_columns' in rules:
            missing_cols = set(rules['required_columns']) - set(data.columns)
            if missing_cols:
                validation_results['issues'].append(
                    f"Missing required columns: {missing_cols}"
                )
        
        validation_results['passed'] = len(validation_results['issues']) == 0
        return validation_results
    
    @staticmethod
    def clean_dataset(data: Union[pd.DataFrame, np.ndarray],
                     operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Clean a dataset using specified operations."""
        if isinstance(data, np.ndarray):
            data = pd.DataFrame(data)
            
        original_shape = data.shape
        cleaned_data = data.copy()
        
        cleaning_log = []
        for op in operations:
            op_type = op['type']
            
            if op_type == 'remove_duplicates':
                old_count = len(cleaned_data)
                cleaned_data = cleaned_data.drop_duplicates(
                    subset=op.get('columns')
                )
                cleaning_log.append({
                    'operation': 'remove_duplicates',
                    'rows_removed': old_count - len(cleaned_data)
                })
                
            elif op_type == 'fill_missing':
                method = op.get('method', 'mean')
                columns = op.get('columns', cleaned_data.columns)
                
                for col in columns:
                    if col in cleaned_data:
                        null_count = cleaned_data[col].isnull().sum()
                        if method == 'mean':
                            cleaned_data[col] = cleaned_data[col].fillna(
                                cleaned_data[col].mean()
                            )
                        elif method == 'median':
                            cleaned_data[col] = cleaned_data[col].fillna(
                                cleaned_data[col].median()
                            )
                        elif method == 'mode':
                            cleaned_data[col] = cleaned_data[col].fillna(
                                cleaned_data[col].mode()[0]
                            )
                        elif method == 'constant':
                            cleaned_data[col] = cleaned_data[col].fillna(
                                op.get('value')
                            )
                            
                        cleaning_log.append({
                            'operation': 'fill_missing',
                            'column': col,
                            'filled_count': null_count
                        })
                        
            elif op_type == 'remove_outliers':
                method = op.get('method', 'zscore')
                threshold = op.get('threshold', 3)
                columns = op.get('columns', cleaned_data.select_dtypes(include=np.number).columns)
                
                for col in columns:
                    if col in cleaned_data:
                        old_count = len(cleaned_data)
                        if method == 'zscore':
                            z_scores = np.abs(stats.zscore(cleaned_data[col]))
                            cleaned_data = cleaned_data[z_scores < threshold]
                        elif method == 'iqr':
                            Q1 = cleaned_data[col].quantile(0.25)
                            Q3 = cleaned_data[col].quantile(0.75)
                            IQR = Q3 - Q1
                            cleaned_data = cleaned_data[
                                ~((cleaned_data[col] < (Q1 - 1.5 * IQR)) | 
                                  (cleaned_data[col] > (Q3 + 1.5 * IQR)))
                            ]
                            
                        cleaning_log.append({
                            'operation': 'remove_outliers',
                            'column': col,
                            'rows_removed': old_count - len(cleaned_data)
                        })
        
        return {
            'data': cleaned_data,
            'original_shape': original_shape,
            'final_shape': cleaned_data.shape,
            'cleaning_log': cleaning_log
        }
    
    @staticmethod
    def convert_format(data: Any,
                      input_format: str,
                      output_format: str,
                      **kwargs) -> Dict[str, Any]:
        """Convert data between different formats."""
        result = {
            'success': True,
            'output_data': None,
            'error': None
        }
        
        try:
            # Convert input to DataFrame if needed
            if input_format == 'csv':
                if isinstance(data, str):
                    df = pd.read_csv(data)
                else:
                    df = pd.DataFrame(data)
            elif input_format == 'json':
                if isinstance(data, str):
                    df = pd.read_json(data)
                else:
                    df = pd.DataFrame(data)
            elif input_format == 'excel':
                if isinstance(data, str):
                    df = pd.read_excel(data)
                else:
                    df = pd.DataFrame(data)
            else:
                df = pd.DataFrame(data)
            
            # Convert DataFrame to output format
            if output_format == 'csv':
                output = df.to_csv(**kwargs)
            elif output_format == 'json':
                output = df.to_json(**kwargs)
            elif output_format == 'excel':
                output = df.to_excel(**kwargs)
            elif output_format == 'parquet':
                output = df.to_parquet(**kwargs)
            elif output_format == 'numpy':
                output = df.to_numpy()
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
                
            result['output_data'] = output
            
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            
        return result
    
    @staticmethod
    def version_dataset(data: Any,
                       save_path: str,
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a versioned copy of a dataset with metadata."""
        # Create version info
        version_info = {
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {},
            'hash': None
        }
        
        try:
            # Convert data to bytes for hashing
            if isinstance(data, pd.DataFrame):
                data_bytes = data.to_csv().encode()
            elif isinstance(data, np.ndarray):
                data_bytes = data.tobytes()
            else:
                data_bytes = str(data).encode()
            
            # Calculate hash
            version_info['hash'] = hashlib.sha256(data_bytes).hexdigest()
            
            # Save data and version info
            data_path = Path(save_path)
            version_dir = data_path.parent / 'versions' / version_info['hash']
            version_dir.mkdir(parents=True, exist_ok=True)
            
            # Save data
            if isinstance(data, pd.DataFrame):
                data.to_csv(version_dir / 'data.csv')
            elif isinstance(data, np.ndarray):
                np.save(version_dir / 'data.npy', data)
            else:
                with open(version_dir / 'data.txt', 'w') as f:
                    f.write(str(data))
            
            # Save version info
            with open(version_dir / 'version.yaml', 'w') as f:
                yaml.dump(version_info, f)
            
            return {
                'version_hash': version_info['hash'],
                'save_path': str(version_dir),
                'timestamp': version_info['timestamp']
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'version_hash': None,
                'save_path': None
            }


class MLTools:
    """Machine learning utilities for model development and evaluation."""
    
    @staticmethod
    def prepare_data(X: np.ndarray,
                    y: np.ndarray,
                    test_size: float = 0.2,
                    random_state: Optional[int] = None) -> Dict[str, Any]:
        """Prepare data for model training."""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        return {
            'X_train': X_train_scaled,
            'X_test': X_test_scaled,
            'y_train': y_train,
            'y_test': y_test,
            'scaler': scaler
        }
    
    @staticmethod
    def train_model(model: Any,
                   X_train: np.ndarray,
                   y_train: np.ndarray,
                   param_grid: Optional[Dict[str, List[Any]]] = None,
                   cv: int = 5) -> Dict[str, Any]:
        """Train a model with optional hyperparameter tuning."""
        if param_grid:
            # Perform grid search
            grid_search = GridSearchCV(model, param_grid, cv=cv)
            grid_search.fit(X_train, y_train)
            best_model = grid_search.best_estimator_
            
            results = {
                'model': best_model,
                'best_params': grid_search.best_params_,
                'cv_scores': grid_search.cv_results_,
                'best_score': grid_search.best_score_
            }
        else:
            # Train with default parameters
            model.fit(X_train, y_train)
            cv_scores = cross_val_score(model, X_train, y_train, cv=cv)
            
            results = {
                'model': model,
                'cv_scores': {
                    'mean': float(cv_scores.mean()),
                    'std': float(cv_scores.std()),
                    'scores': cv_scores.tolist()
                }
            }
        
        return results
    
    @staticmethod
    def evaluate_model(model: Any,
                      X_test: np.ndarray,
                      y_test: np.ndarray,
                      task_type: str = "classification") -> Dict[str, Any]:
        """Evaluate model performance."""
        y_pred = model.predict(X_test)
        
        metrics = {}
        if task_type == "classification":
            metrics.update({
                'accuracy': float(accuracy_score(y_test, y_pred)),
                'precision': float(precision_score(y_test, y_pred, average='weighted')),
                'recall': float(recall_score(y_test, y_pred, average='weighted')),
                'f1': float(f1_score(y_test, y_pred, average='weighted')),
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
            })
            
            # ROC curve for binary classification
            if len(np.unique(y_test)) == 2:
                y_prob = model.predict_proba(X_test)[:, 1]
                fpr, tpr, _ = roc_curve(y_test, y_prob)
                metrics['roc_auc'] = float(auc(fpr, tpr))
                metrics['roc_curve'] = {
                    'fpr': fpr.tolist(),
                    'tpr': tpr.tolist()
                }
        
        return metrics
    
    @staticmethod
    def analyze_feature_importance(model: Any,
                                 feature_names: List[str],
                                 top_n: Optional[int] = None) -> Dict[str, Any]:
        """Analyze feature importance from the model."""
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importances = np.abs(model.coef_[0]) if len(model.coef_.shape) > 1 else np.abs(model.coef_)
        else:
            raise ValueError("Model does not provide feature importance information")
        
        # Create feature importance pairs
        importance_pairs = list(zip(feature_names, importances))
        importance_pairs.sort(key=lambda x: x[1], reverse=True)
        
        if top_n:
            importance_pairs = importance_pairs[:top_n]
        
        return {
            'feature_importance': [
                {'feature': feat, 'importance': float(imp)}
                for feat, imp in importance_pairs
            ],
            'total_features': len(feature_names)
        }
    
    @staticmethod
    def save_model(model: Any,
                  save_path: str,
                  metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Save trained model and associated metadata."""
        # Create model package
        model_package = {
            'model': model,
            'metadata': metadata or {},
            'saved_at': datetime.now().isoformat()
        }
        
        # Save to disk
        joblib.dump(model_package, save_path)
        
        return {
            'file_path': save_path,
            'model_type': type(model).__name__,
            'metadata': metadata
        }
    
    @staticmethod
    def load_model(load_path: str) -> Dict[str, Any]:
        """Load a saved model and its metadata."""
        model_package = joblib.load(load_path)
        
        return {
            'model': model_package['model'],
            'metadata': model_package['metadata'],
            'saved_at': model_package['saved_at']
        }


class ResearchTools:
    """Tools for research paper analysis and literature review."""
    
    @staticmethod
    def parse_pdf(pdf_path: str) -> Dict[str, Any]:
        """Extract text and metadata from a PDF file."""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Extract text from all pages
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Get document info
            info = reader.metadata
            
            return {
                'text': text,
                'metadata': {
                    'title': info.get('/Title', ''),
                    'author': info.get('/Author', ''),
                    'subject': info.get('/Subject', ''),
                    'keywords': info.get('/Keywords', ''),
                    'creation_date': info.get('/CreationDate', ''),
                    'page_count': len(reader.pages)
                }
            }
    
    @staticmethod
    def search_arxiv(query: str, 
                    max_results: int = 10,
                    sort_by: str = "relevance") -> List[Dict[str, Any]]:
        """Search ArXiv for papers matching the query."""
        client = arxiv.Client()
        # Map string sort criteria to arxiv.SortCriterion
        sort_mapping = {
            "submittedDate": arxiv.SortCriterion.SubmittedDate,
            "lastUpdated": arxiv.SortCriterion.LastUpdatedDate,
            "relevance": arxiv.SortCriterion.Relevance
        }
        
        sort_criterion = sort_mapping.get(sort_by.lower(), arxiv.SortCriterion.SubmittedDate)
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_criterion
        )
        
        results = []
        for paper in client.results(search):
            results.append({
                'title': paper.title,
                'authors': [author.name for author in paper.authors],
                'summary': paper.summary,
                'published': paper.published.isoformat(),
                'updated': paper.updated.isoformat(),
                'doi': paper.doi,
                'arxiv_id': paper.entry_id,
                'pdf_url': paper.pdf_url,
                'categories': paper.categories
            })
            
        return results
    
    @staticmethod
    def generate_citation_graph(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a citation network graph from a list of papers."""
        G = nx.DiGraph()
        
        # Create nodes for papers
        for paper in papers:
            G.add_node(paper['title'], **{
                k: v for k, v in paper.items() 
                if k != 'title' and k != 'references'
            })
        
        # Add citation edges
        for paper in papers:
            if 'references' in paper:
                for ref in paper['references']:
                    if ref in [p['title'] for p in papers]:
                        G.add_edge(paper['title'], ref)
        
        # Calculate network metrics
        metrics = {
            'node_count': G.number_of_nodes(),
            'edge_count': G.number_of_edges(),
            'density': nx.density(G),
            'average_degree': sum(dict(G.degree()).values()) / G.number_of_nodes(),
            'most_cited': sorted(
                G.in_degree(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        }
        
        return {
            'nodes': list(G.nodes(data=True)),
            'edges': list(G.edges()),
            'metrics': metrics
        }
    
    @staticmethod
    def summarize_literature(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a structured summary of multiple research papers."""
        # Collect common themes and topics
        topics = defaultdict(int)
        methods = defaultdict(int)
        findings = []
        
        for paper in papers:
            # Extract topics from title and abstract
            text = f"{paper['title']} {paper.get('abstract', '')}"
            
            # Count research methods mentioned
            method_keywords = ['experiment', 'survey', 'observation', 'simulation']
            for method in method_keywords:
                if method in text.lower():
                    methods[method] += 1
            
            # Collect main findings
            if 'summary' in paper:
                findings.append({
                    'paper': paper['title'],
                    'finding': paper['summary'][:200] + '...'  # Truncate for brevity
                })
        
        return {
            'paper_count': len(papers),
            'date_range': {
                'start': min(p['published'] for p in papers if 'published' in p),
                'end': max(p['published'] for p in papers if 'published' in p)
            },
            'common_topics': dict(sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]),
            'research_methods': dict(methods),
            'key_findings': findings,
            'generated_at': datetime.now().isoformat()
        }


class AgentTools:
    """A collection of utility tools that can be used with CrimsonAgent."""
    
    @staticmethod
    def plot_experiment_results(data: List[float], 
                              title: str = "Experiment Results",
                              xlabel: str = "Sample",
                              ylabel: str = "Value",
                              plot_type: str = "line",
                              save_path: Optional[str] = None) -> Dict[str, Any]:
        """Create visualization of experimental data."""
        plt.figure(figsize=(10, 6))
        
        if plot_type == "line":
            plt.plot(data, marker='o')
        elif plot_type == "scatter":
            plt.scatter(range(len(data)), data)
        elif plot_type == "histogram":
            plt.hist(data, bins='auto', alpha=0.7)
        elif plot_type == "box":
            plt.boxplot(data)
            
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
            return {"file_path": save_path}
            
        return {"figure": plt.gcf()}
    
    @staticmethod
    def create_interactive_plot(data: Dict[str, List[float]],
                              plot_type: str = "scatter",
                              title: str = "Interactive Plot",
                              save_path: Optional[str] = None) -> Dict[str, Any]:
        """Create interactive Plotly visualization."""
        if plot_type == "scatter":
            fig = px.scatter(data)
        elif plot_type == "line":
            fig = px.line(data)
        elif plot_type == "bar":
            fig = px.bar(data)
        elif plot_type == "box":
            fig = px.box(data)
            
        fig.update_layout(title=title)
        
        if save_path:
            fig.write_html(save_path)
            return {"file_path": save_path}
            
        return {"figure": fig}
    
    @staticmethod
    def perform_statistical_tests(data1: List[float], 
                                data2: Optional[List[float]] = None,
                                test_type: str = "ttest") -> Dict[str, Any]:
        """Perform statistical tests on experimental data."""
        results = {}
        
        if test_type == "ttest":
            if data2 is not None:
                stat, pval = stats.ttest_ind(data1, data2)
                results["test_type"] = "Independent t-test"
            else:
                stat, pval = stats.ttest_1samp(data1, 0)
                results["test_type"] = "One-sample t-test"
            
            results.update({
                "statistic": float(stat),
                "p_value": float(pval),
                "significant": pval < 0.05
            })
            
        elif test_type == "normality":
            stat, pval = stats.normaltest(data1)
            results.update({
                "test_type": "Normality test",
                "statistic": float(stat),
                "p_value": float(pval),
                "is_normal": pval > 0.05
            })
            
        elif test_type == "correlation":
            if data2 is None:
                raise ValueError("Second dataset required for correlation analysis")
            corr, pval = stats.pearsonr(data1, data2)
            results.update({
                "test_type": "Pearson correlation",
                "correlation": float(corr),
                "p_value": float(pval),
                "significant": pval < 0.05
            })
            
        return results
    
    @staticmethod
    def fit_distribution(data: List[float],
                        dist_type: str = "normal") -> Dict[str, Any]:
        """Fit a statistical distribution to the data."""
        if dist_type == "normal":
            params = stats.norm.fit(data)
            dist = stats.norm(*params)
        elif dist_type == "gamma":
            params = stats.gamma.fit(data)
            dist = stats.gamma(*params)
        elif dist_type == "exponential":
            params = stats.expon.fit(data)
            dist = stats.expon(*params)
            
        # Generate fitted distribution points
        x = np.linspace(min(data), max(data), 100)
        y = dist.pdf(x)
        
        return {
            "distribution": dist_type,
            "parameters": [float(p) for p in params],
            "fitted_x": x.tolist(),
            "fitted_y": y.tolist(),
            "log_likelihood": float(np.sum(dist.logpdf(data)))
        }
    
    @staticmethod
    def parse_scientific_notation(text: str) -> List[float]:
        """Extract numbers in scientific notation from text."""
        pattern = r'[-+]?\d*\.?\d+[eE][-+]?\d+'
        return [float(match) for match in re.findall(pattern, text)]
    
    @staticmethod
    def format_citation(authors: List[str], title: str, journal: str, 
                       year: int, doi: Optional[str] = None) -> str:
        """Format a scientific citation in APA style."""
        citation = f"{', '.join(authors)} ({year}). {title}. {journal}"
        if doi:
            citation += f". DOI: {doi}"
        return citation
    
    @staticmethod
    def analyze_experiment_data(data: List[float], 
                              confidence_level: float = 0.95) -> Dict[str, Any]:
        """Perform statistical analysis on experimental data."""
        results = {
            'mean': float(np.mean(data)),
            'std_dev': float(np.std(data)),
            'sample_size': len(data),
            'confidence_interval': None
        }
        
        # Calculate confidence interval
        from scipy import stats
        ci = stats.t.interval(confidence_level, len(data)-1,
                            loc=np.mean(data),
                            scale=stats.sem(data))
        results['confidence_interval'] = (float(ci[0]), float(ci[1]))
        
        return results
    
    @staticmethod
    def create_experiment_protocol(steps: List[str], 
                                 materials: List[str],
                                 duration: str,
                                 conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Create a structured experiment protocol."""
        return {
            'protocol_id': f"EXP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'steps': steps,
            'materials': materials,
            'estimated_duration': duration,
            'conditions': conditions,
            'created_at': datetime.now().isoformat()
        }
    
    @staticmethod
    def extract_paper_metadata(text: str) -> Dict[str, Any]:
        """Extract metadata from research paper text."""
        # Basic metadata extraction
        title_pattern = r'(?i)Title:\s*(.*?)(?=\n|$)'
        abstract_pattern = r'(?i)Abstract:\s*(.*?)(?=\n\n|\Z)'
        
        metadata = {
            'title': '',
            'abstract': '',
            'keywords': [],
            'references': []
        }
        
        # Extract title
        if title_match := re.search(title_pattern, text.strip()):
            metadata['title'] = f"Title: {title_match.group(1).strip()}"
            
        # Extract abstract
        if abstract_match := re.search(abstract_pattern, text, re.DOTALL):
            metadata['abstract'] = abstract_match.group(1).strip()
        
        # Extract keywords
        keywords_pattern = r'(?i)Keywords:\s*(.*?)(?=\n\n|\Z)'
        if keywords_match := re.search(keywords_pattern, text, re.DOTALL):
            metadata['keywords'] = [k.strip() for k in keywords_match.group(1).split(',')]
            
        return metadata
    
    @staticmethod
    def create_task_plan(objective: str, 
                        subtasks: List[str],
                        dependencies: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
        """Create a structured task plan with dependencies."""
        task_plan = {
            'objective': objective,
            'subtasks': [{'id': f'task-{i+1}', 'description': task, 'status': 'pending'}
                        for i, task in enumerate(subtasks)],
            'created_at': datetime.now().isoformat(),
            'status': 'not_started'
        }
        
        if dependencies:
            task_plan['dependencies'] = dependencies
            
        return task_plan
    
    @staticmethod
    def track_task_progress(task_plan: Dict[str, Any], 
                           completed_tasks: List[str]) -> Dict[str, Any]:
        """Update task plan with completed tasks and calculate progress."""
        total_tasks = len(task_plan['subtasks'])
        completed_count = 0
        
        for task in task_plan['subtasks']:
            if task['id'] in completed_tasks:
                task['status'] = 'completed'
                completed_count += 1
                
        progress = (completed_count / total_tasks) * 100
        
        task_plan['progress'] = progress
        task_plan['status'] = 'completed' if progress == 100 else 'in_progress'
        task_plan['last_updated'] = datetime.now().isoformat()
        
        return task_plan
    
    @staticmethod
    def simulate_experiment(protocol: Dict[str, Any], 
                          variables: Dict[str, Any],
                          iterations: int = 1) -> Dict[str, Any]:
        """Simulate an experiment based on protocol and variables."""
        results = []
        for i in range(iterations):
            # Add random variation to simulate real experimental conditions
            iteration_vars = {
                k: v * (1 + np.random.normal(0, 0.05))  # 5% random variation
                for k, v in variables.items()
                if isinstance(v, (int, float))
            }
            
            results.append({
                'iteration': i + 1,
                'variables': iteration_vars,
                'timestamp': datetime.now().isoformat()
            })
            
        return {
            'protocol_id': protocol['protocol_id'],
            'iterations': iterations,
            'results': results,
            'summary_stats': AgentTools.analyze_experiment_data(
                [r['variables'][list(variables.keys())[0]] for r in results]
            )
        }
