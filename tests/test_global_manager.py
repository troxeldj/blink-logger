#!/usr/bin/env python3
# mypy: ignore-errors
"""
Comprehensive test suite for GlobalManager singleton class.

This module tests the GlobalManager functionality including:
- Singleton pattern implementation
- Global logger tracking and management
- Integration with Logger and LoggerBuilder
- Thread safety considerations
- Automatic logger registration

Test Coverage:
- Singleton pattern enforcement
- Global manager instance management
- Logger auto-registration from Logger constructor
- Logger auto-registration from LoggerBuilder.build()
- Thread safety of singleton creation
- Global manager operations delegation to LogManager
- State persistence across calls
"""

import pytest
import sys
import os
import threading
import time
from unittest.mock import Mock, patch

# Add the parent directory to the path to allow imports from the main library
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.global_manager import GlobalManager
from managers.log_manager import LogManager
from core.logger import Logger
from core.level import LoggingLevel
from formatters.simple_formatter import SimpleFormatter
from appenders.console_appender import ConsoleAppender
from appenders.base_appender import BaseAppender
from builders.logger_builder import LoggerBuilder


@pytest.fixture(autouse=True)
def reset_global_manager():
    """Reset GlobalManager singleton before each test."""
    # Clear the singleton instance before each test
    GlobalManager._instance = None
    yield
    # Clean up after test
    if GlobalManager._instance is not None:
        GlobalManager._instance.clear_loggers()
    GlobalManager._instance = None


@pytest.fixture
def mock_appender():
    """Fixture for creating a mock appender."""
    return Mock(spec=BaseAppender)


class TestGlobalManagerSingleton:
    """Test GlobalManager singleton pattern implementation."""
    
    def test_singleton_creation(self):
        """Test that GlobalManager creates only one instance."""
        instance1 = GlobalManager()
        instance2 = GlobalManager()
        
        assert instance1 is instance2
        assert isinstance(instance1, LogManager)
        assert isinstance(instance2, LogManager)
    
    def test_get_instance_singleton(self):
        """Test that get_instance returns the same instance."""
        instance1 = GlobalManager.get_instance()
        instance2 = GlobalManager.get_instance()
        
        assert instance1 is instance2
        assert isinstance(instance1, LogManager)
    
    def test_new_and_get_instance_same(self):
        """Test that __new__ and get_instance return the same instance."""
        instance1 = GlobalManager()
        instance2 = GlobalManager.get_instance()
        
        assert instance1 is instance2
    
    def test_singleton_properties(self):
        """Test singleton instance has correct properties."""
        instance = GlobalManager()
        
        assert instance.name == "GlobalLogManager"
        assert isinstance(instance.loggers, dict)
        assert len(instance.loggers) == 0
    
    def test_singleton_persistence(self, mock_appender):
        """Test that singleton persists state between calls."""
        # First access - add a logger
        instance1 = GlobalManager()
        logger = Logger("persistent_test", LoggingLevel.INFO, [mock_appender])
        # Note: Logger constructor automatically adds to GlobalManager, so we need to clear first
        instance1.clear_loggers()
        instance1.add_logger(logger)
        
        # Second access - should have the same logger
        instance2 = GlobalManager()
        
        assert len(instance2) == 1
        assert "persistent_test" in instance2
        assert instance2.get_logger("persistent_test") is logger


class TestGlobalManagerThreadSafety:
    """Test GlobalManager thread safety."""
    
    def test_singleton_thread_safety(self):
        """Test that singleton is thread-safe."""
        instances = []
        
        def create_instance():
            instance = GlobalManager()
            instances.append(instance)
        
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=create_instance)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All instances should be the same
        assert len(instances) == 10
        first_instance = instances[0]
        for instance in instances:
            assert instance is first_instance
    
    def test_get_instance_thread_safety(self):
        """Test that get_instance is thread-safe."""
        instances = []
        
        def get_instance():
            instance = GlobalManager.get_instance()
            instances.append(instance)
        
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=get_instance)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All instances should be the same
        assert len(instances) == 10
        first_instance = instances[0]
        for instance in instances:
            assert instance is first_instance


class TestGlobalManagerAutoRegistration:
    """Test automatic logger registration from Logger constructor."""
    
    def test_logger_auto_registration(self, mock_appender):
        """Test that Logger constructor automatically registers with GlobalManager."""
        # Clear any existing loggers
        global_manager = GlobalManager()
        global_manager.clear_loggers()
        
        # Create a logger - should auto-register
        logger = Logger("auto_registered", LoggingLevel.INFO, [mock_appender])
        
        # Check it was registered
        assert len(global_manager) == 1
        assert "auto_registered" in global_manager
        assert global_manager.get_logger("auto_registered") is logger
    
    def test_multiple_logger_auto_registration(self, mock_appender):
        """Test multiple loggers auto-register correctly."""
        global_manager = GlobalManager()
        global_manager.clear_loggers()
        
        # Create multiple loggers
        logger1 = Logger("auto1", LoggingLevel.INFO, [mock_appender])
        logger2 = Logger("auto2", LoggingLevel.DEBUG, [mock_appender])
        logger3 = Logger("auto3", LoggingLevel.WARNING, [mock_appender])
        
        # All should be registered
        assert len(global_manager) == 3
        assert "auto1" in global_manager
        assert "auto2" in global_manager
        assert "auto3" in global_manager
        assert global_manager.get_logger("auto1") is logger1
        assert global_manager.get_logger("auto2") is logger2
        assert global_manager.get_logger("auto3") is logger3
    
    def test_duplicate_name_logger_registration_error(self, mock_appender):
        """Test that duplicate logger names raise errors during auto-registration."""
        global_manager = GlobalManager()
        global_manager.clear_loggers()
        
        # Create first logger
        logger1 = Logger("duplicate", LoggingLevel.INFO, [mock_appender])
        assert len(global_manager) == 1
        
        # Create second logger with same name - should raise error
        with pytest.raises(ValueError, match="A logger with the name 'duplicate' already exists"):
            Logger("duplicate", LoggingLevel.DEBUG, [mock_appender])


class TestGlobalManagerBuilderIntegration:
    """Test GlobalManager integration with LoggerBuilder."""
    
    def test_builder_auto_registration(self, mock_appender):
        """Test that LoggerBuilder.build() automatically registers with GlobalManager."""
        global_manager = GlobalManager()
        global_manager.clear_loggers()
        
        # Build a logger using LoggerBuilder
        logger = (LoggerBuilder()
                 .set_name("builder_registered")
                 .set_level(LoggingLevel.DEBUG)
                 .add_appender(mock_appender)
                 .build())
        
        # Check it was registered
        assert len(global_manager) == 1
        assert "builder_registered" in global_manager
        assert global_manager.get_logger("builder_registered") is logger
    
    def test_multiple_builder_registrations(self, mock_appender):
        """Test multiple LoggerBuilder builds register correctly."""
        global_manager = GlobalManager()
        global_manager.clear_loggers()
        
        # Build multiple loggers
        logger1 = (LoggerBuilder()
                  .set_name("builder1")
                  
                  .add_appender(mock_appender)
                  .build())
        
        logger2 = (LoggerBuilder()
                  .set_name("builder2")
                  .set_level(LoggingLevel.WARNING)
                  
                  .add_appender(mock_appender)
                  .build())
        
        # Both should be registered
        assert len(global_manager) == 2
        assert "builder1" in global_manager
        assert "builder2" in global_manager
        assert global_manager.get_logger("builder1") is logger1
        assert global_manager.get_logger("builder2") is logger2
    
    def test_builder_duplicate_name_error(self, mock_appender):
        """Test that LoggerBuilder with duplicate name raises error."""
        global_manager = GlobalManager()
        global_manager.clear_loggers()
        
        # Build first logger
        (LoggerBuilder()
         .set_name("builder_duplicate")
         
         .add_appender(mock_appender)
         .build())
        
        # Build second logger with same name - should raise error
        with pytest.raises(ValueError, match="A logger with the name 'builder_duplicate' already exists"):
            (LoggerBuilder()
             .set_name("builder_duplicate")
             
             .add_appender(mock_appender)
             .build())


class TestGlobalManagerOperations:
    """Test GlobalManager operations delegation to LogManager."""
    
    def test_global_manager_inherits_logmanager_methods(self):
        """Test that GlobalManager has all LogManager methods."""
        global_manager = GlobalManager()
        
        # Check that it has LogManager methods
        assert hasattr(global_manager, 'add_logger')
        assert hasattr(global_manager, 'get_logger')
        assert hasattr(global_manager, 'remove_logger')
        assert hasattr(global_manager, 'get_all_loggers')
        assert hasattr(global_manager, 'clear_loggers')
        assert hasattr(global_manager, '__contains__')
        assert hasattr(global_manager, '__getitem__')
        assert hasattr(global_manager, '__setitem__')
        assert hasattr(global_manager, '__delitem__')
        assert hasattr(global_manager, '__len__')
        assert hasattr(global_manager, '__iter__')
    
    def test_manual_add_logger(self, mock_appender):
        """Test manually adding logger to GlobalManager."""
        global_manager = GlobalManager()
        global_manager.clear_loggers()
        
        logger = Logger("manual_add", LoggingLevel.INFO, [mock_appender])
        # First clear the auto-registered logger
        global_manager.clear_loggers()
        
        # Manually add the logger
        global_manager.add_logger(logger)
        
        assert len(global_manager) == 1
        assert "manual_add" in global_manager
        assert global_manager.get_logger("manual_add") is logger
    
    def test_get_all_loggers_from_global(self, mock_appender):
        """Test getting all loggers from GlobalManager."""
        global_manager = GlobalManager()
        global_manager.clear_loggers()
        
        # Create some loggers (they auto-register)
        logger1 = Logger("global1", LoggingLevel.INFO, [mock_appender])
        logger2 = Logger("global2", LoggingLevel.DEBUG, [mock_appender])
        
        all_loggers = global_manager.get_all_loggers()
        
        assert len(all_loggers) == 2
        assert logger1 in all_loggers
        assert logger2 in all_loggers
    
    def test_remove_logger_from_global(self, mock_appender):
        """Test removing logger from GlobalManager."""
        global_manager = GlobalManager()
        global_manager.clear_loggers()
        
        # Create and auto-register a logger
        logger = Logger("to_remove", LoggingLevel.INFO, [mock_appender])
        assert "to_remove" in global_manager
        
        # Remove the logger
        global_manager.remove_logger("to_remove")
        
        assert "to_remove" not in global_manager
        assert len(global_manager) == 0
    
    def test_clear_all_loggers_from_global(self, mock_appender):
        """Test clearing all loggers from GlobalManager."""
        global_manager = GlobalManager()
        global_manager.clear_loggers()
        
        # Create multiple loggers
        Logger("clear1", LoggingLevel.INFO, [mock_appender])
        Logger("clear2", LoggingLevel.DEBUG, [mock_appender])
        Logger("clear3", LoggingLevel.WARNING, [mock_appender])
        
        assert len(global_manager) == 3
        
        # Clear all
        global_manager.clear_loggers()
        
        assert len(global_manager) == 0
    
    def test_dict_like_operations_on_global(self, mock_appender):
        """Test dictionary-like operations on GlobalManager."""
        global_manager = GlobalManager()
        global_manager.clear_loggers()
        
        logger = Logger("dict_test", LoggingLevel.INFO, [mock_appender])
        global_manager.clear_loggers()  # Clear auto-registered
        
        # Test setitem
        global_manager["dict_test"] = logger
        assert "dict_test" in global_manager
        
        # Test getitem
        retrieved = global_manager["dict_test"]
        assert retrieved is logger
        
        # Test delitem
        del global_manager["dict_test"]
        assert "dict_test" not in global_manager


class TestGlobalManagerStringRepresentations:
    """Test GlobalManager string representation methods."""
    
    def test_global_manager_repr(self):
        """Test GlobalManager __repr__ method."""
        global_manager = GlobalManager()
        repr_str = repr(global_manager)
        
        # GlobalManager returns a LogManager instance, so check for LogManager repr
        assert "LogManager(loggers=" in repr_str
    
    def test_global_manager_str(self):
        """Test GlobalManager __str__ method."""
        global_manager = GlobalManager()
        str_repr = str(global_manager)
        
        # GlobalManager returns a LogManager instance, so check for LogManager str
        assert "LogManager with" in str_repr and "loggers:" in str_repr


class TestGlobalManagerMixedRegistration:
    """Test mixed registration scenarios (Logger + LoggerBuilder)."""
    
    def test_mixed_logger_and_builder_registration(self, mock_appender):
        """Test loggers from both sources register correctly."""
        global_manager = GlobalManager()
        global_manager.clear_loggers()
        
        # Create logger directly
        direct_logger = Logger("direct", LoggingLevel.INFO, [mock_appender])
        
        # Create logger via builder
        builder_logger = (LoggerBuilder()
                         .set_name("builder")
                         .set_level(LoggingLevel.DEBUG)
                         
                         .add_appender(mock_appender)
                         .build())
        
        # Both should be registered
        assert len(global_manager) == 2
        assert "direct" in global_manager
        assert "builder" in global_manager
        assert global_manager.get_logger("direct") is direct_logger
        assert global_manager.get_logger("builder") is builder_logger
    
    def test_complex_registration_scenario(self, mock_appender):
        """Test complex scenario with multiple registration types."""
        global_manager = GlobalManager()
        global_manager.clear_loggers()
        
        # Direct Logger creation
        logger1 = Logger("scenario1", LoggingLevel.INFO, [mock_appender])
        
        # LoggerBuilder creation
        logger2 = (LoggerBuilder()
                  .set_name("scenario2")
                  
                  .add_appender(mock_appender)
                  .build())
        
        # Manual addition (without auto-registration)
        logger3 = Logger("scenario3", LoggingLevel.WARNING, [mock_appender])
        global_manager.remove_logger("scenario3")  # Remove auto-registered
        global_manager.add_logger(logger3)  # Manually add
        
        # Verify all are registered correctly
        assert len(global_manager) == 3
        all_loggers = global_manager.get_all_loggers()
        assert logger1 in all_loggers
        assert logger2 in all_loggers
        assert logger3 in all_loggers


class TestGlobalManagerEdgeCases:
    """Test GlobalManager edge cases and error conditions."""
    
    def test_singleton_reset_behavior(self, mock_appender):
        """Test behavior when singleton is manually reset."""
        # Create first instance and add logger
        instance1 = GlobalManager()
        instance1.clear_loggers()
        logger = Logger("reset_test", LoggingLevel.INFO, [mock_appender])
        instance1.clear_loggers()
        instance1.add_logger(logger)
        
        assert len(instance1) == 1
        
        # Manually reset singleton (simulating what reset fixture does)
        GlobalManager._instance = None
        
        # Create new instance - should be empty
        instance2 = GlobalManager()
        assert len(instance2) == 0
        assert instance1 is not instance2
    
    def test_global_manager_with_real_appenders(self):
        """Test GlobalManager with real appender components."""
        global_manager = GlobalManager()
        global_manager.clear_loggers()
        
        # Create logger with real ConsoleAppender
        console_appender = ConsoleAppender()
        logger = Logger(
            "real_appender_test",
            LoggingLevel.INFO,
            [console_appender]
        )
        
        # Should be auto-registered
        assert "real_appender_test" in global_manager
        retrieved = global_manager.get_logger("real_appender_test")
        assert retrieved is logger
        
        # Test that logger still functions
        try:
            retrieved.log(LoggingLevel.INFO, "Test message through GlobalManager")
        except Exception as e:
            pytest.fail(f"Logger failed to log: {e}")
    
    def test_concurrent_registration_safety(self, mock_appender):
        """Test concurrent logger registration safety."""
        global_manager = GlobalManager()
        global_manager.clear_loggers()
        
        def create_logger(thread_id):
            try:
                logger = Logger(
                    f"concurrent_{thread_id}",
                    LoggingLevel.INFO,
                    [mock_appender]
                )
                return logger
            except Exception:
                return None
        
        threads = []
        results = []
        
        for i in range(5):
            thread = threading.Thread(
                target=lambda tid=i: results.append(create_logger(tid))
            )
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check results
        successful_loggers = [r for r in results if r is not None]
        assert len(successful_loggers) == 5
        assert len(global_manager) == 5


def run_manual_tests():
    """Manual test runner for verification."""
    print("Running GlobalManager manual tests...")
    
    # Reset singleton for clean test
    GlobalManager._instance = None
    
    # Test 1: Singleton pattern
    print("\n1. Testing singleton pattern:")
    try:
        instance1 = GlobalManager()
        instance2 = GlobalManager.get_instance()
        instance3 = GlobalManager()
        
        assert instance1 is instance2 is instance3
        print("✓ Singleton pattern works correctly")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Auto-registration
    print("\n2. Testing auto-registration:")
    try:
        GlobalManager._instance = None
        global_manager = GlobalManager()
        initial_count = len(global_manager)
        
        # Create logger - should auto-register
        from unittest.mock import Mock
        mock_appender = Mock(spec=BaseAppender)
        logger = Logger("manual_auto_test", LoggingLevel.INFO, [mock_appender])
        
        assert len(global_manager) == initial_count + 1
        assert "manual_auto_test" in global_manager
        print("✓ Auto-registration works correctly")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: LoggerBuilder integration
    print("\n3. Testing LoggerBuilder integration:")
    try:
        GlobalManager._instance = None
        global_manager = GlobalManager()
        global_manager.clear_loggers()
        
        # Build logger - should auto-register
        mock_appender = Mock(spec=BaseAppender)
        logger = (LoggerBuilder()
                 .set_name("manual_builder_test")
                 
                 .add_appender(mock_appender)
                 .build())
        
        assert len(global_manager) == 1
        assert "manual_builder_test" in global_manager
        assert global_manager.get_logger("manual_builder_test") is logger
        print("✓ LoggerBuilder integration works correctly")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Thread safety
    print("\n4. Testing thread safety:")
    try:
        GlobalManager._instance = None
        instances = []
        
        def create_instance():
            instances.append(GlobalManager())
        
        threads = [threading.Thread(target=create_instance) for _ in range(5)]
        
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All should be the same instance
        first = instances[0]
        assert all(instance is first for instance in instances)
        print("✓ Thread safety works correctly")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\nGlobalManager manual tests completed!")


if __name__ == "__main__":
    run_manual_tests()
