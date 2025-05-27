"""
Unit tests for the FileExporter class.
"""

# pylint: disable=W0212
import os
import threading
from unittest.mock import Mock, patch

from trainloop_llm_logging.exporter import FileExporter
from trainloop_llm_logging.types import LLMCallData


class TestFileExporter:
    """Test the FileExporter class."""

    def test_init_creates_timer(self):
        """Test that FileExporter initializes with a timer."""
        exporter = FileExporter()

        assert exporter._interval_s == 10
        assert exporter._batch_len == 5
        assert not exporter.buf
        assert exporter.lock is not None
        assert exporter.timer is not None
        assert isinstance(exporter.timer, threading.Timer)
        assert exporter.timer.daemon is True

        # Clean up
        exporter.timer.cancel()

    def test_init_with_custom_params(self):
        """Test FileExporter with custom interval and batch length."""
        exporter = FileExporter(interval=30, batch_len=10)

        assert exporter._interval_s == 30
        assert exporter._batch_len == 10

        # Clean up
        exporter.timer.cancel()

    def test_record_llm_call_checks_is_llm_request(self):
        """Test that record_llm_call checks isLLMRequest flag."""
        exporter = FileExporter()

        # Call without isLLMRequest flag
        call_data: LLMCallData = {
            "tag": "test",
            "requestBodyStr": '{"model": "gpt-4"}',
            "responseBodyStr": '{"content": "Hello"}',
        }

        exporter.record_llm_call(call_data)
        assert len(exporter.buf) == 0  # Should not be recorded

        # Call with isLLMRequest=False
        call_data["isLLMRequest"] = False
        exporter.record_llm_call(call_data)
        assert len(exporter.buf) == 0

        # Call with isLLMRequest=True
        call_data["isLLMRequest"] = True
        exporter.record_llm_call(call_data)
        assert len(exporter.buf) == 1

        # Clean up
        exporter.timer.cancel()

    @patch("trainloop_llm_logging.exporter.save_samples")
    @patch("trainloop_llm_logging.exporter.update_registry")
    @patch("trainloop_llm_logging.exporter.parse_request_body")
    @patch("trainloop_llm_logging.exporter.parse_response_body")
    @patch.dict(os.environ, {"TRAINLOOP_DATA_FOLDER": "/tmp/trainloop"})
    def test_batch_export_triggers_when_buffer_full(
        self,
        mock_parse_response,
        mock_parse_request,
        mock_update_registry,
        mock_save_samples,
    ):
        """Test that export is triggered when buffer reaches batch size."""
        # Set up mocks
        mock_parse_request.return_value = {
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "gpt-4",
            "modelParams": {},
        }
        mock_parse_response.return_value = {"content": "Hi there!"}

        exporter = FileExporter(batch_len=2)

        # Add calls to reach batch size
        call1: LLMCallData = {
            "tag": "test-1",
            "requestBodyStr": '{"model": "gpt-4"}',
            "responseBodyStr": '{"content": "Response 1"}',
            "isLLMRequest": True,
            "durationMs": 100,
            "location": {"file": "test.py", "lineNumber": "10"},
        }
        call2: LLMCallData = {
            "tag": "test-2",
            "requestBodyStr": '{"model": "gpt-4"}',
            "responseBodyStr": '{"content": "Response 2"}',
            "isLLMRequest": True,
            "durationMs": 200,
            "location": {"file": "test.py", "lineNumber": "20"},
        }

        exporter.record_llm_call(call1)
        assert len(exporter.buf) == 1
        assert mock_save_samples.call_count == 0

        exporter.record_llm_call(call2)
        assert len(exporter.buf) == 0  # Buffer should be cleared after export
        assert mock_save_samples.call_count == 1

        # Verify update_registry was called for both calls
        assert mock_update_registry.call_count == 2

        # Clean up
        exporter.timer.cancel()

    @patch("trainloop_llm_logging.exporter.save_samples")
    @patch.dict(os.environ, {}, clear=True)
    def test_export_skips_when_no_data_folder(self, mock_save_samples):
        """Test that export skips when TRAINLOOP_DATA_FOLDER is not set."""
        exporter = FileExporter()

        # Add a call
        call_data: LLMCallData = {
            "tag": "test",
            "requestBodyStr": '{"model": "gpt-4"}',
            "responseBodyStr": '{"content": "Hello"}',
            "isLLMRequest": True,
        }
        exporter.buf.append(call_data)

        # Export should clear buffer but not save
        exporter._export()

        assert len(exporter.buf) == 0
        mock_save_samples.assert_not_called()

        # Clean up
        exporter.timer.cancel()

    @patch("trainloop_llm_logging.exporter.save_samples")
    @patch("trainloop_llm_logging.exporter.update_registry")
    @patch("trainloop_llm_logging.exporter.parse_request_body")
    @patch("trainloop_llm_logging.exporter.parse_response_body")
    @patch.dict(os.environ, {"TRAINLOOP_DATA_FOLDER": "/tmp/trainloop"})
    def test_export_handles_parse_failures(
        self,
        mock_parse_response,
        mock_parse_request,
        mock_update_registry,
        mock_save_samples,
    ):
        """Test that export handles parse failures gracefully."""
        # Set up mocks to return None (parse failure)
        mock_parse_request.return_value = None
        mock_parse_response.return_value = {"content": "Response"}

        exporter = FileExporter()

        # Add calls
        call_data: LLMCallData = {
            "tag": "test",
            "requestBodyStr": "invalid json",
            "responseBodyStr": '{"content": "Response"}',
            "isLLMRequest": True,
        }
        exporter.buf.append(call_data)

        exporter._export()

        # Should clear buffer but not save any samples
        assert len(exporter.buf) == 0
        mock_save_samples.assert_called_once_with("/tmp/trainloop", [])  # Empty list

        # Clean up
        exporter.timer.cancel()

    @patch("trainloop_llm_logging.exporter.save_samples")
    @patch("trainloop_llm_logging.exporter.update_registry")
    @patch("trainloop_llm_logging.exporter.parse_request_body")
    @patch("trainloop_llm_logging.exporter.parse_response_body")
    @patch("trainloop_llm_logging.exporter.caller_site")
    @patch.dict(os.environ, {"TRAINLOOP_DATA_FOLDER": "/tmp/trainloop"})
    def test_export_creates_collected_samples(
        self,
        mock_caller_site,
        mock_parse_response,
        mock_parse_request,
        mock_update_registry,
        mock_save_samples,
    ):
        """Test that export creates CollectedSample objects correctly."""
        # Set up mocks
        mock_parse_request.return_value = {
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "gpt-4",
            "modelParams": {"temperature": 0.7},
        }
        mock_parse_response.return_value = {"content": "Hi there!"}
        mock_caller_site.return_value = {"file": "auto.py", "lineNumber": "50"}

        exporter = FileExporter()

        # Add a call with all fields
        call_data: LLMCallData = {
            "tag": "test-tag",
            "requestBodyStr": '{"model": "gpt-4"}',
            "responseBodyStr": '{"content": "Hi"}',
            "isLLMRequest": True,
            "durationMs": 150,
            "startTimeMs": 1000,
            "endTimeMs": 1150,
            "url": "https://api.openai.com/v1/chat/completions",
            "location": {"file": "test.py", "lineNumber": "25"},
        }
        exporter.buf.append(call_data)

        exporter._export()

        # Verify the sample was created correctly
        mock_save_samples.assert_called_once()
        samples = mock_save_samples.call_args[0][1]
        assert len(samples) == 1

        sample = samples[0]
        assert sample["tag"] == "test-tag"
        assert sample["input"] == [{"role": "user", "content": "Hello"}]
        assert sample["output"] == {"content": "Hi there!"}
        assert sample["model"] == "gpt-4"
        assert sample["modelParams"] == {"temperature": 0.7}
        assert sample["durationMs"] == 150
        assert sample["startTimeMs"] == 1000
        assert sample["endTimeMs"] == 1150
        assert sample["url"] == "https://api.openai.com/v1/chat/completions"
        assert sample["location"] == {"file": "test.py", "lineNumber": "25"}

        # Clean up
        exporter.timer.cancel()

    @patch("trainloop_llm_logging.exporter.threading.Timer")
    @patch("trainloop_llm_logging.exporter.save_samples")
    @patch.dict(os.environ, {"TRAINLOOP_DATA_FOLDER": "/tmp/trainloop"})
    def test_flush_loop_reschedules(self, mock_save_samples, mock_timer_class):
        """Test that _flush_loop reschedules itself."""
        # Create mock timer
        mock_timer = Mock()
        mock_timer_class.return_value = mock_timer

        exporter = FileExporter(interval=5)

        # Reset mock to track new timer creation
        mock_timer_class.reset_mock()

        # Call flush loop
        exporter._flush_loop()

        # Should create a new timer
        mock_timer_class.assert_called_once_with(5, exporter._flush_loop)
        mock_timer.daemon = True
        mock_timer.start.assert_called_once()

        # Clean up original timer
        exporter.timer.cancel()

    @patch("trainloop_llm_logging.exporter.save_samples")
    @patch.dict(os.environ, {"TRAINLOOP_DATA_FOLDER": "/tmp/trainloop"})
    def test_flush_exports_immediately(self, mock_save_samples):
        """Test that flush() exports immediately."""
        exporter = FileExporter()

        # Add some calls
        for i in range(3):
            call_data: LLMCallData = {
                "tag": f"test-{i}",
                "requestBodyStr": '{"model": "gpt-4"}',
                "responseBodyStr": '{"content": "Response"}',
                "isLLMRequest": True,
            }
            exporter.buf.append(call_data)

        # Flush should export immediately
        exporter.flush()

        assert len(exporter.buf) == 0

        # Clean up
        exporter.timer.cancel()

    @patch("trainloop_llm_logging.exporter.save_samples")
    @patch.dict(os.environ, {"TRAINLOOP_DATA_FOLDER": "/tmp/trainloop"})
    def test_shutdown_cancels_timer_and_flushes(self, mock_save_samples):
        """Test that shutdown cancels timer and flushes remaining data."""
        exporter = FileExporter()

        # Add a call
        call_data: LLMCallData = {
            "tag": "shutdown-test",
            "requestBodyStr": '{"model": "gpt-4"}',
            "responseBodyStr": '{"content": "Response"}',
            "isLLMRequest": True,
        }
        exporter.buf.append(call_data)

        # Mock the timer
        mock_timer = Mock()
        exporter.timer = mock_timer

        exporter.shutdown()

        # Should cancel timer
        mock_timer.cancel.assert_called_once()

        # Should flush remaining data
        assert len(exporter.buf) == 0

    # @patch("trainloop_llm_logging.exporter.save_samples")
    # @patch("trainloop_llm_logging.exporter.update_registry")
    # @patch("trainloop_llm_logging.exporter.parse_request_body")
    # @patch("trainloop_llm_logging.exporter.parse_response_body")
    # @patch.dict(os.environ, {"TRAINLOOP_DATA_FOLDER": "/tmp/trainloop"})
    # def test_thread_safety_concurrent_records(
    #     self,
    #     mock_parse_response,
    #     mock_parse_request,
    #     mock_update_registry,
    #     mock_save_samples,
    # ):
    #     """Test thread safety when recording calls concurrently."""
    #     # Set up mocks to prevent actual export
    #     mock_parse_request.return_value = {
    #         "model": "gpt-4",
    #         "messages": [{"role": "user", "content": "test"}],
    #         "modelParams": {},
    #     }
    #     mock_parse_response.return_value = {"content": "Response"}

    #     # Prevent the timer from auto-flushing during the test
    #     with patch("trainloop_llm_logging.exporter.threading.Timer") as mock_timer:
    #         # Make the mock timer do nothing
    #         mock_timer.return_value = Mock(daemon=True, start=Mock())

    #         exporter = FileExporter(
    #             batch_len=100
    #         )  # High batch size to avoid auto-export

    #         # Create multiple threads that record calls
    #         num_threads = 10
    #         calls_per_thread = 10

    #         def record_calls(thread_id):
    #             for i in range(calls_per_thread):
    #                 call_data: LLMCallData = {
    #                     "tag": f"thread-{thread_id}-call-{i}",
    #                     "requestBodyStr": '{"model": "gpt-4"}',
    #                     "responseBodyStr": '{"content": "Response"}',
    #                     "isLLMRequest": True,
    #                 }
    #                 exporter.record_llm_call(call_data)

    #         threads = []
    #         for i in range(num_threads):
    #             thread = threading.Thread(target=record_calls, args=(i,))
    #             threads.append(thread)
    #             thread.start()

    #         # Wait for all threads
    #         for thread in threads:
    #             thread.join()

    #         # All calls should be in buffer
    #         assert len(exporter.buf) == num_threads * calls_per_thread

    @patch("trainloop_llm_logging.exporter.save_samples")
    @patch("trainloop_llm_logging.exporter.update_registry")
    @patch("trainloop_llm_logging.exporter.parse_request_body")
    @patch("trainloop_llm_logging.exporter.parse_response_body")
    @patch("trainloop_llm_logging.exporter.caller_site")
    @patch.dict(os.environ, {"TRAINLOOP_DATA_FOLDER": "/tmp/trainloop"})
    def test_export_uses_caller_site_when_no_location(
        self,
        mock_caller_site,
        mock_parse_response,
        mock_parse_request,
        mock_update_registry,
        mock_save_samples,
    ):
        """Test that export uses caller_site() when location is not provided."""
        # Set up mocks
        mock_parse_request.return_value = {
            "messages": [],
            "model": "gpt-4",
            "modelParams": {},
        }
        mock_parse_response.return_value = {"content": "Response"}
        mock_caller_site.return_value = {"file": "unknown.py", "lineNumber": "0"}

        exporter = FileExporter()

        # Add call without location
        call_data: LLMCallData = {
            "tag": "no-location",
            "requestBodyStr": "{}",
            "responseBodyStr": "{}",
            "isLLMRequest": True,
        }
        exporter.buf.append(call_data)

        exporter._export()

        # Should have used caller_site
        mock_caller_site.assert_called_once()

        # Verify update_registry was called with fallback location
        mock_update_registry.assert_called_once_with(
            "/tmp/trainloop", {"file": "unknown.py", "lineNumber": "0"}, "no-location"
        )

        # Clean up
        exporter.timer.cancel()
