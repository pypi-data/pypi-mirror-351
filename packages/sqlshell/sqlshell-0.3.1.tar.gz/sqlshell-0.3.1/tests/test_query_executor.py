import unittest
from PyQt6.QtCore import QObject
from sqlshell.query_executor import QueryExecutor

class TestQueryExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = QueryExecutor()
        
    def test_get_current_query_single_query(self):
        text = "SELECT * FROM users;"
        cursor_pos = 10
        query = self.executor.get_current_query(text, cursor_pos)
        self.assertEqual(query, "SELECT * FROM users;")
        
    def test_get_current_query_multiple_queries(self):
        text = """SELECT * FROM users;
SELECT * FROM orders;
SELECT * FROM products;"""
        cursor_pos = 30  # Position in second query
        query = self.executor.get_current_query(text, cursor_pos)
        self.assertEqual(query, "SELECT * FROM orders;")
        
    def test_get_current_query_no_semicolon(self):
        text = "SELECT * FROM users"
        cursor_pos = 10
        query = self.executor.get_current_query(text, cursor_pos)
        self.assertEqual(query, "SELECT * FROM users;")
        
    def test_get_all_queries_simple(self):
        text = """SELECT * FROM users;
SELECT * FROM orders;
SELECT * FROM products;"""
        queries = self.executor.get_all_queries(text)
        self.assertEqual(len(queries), 3)
        self.assertEqual(queries[0], "SELECT * FROM users;")
        self.assertEqual(queries[1], "SELECT * FROM orders;")
        self.assertEqual(queries[2], "SELECT * FROM products;")
        
    def test_get_all_queries_with_strings(self):
        text = """SELECT * FROM users WHERE name = 'John; Doe';
SELECT * FROM orders;"""
        queries = self.executor.get_all_queries(text)
        self.assertEqual(len(queries), 2)
        self.assertEqual(queries[0], "SELECT * FROM users WHERE name = 'John; Doe';")
        
    def test_get_all_queries_with_comments(self):
        text = """-- This is a comment
SELECT * FROM users; -- Another comment
/* Multi-line
   comment */
SELECT * FROM orders;"""
        queries = self.executor.get_all_queries(text)
        self.assertEqual(len(queries), 2)
        self.assertEqual(queries[0], "-- This is a comment\nSELECT * FROM users; -- Another comment")
        self.assertEqual(queries[1], "/* Multi-line\n   comment */\nSELECT * FROM orders;")
        
    def test_execute_current_query(self):
        text = """SELECT * FROM users;
SELECT * FROM orders;"""
        cursor_pos = 30  # Position in second query
        
        # Track emitted signals
        executed_queries = []
        def on_query_executed(query):
            executed_queries.append(query)
            
        self.executor.query_executed.connect(on_query_executed)
        
        query = self.executor.execute_current_query(text, cursor_pos)
        self.assertEqual(query, "SELECT * FROM orders;")
        self.assertEqual(len(executed_queries), 1)
        self.assertEqual(executed_queries[0], "SELECT * FROM orders;")
        
    def test_execute_all_queries(self):
        text = """SELECT * FROM users;
SELECT * FROM orders;
SELECT * FROM products;"""
        
        # Track emitted signals
        executed_queries = []
        def on_query_executed(query):
            executed_queries.append(query)
            
        self.executor.query_executed.connect(on_query_executed)
        
        queries = self.executor.execute_all_queries(text)
        self.assertEqual(len(queries), 3)
        self.assertEqual(len(executed_queries), 3)
        self.assertEqual(executed_queries, queries)

if __name__ == '__main__':
    unittest.main() 