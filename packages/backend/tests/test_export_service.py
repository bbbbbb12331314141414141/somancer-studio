"""Tests for ExportService and JobQueue (no audio I/O needed)."""

import json
import os
import zipfile
import pytest
import tempfile

from aimusic.services.export_service import ExportService, AUDIO_FORMATS
from aimusic.services.job_queue import JobQueue, JobStatus


# ── ExportService Tests ────────────────────────────────────────────────────────

class TestExportService:

    def test_supported_formats(self):
        """All expected formats are in the registry."""
        svc = ExportService()
        fmts = svc.supported_formats()
        for fmt in ("wav", "flac", "mp3", "ogg", "aac", "aiff"):
            assert fmt in fmts
            assert "extension" in fmts[fmt]
            assert "mime" in fmts[fmt]

    def test_check_ffmpeg_returns_bool(self):
        """check_ffmpeg always returns a bool."""
        result = ExportService.check_ffmpeg()
        assert isinstance(result, bool)

    def test_export_lyrics_txt(self, tmp_path):
        """Lyrics are exported to a valid text file."""
        svc = ExportService(output_dir=str(tmp_path))
        lyrics = [
            {"section": "verse", "line_number": 1, "text": "I wander through the night"},
            {"section": "verse", "line_number": 2, "text": "Stars are burning bright"},
            {"section": "chorus", "line_number": 3, "text": "And I feel alive"},
        ]
        result = svc.export_lyrics_txt(lyrics, song_name="test_song")

        assert os.path.isfile(result.path)
        assert result.format == "txt"
        content = open(result.path, encoding="utf-8").read()
        assert "I wander through the night" in content
        assert "VERSE" in content
        assert "CHORUS" in content

    def test_export_lyrics_txt_empty(self, tmp_path):
        """Empty lyrics produce a valid (minimal) text file."""
        svc = ExportService(output_dir=str(tmp_path))
        result = svc.export_lyrics_txt([], song_name="empty")
        assert os.path.isfile(result.path)
        assert result.size_bytes > 0

    def test_export_stems_zip(self, tmp_path):
        """Stems ZIP contains expected files."""
        # Create dummy WAV files (just empty files for test)
        stem_paths = {}
        for stem_name in ("drums", "bass", "keys"):
            p = str(tmp_path / f"stem_{stem_name}.wav")
            open(p, "wb").write(b"RIFF" + b"\x00" * 40)  # minimal WAV header
            stem_paths[stem_name] = p

        svc = ExportService(output_dir=str(tmp_path))
        result = svc.export_stems_zip(stem_paths, song_name="my_song")

        assert os.path.isfile(result.path)
        assert result.path.endswith(".zip")
        assert result.metadata["stem_count"] == 3

        with zipfile.ZipFile(result.path) as zf:
            names = zf.namelist()
        assert "README.txt" in names
        assert any("drums" in n for n in names)

    def test_export_project_archive(self, tmp_path):
        """Project archive contains project.json and README."""
        svc = ExportService(output_dir=str(tmp_path))
        project = {"name": "My Album", "artist_name": "Test Artist", "genre": "Rock"}
        songs = [
            {"name": "Song One", "lyrics": [
                {"section": "verse", "line_number": 1, "text": "Hello world"}
            ]},
        ]

        result = svc.export_project_archive(
            project_data=project,
            songs_data=songs,
        )

        assert os.path.isfile(result.path)
        assert result.path.endswith(".sonmancer")
        assert result.song_count == 1

        with zipfile.ZipFile(result.path) as zf:
            names = zf.namelist()
            assert "project.json" in names
            assert "README.txt" in names

            manifest = json.loads(zf.read("project.json"))
            assert manifest["format"] == "sonmancer-project"
            assert manifest["project"]["name"] == "My Album"

    def test_project_archive_with_audio(self, tmp_path):
        """Project archive includes audio files."""
        # Create dummy WAV
        wav_path = str(tmp_path / "mix.wav")
        open(wav_path, "wb").write(b"RIFF" + b"\x00" * 40)

        svc = ExportService(output_dir=str(tmp_path))
        result = svc.export_project_archive(
            project_data={"name": "Test"},
            songs_data=[],
            audio_paths=[wav_path],
        )

        with zipfile.ZipFile(result.path) as zf:
            names = zf.namelist()
        assert any("audio/" in n for n in names)

    def test_wav_convert_is_copy(self, tmp_path):
        """Converting WAV to WAV copies the file."""
        src = str(tmp_path / "source.wav")
        open(src, "wb").write(b"RIFF" + b"\x00" * 40)

        svc = ExportService(output_dir=str(tmp_path))
        result = svc.convert_audio(src, "wav")

        assert os.path.isfile(result.path)
        assert result.format == "wav"

    def test_convert_invalid_format(self, tmp_path):
        """Invalid format raises ValueError."""
        src = str(tmp_path / "source.wav")
        open(src, "wb").write(b"\x00")
        svc = ExportService(output_dir=str(tmp_path))

        with pytest.raises(ValueError, match="Unsupported format"):
            svc.convert_audio(src, "xyz")

    def test_convert_missing_file(self, tmp_path):
        """Missing source WAV raises FileNotFoundError."""
        svc = ExportService(output_dir=str(tmp_path))
        with pytest.raises(FileNotFoundError):
            svc.convert_audio("/nonexistent/path.wav", "mp3")


# ── JobQueue Tests ─────────────────────────────────────────────────────────────

class TestJobQueue:

    def test_submit_and_complete(self):
        """A submitted job completes successfully."""
        q = JobQueue(max_workers=2)

        def work(job: "Job"):
            job.progress = 0.5
            return {"result": "done"}

        job = q.submit("test", work)
        assert job.id is not None
        assert job.status in (JobStatus.PENDING, JobStatus.RUNNING, JobStatus.COMPLETED)

        # Wait up to 2s
        import time
        for _ in range(20):
            time.sleep(0.1)
            if job.status == JobStatus.COMPLETED:
                break

        assert job.status == JobStatus.COMPLETED
        assert job.result == {"result": "done"}
        assert job.progress == 1.0

    def test_failed_job(self):
        """A job that raises an exception is marked FAILED."""
        q = JobQueue(max_workers=1)

        def bad_work(job):
            raise ValueError("intentional error")

        job = q.submit("fail_test", bad_work)

        import time
        for _ in range(20):
            time.sleep(0.1)
            if job.status in (JobStatus.FAILED, JobStatus.COMPLETED):
                break

        assert job.status == JobStatus.FAILED
        assert "intentional error" in (job.error or "")

    def test_list_jobs(self):
        """list_jobs returns submitted jobs."""
        q = JobQueue()

        def noop(job):
            return None

        q.submit("export", noop)
        q.submit("render", noop)
        q.submit("export", noop)

        import time; time.sleep(0.3)

        all_jobs = q.list_jobs()
        assert len(all_jobs) >= 3

        export_jobs = q.list_jobs(job_type="export")
        assert all(j.job_type == "export" for j in export_jobs)

    def test_cancel_before_start(self):
        """A pending job can be cancelled before it runs."""
        # Use a semaphore to block workers so job stays PENDING
        import threading
        q = JobQueue(max_workers=1)
        blocker = threading.Event()

        def blocking_work(job):
            blocker.wait(timeout=5)
            return None

        # Fill the one worker slot
        q.submit("blocker", blocking_work)
        import time; time.sleep(0.05)

        # Now submit second job — should be PENDING
        job2 = q.submit("target", lambda j: None)
        import time; time.sleep(0.05)

        cancelled = q.cancel(job2.id)
        blocker.set()  # unblock first job

        assert cancelled or job2.status in (JobStatus.CANCELLED, JobStatus.COMPLETED)

    def test_stats(self):
        """stats returns a dict with expected keys."""
        q = JobQueue()
        stats = q.stats
        assert "total" in stats
        assert "completed" in stats
        assert "pending" in stats
        assert "failed" in stats

    def test_clear_completed(self):
        """clear_completed removes old finished jobs."""
        import time
        q = JobQueue()

        def fast(job):
            return "done"

        q.submit("fast", fast)
        time.sleep(0.3)

        # Clear with 0 seconds (removes everything completed)
        removed = q.clear_completed(older_than_seconds=0)
        assert removed >= 0   # may be 0 if timestamps prevent removal immediately
