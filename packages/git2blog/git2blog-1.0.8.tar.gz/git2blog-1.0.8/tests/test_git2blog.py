#!/usr/bin/env python3
"""
Testy jednostkowe dla git2blog
"""

import unittest
import tempfile
import shutil
import os
import sys
import json
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock

# Dodaj katalog główny do ścieżki
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from git2blog import Git2Blog
except ImportError:
    # Fallback jeśli moduł nie jest dostępny
    Git2Blog = None

class TestGit2Blog(unittest.TestCase):
    """Testy dla klasy Git2Blog"""
    
    def setUp(self):
        """Przygotowanie przed każdym testem"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'ollama_url': 'http://localhost:11434',
            'model': 'llama3.2',
            'output_dir': 'test_blog',
            'blog_title': 'Test Blog',
            'author': 'Test Author',
            'commit_limit': 10
        }
        
        # Mock commits do testów
        self.sample_commits = [
            {
                'hash': 'abc123',
                'author': 'Jan Kowalski',
                'email': 'jan@example.com',
                'date': '2025-01-15 10:30:00',
                'subject': 'Dodaj nową funkcję logowania',
                'body': 'Implementacja systemu logowania użytkowników z walidacją email'
            },
            {
                'hash': 'def456',
                'author': 'Anna Nowak',
                'email': 'anna@example.com',
                'date': '2025-01-14 15:45:00',
                'subject': 'Popraw błąd w interfejsie',
                'body': 'Naprawiono problem z wyświetlaniem menu na urządzeniach mobilnych'
            }
        ]
    
    def tearDown(self):
        """Sprzątanie po testach"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @unittest.skipIf(Git2Blog is None, "Git2Blog module nie jest dostępny")
    def test_init(self):
        """Test inicjalizacji Git2Blog"""
        with patch('builtins.open', create=True) as mock_open:
            with patch('os.path.exists', return_value=False):
                git2blog = Git2Blog('nonexistent.yaml')
                self.assertEqual(git2blog.config, {})
                self.assertEqual(git2blog.ollama_url, 'http://localhost:11434')
                self.assertEqual(git2blog.model, 'llama3.2')
    
    @unittest.skipIf(Git2Blog is None, "Git2Blog module nie jest dostępny")
    def test_create_default_config(self):
        """Test tworzenia domyślnej konfiguracji"""
        os.chdir(self.temp_dir)
        
        git2blog = Git2Blog()
        git2blog.create_default_config()
        
        self.assertTrue(os.path.exists('git2blog.yaml'))
        
        # Sprawdź zawartość pliku
        with open('git2blog.yaml', 'r', encoding='utf-8') as f:
            import yaml
            config = yaml.safe_load(f)
            self.assertIn('ollama_url', config)
            self.assertIn('model', config)
            self.assertIn('blog_title', config)
    
    @patch('subprocess.run')
    @unittest.skipIf(Git2Blog is None, "Git2Blog module nie jest dostępny")
    def test_get_git_commits(self, mock_run):
        """Test pobierania commitów Git"""
        # Mock odpowiedzi subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123|Jan Kowalski|jan@example.com|2025-01-15|Test commit|Test body\n"
        mock_run.return_value = mock_result
        
        git2blog = Git2Blog()
        commits = git2blog.get_git_commits(limit=1)
        
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0]['hash'], 'abc123')
        self.assertEqual(commits[0]['author'], 'Jan Kowalski')
        self.assertEqual(commits[0]['subject'], 'Test commit')
    
    @patch('requests.post')
    @unittest.skipIf(Git2Blog is None, "Git2Blog module nie jest dostępny")
    def test_call_ollama_success(self, mock_post):
        """Test udanego wywołania Ollama API"""
        # Mock odpowiedzi Ollama
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'response': 'Wygenerowany tekst bloga'}
        mock_post.return_value = mock_response
        
        git2blog = Git2Blog()
        result = git2blog.call_ollama("Test prompt")
        
        self.assertEqual(result, 'Wygenerowany tekst bloga')
        mock_post.assert_called_once()
    
    @patch('requests.post')
    @unittest.skipIf(Git2Blog is None, "Git2Blog module nie jest dostępny")
    def test_call_ollama_failure(self, mock_post):
        """Test nieudanego wywołania Ollama API"""
        # Mock błędnej odpowiedzi
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        git2blog = Git2Blog()
        result = git2blog.call_ollama("Test prompt")
        
        self.assertEqual(result, "")
    
    @unittest.skipIf(Git2Blog is None, "Git2Blog module nie jest dostępny")
    def test_create_html_post(self):
        """Test tworzenia HTML posta"""
        git2blog = Git2Blog()
        
        post = {
            'title': 'Test Post',
            'content': 'To jest testowa treść posta.',
            'date': '2025-01-15 10:30:00',
            'author': 'Test Author',
            'commit_hash': 'abc123'
        }
        
        html = git2blog.create_html_post(post)
        
        self.assertIn('Test Post', html)
        self.assertIn('To jest testowa treść posta.', html)
        self.assertIn('Test Author', html)
        self.assertIn('abc123', html)
        self.assertIn('<!DOCTYPE html>', html)
    
    @unittest.skipIf(Git2Blog is None, "Git2Blog module nie jest dostępny")
    def test_create_index_page(self):
        """Test tworzenia strony głównej"""
        git2blog = Git2Blog()
        
        posts = [
            {
                'title': 'Post 1',
                'content': 'Treść pierwszego posta.',
                'date': '2025-01-15 10:30:00',
                'author': 'Autor 1',
                'commit_hash': 'abc123'
            },
            {
                'title': 'Post 2',
                'content': 'Treść drugiego posta.',
                'date': '2025-01-14 15:45:00',
                'author': 'Autor 2',
                'commit_hash': 'def456'
            }
        ]
        
        html = git2blog.create_index_page(posts)
        
        self.assertIn('Post 1', html)
        self.assertIn('Post 2', html)
        self.assertIn('Treść pierwszego posta.', html)
        self.assertIn('Treść drugiego posta.', html)
        self.assertIn('Autor 1', html)
        self.assertIn('Autor 2', html)
        self.assertIn('abc123', html)
        self.assertIn('def456', html)

class TestGit2BlogIntegration(unittest.TestCase):
    """Testy integracyjne"""
    
    def setUp(self):
        """Przygotowanie środowiska testowego"""
        self.temp_dir = tempfile.mkdtemp()
        try:
            self.original_dir = os.getcwd()
        except FileNotFoundError:
            self.original_dir = "/tmp"
        os.chdir(self.temp_dir)
        
        # Utwórz fałszywe repozytorium Git
        os.makedirs('.git')
    
    def tearDown(self):
        """Sprzątanie"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('subprocess.run')
    @patch('requests.post')
    @patch('requests.get')
    @unittest.skipIf(Git2Blog is None, "Git2Blog module nie jest dostępny")
    def test_full_blog_generation(self, mock_get, mock_post, mock_run):
        """Test pełnego procesu generowania bloga"""
        # Mock sprawdzenia Ollama
        mock_get.return_value.status_code = 200
        
        # Mock commitów Git
        mock_git_result = Mock()
        mock_git_result.returncode = 0
        mock_git_result.stdout = "abc123|Jan Kowalski|jan@example.com|2025-01-15|Test commit|Test body"
        mock_run.return_value = mock_git_result
        
        # Mock odpowiedzi Ollama
        mock_ollama_response = Mock()
        mock_ollama_response.status_code = 200
        mock_ollama_response.json.return_value = {'response': 'Wygenerowany post blogowy'}
        mock_post.return_value = mock_ollama_response
        
        # Utwórz konfigurację
        config = {
            'ollama_url': 'http://localhost:11434',
            'model': 'llama3.2',
            'output_dir': 'blog',
            'blog_title': 'Test Blog',
            'commit_limit': 1
        }
        
        with patch('yaml.safe_load', return_value=config):
            with patch('os.path.exists', return_value=True):
                # Create a minimal test.yaml file so open() does not fail
                with open('test.yaml', 'w', encoding='utf-8') as f:
                    f.write('dummy: value')
                git2blog = Git2Blog('test.yaml')
                git2blog.generate_blog()
        
        # Sprawdź czy pliki zostały utworzone
        self.assertTrue(os.path.exists('blog'))
        self.assertTrue(os.path.exists('blog/index.html'))
        self.assertTrue(os.path.exists('blog/post_1.html'))

class TestConfigValidation(unittest.TestCase):
    """Testy walidacji konfiguracji"""
    
    @unittest.skipIf(Git2Blog is None, "Git2Blog module nie jest dostępny")
    def test_default_values(self):
        """Test domyślnych wartości konfiguracji"""
        with patch('os.path.exists', return_value=False):
            git2blog = Git2Blog('nonexistent.yaml')
            
            self.assertEqual(git2blog.ollama_url, 'http://localhost:11434')
            self.assertEqual(git2blog.model, 'llama3.2')
            self.assertEqual(str(git2blog.output_dir), 'blog')

class TestUtilityFunctions(unittest.TestCase):
    """Testy funkcji pomocniczych"""
    
    def test_sample_commits_fixture(self):
        """Test ładowania przykładowych commitów"""
        fixtures_dir = Path(__file__).parent / 'fixtures'
        
        # Utwórz katalog fixtures jeśli nie istnieje
        fixtures_dir.mkdir(exist_ok=True)
        
        sample_commits = [
            {
                "hash": "abc123",
                "author": "Jan Kowalski", 
                "email": "jan@example.com",
                "date": "2025-01-15 10:30:00",
                "subject": "Dodaj funkcję X",
                "body": "Implementacja nowej funkcji X"
            }
        ]
        
        # Zapisz przykładowe dane
        with open(fixtures_dir / 'sample_commits.json', 'w', encoding='utf-8') as f:
            json.dump(sample_commits, f, ensure_ascii=False, indent=2)
        
        # Wczytaj i sprawdź
        with open(fixtures_dir / 'sample_commits.json', 'r', encoding='utf-8') as f:
            loaded_commits = json.load(f)
        
        self.assertEqual(len(loaded_commits), 1)
        self.assertEqual(loaded_commits[0]['author'], 'Jan Kowalski')

if __name__ == '__main__':
    # Uruchom testy
    unittest.main(verbosity=2)